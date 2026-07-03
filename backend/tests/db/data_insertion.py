"""
PRISM — Seed Data Insertion (ROWID-aware)
==========================================
Catalyst DataStore FK columns require the internal ROWID of the referenced row,
NOT the custom ID value you supply. This script:
  1. Inserts each parent table first
  2. Reads back the assigned ROWIDs from the response
  3. Uses those ROWIDs in all child FK columns

INSERTION ORDER (FK dependency order):
  1.  State
  2.  District          → State
  3.  UnitType
  4.  Unit              → UnitType, State, District
  5.  Court             → District, State
  6.  Rank
  7.  Designation
  8.  Employee          → District, Unit, Rank, Designation
  9.  CaseCategory
  10. GravityOffence
  11. CrimeHead
  12. CrimeSubHead      → CrimeHead
  13. Act
  14. Section           → Act
  15. CrimeHeadActSection → CrimeHead, Act
  16. OccupationMaster
  17. ReligionMaster
  18. CasteMaster
  19. CaseStatusMaster
  20. CaseMaster        → Employee, Unit, CaseCategory, GravityOffence,
                          CrimeHead, CrimeSubHead, CaseStatusMaster, Court
  21. Accused           → CaseMaster
  22. Victim            → CaseMaster
  23. ComplainantDetails → CaseMaster, OccupationMaster, ReligionMaster, CasteMaster
  24. ActSectionAssociation → CaseMaster, Act, Section
  25. ArrestSurrender   → CaseMaster, State, District, Unit, Employee, Court, Accused
  26. ChargesheetDetails → CaseMaster, Employee
"""

from fastapi import Request, APIRouter
import zcatalyst_sdk

router = APIRouter(prefix="/db", tags=["insertion"])


def get_datastore(req: Request):
    catalyst_app = zcatalyst_sdk.initialize(req=req)
    return catalyst_app.datastore()


def insert(datastore, table_name: str, rows: list[dict]) -> tuple[dict, list[dict]]:
    """
    Insert rows and return (result_summary, inserted_rows_with_rowids).
    Catalyst returns the inserted rows with their ROWID in the response.
    """
    try:
        table = datastore.table(table_name)
        response = table.insert_rows(rows)
        print(type(response))
        print(response)
        # response is a list of inserted row dicts, each containing ROWID
        inserted = response if isinstance(response, list) else []
        print(f"  {table_name}: inserted {len(inserted)} rows")
        for r in inserted:
            print(f"ROWID {r.get('ROWID')} | {r}")
        return {"table": table_name, "status": "ok", "count": len(inserted)}, inserted
    except Exception as e:
        print(f"    {table_name}: FAILED — {e}")
        return {"table": table_name, "status": "error", "error": str(e)}, []


def rowids(inserted: list[dict]) -> list[int]:
    """Extract ROWIDs from inserted rows in order."""
    return [r["ROWID"] for r in inserted]


