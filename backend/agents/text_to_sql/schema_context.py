"""
Database schema context for text-to-SQL agent.
Exhaustive column-level reference derived from db/db-table-schema.md.
This is fed verbatim into the LLM system prompt — be precise and explicit.
"""

SCHEMA_CONTEXT = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KARNATAKA POLICE FIR DATABASE — COMPLETE SCHEMA REFERENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ZCQL JOIN SYNTAX NOTE:
  All primary key joins use ROWID, NOT the named PK column.
  Pattern: ChildTable.ForeignKeyColumn = ParentTable.ROWID
  Example: Unit.ROWID = CaseMaster.PoliceStationID

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORE TABLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TABLE: CaseMaster  [CENTRAL — start every query here]
  COLUMNS (exact names, case-sensitive):
    CaseMasterID        INT   PK
    CrimeNo             VARCHAR  — structured FIR number (e.g. "104430006202600001")
    CaseNo              VARCHAR  — shorter case number
    CrimeRegisteredDate DATE     — when FIR was FILED at police station
    IncidentFromDate    DATETIME — when crime HAPPENED (use this for "when did it occur")
    IncidentToDate      DATETIME — end of incident
    InfoReceivedPSDate  DATETIME — when police station received info
    PolicePersonID      INT   FK → Employee.ROWID
    PoliceStationID     INT   FK → Unit.ROWID
    CaseCategoryID      INT   FK → CaseCategory.ROWID
    GravityOffenceID    INT   FK → GravityOffence.ROWID
    CrimeMajorHeadID    INT   FK → CrimeHead.ROWID
    CrimeMinorHeadID    INT   FK → CrimeSubHead.ROWID   ← most specific crime type
    CaseStatusID        INT   FK → CaseStatusMaster.ROWID
    CourtID             INT   FK → Court.ROWID
    latitude            DECIMAL  — can be NULL; always filter IS NOT NULL for geo queries
    longitude           DECIMAL  — can be NULL
    BriefFacts          TEXT     — full narrative of the case
  ❌ COLUMNS THAT DO NOT EXIST ON CaseMaster:
    DistrictID, DistrictName, UnitName, CrimeType, StatusName, AccusedName, VictimName

TABLE: CrimeSubHead  [specific crime type]
  COLUMNS:
    CrimeSubHeadID   INT   PK
    CrimeHeadID      INT   FK → CrimeHead.ROWID
    CrimeHeadName    VARCHAR — e.g. "Murder", "Robbery", "Chain Snatching", "Vehicle Theft"
    SeqID            INT
  JOIN PATTERN: CrimeSubHead.ROWID = CaseMaster.CrimeMinorHeadID
  ❌ Does NOT have: CrimeName, CrimeType, SubHeadName

TABLE: CrimeHead  [broad crime group]
  COLUMNS:
    CrimeHeadID      INT   PK
    CrimeGroupName   VARCHAR — e.g. "Crimes Against Body", "Crimes Against Property"
    Active           BIT
  JOIN PATTERN: CrimeHead.ROWID = CaseMaster.CrimeMajorHeadID  (or via CrimeSubHead.CrimeHeadID)
  ❌ Does NOT have: CrimeHeadName (that column is on CrimeSubHead)

TABLE: CaseStatusMaster  [case status]
  COLUMNS:
    CaseStatusID     INT   PK
    CaseStatusName   VARCHAR — values: "Under Investigation", "Charge Sheeted", "Closed", "Referred to Court", "Stayed"
  JOIN PATTERN: CaseStatusMaster.ROWID = CaseMaster.CaseStatusID

TABLE: Unit  [police station]
  COLUMNS:
    UnitID           INT   PK
    UnitName         VARCHAR — name of police station
    TypeID           INT   FK → UnitType.ROWID
    ParentUnit       INT   self-ref
    StateID          INT   FK → State.ROWID
    DistrictID       INT   FK → District.ROWID
    Active           BIT
  JOIN PATTERN: Unit.ROWID = CaseMaster.PoliceStationID
  ❌ Does NOT have: StationName, PoliceStation

