"""
Database schema context for text-to-SQL agent.
Provides condensed schema information and ZCQL-specific rules for LLM query generation.
"""

SCHEMA_CONTEXT = """
# Karnataka Police FIR Database Schema for ZCQL Query Generation

## ZCQL-SPECIFIC LIMITATIONS (CRITICAL)
- NO CASE WHEN statements
- NO subqueries
- NO date functions (NOW(), DATE_TRUNC, etc.) - compute dates in Python
- Max 4 JOINs per query
- Max 20 columns, 300 rows per SELECT
- Use ROWID for primary key references
- Table aliases only in SELECT statements
- Always include LIMIT clause (default 50)

## CORE TABLES

### CaseMaster (CENTRAL TABLE - Start all queries here)
Columns: CaseMasterID (PK), CrimeNo, CaseNo, CrimeRegisteredDate, PolicePersonID, PoliceStationID, 
CaseCategoryID, GravityOffenceID, CrimeMajorHeadID, CrimeMinorHeadID, CaseStatusID, CourtID,
IncidentFromDate, IncidentToDate, InfoReceivedPSDate, latitude, longitude, BriefFacts

Key Notes:
- IncidentFromDate ≠ CrimeRegisteredDate (incident date vs report date)
- latitude/longitude can be NULL - filter with IS NOT NULL
- BriefFacts contains narrative context for RAG/MO extraction
- CrimeMinorHeadID = most specific crime type

### CrimeSubHead (Crime Types)
Columns: CrimeSubHeadID (PK), CrimeHeadID, CrimeHeadName, SeqID
Join: CaseMaster.CrimeMinorHeadID → CrimeSubHead.CrimeSubHeadID

### CaseStatusMaster (Status)
Columns: CaseStatusID (PK), CaseStatusName
Values: Under Investigation, Charge Sheeted, Closed, Referred to Court, Stayed
Join: CaseMaster.CaseStatusID → CaseStatusMaster.CaseStatusID

### Unit (Police Stations)
Columns: UnitID (PK), UnitName, TypeID, ParentUnit, StateID, DistrictID
Join: CaseMaster.PoliceStationID → Unit.UnitID

### District (Geography)
Columns: DistrictID (PK), DistrictName, StateID
Join: Unit.DistrictID → District.DistrictID

### Accused (Per FIR)
Columns: AccusedMasterID (PK), CaseMasterID, AccusedName, AgeYear, GenderID, PersonID
Join: CaseMaster.CaseMasterID → Accused.CaseMasterID
Note: No cross-case identity - use fuzzy matching on Name + Age + Gender

### Victim (Per FIR)
Columns: VictimMasterID (PK), CaseMasterID, VictimName, AgeYear, GenderID, VictimPolice
Join: CaseMaster.CaseMasterID → Victim.CaseMasterID

### ArrestSurrender (Arrest Events)
Columns: ArrestSurrenderID (PK), CaseMasterID, AccusedMasterID, ArrestSurrenderDate, 
ArrestSurrenderStateId, ArrestSurrenderDistrictId, PoliceStationID, IOID, CourtID
Join: CaseMaster.CaseMasterID → ArrestSurrender.CaseMasterID
Note: Accused without ArrestSurrender = absconding

### ActSectionAssociation (Legal Charges)
Columns: CaseMasterID, ActID, SectionID, ActOrderID, SectionOrderID
Join: CaseMaster.CaseMasterID → ActSectionAssociation.CaseMasterID
Note: Junction table - composite key (CaseMasterID, ActID, SectionID)

### Act (Legal Acts)
Columns: ActCode (PK), ActDescription, ShortName, Active
Join: ActSectionAssociation.ActID → Act.ActCode

### Section (Legal Sections)
Columns: ActCode, SectionCode, SectionDescription, Active
Join: ActSectionAssociation.SectionID → Section.SectionCode
Note: Composite key (ActCode, SectionCode)

## JOIN PATH RULES

Rule 1: Always start from CaseMaster
Rule 2: Geography: CaseMaster → Unit → District
Rule 3: Crime type: CaseMaster → CrimeSubHead
Rule 4: Status: CaseMaster → CaseStatusMaster
Rule 5: Accused: CaseMaster → Accused
Rule 6: Arrest: CaseMaster → ArrestSurrender
Rule 7: Legal sections: CaseMaster → ActSectionAssociation → Act + Section

## COLUMN NAME MAPPINGS FOR NATURAL LANGUAGE
- "district" → District.DistrictName
- "crime type" → CrimeSubHead.CrimeHeadName
- "status" → CaseStatusMaster.CaseStatusName
- "police station" → Unit.UnitName
- "FIR number" → CaseMaster.CrimeNo
- "case number" → CaseMaster.CaseNo
- "incident date" → CaseMaster.IncidentFromDate
- "registration date" → CaseMaster.CrimeRegisteredDate

## EXAMPLE QUERY PATTERNS

### Query: "Show me robbery cases in Bengaluru North"
SELECT CaseMaster.CrimeNo, CrimeSubHead.CrimeHeadName, District.DistrictName, CaseStatusMaster.CaseStatusName
FROM CaseMaster
INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.UnitID
INNER JOIN District ON Unit.DistrictID = District.DistrictID
INNER JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.CrimeSubHeadID
INNER JOIN CaseStatusMaster ON CaseMaster.CaseStatusID = CaseStatusMaster.CaseStatusID
WHERE District.DistrictName = 'Bengaluru North' AND CrimeSubHead.CrimeHeadName = 'Robbery'
LIMIT 50

### Query: "Active murder cases in last 30 days"
SELECT CaseMaster.CrimeNo, CaseMaster.IncidentFromDate, Unit.UnitName, CrimeSubHead.CrimeHeadName
FROM CaseMaster
INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.UnitID
INNER JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.CrimeSubHeadID
INNER JOIN CaseStatusMaster ON CaseMaster.CaseStatusID = CaseStatusMaster.CaseStatusID
WHERE CrimeSubHead.CrimeHeadName = 'Murder' AND CaseStatusMaster.CaseStatusName = 'Under Investigation'
AND CaseMaster.IncidentFromDate >= '2026-06-10'
LIMIT 50

### Query: "Accused named Suresh Hegde"
SELECT CaseMaster.CrimeNo, Accused.AccusedName, Accused.AgeYear, CrimeSubHead.CrimeHeadName
FROM CaseMaster
INNER JOIN Accused ON CaseMaster.CaseMasterID = Accused.CaseMasterID
INNER JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.CrimeSubHeadID
WHERE Accused.AccusedName LIKE '%Suresh%' AND Accused.AccusedName LIKE '%Hegde%'
LIMIT 50

### Query: "Cases by district with count"
SELECT District.DistrictName, COUNT(CaseMaster.CaseMasterID) as case_count
FROM CaseMaster
INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.UnitID
INNER JOIN District ON Unit.DistrictID = District.DistrictID
GROUP BY District.DistrictName
ORDER BY case_count DESC
LIMIT 50

## IMPORTANT REMINDERS
1. Always use LIMIT clause to avoid excessive results
2. Use INNER JOIN for required relationships, LEFT JOIN for optional
3. Date filters use string literals: 'YYYY-MM-DD'
4. String comparisons use LIKE with wildcards: '%value%'
5. Compute dates in Python before passing to query
6. Never use CASE WHEN - use Python post-processing instead
7. Never use subqueries - break into multiple queries if needed
8. Max 4 JOINs - prioritize essential joins
9. Use ROWID when joining to tables without explicit PK in context
10. Always validate table names exist in schema before generating query
"""