@router.get("/test/insert_data")
def seed_all(request: Request):

    ds = get_datastore(request)
    results = []

    print("\n========== PRISM SEED DATA INSERTION ==========\n")

    # ─────────────────────────────────────────────────────────────────
    # 1. State  (no FK)
    # ─────────────────────────────────────────────────────────────────
    res, state_rows = insert(ds, "State", [
        {"StateName": "Karnataka",      "NationalityID": 1, "Active": True},
        {"StateName": "Tamil Nadu",     "NationalityID": 1, "Active": True},
        {"StateName": "Andhra Pradesh", "NationalityID": 1, "Active": True},
        {"StateName": "Maharashtra",    "NationalityID": 1, "Active": True},
    ])
    results.append(res)
    # Map index → ROWID  (0=Karnataka, 1=Tamil Nadu, 2=Andhra, 3=Maharashtra)
    state_rid = rowids(state_rows)
    # state_rid[0] = Karnataka ROWID  ← used by all districts below

    # ─────────────────────────────────────────────────────────────────
    # 2. District  (FK → State)
    # ─────────────────────────────────────────────────────────────────
    res, district_rows = insert(ds, "District", [
        {"DistrictName": "Bengaluru Urban",  "StateID": state_rid[0], "Active": True},
        {"DistrictName": "Mysuru",           "StateID": state_rid[0], "Active": True},
        {"DistrictName": "Dakshina Kannada", "StateID": state_rid[0], "Active": True},
        {"DistrictName": "Belagavi",         "StateID": state_rid[0], "Active": True},
    ])
    results.append(res)
    # dist_rid[0]=Bengaluru, [1]=Mysuru, [2]=DK, [3]=Belagavi
    dist_rid = rowids(district_rows)

    # ─────────────────────────────────────────────────────────────────
    # 3. UnitType  (no FK)
    # ─────────────────────────────────────────────────────────────────
    res, unittype_rows = insert(ds, "UnitType", [
        {"UnitTypeName": "Police Station",         "CityDistState": "City",     "Hierarchy": 3, "Active": True},
        {"UnitTypeName": "Circle Office",          "CityDistState": "District", "Hierarchy": 2, "Active": True},
        {"UnitTypeName": "District Armed Reserve", "CityDistState": "District", "Hierarchy": 2, "Active": True},
        {"UnitTypeName": "District HQ",            "CityDistState": "District", "Hierarchy": 1, "Active": True},
    ])
    results.append(res)
    ut_rid = rowids(unittype_rows)
    # ut_rid[0] = Police Station

    # ─────────────────────────────────────────────────────────────────
    # 4. Unit  (FK → UnitType, State, District)
    # ─────────────────────────────────────────────────────────────────
    res, unit_rows = insert(ds, "Unit", [
        {
            "UnitName": "Cubbon Park Police Station",
            "TypeID": ut_rid[0], "ParentUnit": None,
            "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0],
            "Active": True
        },
        {
            "UnitName": "Koramangala Police Station",
            "TypeID": ut_rid[0], "ParentUnit": None,
            "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0],
            "Active": True
        },
        {
            "UnitName": "Mysuru City Police Station",
            "TypeID": ut_rid[0], "ParentUnit": None,
            "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[1],
            "Active": True
        },
        {
            "UnitName": "Mangaluru Central Police Station",
            "TypeID": ut_rid[0], "ParentUnit": None,
            "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[2],
            "Active": True
        },
    ])
    results.append(res)
    # unit_rid[0]=Cubbon, [1]=Koramangala, [2]=Mysuru, [3]=Mangaluru
    unit_rid = rowids(unit_rows)

    # ─────────────────────────────────────────────────────────────────
    # 5. Court  (FK → District, State)
    # ─────────────────────────────────────────────────────────────────
    res, court_rows = insert(ds, "Court", [
        {"CourtName": "City Civil Court Bengaluru",     "DistrictID": dist_rid[0], "StateID": state_rid[0], "Active": True},
        {"CourtName": "Mysuru District Sessions Court", "DistrictID": dist_rid[1], "StateID": state_rid[0], "Active": True},
        {"CourtName": "DK District Court Mangaluru",    "DistrictID": dist_rid[2], "StateID": state_rid[0], "Active": True},
        {"CourtName": "Belagavi Sessions Court",        "DistrictID": dist_rid[3], "StateID": state_rid[0], "Active": True},
    ])
    results.append(res)
    # court_rid[0]=Bengaluru court, [1]=Mysuru, [2]=DK, [3]=Belagavi
    court_rid = rowids(court_rows)

    # ─────────────────────────────────────────────────────────────────
    # 6. Rank  (no FK)
    # ─────────────────────────────────────────────────────────────────
    res, rank_rows = insert(ds, "Rank", [
        {"RankName": "Constable",      "Hierarchy": 5, "Active": True},
        {"RankName": "Head Constable", "Hierarchy": 4, "Active": True},
        {"RankName": "Sub Inspector",  "Hierarchy": 3, "Active": True},
        {"RankName": "Inspector",      "Hierarchy": 2, "Active": True},
    ])
    results.append(res)
    # rank_rid[0]=Constable, [1]=Head Const, [2]=SI, [3]=Inspector
    rank_rid = rowids(rank_rows)

    # ─────────────────────────────────────────────────────────────────
    # 7. Designation  (no FK)
    # ─────────────────────────────────────────────────────────────────
    res, desig_rows = insert(ds, "Designation", [
        {"DesignationName": "Station House Officer", "Active": True, "SortOrder": 1},
        {"DesignationName": "Investigating Officer", "Active": True, "SortOrder": 2},
        {"DesignationName": "Station Writer",        "Active": True, "SortOrder": 3},
        {"DesignationName": "Beat Officer",          "Active": True, "SortOrder": 4},
    ])
    results.append(res)
    # desig_rid[0]=SHO, [1]=IO, [2]=Writer, [3]=Beat
    desig_rid = rowids(desig_rows)

    # ─────────────────────────────────────────────────────────────────
    # 8. Employee  (FK → District, Unit, Rank, Designation)
    # ─────────────────────────────────────────────────────────────────
    res, emp_rows = insert(ds, "Employee", [
        {
            "KGID": "KG2001101", "FirstName": "Rajesh Kumar",
            "EmployeeDOB": "1985-03-15", "GenderID": 1, "BloodGroupID": 2,
            "PhysicallyChallenged": False, "AppointmentDate": "2008-06-01",
            "DistrictID": dist_rid[0], "UnitID": unit_rid[0],
            "RankID": rank_rid[3], "DesignationID": desig_rid[0]
        },
        {
            "KGID": "KG2001102", "FirstName": "Priya Sharma",
            "EmployeeDOB": "1990-07-22", "GenderID": 2, "BloodGroupID": 1,
            "PhysicallyChallenged": False, "AppointmentDate": "2013-09-15",
            "DistrictID": dist_rid[0], "UnitID": unit_rid[0],
            "RankID": rank_rid[2], "DesignationID": desig_rid[1]
        },
        {
            "KGID": "KG2001103", "FirstName": "Mohammed Farooq",
            "EmployeeDOB": "1982-11-08", "GenderID": 1, "BloodGroupID": 3,
            "PhysicallyChallenged": False, "AppointmentDate": "2005-03-20",
            "DistrictID": dist_rid[1], "UnitID": unit_rid[2],
            "RankID": rank_rid[3], "DesignationID": desig_rid[0]
        },
        {
            "KGID": "KG2001104", "FirstName": "Anitha Reddy",
            "EmployeeDOB": "1993-05-30", "GenderID": 2, "BloodGroupID": 4,
            "PhysicallyChallenged": False, "AppointmentDate": "2016-11-01",
            "DistrictID": dist_rid[1], "UnitID": unit_rid[2],
            "RankID": rank_rid[2], "DesignationID": desig_rid[1]
        },
    ])
    results.append(res)
    # emp_rid[0]=Rajesh(SHO Cubbon), [1]=Priya(IO Cubbon),
    # emp_rid[2]=Farooq(SHO Mysuru), [3]=Anitha(IO Mysuru)
    emp_rid = rowids(emp_rows)

    # ─────────────────────────────────────────────────────────────────
    # 9. CaseCategory  (no FK)
    # ─────────────────────────────────────────────────────────────────
    res, casecat_rows = insert(ds, "CaseCategory", [
        {"LookupValue": "FIR"},
        {"LookupValue": "UDR"},
        {"LookupValue": "PAR"},
        {"LookupValue": "Zero FIR"},
    ])
    results.append(res)
    # casecat_rid[0]=FIR
    casecat_rid = rowids(casecat_rows)

    # ─────────────────────────────────────────────────────────────────
    # 10. GravityOffence  (no FK)
    # ─────────────────────────────────────────────────────────────────
    res, gravity_rows = insert(ds, "GravityOffence", [
        {"LookupValue": "Heinous"},
        {"LookupValue": "Serious"},
        {"LookupValue": "Non-Heinous"},
    ])
    results.append(res)
    # gravity_rid[0]=Heinous, [1]=Serious, [2]=Non-Heinous
    gravity_rid = rowids(gravity_rows)

    # ─────────────────────────────────────────────────────────────────
    # 11. CrimeHead  (no FK)
    # ─────────────────────────────────────────────────────────────────
    res, crimehead_rows = insert(ds, "CrimeHead", [
        {"CrimeGroupName": "Crimes Against Body",     "Active": True},
        {"CrimeGroupName": "Crimes Against Property", "Active": True},
        {"CrimeGroupName": "Crimes Against Women",    "Active": True},
        {"CrimeGroupName": "Cyber Crimes",            "Active": True},
    ])
    results.append(res)
    # ch_rid[0]=Body, [1]=Property, [2]=Women, [3]=Cyber
    ch_rid = rowids(crimehead_rows)

    # ─────────────────────────────────────────────────────────────────
    # 12. CrimeSubHead  (FK → CrimeHead)
    # ─────────────────────────────────────────────────────────────────
    res, csh_rows = insert(ds, "CrimeSubHead", [
        {"CrimeHeadID": ch_rid[0], "CrimeHeadName": "Murder",            "SeqID": 1},
        {"CrimeHeadID": ch_rid[0], "CrimeHeadName": "Attempt to Murder", "SeqID": 2},
        {"CrimeHeadID": ch_rid[1], "CrimeHeadName": "Robbery",           "SeqID": 1},
        {"CrimeHeadID": ch_rid[1], "CrimeHeadName": "Chain Snatching",   "SeqID": 2},
        {"CrimeHeadID": ch_rid[1], "CrimeHeadName": "Vehicle Theft",     "SeqID": 3},
        {"CrimeHeadID": ch_rid[1], "CrimeHeadName": "Burglary",          "SeqID": 4},
        {"CrimeHeadID": ch_rid[2], "CrimeHeadName": "Harassment",        "SeqID": 1},
        {"CrimeHeadID": ch_rid[3], "CrimeHeadName": "Online Fraud",      "SeqID": 1},
    ])
    results.append(res)
    # csh_rid[0]=Murder, [1]=AttemptMurder, [2]=Robbery,
    # csh_rid[3]=ChainSnatching, [4]=VehicleTheft, [5]=Burglary,
    # csh_rid[6]=Harassment, [7]=OnlineFraud
    csh_rid = rowids(csh_rows)

    # ─────────────────────────────────────────────────────────────────
    # 13. Act  (no FK)
    # ─────────────────────────────────────────────────────────────────
    res, act_rows = insert(ds, "Act", [
        {"ActDescription": "Indian Penal Code, 1860",                               "ShortName": "IPC",   "Active": True},
        {"ActDescription": "Narcotic Drugs and Psychotropic Substances Act, 1985",  "ShortName": "NDPS",  "Active": True},
        {"ActDescription": "Information Technology Act, 2000",                      "ShortName": "IT Act","Active": True},
        {"ActDescription": "Protection of Children from Sexual Offences Act, 2012", "ShortName": "POCSO", "Active": True},
    ])
    results.append(res)
    # act_rid[0]=IPC, [1]=NDPS, [2]=IT, [3]=POCSO
    act_rid = rowids(act_rows)

    # ─────────────────────────────────────────────────────────────────
    # 14. Section  (FK → Act via ROWID, not ActCode string)
    # ─────────────────────────────────────────────────────────────────
    res, section_rows = insert(ds, "Section", [
        {"ActCode": act_rid[0], "SectionCode": "302", "SectionDescription": "Punishment for murder",                          "Active": True},
        {"ActCode": act_rid[0], "SectionCode": "307", "SectionDescription": "Attempt to commit murder",                       "Active": True},
        {"ActCode": act_rid[0], "SectionCode": "379", "SectionDescription": "Punishment for theft",                           "Active": True},
        {"ActCode": act_rid[0], "SectionCode": "392", "SectionDescription": "Punishment for robbery",                         "Active": True},
        {"ActCode": act_rid[0], "SectionCode": "411", "SectionDescription": "Dishonestly receiving stolen property",          "Active": True},
        {"ActCode": act_rid[0], "SectionCode": "420", "SectionDescription": "Cheating and dishonestly inducing delivery",     "Active": True},
        {"ActCode": act_rid[2], "SectionCode": "66C", "SectionDescription": "Identity theft",                                 "Active": True},
        {"ActCode": act_rid[2], "SectionCode": "66D", "SectionDescription": "Cheating by personation using computer resource","Active": True},
    ])
    results.append(res)
    # sec_rid[0]=302, [1]=307, [2]=379, [3]=392,
    # sec_rid[4]=411, [5]=420, [6]=66C, [7]=66D
    sec_rid = rowids(section_rows)

    # ─────────────────────────────────────────────────────────────────
    # 15. CrimeHeadActSection  (FK → CrimeHead, Act)
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "CrimeHeadActSection", [
        {"CrimeHeadID": ch_rid[0], "ActCode": act_rid[0], "SectionCode": "302"},
        {"CrimeHeadID": ch_rid[0], "ActCode": act_rid[0], "SectionCode": "307"},
        {"CrimeHeadID": ch_rid[1], "ActCode": act_rid[0], "SectionCode": "379"},
        {"CrimeHeadID": ch_rid[1], "ActCode": act_rid[0], "SectionCode": "392"},
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # 16. OccupationMaster  (no FK)
    # ─────────────────────────────────────────────────────────────────
    res, occ_rows = insert(ds, "OccupationMaster", [
        {"OccupationName": "Farmer"},
        {"OccupationName": "Government Employee"},
        {"OccupationName": "Business"},
        {"OccupationName": "Daily Wage Worker"},
        {"OccupationName": "Student"},
    ])
    results.append(res)
    # occ_rid[0]=Farmer,[1]=GovtEmp,[2]=Business,[3]=DailyWage,[4]=Student
    occ_rid = rowids(occ_rows)

    # ─────────────────────────────────────────────────────────────────
    # 17. ReligionMaster  (no FK)
    # ─────────────────────────────────────────────────────────────────
    res, rel_rows = insert(ds, "ReligionMaster", [
        {"ReligionName": "Hindu"},
        {"ReligionName": "Muslim"},
        {"ReligionName": "Christian"},
        {"ReligionName": "Jain"},
    ])
    results.append(res)
    # rel_rid[0]=Hindu
    rel_rid = rowids(rel_rows)

    # ─────────────────────────────────────────────────────────────────
    # 18. CasteMaster  (no FK — uses lowercase column names)
    # ─────────────────────────────────────────────────────────────────
    res, caste_rows = insert(ds, "CasteMaster", [
        {"caste_master_name": "General"},
        {"caste_master_name": "OBC"},
        {"caste_master_name": "SC"},
        {"caste_master_name": "ST"},
    ])
    results.append(res)
    # caste_rid[0]=General,[1]=OBC,[2]=SC,[3]=ST
    caste_rid = rowids(caste_rows)

    # ─────────────────────────────────────────────────────────────────
    # 19. CaseStatusMaster  (no FK)
    # ─────────────────────────────────────────────────────────────────
    res, status_rows = insert(ds, "CaseStatusMaster", [
        {"CaseStatusName": "Under Investigation"},
        {"CaseStatusName": "Charge Sheeted"},
        {"CaseStatusName": "Referred to Court"},
        {"CaseStatusName": "Closed"},
    ])
    results.append(res)
    # status_rid[0]=UnderInvestigation,[1]=ChargeSheeted,[2]=ReferredCourt,[3]=Closed
    status_rid = rowids(status_rows)

    # ─────────────────────────────────────────────────────────────────
    # 20. CaseMaster  (FK → Employee, Unit, CaseCategory, GravityOffence,
    #                       CrimeHead, CrimeSubHead, CaseStatusMaster, Court)
    # ─────────────────────────────────────────────────────────────────
    res, case_rows = insert(ds, "CaseMaster", [
        {
            "CrimeNo": "104430100120240001",
            "CaseNo": "202400001",
            "CrimeRegisteredDate": "2024-03-15",
            "PolicePersonID":  emp_rid[0],        # Rajesh Kumar (SHO)
            "PoliceStationID": unit_rid[0],        # Cubbon Park PS
            "CaseCategoryID":  casecat_rid[0],    # FIR
            "GravityOffenceID": gravity_rid[0],   # Heinous
            "CrimeMajorHeadID": ch_rid[0],        # Crimes Against Body
            "CrimeMinorHeadID": csh_rid[0],       # Murder
            "CaseStatusID":    status_rid[0],     # Under Investigation
            "CourtID":         court_rid[0],      # Bengaluru Civil Court
            "IncidentFromDate": "2024-03-14 22:30:00",
            "IncidentToDate":   "2024-03-14 23:00:00",
            "InfoReceivedPSDate": "2024-03-15 01:15:00",
            "latitude":  12.9716,
            "longitude": 77.5946,
            "BriefFacts": "On 14-03-2024 at approximately 22:30 hrs, the complainant Suresh Nair reported that his neighbour was found dead in his residence near Cubbon Park. The victim had multiple stab wounds on the chest. Two suspects were seen fleeing the scene on a black motorcycle. Preliminary investigation suggests a property dispute as the motive."
        },
        {
            "CrimeNo": "104430100120240002",
            "CaseNo": "202400002",
            "CrimeRegisteredDate": "2024-04-02",
            "PolicePersonID":  emp_rid[1],        # Priya Sharma (IO)
            "PoliceStationID": unit_rid[0],        # Cubbon Park PS
            "CaseCategoryID":  casecat_rid[0],    # FIR
            "GravityOffenceID": gravity_rid[1],   # Serious
            "CrimeMajorHeadID": ch_rid[1],        # Crimes Against Property
            "CrimeMinorHeadID": csh_rid[3],       # Chain Snatching
            "CaseStatusID":    status_rid[0],     # Under Investigation
            "CourtID":         None,
            "IncidentFromDate": "2024-04-02 08:15:00",
            "IncidentToDate":   "2024-04-02 08:20:00",
            "InfoReceivedPSDate": "2024-04-02 09:00:00",
            "latitude":  12.9352,
            "longitude": 77.6245,
            "BriefFacts": "On 02-04-2024 at 08:15 hrs, complainant Lakshmi Devi (age 62) reported that while she was walking near Koramangala market, two persons on a two-wheeler snatched her gold chain valued at Rs 45,000. The accused fled towards the Silk Board junction. Victim sustained minor injuries to neck. CCTV footage being collected."
        },
        {
            "CrimeNo": "104430100320240001",
            "CaseNo": "202400001",
            "CrimeRegisteredDate": "2024-05-20",
            "PolicePersonID":  emp_rid[2],        # Mohammed Farooq (SHO)
            "PoliceStationID": unit_rid[2],        # Mysuru City PS
            "CaseCategoryID":  casecat_rid[0],    # FIR
            "GravityOffenceID": gravity_rid[1],   # Serious
            "CrimeMajorHeadID": ch_rid[1],        # Crimes Against Property
            "CrimeMinorHeadID": csh_rid[4],       # Vehicle Theft
            "CaseStatusID":    status_rid[1],     # Charge Sheeted
            "CourtID":         court_rid[1],      # Mysuru Court
            "IncidentFromDate": "2024-05-19 23:45:00",
            "IncidentToDate":   "2024-05-20 00:30:00",
            "InfoReceivedPSDate": "2024-05-20 07:00:00",
            "latitude":  12.2958,
            "longitude": 76.6394,
            "BriefFacts": "On 19-05-2024 between 23:45 hrs and 00:30 hrs, the complainant Ramesh Gowda reported that his Honda City car (KA-09-MF-7823) was stolen from the parking area of Mysuru Palace Road. The vehicle was found abandoned in Bannimantap industrial area the following day. Fingerprints recovered from door handle."
        },
        {
            "CrimeNo": "104430100120240003",
            "CaseNo": "202400003",
            "CrimeRegisteredDate": "2024-06-10",
            "PolicePersonID":  emp_rid[1],        # Priya Sharma (IO)
            "PoliceStationID": unit_rid[0],        # Cubbon Park PS
            "CaseCategoryID":  casecat_rid[0],    # FIR
            "GravityOffenceID": gravity_rid[2],   # Non-Heinous
            "CrimeMajorHeadID": ch_rid[3],        # Cyber Crimes
            "CrimeMinorHeadID": csh_rid[7],       # Online Fraud
            "CaseStatusID":    status_rid[0],     # Under Investigation
            "CourtID":         None,
            "IncidentFromDate": "2024-06-08 14:00:00",
            "IncidentToDate":   "2024-06-08 15:30:00",
            "InfoReceivedPSDate": "2024-06-10 11:20:00",
            "latitude":  12.9789,
            "longitude": 77.5917,
            "BriefFacts": "On 10-06-2024, complainant Anil Mehta reported that he received a phone call from an unknown person posing as a bank official. The accused convinced the complainant to share his OTP and subsequently transferred Rs 1,20,000 from his savings account. The call originated from a number registered in Rajasthan. Cyber cell has been informed."
        },
    ])
    results.append(res)
    # case_rid[0]=Case1001(murder), [1]=Case1002(chain snatch),
    # case_rid[2]=Case1003(vehicle theft), [3]=Case1004(cyber fraud)
    case_rid = rowids(case_rows)

    # ─────────────────────────────────────────────────────────────────
    # 21. Accused  (FK → CaseMaster)
    # ─────────────────────────────────────────────────────────────────
    res, accused_rows = insert(ds, "Accused", [
        # Case 1001 — murder, two accused
        {"CaseMasterID": case_rid[0], "AccusedName": "Abdul Rauf Khan",              "AgeYear": 31, "GenderID": 1, "PersonID": "A1"},
        {"CaseMasterID": case_rid[0], "AccusedName": "Syed Imran",                   "AgeYear": 27, "GenderID": 1, "PersonID": "A2"},
        # Case 1002 — chain snatching
        {"CaseMasterID": case_rid[1], "AccusedName": "Abdul Rauf Khan",              "AgeYear": 31, "GenderID": 1, "PersonID": "A1"},
        # Case 1003 — vehicle theft
        {"CaseMasterID": case_rid[2], "AccusedName": "Venkatesh Prasad",             "AgeYear": 24, "GenderID": 1, "PersonID": "A1"},
        {"CaseMasterID": case_rid[2], "AccusedName": "Ravi Kumar B",                 "AgeYear": 22, "GenderID": 1, "PersonID": "A2"},
        # Case 1004 — cyber fraud (unknown accused)
        {"CaseMasterID": case_rid[3], "AccusedName": "Unknown — Under Investigation","AgeYear": None,"GenderID": None,"PersonID": "A1"},
    ])
    results.append(res)
    # acc_rid[0]=AbdulRauf(1001), [1]=SyedImran(1001), [2]=AbdulRauf(1002),
    # acc_rid[3]=Venkatesh(1003), [4]=RaviKumar(1003), [5]=Unknown(1004)
    acc_rid = rowids(accused_rows)

    # ─────────────────────────────────────────────────────────────────
    # 22. Victim  (FK → CaseMaster)
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "Victim", [
        {"CaseMasterID": case_rid[0], "VictimName": "Prakash Naidu", "AgeYear": 45, "GenderID": 1, "VictimPolice": False},
        {"CaseMasterID": case_rid[1], "VictimName": "Lakshmi Devi",  "AgeYear": 62, "GenderID": 2, "VictimPolice": False},
        {"CaseMasterID": case_rid[2], "VictimName": "Ramesh Gowda",  "AgeYear": 38, "GenderID": 1, "VictimPolice": False},
        {"CaseMasterID": case_rid[3], "VictimName": "Anil Mehta",    "AgeYear": 52, "GenderID": 1, "VictimPolice": False},
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # 23. ComplainantDetails  (FK → CaseMaster, OccupationMaster, ReligionMaster, CasteMaster)
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "ComplainantDetails", [
        {
            "CaseMasterID": case_rid[0], "ComplainantName": "Suresh Nair",  "AgeYear": 40,
            "OccupationID": occ_rid[1], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1
        },
        {
            "CaseMasterID": case_rid[1], "ComplainantName": "Lakshmi Devi", "AgeYear": 62,
            "OccupationID": occ_rid[3], "ReligionID": rel_rid[0], "CasteID": caste_rid[1], "GenderID": 2
        },
        {
            "CaseMasterID": case_rid[2], "ComplainantName": "Ramesh Gowda", "AgeYear": 38,
            "OccupationID": occ_rid[2], "ReligionID": rel_rid[0], "CasteID": caste_rid[1], "GenderID": 1
        },
        {
            "CaseMasterID": case_rid[3], "ComplainantName": "Anil Mehta",   "AgeYear": 52,
            "OccupationID": occ_rid[1], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1
        },
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # 24. ActSectionAssociation  (FK → CaseMaster, Act, Section)
    # ActID and SectionID are lookup columns → use ROWIDs
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "ActSectionAssociation", [
        # Case 1001 — murder: IPC 302
        {"CaseMasterID": case_rid[0], "ActID": act_rid[0], "SectionID": sec_rid[0], "ActOrderID": 1, "SectionOrderID": 1},
        # Case 1002 — chain snatching: IPC 392 + IPC 379
        {"CaseMasterID": case_rid[1], "ActID": act_rid[0], "SectionID": sec_rid[3], "ActOrderID": 1, "SectionOrderID": 1},
        {"CaseMasterID": case_rid[1], "ActID": act_rid[0], "SectionID": sec_rid[2], "ActOrderID": 1, "SectionOrderID": 2},
        # Case 1003 — vehicle theft: IPC 379 + IPC 411
        {"CaseMasterID": case_rid[2], "ActID": act_rid[0], "SectionID": sec_rid[2], "ActOrderID": 1, "SectionOrderID": 1},
        {"CaseMasterID": case_rid[2], "ActID": act_rid[0], "SectionID": sec_rid[4], "ActOrderID": 1, "SectionOrderID": 2},
        # Case 1004 — cyber fraud: IT 66C + IT 66D + IPC 420
        {"CaseMasterID": case_rid[3], "ActID": act_rid[2], "SectionID": sec_rid[6], "ActOrderID": 1, "SectionOrderID": 1},
        {"CaseMasterID": case_rid[3], "ActID": act_rid[2], "SectionID": sec_rid[7], "ActOrderID": 1, "SectionOrderID": 2},
        {"CaseMasterID": case_rid[3], "ActID": act_rid[0], "SectionID": sec_rid[5], "ActOrderID": 2, "SectionOrderID": 1},
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # 25. ArrestSurrender  (FK → CaseMaster, State, District, Unit, Employee, Court, Accused)
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "ArrestSurrender", [
        # Case 1001 — A1 (Abdul Rauf Khan) arrested
        {
            "CaseMasterID": case_rid[0],
            "ArrestSurrenderTypeID": 1,
            "ArrestSurrenderDate": "2024-03-18",
            "ArrestSurrenderStateId":    state_rid[0],
            "ArrestSurrenderDistrictId": dist_rid[0],
            "PoliceStationID": unit_rid[0],
            "IOID":            emp_rid[1],   # Priya Sharma (IO)
            "CourtID":         court_rid[0],
            "AccusedMasterID": acc_rid[0],   # Abdul Rauf Khan
            "IsAccused": True,
            "IsComplainantAccused": False
        },
        # Case 1001 — A2 (Syed Imran) arrested same day
        {
            "CaseMasterID": case_rid[0],
            "ArrestSurrenderTypeID": 1,
            "ArrestSurrenderDate": "2024-03-18",
            "ArrestSurrenderStateId":    state_rid[0],
            "ArrestSurrenderDistrictId": dist_rid[0],
            "PoliceStationID": unit_rid[0],
            "IOID":            emp_rid[1],
            "CourtID":         court_rid[0],
            "AccusedMasterID": acc_rid[1],   # Syed Imran
            "IsAccused": True,
            "IsComplainantAccused": False
        },
        # Case 1003 — A2 (Ravi Kumar B) arrested; A1 still absconding
        {
            "CaseMasterID": case_rid[2],
            "ArrestSurrenderTypeID": 1,
            "ArrestSurrenderDate": "2024-06-01",
            "ArrestSurrenderStateId":    state_rid[0],
            "ArrestSurrenderDistrictId": dist_rid[1],
            "PoliceStationID": unit_rid[2],
            "IOID":            emp_rid[3],   # Anitha Reddy (IO Mysuru)
            "CourtID":         court_rid[1],
            "AccusedMasterID": acc_rid[4],   # Ravi Kumar B
            "IsAccused": True,
            "IsComplainantAccused": False
        },
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # 26. ChargesheetDetails  (FK → CaseMaster, Employee)
    # Only Case 1003 is chargesheeted.
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "ChargesheetDetails", [
        {
            "CaseMasterID":    case_rid[2],   # Case 1003 — vehicle theft
            "csdate":          "2024-07-15 10:00:00",
            "cstype":          "A",
            "PolicePersonID":  emp_rid[2],    # Mohammed Farooq (SHO Mysuru)
        },
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────────────────
    success_count = sum(1 for r in results if r["status"] == "ok")
    failed = [r for r in results if r["status"] == "error"]

    print(f"\n========== SEED COMPLETE ==========")
    print(f" Successful: {success_count}/{len(results)} tables")
    if failed:
        print(f" Failed: {[r['table'] for r in failed]}")
    print("====================================\n")

    return {
        "status": "complete",
        "successful_tables": success_count,
        "total_tables": len(results),
        "failed": failed,
        "results": results
    }