TABLE: District  [geography]
  COLUMNS:
    DistrictID       INT   PK
    DistrictName     VARCHAR — e.g. "Bengaluru Urban", "Mysuru", "Dakshina Kannada"
    StateID          INT   FK → State.ROWID
    Active           BIT
  JOIN PATTERN: District.ROWID = Unit.DistrictID
  NOTE: There is NO DistrictID column on CaseMaster. Always go CaseMaster → Unit → District.

TABLE: State
  COLUMNS:
    StateID          INT   PK
    StateName        VARCHAR
    Active           BIT
  JOIN PATTERN: State.ROWID = District.StateID

TABLE: Accused  [per-FIR, one row per accused person]
  COLUMNS:
    AccusedMasterID  INT   PK
    CaseMasterID     INT   FK → CaseMaster.ROWID
    AccusedName      VARCHAR — full name of accused
    AgeYear          INT   — age at time of FIR (can be NULL)
    GenderID         INT   — M/F/T
    PersonID         VARCHAR — "A1", "A2", "A3"… A1 = primary accused
  JOIN PATTERN: CaseMaster.ROWID = Accused.CaseMasterID
  ❌ Does NOT have: Name, Age, Accused, AccusedID, FIRId

TABLE: Victim  [per-FIR, one row per victim]
  COLUMNS:
    VictimMasterID   INT   PK
    CaseMasterID     INT   FK → CaseMaster.ROWID
    VictimName       VARCHAR — full name of victim
    AgeYear          INT
    GenderID         INT
    VictimPolice     VARCHAR — "1" if victim is a police officer
  JOIN PATTERN: CaseMaster.ROWID = Victim.CaseMasterID
  ❌ Does NOT have: Name, Age, VictimID

TABLE: ArrestSurrender  [arrest/surrender events]
  COLUMNS:
    ArrestSurrenderID         INT   PK
    CaseMasterID              INT   FK → CaseMaster.ROWID
    AccusedMasterID           INT   FK → Accused.ROWID
    ArrestSurrenderDate       DATE
    ArrestSurrenderStateId    INT   FK → State.ROWID
    ArrestSurrenderDistrictId INT   FK → District.ROWID
    PoliceStationID           INT   FK → Unit.ROWID
    IOID                      INT   FK → Employee.ROWID  (Investigating Officer)
    CourtID                   INT   FK → Court.ROWID
    IsAccused                 BIT
    IsComplainantAccused      BIT
  JOIN PATTERN: CaseMaster.ROWID = ArrestSurrender.CaseMasterID
  NOTE: Accused with NO ArrestSurrender row = still absconding. Use LEFT JOIN to detect.

TABLE: ComplainantDetails
  COLUMNS:
    ComplainantID    INT   PK
    CaseMasterID     INT   FK → CaseMaster.ROWID
    ComplainantName  VARCHAR
    AgeYear          INT
    OccupationID     INT   FK → OccupationMaster.ROWID
    ReligionID       INT   FK → ReligionMaster.ROWID
    CasteID          INT   FK → CasteMaster.ROWID
    GenderID         INT
  JOIN PATTERN: CaseMaster.ROWID = ComplainantDetails.CaseMasterID

TABLE: ChargesheetDetails  [final legal outcome — NOT all cases have one]
  COLUMNS:
    CSID             INT   PK
    CaseMasterID     INT   FK → CaseMaster.ROWID
    csdate           DATETIME
    cstype           CHAR — "A"=Chargesheeted, "B"=False Case, "C"=Undetected/Unsolved
    PolicePersonID   INT   FK → Employee.ROWID
  JOIN PATTERN: LEFT JOIN ChargesheetDetails ON CaseMaster.ROWID = ChargesheetDetails.CaseMasterID
  ⚠️  ALWAYS use LEFT JOIN — only resolved cases have a chargesheet row.

TABLE: ActSectionAssociation  [legal acts & sections per case]
  COLUMNS:
    CaseMasterID     INT   FK → CaseMaster.ROWID
    ActID            INT   FK → Act.ROWID
    SectionID        INT   FK → Section.ROWID
    ActOrderID       INT
    SectionOrderID   INT
  JOIN PATTERN: CaseMaster.ROWID = ActSectionAssociation.CaseMasterID

TABLE: Act  [legal acts, e.g. IPC, NDPS]
  COLUMNS:
    ActCode          VARCHAR PK
    ActDescription   VARCHAR
    ShortName        VARCHAR
    Active           BIT
  JOIN PATTERN: Act.ROWID = ActSectionAssociation.ActID

TABLE: Section  [sections within an act]
  COLUMNS:
    ActCode          VARCHAR FK → Act.ROWID
    SectionCode      VARCHAR — e.g. "302", "379", "420"
    SectionDescription VARCHAR
    Active           BIT
  JOIN PATTERN: Section.ROWID = ActSectionAssociation.SectionID

TABLE: Employee  [police staff]
  COLUMNS:
    EmployeeID       INT   PK
    DistrictID       INT   FK → District.ROWID
    UnitID           INT   FK → Unit.ROWID
    RankID           INT   FK → Rank.ROWID
    DesignationID    INT   FK → Designation.ROWID
    KGID             VARCHAR
    FirstName        VARCHAR
    EmployeeDOB      DATE
    GenderID         INT
  JOIN PATTERN: Employee.ROWID = CaseMaster.PolicePersonID

TABLE: GravityOffence  [severity of offence]
  COLUMNS:
    GravityOffenceID INT   PK
    LookupValue      VARCHAR — "Heinous", "Serious", "Non-Heinous"
  JOIN PATTERN: GravityOffence.ROWID = CaseMaster.GravityOffenceID

TABLE: CaseCategory
  COLUMNS:
    CaseCategoryID   INT   PK
    LookupValue      VARCHAR — "FIR", "UDR", "PAR", "Zero FIR"
  JOIN PATTERN: CaseCategory.ROWID = CaseMaster.CaseCategoryID

TABLE: Court
  COLUMNS:
    CourtID          INT   PK
    CourtName        VARCHAR
    DistrictID       INT   FK → District.ROWID
    StateID          INT   FK → State.ROWID
    Active           BIT

TABLE: OccupationMaster
  COLUMNS:
    OccupationID     INT   PK
    OccupationName   VARCHAR

TABLE: CasteMaster  [NOTE: lowercase column names]
  COLUMNS:
    caste_master_id   INT   PK   ← all lowercase
    caste_master_name VARCHAR   ← all lowercase
  JOIN PATTERN: CasteMaster.caste_master_id = ComplainantDetails.CasteID  (do NOT use ROWID here)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DERIVED / ANALYTICS TABLES (Drishti-specific)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TABLE: dashboard_stats
  COLUMNS: stat_id, computed_at, total_firs, active_cases,
           high_risk_offender_count, active_alert_count,
           district_crime_json, trend_sparklines_json

TABLE: crime_alerts
  COLUMNS: alert_id, created_at, district_id, crime_sub_head_id,
           spike_ratio, severity, alert_message, is_acknowledged

TABLE: risk_scores
  COLUMNS: risk_score_id, accused_name, accused_age, gender_id,
           fir_count, district_ids, crime_types, is_absconding,
           gravity_avg, risk_score, mo_tag, computed_at

TABLE: conversations
  COLUMNS: conversation_id, user_id, session_id, role, content,
           sql_generated, created_at

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NATURAL LANGUAGE → COLUMN MAPPING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"district" / "location"     → District.DistrictName
"crime type" / "crime"      → CrimeSubHead.CrimeHeadName
"broad crime group"         → CrimeHead.CrimeGroupName
"status" / "case status"    → CaseStatusMaster.CaseStatusName
"police station" / "unit"   → Unit.UnitName
"FIR number" / "FIR no"     → CaseMaster.CrimeNo
"case number"               → CaseMaster.CaseNo
"when crime happened"       → CaseMaster.IncidentFromDate
"when FIR was filed"        → CaseMaster.CrimeRegisteredDate
"accused name"              → Accused.AccusedName
"victim name"               → Victim.VictimName
"age of accused"            → Accused.AgeYear
"age of victim"             → Victim.AgeYear
"gravity" / "severity"      → GravityOffence.LookupValue
"absconding"                → Accused LEFT JOIN ArrestSurrender WHERE ArrestSurrender.ROWID IS NULL
"under investigation"       → CaseStatusMaster.CaseStatusName = 'Under Investigation'
"chargesheeted"             → ChargesheetDetails.cstype = 'A'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXACT JOIN PATTERNS (copy these exactly)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Geography (district filter):
  INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
  INNER JOIN District ON Unit.DistrictID = District.ROWID

Crime type:
  INNER JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID

Status:
  INNER JOIN CaseStatusMaster ON CaseMaster.CaseStatusID = CaseStatusMaster.ROWID

Accused:
  INNER JOIN Accused ON CaseMaster.ROWID = Accused.CaseMasterID

Victim:
  INNER JOIN Victim ON CaseMaster.ROWID = Victim.CaseMasterID

ArrestSurrender:
  LEFT JOIN ArrestSurrender ON CaseMaster.ROWID = ArrestSurrender.CaseMasterID

Chargesheet:
  LEFT JOIN ChargesheetDetails ON CaseMaster.ROWID = ChargesheetDetails.CaseMasterID

Gravity:
  INNER JOIN GravityOffence ON CaseMaster.GravityOffenceID = GravityOffence.ROWID

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WORKING EXAMPLE QUERIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Query: "Show me robbery cases in Bengaluru North"
SELECT CaseMaster.CrimeNo, CrimeSubHead.CrimeHeadName, District.DistrictName, CaseStatusMaster.CaseStatusName
FROM CaseMaster
INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
INNER JOIN District ON Unit.DistrictID = District.ROWID
INNER JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
INNER JOIN CaseStatusMaster ON CaseMaster.CaseStatusID = CaseStatusMaster.ROWID
WHERE District.DistrictName = 'Bengaluru North' AND CrimeSubHead.CrimeHeadName LIKE '*Robbery*'
LIMIT 50

Query: "Murder cases under investigation since 2026"
SELECT CaseMaster.CrimeNo, CaseMaster.IncidentFromDate, Unit.UnitName, CrimeSubHead.CrimeHeadName
FROM CaseMaster
INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
INNER JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
INNER JOIN CaseStatusMaster ON CaseMaster.CaseStatusID = CaseStatusMaster.ROWID
WHERE CrimeSubHead.CrimeHeadName LIKE '*Murder*' AND CaseStatusMaster.CaseStatusName = 'Under Investigation'
AND CaseMaster.IncidentFromDate >= '2026-01-01'
LIMIT 50

Query: "Find accused named Raju"
SELECT CaseMaster.CrimeNo, Accused.AccusedName, Accused.AgeYear, CrimeSubHead.CrimeHeadName, District.DistrictName
FROM CaseMaster
INNER JOIN Accused ON CaseMaster.ROWID = Accused.CaseMasterID
INNER JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
INNER JOIN District ON Unit.DistrictID = District.ROWID
WHERE Accused.AccusedName LIKE '*Raju*'
LIMIT 50

Query: "Count FIRs per district"
SELECT District.DistrictName, COUNT(CaseMaster.ROWID) as case_count
FROM CaseMaster
INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
INNER JOIN District ON Unit.DistrictID = District.ROWID
GROUP BY District.DistrictName
ORDER BY case_count DESC

Query: "Theft cases where accused is absconding"
SELECT CaseMaster.CrimeNo, Accused.AccusedName, Accused.AgeYear, District.DistrictName
FROM CaseMaster
INNER JOIN Accused ON CaseMaster.ROWID = Accused.CaseMasterID
INNER JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
INNER JOIN District ON Unit.DistrictID = District.ROWID
LEFT JOIN ArrestSurrender ON Accused.ROWID = ArrestSurrender.AccusedMasterID
WHERE CrimeSubHead.CrimeHeadName LIKE '*Theft*' AND ArrestSurrender.ROWID IS NULL
LIMIT 50

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Start every query from CaseMaster.
2. Geography path: CaseMaster → Unit (PoliceStationID) → District (DistrictID). NO SHORTCUT.
3. Crime type: CaseMaster.CrimeMinorHeadID → CrimeSubHead.ROWID → CrimeSubHead.CrimeHeadName
4. LEFT JOIN ChargesheetDetails and ArrestSurrender — not all cases have these rows.
5. LIKE wildcard is * not % — e.g. LIKE '*Robbery*' not LIKE '%Robbery%'
6. Use ROWID for all joins (except CasteMaster which uses caste_master_id).
7. Max 4 JOINs. Choose the most essential ones.
8. Always LIMIT 50 for row queries. No LIMIT needed for GROUP BY aggregations.
9. DO NOT use columns that are not listed above — return empty zcql_query instead.
"""
