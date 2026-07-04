"""
PRISM — Seed Data Insertion (ROWID-aware, 4x Scale)
==================================================
Catalyst DataStore FK columns require the internal ROWID of the referenced row,
NOT the custom ID value you supply. This script:
  1. Inserts each parent table first
  2. Reads back the assigned ROWIDs from the response
  3. Uses those ROWIDs in all child FK columns
  4. Scale: 4 times the original dataset (16 Cases, 24 Accused, etc.)
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
        # response is a list of inserted row dicts, each containing ROWID
        inserted = response if isinstance(response, list) else []
        print(f"  {table_name}: inserted {len(inserted)} rows")
        for r in inserted:
            print(f"ROWID {r.get('ROWID')} | {r}")
        return {"table": table_name, "status": "ok", "count": len(inserted)}, inserted
    except Exception as e:
        print(f"    {table_name}: FAILED — {e}")
        try:
            details = datastore.get_table_details(table_name)
            columns = [col.get('column_name') for col in details.get('column_details', [])]
            print(f"    {table_name} Valid Columns: {columns}")
        except Exception as meta_e:
            print(f"    Could not fetch table details: {meta_e}")
        return {"table": table_name, "status": "error", "error": str(e)}, []


def rowids(inserted: list[dict]) -> list[int]:
    """Extract ROWIDs from inserted rows in order."""
    return [int(r["ROWID"]) for r in inserted]


@router.get("/test/insert_data")
def seed_all(request: Request):

    ds = get_datastore(request)
    results = []

    print("\n========== PRISM SEED DATA INSERTION (4X SCALE) ==========\n")

    # ─────────────────────────────────────────────────────────────────
    # 1. State (no FK) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, state_rows = insert(ds, "State", [
        {"StateName": "Karnataka",      "NationalityID": 1, "Active": True},
        {"StateName": "Tamil Nadu",     "NationalityID": 1, "Active": True},
        {"StateName": "Andhra Pradesh", "NationalityID": 1, "Active": True},
        {"StateName": "Maharashtra",    "NationalityID": 1, "Active": True},
        {"StateName": "Kerala",         "NationalityID": 1, "Active": True},
        {"StateName": "Telangana",      "NationalityID": 1, "Active": True},
        {"StateName": "Goa",            "NationalityID": 1, "Active": True},
        {"StateName": "Gujarat",        "NationalityID": 1, "Active": True},
        {"StateName": "Rajasthan",      "NationalityID": 1, "Active": True},
        {"StateName": "Madhya Pradesh", "NationalityID": 1, "Active": True},
        {"StateName": "Uttar Pradesh",  "NationalityID": 1, "Active": True},
        {"StateName": "Bihar",          "NationalityID": 1, "Active": True},
        {"StateName": "West Bengal",    "NationalityID": 1, "Active": True},
        {"StateName": "Odisha",         "NationalityID": 1, "Active": True},
        {"StateName": "Punjab",         "NationalityID": 1, "Active": True},
        {"StateName": "Haryana",        "NationalityID": 1, "Active": True},
    ])
    results.append(res)
    state_rid = rowids(state_rows)

    # ─────────────────────────────────────────────────────────────────
    # 2. District (FK → State) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, district_rows = insert(ds, "District", [
        {"DistrictName": "Bengaluru Urban",  "StateID": state_rid[0],  "Active": True},
        {"DistrictName": "Mysuru",           "StateID": state_rid[0],  "Active": True},
        {"DistrictName": "Dakshina Kannada", "StateID": state_rid[0],  "Active": True},
        {"DistrictName": "Belagavi",         "StateID": state_rid[0],  "Active": True},
        {"DistrictName": "Dharwad",          "StateID": state_rid[0],  "Active": True},
        {"DistrictName": "Udupi",            "StateID": state_rid[0],  "Active": True},
        {"DistrictName": "Kalaburagi",       "StateID": state_rid[0],  "Active": True},
        {"DistrictName": "Chennai",          "StateID": state_rid[1],  "Active": True},
        {"DistrictName": "Madurai",          "StateID": state_rid[1],  "Active": True},
        {"DistrictName": "Coimbatore",       "StateID": state_rid[1],  "Active": True},
        {"DistrictName": "Vijayawada",       "StateID": state_rid[2],  "Active": True},
        {"DistrictName": "Visakhapatnam",    "StateID": state_rid[2],  "Active": True},
        {"DistrictName": "Mumbai City",      "StateID": state_rid[3],  "Active": True},
        {"DistrictName": "Pune",             "StateID": state_rid[3],  "Active": True},
        {"DistrictName": "Nagpur",           "StateID": state_rid[3],  "Active": True},
        {"DistrictName": "North Goa",        "StateID": state_rid[6],  "Active": True},
    ])
    results.append(res)
    dist_rid = rowids(district_rows)

    # ─────────────────────────────────────────────────────────────────
    # 3. UnitType (no FK) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, unittype_rows = insert(ds, "UnitType", [
        {"UnitTypeName": "Police Station",         "CityDistState": "City",     "Hierarchy": 3, "Active": True},
        {"UnitTypeName": "Circle Office",          "CityDistState": "District", "Hierarchy": 2, "Active": True},
        {"UnitTypeName": "District Armed Reserve", "CityDistState": "District", "Hierarchy": 2, "Active": True},
        {"UnitTypeName": "District HQ",            "CityDistState": "District", "Hierarchy": 1, "Active": True},
        {"UnitTypeName": "Traffic Police Station", "CityDistState": "City",     "Hierarchy": 3, "Active": True},
        {"UnitTypeName": "Cyber Crime PS",         "CityDistState": "City",     "Hierarchy": 3, "Active": True},
        {"UnitTypeName": "CID",                    "CityDistState": "State",    "Hierarchy": 1, "Active": True},
        {"UnitTypeName": "Crime Branch",           "CityDistState": "District", "Hierarchy": 2, "Active": True},
        {"UnitTypeName": "Anti-Narcotics Cell",    "CityDistState": "State",    "Hierarchy": 2, "Active": True},
        {"UnitTypeName": "Railway Police Station", "CityDistState": "City",     "Hierarchy": 3, "Active": True},
        {"UnitTypeName": "Women Police Station",   "CityDistState": "City",     "Hierarchy": 3, "Active": True},
        {"UnitTypeName": "Special Branch",         "CityDistState": "District", "Hierarchy": 2, "Active": True},
        {"UnitTypeName": "Intelligence Wing",      "CityDistState": "State",    "Hierarchy": 1, "Active": True},
        {"UnitTypeName": "KSRP Battalion",         "CityDistState": "State",    "Hierarchy": 2, "Active": True},
        {"UnitTypeName": "Training School",        "CityDistState": "State",    "Hierarchy": 2, "Active": True},
        {"UnitTypeName": "Dog Squad Unit",         "CityDistState": "District", "Hierarchy": 3, "Active": True},
    ])
    results.append(res)
    ut_rid = rowids(unittype_rows)

    # ─────────────────────────────────────────────────────────────────
    # 4. Unit (FK → UnitType, State, District) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, unit_rows = insert(ds, "Unit", [
        {"UnitName": "Cubbon Park Police Station",      "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0], "Active": True},
        {"UnitName": "Koramangala Police Station",      "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0], "Active": True},
        {"UnitName": "Mysuru City Police Station",      "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[1], "Active": True},
        {"UnitName": "Mangaluru Central Police Station", "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[2], "Active": True},
        {"UnitName": "Jayanagar Police Station",        "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0], "Active": True},
        {"UnitName": "Indiranagar Police Station",      "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0], "Active": True},
        {"UnitName": "Dharwad Town Police Station",      "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[4], "Active": True},
        {"UnitName": "Udupi Town Police Station",        "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[5], "Active": True},
        {"UnitName": "Chennai Central Police Station",  "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[1], "DistrictID": dist_rid[7], "Active": True},
        {"UnitName": "Coimbatore Town Police Station",   "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[1], "DistrictID": dist_rid[9], "Active": True},
        {"UnitName": "Vijayawada Town Police Station",   "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[2], "DistrictID": dist_rid[10], "Active": True},
        {"UnitName": "Mumbai Central Police Station",    "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[3], "DistrictID": dist_rid[12], "Active": True},
        {"UnitName": "Bengaluru Cyber Crime PS",        "TypeID": ut_rid[5], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0], "Active": True},
        {"UnitName": "Bengaluru Circle Office",         "TypeID": ut_rid[1], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0], "Active": True},
        {"UnitName": "Mysuru Circle Office",            "TypeID": ut_rid[1], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[1], "Active": True},
        {"UnitName": "Mangaluru DAR Unit",              "TypeID": ut_rid[2], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[2], "Active": True},
    ])
    results.append(res)
    unit_rid = rowids(unit_rows)

    # ─────────────────────────────────────────────────────────────────
    # 5. Court (FK → District, State) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, court_rows = insert(ds, "Court", [
        {"CourtName": "City Civil Court Bengaluru",     "DistrictID": dist_rid[0],  "StateID": state_rid[0], "Active": True},
        {"CourtName": "Mysuru District Sessions Court", "DistrictID": dist_rid[1],  "StateID": state_rid[0], "Active": True},
        {"CourtName": "DK District Court Mangaluru",    "DistrictID": dist_rid[2],  "StateID": state_rid[0], "Active": True},
        {"CourtName": "Belagavi Sessions Court",        "DistrictID": dist_rid[3],  "StateID": state_rid[0], "Active": True},
        {"CourtName": "High Court of Karnataka",        "DistrictID": dist_rid[0],  "StateID": state_rid[0], "Active": True},
        {"CourtName": "Dharwad District Court",         "DistrictID": dist_rid[4],  "StateID": state_rid[0], "Active": True},
        {"CourtName": "Udupi District Court",           "DistrictID": dist_rid[5],  "StateID": state_rid[0], "Active": True},
        {"CourtName": "Kalaburagi Sessions Court",       "DistrictID": dist_rid[6],  "StateID": state_rid[0], "Active": True},
        {"CourtName": "Chennai High Court",             "DistrictID": dist_rid[7],  "StateID": state_rid[1], "Active": True},
        {"CourtName": "Madurai Sessions Court",         "DistrictID": dist_rid[8],  "StateID": state_rid[1], "Active": True},
        {"CourtName": "Coimbatore District Court",      "DistrictID": dist_rid[9],  "StateID": state_rid[1], "Active": True},
        {"CourtName": "Vijayawada Sessions Court",      "DistrictID": dist_rid[10], "StateID": state_rid[2], "Active": True},
        {"CourtName": "Visakhapatnam District Court",   "DistrictID": dist_rid[11], "StateID": state_rid[2], "Active": True},
        {"CourtName": "Mumbai High Court",              "DistrictID": dist_rid[12], "StateID": state_rid[3], "Active": True},
        {"CourtName": "Pune Sessions Court",             "DistrictID": dist_rid[13], "StateID": state_rid[3], "Active": True},
        {"CourtName": "Nagpur Sessions Court",           "DistrictID": dist_rid[14], "StateID": state_rid[3], "Active": True},
    ])
    results.append(res)
    court_rid = rowids(court_rows)

    # ─────────────────────────────────────────────────────────────────
    # 6. Rank (no FK) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, rank_rows = insert(ds, "Rank", [
        {"RankName": "Constable",                      "Hierarchy": 5, "Active": True},
        {"RankName": "Head Constable",                 "Hierarchy": 4, "Active": True},
        {"RankName": "Sub Inspector",                  "Hierarchy": 3, "Active": True},
        {"RankName": "Inspector",                      "Hierarchy": 2, "Active": True},
        {"RankName": "Assistant Sub Inspector",        "Hierarchy": 3, "Active": True},
        {"RankName": "Deputy Superintendent",          "Hierarchy": 2, "Active": True},
        {"RankName": "Superintendent of Police",       "Hierarchy": 1, "Active": True},
        {"RankName": "Deputy Inspector General",       "Hierarchy": 1, "Active": True},
        {"RankName": "Inspector General of Police",    "Hierarchy": 1, "Active": True},
        {"RankName": "Additional Director General",    "Hierarchy": 1, "Active": True},
        {"RankName": "Director General of Police",     "Hierarchy": 1, "Active": True},
        {"RankName": "Senior Constable",               "Hierarchy": 4, "Active": True},
        {"RankName": "Head Constable Grade II",        "Hierarchy": 4, "Active": True},
        {"RankName": "Assistant Inspector",            "Hierarchy": 3, "Active": True},
        {"RankName": "Sub-Divisional Officer",         "Hierarchy": 2, "Active": True},
        {"RankName": "Circle Inspector",               "Hierarchy": 2, "Active": True},
    ])
    results.append(res)
    rank_rid = rowids(rank_rows)

    # ─────────────────────────────────────────────────────────────────
    # 7. Designation (no FK) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, desig_rows = insert(ds, "Designation", [
        {"DesignationName": "Station House Officer",       "Active": True, "SortOrder": 1},
        {"DesignationName": "Investigating Officer",       "Active": True, "SortOrder": 2},
        {"DesignationName": "Station Writer",              "Active": True, "SortOrder": 3},
        {"DesignationName": "Beat Officer",                "Active": True, "SortOrder": 4},
        {"DesignationName": "Assistant Investigating Officer", "Active": True, "SortOrder": 5},
        {"DesignationName": "Duty Officer",                "Active": True, "SortOrder": 6},
        {"DesignationName": "Law and Order Officer",       "Active": True, "SortOrder": 7},
        {"DesignationName": "Crime Branch Chief",          "Active": True, "SortOrder": 8},
        {"DesignationName": "Reader to SP",                "Active": True, "SortOrder": 9},
        {"DesignationName": "Public Relations Officer",    "Active": True, "SortOrder": 10},
        {"DesignationName": "Wireless Operator",           "Active": True, "SortOrder": 11},
        {"DesignationName": "Cyber Analyst",               "Active": True, "SortOrder": 12},
        {"DesignationName": "Forensic Expert",             "Active": True, "SortOrder": 13},
        {"DesignationName": "Dog Squad In-charge",         "Active": True, "SortOrder": 14},
        {"DesignationName": "Armourer",                    "Active": True, "SortOrder": 15},
        {"DesignationName": "Guard Commander",             "Active": True, "SortOrder": 16},
    ])
    results.append(res)
    desig_rid = rowids(desig_rows)

    # ─────────────────────────────────────────────────────────────────
    # 8. Employee (FK → District, Unit, Rank, Designation) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, emp_rows = insert(ds, "Employee", [
        {"KGID": "KG2001101", "FirstName": "Rajesh Kumar",       "EmployeeDOB": "1985-03-15", "GenderID": 1, "BloodGroupID": 2, "PhysicallyChallenged": False, "AppointmentDate": "2008-06-01", "DistrictID": dist_rid[0],  "UnitID": unit_rid[0],  "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"KGID": "KG2001102", "FirstName": "Priya Sharma",        "EmployeeDOB": "1990-07-22", "GenderID": 2, "BloodGroupID": 1, "PhysicallyChallenged": False, "AppointmentDate": "2013-09-15", "DistrictID": dist_rid[0],  "UnitID": unit_rid[0],  "RankID": rank_rid[2], "DesignationID": desig_rid[1]},
        {"KGID": "KG2001103", "FirstName": "Mohammed Farooq",     "EmployeeDOB": "1982-11-08", "GenderID": 1, "BloodGroupID": 3, "PhysicallyChallenged": False, "AppointmentDate": "2005-03-20", "DistrictID": dist_rid[1],  "UnitID": unit_rid[2],  "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"KGID": "KG2001104", "FirstName": "Anitha Reddy",        "EmployeeDOB": "1993-05-30", "GenderID": 2, "BloodGroupID": 4, "PhysicallyChallenged": False, "AppointmentDate": "2016-11-01", "DistrictID": dist_rid[1],  "UnitID": unit_rid[2],  "RankID": rank_rid[2], "DesignationID": desig_rid[1]},
        {"KGID": "KG2001105", "FirstName": "Suresh Patil",        "EmployeeDOB": "1988-12-05", "GenderID": 1, "BloodGroupID": 2, "PhysicallyChallenged": False, "AppointmentDate": "2011-04-10", "DistrictID": dist_rid[0],  "UnitID": unit_rid[0],  "RankID": rank_rid[0], "DesignationID": desig_rid[3]},
        {"KGID": "KG2001106", "FirstName": "Vikram Singh",        "EmployeeDOB": "1984-01-20", "GenderID": 1, "BloodGroupID": 3, "PhysicallyChallenged": False, "AppointmentDate": "2006-08-15", "DistrictID": dist_rid[0],  "UnitID": unit_rid[1],  "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"KGID": "KG2001107", "FirstName": "Deepa N",             "EmployeeDOB": "1991-09-18", "GenderID": 2, "BloodGroupID": 1, "PhysicallyChallenged": False, "AppointmentDate": "2014-05-12", "DistrictID": dist_rid[0],  "UnitID": unit_rid[1],  "RankID": rank_rid[2], "DesignationID": desig_rid[1]},
        {"KGID": "KG2001108", "FirstName": "Ramesh Chandra",      "EmployeeDOB": "1980-05-25", "GenderID": 1, "BloodGroupID": 2, "PhysicallyChallenged": False, "AppointmentDate": "2002-12-01", "DistrictID": dist_rid[4],  "UnitID": unit_rid[6],  "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"KGID": "KG2001109", "FirstName": "Kavitha Murthy",      "EmployeeDOB": "1987-10-31", "GenderID": 2, "BloodGroupID": 4, "PhysicallyChallenged": False, "AppointmentDate": "2009-02-15", "DistrictID": dist_rid[4],  "UnitID": unit_rid[6],  "RankID": rank_rid[2], "DesignationID": desig_rid[1]},
        {"KGID": "KG2001110", "FirstName": "Jayaram Bhat",        "EmployeeDOB": "1978-04-14", "GenderID": 1, "BloodGroupID": 3, "PhysicallyChallenged": False, "AppointmentDate": "2001-09-20", "DistrictID": dist_rid[5],  "UnitID": unit_rid[7],  "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"KGID": "KG2001111", "FirstName": "Abdul Hameed",        "EmployeeDOB": "1983-08-08", "GenderID": 1, "BloodGroupID": 1, "PhysicallyChallenged": False, "AppointmentDate": "2007-06-15", "DistrictID": dist_rid[7],  "UnitID": unit_rid[8],  "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"KGID": "KG2001112", "FirstName": "Meenakshi Sundaram",  "EmployeeDOB": "1992-06-11", "GenderID": 2, "BloodGroupID": 2, "PhysicallyChallenged": False, "AppointmentDate": "2015-08-01", "DistrictID": dist_rid[7],  "UnitID": unit_rid[8],  "RankID": rank_rid[2], "DesignationID": desig_rid[1]},
        {"KGID": "KG2001113", "FirstName": "Sanjay G",            "EmployeeDOB": "1989-11-22", "GenderID": 1, "BloodGroupID": 4, "PhysicallyChallenged": False, "AppointmentDate": "2012-10-15", "DistrictID": dist_rid[10], "UnitID": unit_rid[10], "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"KGID": "KG2001114", "FirstName": "Sunita K",            "EmployeeDOB": "1986-07-07", "GenderID": 2, "BloodGroupID": 1, "PhysicallyChallenged": False, "AppointmentDate": "2010-03-25", "DistrictID": dist_rid[12], "UnitID": unit_rid[11], "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"KGID": "KG2001115", "FirstName": "Prasad Rao",          "EmployeeDOB": "1981-02-28", "GenderID": 1, "BloodGroupID": 2, "PhysicallyChallenged": False, "AppointmentDate": "2004-11-10", "DistrictID": dist_rid[0],  "UnitID": unit_rid[0],  "RankID": rank_rid[1], "DesignationID": desig_rid[2]},
        {"KGID": "KG2001116", "FirstName": "Vinay Kumar",         "EmployeeDOB": "1995-04-19", "GenderID": 1, "BloodGroupID": 3, "PhysicallyChallenged": False, "AppointmentDate": "2018-09-01", "DistrictID": dist_rid[0],  "UnitID": unit_rid[0],  "RankID": rank_rid[0], "DesignationID": desig_rid[3]},
    ])
    results.append(res)
    emp_rid = rowids(emp_rows)

    # ─────────────────────────────────────────────────────────────────
    # 9. CaseCategory (no FK) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, casecat_rows = insert(ds, "CaseCategory", [
        {"LookupValue": "FIR"},
        {"LookupValue": "UDR"},
        {"LookupValue": "PAR"},
        {"LookupValue": "Zero FIR"},
        {"LookupValue": "NCR"},
        {"LookupValue": "Missing Report"},
        {"LookupValue": "Petty Case"},
        {"LookupValue": "Preventive Case"},
        {"LookupValue": "NCR-Petty"},
        {"LookupValue": "UDR-Accidental"},
        {"LookupValue": "UDR-Suicide"},
        {"LookupValue": "UDR-Suspicious"},
        {"LookupValue": "Juvenile Case"},
        {"LookupValue": "Sessions Case"},
        {"LookupValue": "Special Court Case"},
        {"LookupValue": "Lok Adalat Case"},
    ])
    results.append(res)
    casecat_rid = rowids(casecat_rows)

    # ─────────────────────────────────────────────────────────────────
    # 10. GravityOffence (no FK) -> 12 rows (4x original 3)
    # ─────────────────────────────────────────────────────────────────
    res, gravity_rows = insert(ds, "GravityOffence", [
        {"LookupValue": "Heinous"},
        {"LookupValue": "Serious"},
        {"LookupValue": "Non-Heinous"},
        {"LookupValue": "Minor"},
        {"LookupValue": "Petty"},
        {"LookupValue": "Moderate"},
        {"LookupValue": "Critical"},
        {"LookupValue": "Extremely Heinous"},
        {"LookupValue": "High Severity"},
        {"LookupValue": "Low Severity"},
        {"LookupValue": "Medium Severity"},
        {"LookupValue": "Statutory"},
    ])
    results.append(res)
    gravity_rid = rowids(gravity_rows)

    # ─────────────────────────────────────────────────────────────────
    # 11. CrimeHead (no FK) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, crimehead_rows = insert(ds, "CrimeHead", [
        {"CrimeGroupName": "Crimes Against Body",     "Active": True},
        {"CrimeGroupName": "Crimes Against Property", "Active": True},
        {"CrimeGroupName": "Crimes Against Women",    "Active": True},
        {"CrimeGroupName": "Cyber Crimes",            "Active": True},
        {"CrimeGroupName": "White Collar Crimes",     "Active": True},
        {"CrimeGroupName": "Narcotics Offenses",      "Active": True},
        {"CrimeGroupName": "Public Order Offenses",   "Active": True},
        {"CrimeGroupName": "Traffic Violations",      "Active": True},
        {"CrimeGroupName": "Economic Offenses",       "Active": True},
        {"CrimeGroupName": "Environmental Crimes",    "Active": True},
        {"CrimeGroupName": "Juvenile Delinquency",    "Active": True},
        {"CrimeGroupName": "Election Offenses",       "Active": True},
        {"CrimeGroupName": "Arms Act Cases",          "Active": True},
        {"CrimeGroupName": "National Security Offenses", "Active": True},
        {"CrimeGroupName": "Excise Act Cases",        "Active": True},
        {"CrimeGroupName": "Government Property Damage", "Active": True},
    ])
    results.append(res)
    ch_rid = rowids(crimehead_rows)

    # ─────────────────────────────────────────────────────────────────
    # 12. CrimeSubHead (FK → CrimeHead) -> 32 rows (4x original 8)
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
        {"CrimeHeadID": ch_rid[0], "CrimeHeadName": "Kidnapping",        "SeqID": 3},
        {"CrimeHeadID": ch_rid[0], "CrimeHeadName": "Grievous Hurt",     "SeqID": 4},
        {"CrimeHeadID": ch_rid[0], "CrimeHeadName": "Assault",           "SeqID": 5},
        {"CrimeHeadID": ch_rid[1], "CrimeHeadName": "Theft",             "SeqID": 5},
        {"CrimeHeadID": ch_rid[1], "CrimeHeadName": "Extortion",         "SeqID": 6},
        {"CrimeHeadID": ch_rid[1], "CrimeHeadName": "Dacoity",           "SeqID": 7},
        {"CrimeHeadID": ch_rid[2], "CrimeHeadName": "Dowry Death",       "SeqID": 2},
        {"CrimeHeadID": ch_rid[2], "CrimeHeadName": "Domestic Violence", "SeqID": 3},
        {"CrimeHeadID": ch_rid[2], "CrimeHeadName": "Stalking",          "SeqID": 4},
        {"CrimeHeadID": ch_rid[3], "CrimeHeadName": "Hacking",           "SeqID": 2},
        {"CrimeHeadID": ch_rid[3], "CrimeHeadName": "Phishing",          "SeqID": 3},
        {"CrimeHeadID": ch_rid[3], "CrimeHeadName": "Identity Theft",    "SeqID": 4},
        {"CrimeHeadID": ch_rid[4], "CrimeHeadName": "Corporate Fraud",   "SeqID": 1},
        {"CrimeHeadID": ch_rid[4], "CrimeHeadName": "Money Laundering",  "SeqID": 2},
        {"CrimeHeadID": ch_rid[5], "CrimeHeadName": "Drug Possession",   "SeqID": 1},
        {"CrimeHeadID": ch_rid[5], "CrimeHeadName": "Drug Trafficking",  "SeqID": 2},
        {"CrimeHeadID": ch_rid[6], "CrimeHeadName": "Rioting",           "SeqID": 1},
        {"CrimeHeadID": ch_rid[6], "CrimeHeadName": "Unlawful Assembly", "SeqID": 2},
        {"CrimeHeadID": ch_rid[7], "CrimeHeadName": "Drunken Driving",   "SeqID": 1},
        {"CrimeHeadID": ch_rid[7], "CrimeHeadName": "Reckless Driving",  "SeqID": 2},
        {"CrimeHeadID": ch_rid[8], "CrimeHeadName": "Tax Evasion",       "SeqID": 1},
        {"CrimeHeadID": ch_rid[8], "CrimeHeadName": "Smuggling",         "SeqID": 2},
        {"CrimeHeadID": ch_rid[9], "CrimeHeadName": "Wildlife Poaching", "SeqID": 1},
        {"CrimeHeadID": ch_rid[12], "CrimeHeadName": "Arms Smuggling",   "SeqID": 1},
    ])
    results.append(res)
    csh_rid = rowids(csh_rows)

    # ─────────────────────────────────────────────────────────────────
    # 13. Act (no FK) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, act_rows = insert(ds, "Act", [
        {"ActDescription": "Indian Penal Code, 1860",                               "ShortName": "IPC",          "Active": True},
        {"ActDescription": "Narcotic Drugs and Psychotropic Substances Act, 1985",  "ShortName": "NDPS",         "Active": True},
        {"ActDescription": "Information Technology Act, 2000",                      "ShortName": "IT Act",       "Active": True},
        {"ActDescription": "Protection of Children from Sexual Offences Act, 2012", "ShortName": "POCSO",        "Active": True},
        {"ActDescription": "Arms Act, 1959",                                        "ShortName": "Arms Act",     "Active": True},
        {"ActDescription": "Prevention of Corruption Act, 1988",                    "ShortName": "PCA",          "Active": True},
        {"ActDescription": "Motor Vehicles Act, 1988",                              "ShortName": "MVA",          "Active": True},
        {"ActDescription": "Excise Act, 1965",                                      "ShortName": "Excise Act",   "Active": True},
        {"ActDescription": "Wildlife Protection Act, 1972",                         "ShortName": "WPA",          "Active": True},
        {"ActDescription": "Prevention of Money Laundering Act, 2002",              "ShortName": "PMLA",         "Active": True},
        {"ActDescription": "Essential Commodities Act, 1955",                      "ShortName": "ECA",          "Active": True},
        {"ActDescription": "Dowry Prohibition Act, 1961",                           "ShortName": "DPA",          "Active": True},
        {"ActDescription": "Domestic Violence Act, 2005",                           "ShortName": "DVA",          "Active": True},
        {"ActDescription": "Copyright Act, 1957",                                   "ShortName": "CRA",          "Active": True},
        {"ActDescription": "Passport Act, 1967",                                    "ShortName": "Passport Act", "Active": True},
        {"ActDescription": "Epidemic Diseases Act, 1897",                           "ShortName": "EDA",          "Active": True},
    ])
    results.append(res)
    act_rid = rowids(act_rows)

    # ─────────────────────────────────────────────────────────────────
    # 14. Section (FK → Act) -> 32 rows (4x original 8)
    # ─────────────────────────────────────────────────────────────────
    res, section_rows = insert(ds, "Section", [
        {"ActCode": act_rid[0],  "SectionCode": "302",  "SectionDescription": "Punishment for murder",                          "Active": True},
        {"ActCode": act_rid[0],  "SectionCode": "307",  "SectionDescription": "Attempt to commit murder",                       "Active": True},
        {"ActCode": act_rid[0],  "SectionCode": "379",  "SectionDescription": "Punishment for theft",                           "Active": True},
        {"ActCode": act_rid[0],  "SectionCode": "392",  "SectionDescription": "Punishment for robbery",                         "Active": True},
        {"ActCode": act_rid[0],  "SectionCode": "411",  "SectionDescription": "Dishonestly receiving stolen property",          "Active": True},
        {"ActCode": act_rid[0],  "SectionCode": "420",  "SectionDescription": "Cheating and dishonestly inducing delivery",     "Active": True},
        {"ActCode": act_rid[2],  "SectionCode": "66C",  "SectionDescription": "Identity theft",                                 "Active": True},
        {"ActCode": act_rid[2],  "SectionCode": "66D",  "SectionDescription": "Cheating by personation using computer resource","Active": True},
        {"ActCode": act_rid[0],  "SectionCode": "363",  "SectionDescription": "Punishment for kidnapping",                      "Active": True},
        {"ActCode": act_rid[0],  "SectionCode": "326",  "SectionDescription": "Voluntarily causing grievous hurt by weapons",    "Active": True},
        {"ActCode": act_rid[0],  "SectionCode": "354",  "SectionDescription": "Assault or criminal force to woman",              "Active": True},
        {"ActCode": act_rid[0],  "SectionCode": "384",  "SectionDescription": "Punishment for extortion",                       "Active": True},
        {"ActCode": act_rid[0],  "SectionCode": "395",  "SectionDescription": "Punishment for dacoity",                        "Active": True},
        {"ActCode": act_rid[0],  "SectionCode": "498A", "SectionDescription": "Husband or relative subjecting woman to cruelty","Active": True},
        {"ActCode": act_rid[0],  "SectionCode": "304B", "SectionDescription": "Dowry death",                                    "Active": True},
        {"ActCode": act_rid[1],  "SectionCode": "20",   "SectionDescription": "Contravention in relation to cannabis plant",    "Active": True},
        {"ActCode": act_rid[1],  "SectionCode": "22",   "SectionDescription": "Contravention in relation to psychotropic subst", "Active": True},
        {"ActCode": act_rid[2],  "SectionCode": "66",   "SectionDescription": "Computer related offences",                      "Active": True},
        {"ActCode": act_rid[2],  "SectionCode": "66E",  "SectionDescription": "Violation of privacy",                           "Active": True},
        {"ActCode": act_rid[3],  "SectionCode": "4",    "SectionDescription": "Punishment for penetrative sexual assault",      "Active": True},
        {"ActCode": act_rid[4],  "SectionCode": "25",   "SectionDescription": "Possession of unlicensed arms",                  "Active": True},
        {"ActCode": act_rid[4],  "SectionCode": "27",   "SectionDescription": "Punishment for using arms",                      "Active": True},
        {"ActCode": act_rid[5],  "SectionCode": "7",    "SectionDescription": "Public servant taking gratification",            "Active": True},
        {"ActCode": act_rid[5],  "SectionCode": "13",   "SectionDescription": "Criminal misconduct by a public servant",        "Active": True},
        {"ActCode": act_rid[6],  "SectionCode": "185",  "SectionDescription": "Drunken driving offence",                        "Active": True},
        {"ActCode": act_rid[6],  "SectionCode": "184",  "SectionDescription": "Driving dangerously",                            "Active": True},
        {"ActCode": act_rid[7],  "SectionCode": "32",   "SectionDescription": "Illegal import/export of intoxicants",           "Active": True},
        {"ActCode": act_rid[7],  "SectionCode": "34",   "SectionDescription": "Illegal possession of intoxicants",             "Active": True},
        {"ActCode": act_rid[8],  "SectionCode": "9",    "SectionDescription": "Hunting of wild animals prohibited",             "Active": True},
        {"ActCode": act_rid[9],  "SectionCode": "3",    "SectionDescription": "Offence of money laundering",                    "Active": True},
        {"ActCode": act_rid[11], "SectionCode": "3",    "SectionDescription": "Penalty for giving or taking dowry",             "Active": True},
        {"ActCode": act_rid[12], "SectionCode": "18",   "SectionDescription": "Protection orders in domestic violence",         "Active": True},
    ])
    results.append(res)
    sec_rid = rowids(section_rows)

    # ─────────────────────────────────────────────────────────────────
    # 15. CrimeHeadActSection (FK → CrimeHead, Act) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "CrimeHeadActSection", [
        {"CrimeHeadID": ch_rid[0],  "ActCode": act_rid[0], "SectionCode": "302"},
        {"CrimeHeadID": ch_rid[0],  "ActCode": act_rid[0], "SectionCode": "307"},
        {"CrimeHeadID": ch_rid[1],  "ActCode": act_rid[0], "SectionCode": "379"},
        {"CrimeHeadID": ch_rid[1],  "ActCode": act_rid[0], "SectionCode": "392"},
        {"CrimeHeadID": ch_rid[0],  "ActCode": act_rid[0], "SectionCode": "363"},
        {"CrimeHeadID": ch_rid[0],  "ActCode": act_rid[0], "SectionCode": "326"},
        {"CrimeHeadID": ch_rid[2],  "ActCode": act_rid[0], "SectionCode": "354"},
        {"CrimeHeadID": ch_rid[1],  "ActCode": act_rid[0], "SectionCode": "384"},
        {"CrimeHeadID": ch_rid[1],  "ActCode": act_rid[0], "SectionCode": "395"},
        {"CrimeHeadID": ch_rid[3],  "ActCode": act_rid[2], "SectionCode": "66C"},
        {"CrimeHeadID": ch_rid[3],  "ActCode": act_rid[2], "SectionCode": "66D"},
        {"CrimeHeadID": ch_rid[3],  "ActCode": act_rid[2], "SectionCode": "66E"},
        {"CrimeHeadID": ch_rid[5],  "ActCode": act_rid[1], "SectionCode": "20"},
        {"CrimeHeadID": ch_rid[5],  "ActCode": act_rid[1], "SectionCode": "22"},
        {"CrimeHeadID": ch_rid[7],  "ActCode": act_rid[6], "SectionCode": "185"},
        {"CrimeHeadID": ch_rid[7],  "ActCode": act_rid[6], "SectionCode": "184"},
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # 16. OccupationMaster (no FK) -> 20 rows (4x original 5)
    # ─────────────────────────────────────────────────────────────────
    res, occ_rows = insert(ds, "OccupationMaster", [
        {"OccupationName": "Farmer"},
        {"OccupationName": "Government Employee"},
        {"OccupationName": "Business"},
        {"OccupationName": "Daily Wage Worker"},
        {"OccupationName": "Student"},
        {"OccupationName": "Software Engineer"},
        {"OccupationName": "Doctor"},
        {"OccupationName": "Lawyer"},
        {"OccupationName": "Teacher"},
        {"OccupationName": "Driver"},
        {"OccupationName": "Housewife"},
        {"OccupationName": "Unemployed"},
        {"OccupationName": "Retired"},
        {"OccupationName": "Police Personnel"},
        {"OccupationName": "IT Analyst"},
        {"OccupationName": "Security Guard"},
        {"OccupationName": "Electrician"},
        {"OccupationName": "Plumber"},
        {"OccupationName": "Shopkeeper"},
        {"OccupationName": "Artist"},
    ])
    results.append(res)
    occ_rid = rowids(occ_rows)

    # ─────────────────────────────────────────────────────────────────
    # 17. ReligionMaster (no FK) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, rel_rows = insert(ds, "ReligionMaster", [
        {"ReligionName": "Hindu"},
        {"ReligionName": "Muslim"},
        {"ReligionName": "Christian"},
        {"ReligionName": "Jain"},
        {"ReligionName": "Sikh"},
        {"ReligionName": "Buddhist"},
        {"ReligionName": "Parsi"},
        {"ReligionName": "Jewish"},
        {"ReligionName": "Tribal Religion"},
        {"ReligionName": "Bahai"},
        {"ReligionName": "Atheist"},
        {"ReligionName": "Agnostic"},
        {"ReligionName": "Spiritualist"},
        {"ReligionName": "Humanist"},
        {"ReligionName": "Other"},
        {"ReligionName": "Not Disclosed"},
    ])
    results.append(res)
    rel_rid = rowids(rel_rows)

    # ─────────────────────────────────────────────────────────────────
    # 18. CasteMaster (no FK) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, caste_rows = insert(ds, "CasteMaster", [
        {"caste_master_name": "General"},
        {"caste_master_name": "OBC"},
        {"caste_master_name": "SC"},
        {"caste_master_name": "ST"},
        {"caste_master_name": "Lingayat"},
        {"caste_master_name": "Vokkaliga"},
        {"caste_master_name": "Kuruba"},
        {"caste_master_name": "Madiga"},
        {"caste_master_name": "Chalavadi"},
        {"caste_master_name": "Billava"},
        {"caste_master_name": "Bunt"},
        {"caste_master_name": "Mogaveera"},
        {"caste_master_name": "Idiga"},
        {"caste_master_name": "Devanga"},
        {"caste_master_name": "Sadar"},
        {"caste_master_name": "Nayaka"},
    ])
    results.append(res)
    caste_rid = rowids(caste_rows)

    # ─────────────────────────────────────────────────────────────────
    # 19. CaseStatusMaster (no FK) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, status_rows = insert(ds, "CaseStatusMaster", [
        {"CaseStatusName": "Under Investigation"},
        {"CaseStatusName": "Charge Sheeted"},
        {"CaseStatusName": "Referred to Court"},
        {"CaseStatusName": "Closed"},
        {"CaseStatusName": "Stayed by High Court"},
        {"CaseStatusName": "Compromised"},
        {"CaseStatusName": "Convicted"},
        {"CaseStatusName": "Acquitted"},
        {"CaseStatusName": "Abated (Accused Dead)"},
        {"CaseStatusName": "Quashed"},
        {"CaseStatusName": "Pending Trial"},
        {"CaseStatusName": "Transfer to other PS"},
        {"CaseStatusName": "Reopened"},
        {"CaseStatusName": "Untraceable (FR-C)"},
        {"CaseStatusName": "False Case (FR-B)"},
        {"CaseStatusName": "Mistake of Fact (FR-G)"},
    ])
    results.append(res)
    status_rid = rowids(status_rows)

    # ─────────────────────────────────────────────────────────────────
    # 20. CaseMaster (FK → Employee, Unit, CaseCategory, GravityOffence,
    #                       CrimeHead, CrimeSubHead, CaseStatusMaster, Court) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, case_rows = insert(ds, "CaseMaster", [
        # Original 4 Cases
        {
            "CrimeNo": "104430100120240001", "CaseNo": "202400001", "CrimeRegisteredDate": "2024-03-15",
            "PolicePersonID": emp_rid[0], "PoliceStationID": unit_rid[0], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[0], "CrimeMajorHeadID": ch_rid[0], "CrimeMinorHeadID": csh_rid[0],
            "CaseStatusID": status_rid[0], "CourtID": court_rid[0], "IncidentFromDate": "2024-03-14 22:30:00",
            "IncidentToDate": "2024-03-14 23:00:00", "InfoReceivedPSDate": "2024-03-15 01:15:00",
            "latitude": 12.9716, "longitude": 77.5946,
            "BriefFacts": "On 14-03-2024 at approximately 22:30 hrs, the complainant Suresh Nair reported that his neighbour was found dead in his residence near Cubbon Park. The victim had multiple stab wounds on the chest."
        },
        {
            "CrimeNo": "104430100120240002", "CaseNo": "202400002", "CrimeRegisteredDate": "2024-04-02",
            "PolicePersonID": emp_rid[1], "PoliceStationID": unit_rid[0], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[1], "CrimeMajorHeadID": ch_rid[1], "CrimeMinorHeadID": csh_rid[3],
            "CaseStatusID": status_rid[0], "CourtID": None, "IncidentFromDate": "2024-04-02 08:15:00",
            "IncidentToDate": "2024-04-02 08:20:00", "InfoReceivedPSDate": "2024-04-02 09:00:00",
            "latitude": 12.9352, "longitude": 77.6245,
            "BriefFacts": "On 02-04-2024 at 08:15 hrs, complainant Lakshmi Devi reported that two persons on a two-wheeler snatched her gold chain valued at Rs 45,000 near Koramangala market."
        },
        {
            "CrimeNo": "104430100320240001", "CaseNo": "202400001", "CrimeRegisteredDate": "2024-05-20",
            "PolicePersonID": emp_rid[2], "PoliceStationID": unit_rid[2], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[1], "CrimeMajorHeadID": ch_rid[1], "CrimeMinorHeadID": csh_rid[4],
            "CaseStatusID": status_rid[1], "CourtID": court_rid[1], "IncidentFromDate": "2024-05-19 23:45:00",
            "IncidentToDate": "2024-05-20 00:30:00", "InfoReceivedPSDate": "2024-05-20 07:00:00",
            "latitude": 12.2958, "longitude": 76.6394,
            "BriefFacts": "On 19-05-2024, complainant Ramesh Gowda reported that his Honda City car was stolen from the parking area of Mysuru Palace Road. It was found abandoned in Bannimantap."
        },
        {
            "CrimeNo": "104430100120240003", "CaseNo": "202400003", "CrimeRegisteredDate": "2024-06-10",
            "PolicePersonID": emp_rid[1], "PoliceStationID": unit_rid[0], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[2], "CrimeMajorHeadID": ch_rid[3], "CrimeMinorHeadID": csh_rid[7],
            "CaseStatusID": status_rid[0], "CourtID": None, "IncidentFromDate": "2024-06-08 14:00:00",
            "IncidentToDate": "2024-06-08 15:30:00", "InfoReceivedPSDate": "2024-06-10 11:20:00",
            "latitude": 12.9789, "longitude": 77.5917,
            "BriefFacts": "On 10-06-2024, complainant Anil Mehta reported that he received a call from an unknown person posing as a bank official who cheated him of Rs 1,20,000 via OTP."
        },
        # Case 5 (Kidnapping)
        {
            "CrimeNo": "104430100120240005", "CaseNo": "202400005", "CrimeRegisteredDate": "2024-07-01",
            "PolicePersonID": emp_rid[6], "PoliceStationID": unit_rid[1], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[0], "CrimeMajorHeadID": ch_rid[0], "CrimeMinorHeadID": csh_rid[8],
            "CaseStatusID": status_rid[0], "CourtID": court_rid[0], "IncidentFromDate": "2024-06-30 16:00:00",
            "IncidentToDate": "2024-06-30 18:00:00", "InfoReceivedPSDate": "2024-07-01 09:30:00",
            "latitude": 12.9344, "longitude": 77.6192,
            "BriefFacts": "Complainant Vikram Gowda reported that his 10-year-old son was kidnapped by unidentified persons while returning from school. A ransom call was received demanding Rs 5 lakhs."
        },
        # Case 6 (Grievous Hurt)
        {
            "CrimeNo": "104430100120240006", "CaseNo": "202400006", "CrimeRegisteredDate": "2024-07-15",
            "PolicePersonID": emp_rid[6], "PoliceStationID": unit_rid[1], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[2], "CrimeMajorHeadID": ch_rid[0], "CrimeMinorHeadID": csh_rid[9],
            "CaseStatusID": status_rid[0], "CourtID": None, "IncidentFromDate": "2024-07-14 21:00:00",
            "IncidentToDate": "2024-07-14 21:30:00", "InfoReceivedPSDate": "2024-07-15 08:00:00",
            "latitude": 12.9279, "longitude": 77.6271,
            "BriefFacts": "A street brawl broke out in Koramangala 4th block. The victim Girish K was assaulted by a local gang with iron rods, sustaining grievous head injuries."
        },
        # Case 7 (Dacoity)
        {
            "CrimeNo": "104430100120240007", "CaseNo": "202400007", "CrimeRegisteredDate": "2024-08-01",
            "PolicePersonID": emp_rid[7], "PoliceStationID": unit_rid[6], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[0], "CrimeMajorHeadID": ch_rid[1], "CrimeMinorHeadID": csh_rid[13],
            "CaseStatusID": status_rid[0], "CourtID": court_rid[5], "IncidentFromDate": "2024-07-31 23:30:00",
            "IncidentToDate": "2024-08-01 02:00:00", "InfoReceivedPSDate": "2024-08-01 06:00:00",
            "latitude": 15.4589, "longitude": 75.0078,
            "BriefFacts": "A gang of 5 armed robbers broke into the Dharwad Coop Bank, held the security guard hostage, and looted cash worth Rs 45 lakhs from the safe."
        },
        # Case 8 (Domestic Violence)
        {
            "CrimeNo": "104430100120240008", "CaseNo": "202400008", "CrimeRegisteredDate": "2024-08-10",
            "PolicePersonID": emp_rid[8], "PoliceStationID": unit_rid[6], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[1], "CrimeMajorHeadID": ch_rid[2], "CrimeMinorHeadID": csh_rid[15],
            "CaseStatusID": status_rid[0], "CourtID": None, "IncidentFromDate": "2024-08-09 20:00:00",
            "IncidentToDate": "2024-08-09 23:00:00", "InfoReceivedPSDate": "2024-08-10 10:00:00",
            "latitude": 15.4512, "longitude": 75.0125,
            "BriefFacts": "Victim Shalini Prasad filed a complaint against her husband and in-laws for continuous physical harassment and demands for extra dowry."
        },
        # Case 9 (POCSO)
        {
            "CrimeNo": "104430100120240009", "CaseNo": "202400009", "CrimeRegisteredDate": "2024-08-20",
            "PolicePersonID": emp_rid[9], "PoliceStationID": unit_rid[7], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[0], "CrimeMajorHeadID": ch_rid[2], "CrimeMinorHeadID": csh_rid[14],
            "CaseStatusID": status_rid[0], "CourtID": court_rid[6], "IncidentFromDate": "2024-08-19 14:00:00",
            "IncidentToDate": "2024-08-19 15:00:00", "InfoReceivedPSDate": "2024-08-20 11:00:00",
            "latitude": 13.3408, "longitude": 74.7421,
            "BriefFacts": "A POCSO case registered against a tuition teacher Vikas M for sexually abusing a minor student aged 14 during tuition hours in Udupi."
        },
        # Case 10 (Drug Possession)
        {
            "CrimeNo": "104430100120240010", "CaseNo": "202400010", "CrimeRegisteredDate": "2024-09-01",
            "PolicePersonID": emp_rid[10], "PoliceStationID": unit_rid[8], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[0], "CrimeMajorHeadID": ch_rid[5], "CrimeMinorHeadID": csh_rid[22],
            "CaseStatusID": status_rid[1], "CourtID": court_rid[8], "IncidentFromDate": "2024-08-31 22:00:00",
            "IncidentToDate": "2024-08-31 22:30:00", "InfoReceivedPSDate": "2024-09-01 02:00:00",
            "latitude": 13.0827, "longitude": 80.2707,
            "BriefFacts": "During a routine vehicle patrol near Chennai Central, accused Peter D'Souza was caught possessing 250g of MDMA crystals inside his scooter."
        },
        # Case 11 (Rioting)
        {
            "CrimeNo": "104430100120240011", "CaseNo": "202400011", "CrimeRegisteredDate": "2024-09-15",
            "PolicePersonID": emp_rid[11], "PoliceStationID": unit_rid[8], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[1], "CrimeMajorHeadID": ch_rid[6], "CrimeMinorHeadID": csh_rid[24],
            "CaseStatusID": status_rid[0], "CourtID": None, "IncidentFromDate": "2024-09-14 18:00:00",
            "IncidentToDate": "2024-09-14 20:00:00", "InfoReceivedPSDate": "2024-09-15 09:00:00",
            "latitude": 13.0872, "longitude": 80.2784,
            "BriefFacts": "Clash between two local factions in Chennai Central resulting in stone pelting, damage to public buses, and injuries to officers on duty."
        },
        # Case 12 (Drunken Driving)
        {
            "CrimeNo": "104430100120240012", "CaseNo": "202400012", "CrimeRegisteredDate": "2024-09-25",
            "PolicePersonID": emp_rid[0], "PoliceStationID": unit_rid[0], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[2], "CrimeMajorHeadID": ch_rid[7], "CrimeMinorHeadID": csh_rid[26],
            "CaseStatusID": status_rid[3], "CourtID": court_rid[0], "IncidentFromDate": "2024-09-24 23:30:00",
            "IncidentToDate": "2024-09-24 23:45:00", "InfoReceivedPSDate": "2024-09-25 01:00:00",
            "latitude": 12.9731, "longitude": 77.5962,
            "BriefFacts": "Accused Rajeev Hegde crashed his car into a pedestrian safety barrier at Cubbon Park under heavy alcohol influence (BAC measured at 150mg/100ml)."
        },
        # Case 13 (Hacking)
        {
            "CrimeNo": "104430100120240013", "CaseNo": "202400013", "CrimeRegisteredDate": "2024-10-05",
            "PolicePersonID": emp_rid[1], "PoliceStationID": unit_rid[0], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[1], "CrimeMajorHeadID": ch_rid[3], "CrimeMinorHeadID": csh_rid[17],
            "CaseStatusID": status_rid[0], "CourtID": None, "IncidentFromDate": "2024-10-03 00:00:00",
            "IncidentToDate": "2024-10-04 12:00:00", "InfoReceivedPSDate": "2024-10-05 10:00:00",
            "latitude": 12.9719, "longitude": 77.5937,
            "BriefFacts": "A corporate server of ABC Technologies was breached. Ransomware was deployed encrypting crucial database backups and demanding Bitcoins."
        },
        # Case 14 (UDR Case)
        {
            "CrimeNo": "304430100120240014", "CaseNo": "202400014", "CrimeRegisteredDate": "2024-10-15",
            "PolicePersonID": emp_rid[2], "PoliceStationID": unit_rid[2], "CaseCategoryID": casecat_rid[1],
            "GravityOffenceID": gravity_rid[2], "CrimeMajorHeadID": ch_rid[0], "CrimeMinorHeadID": csh_rid[0],
            "CaseStatusID": status_rid[3], "CourtID": None, "IncidentFromDate": "2024-10-14 10:00:00",
            "IncidentToDate": "2024-10-14 14:00:00", "InfoReceivedPSDate": "2024-10-15 08:30:00",
            "latitude": 12.2981, "longitude": 76.6415,
            "BriefFacts": "Unnatural Death Report filed. Body of villager Somappa (age 55) found floating in a village lake near Mysuru. No external wounds visible."
        },
        # Case 15 (Zero FIR)
        {
            "CrimeNo": "804430100120240015", "CaseNo": "202400015", "CrimeRegisteredDate": "2024-10-20",
            "PolicePersonID": emp_rid[3], "PoliceStationID": unit_rid[2], "CaseCategoryID": casecat_rid[3],
            "GravityOffenceID": gravity_rid[1], "CrimeMajorHeadID": ch_rid[1], "CrimeMinorHeadID": csh_rid[2],
            "CaseStatusID": status_rid[0], "CourtID": None, "IncidentFromDate": "2024-10-19 12:00:00",
            "IncidentToDate": "2024-10-19 13:00:00", "InfoReceivedPSDate": "2024-10-20 09:00:00",
            "latitude": 12.3012, "longitude": 76.6288,
            "BriefFacts": "Complainant Girija Bai reported that she was robbed of her purse containing cash and jewelry while traveling. Forwarded to original jurisdiction."
        },
        # Case 16 (Money Laundering)
        {
            "CrimeNo": "104430100120240016", "CaseNo": "202400016", "CrimeRegisteredDate": "2024-11-01",
            "PolicePersonID": emp_rid[12], "PoliceStationID": unit_rid[10], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[0], "CrimeMajorHeadID": ch_rid[8], "CrimeMinorHeadID": csh_rid[21],
            "CaseStatusID": status_rid[0], "CourtID": court_rid[11], "IncidentFromDate": "2024-05-01 09:00:00",
            "IncidentToDate": "2024-10-31 17:00:00", "InfoReceivedPSDate": "2024-11-01 10:30:00",
            "latitude": 16.5062, "longitude": 80.6480,
            "BriefFacts": "Vijay Mallya Jr was investigated for routing black money through multiple shell companies in Vijayawada to buy premium real estate assets."
        },
    ])
    results.append(res)
    case_rid = rowids(case_rows)

    if not case_rid:
        print("\nABORTING: CaseMaster insertion failed. Cannot proceed with child tables.")
        return {"status": "partial", "error": "CaseMaster insertion failed", "results": results}

    # ─────────────────────────────────────────────────────────────────
    # 21. Accused (FK → CaseMaster) -> 24 rows (4x original 6)
    # ─────────────────────────────────────────────────────────────────
    res, accused_rows = insert(ds, "Accused", [
        # Case 1 (murder)
        {"CaseMasterID": case_rid[0], "AccusedName": "Abdul Rauf Khan",              "AgeYear": 31, "GenderID": 1, "PersonID": "A1"},
        {"CaseMasterID": case_rid[0], "AccusedName": "Syed Imran",                   "AgeYear": 27, "GenderID": 1, "PersonID": "A2"},
        # Case 2 (chain snatching)
        {"CaseMasterID": case_rid[1], "AccusedName": "Abdul Rauf Khan",              "AgeYear": 31, "GenderID": 1, "PersonID": "A1"},
        # Case 3 (vehicle theft)
        {"CaseMasterID": case_rid[2], "AccusedName": "Venkatesh Prasad",             "AgeYear": 24, "GenderID": 1, "PersonID": "A1"},
        {"CaseMasterID": case_rid[2], "AccusedName": "Ravi Kumar B",                 "AgeYear": 22, "GenderID": 1, "PersonID": "A2"},
        # Case 4 (cyber fraud)
        {"CaseMasterID": case_rid[3], "AccusedName": "Unknown — Under Investigation","AgeYear": None,"GenderID": None,"PersonID": "A1"},
        # Case 5 (kidnapping)
        {"CaseMasterID": case_rid[4], "AccusedName": "Vikram Gowda",                 "AgeYear": 35, "GenderID": 1, "PersonID": "A1"},
        # Case 6 (grievous hurt)
        {"CaseMasterID": case_rid[5], "AccusedName": "Raju Naik",                    "AgeYear": 29, "GenderID": 1, "PersonID": "A1"},
        # Case 7 (dacoity)
        {"CaseMasterID": case_rid[6], "AccusedName": "Someshwara Rao",               "AgeYear": 41, "GenderID": 1, "PersonID": "A1"},
        {"CaseMasterID": case_rid[6], "AccusedName": "Kishore Kumar",                "AgeYear": 30, "GenderID": 1, "PersonID": "A2"},
        {"CaseMasterID": case_rid[6], "AccusedName": "Dinesh Naik",                  "AgeYear": 28, "GenderID": 1, "PersonID": "A3"},
        {"CaseMasterID": case_rid[6], "AccusedName": "Mohan Lal",                    "AgeYear": 33, "GenderID": 1, "PersonID": "A4"},
        # Case 8 (DV)
        {"CaseMasterID": case_rid[7], "AccusedName": "Harish Prasad",                "AgeYear": 32, "GenderID": 1, "PersonID": "A1"},
        # Case 9 (POCSO)
        {"CaseMasterID": case_rid[8], "AccusedName": "Vikas M",                      "AgeYear": 45, "GenderID": 1, "PersonID": "A1"},
        # Case 10 (drugs)
        {"CaseMasterID": case_rid[9], "AccusedName": "Peter D'Souza",                "AgeYear": 26, "GenderID": 1, "PersonID": "A1"},
        # Case 11 (rioting)
        {"CaseMasterID": case_rid[10], "AccusedName": "Rakesh K",                    "AgeYear": 23, "GenderID": 1, "PersonID": "A1"},
        {"CaseMasterID": case_rid[10], "AccusedName": "Santosh G",                   "AgeYear": 25, "GenderID": 1, "PersonID": "A2"},
        {"CaseMasterID": case_rid[10], "AccusedName": "Manju N",                     "AgeYear": 22, "GenderID": 1, "PersonID": "A3"},
        # Case 12 (traffic)
        {"CaseMasterID": case_rid[11], "AccusedName": "Rajeev Hegde",                "AgeYear": 38, "GenderID": 1, "PersonID": "A1"},
        # Case 13 (hacking)
        {"CaseMasterID": case_rid[12], "AccusedName": "Karan Johar",                 "AgeYear": 24, "GenderID": 1, "PersonID": "A1"},
        # Case 14 (UDR)
        {"CaseMasterID": case_rid[13], "AccusedName": "Unknown",                     "AgeYear": None,"GenderID": None,"PersonID": "A1"},
        # Case 15 (zero FIR)
        {"CaseMasterID": case_rid[14], "AccusedName": "Shankar Lal",                 "AgeYear": 29, "GenderID": 1, "PersonID": "A1"},
        # Case 16 (PMLA)
        {"CaseMasterID": case_rid[15], "AccusedName": "Vijay Mallya Jr",             "AgeYear": 48, "GenderID": 1, "PersonID": "A1"},
    ])
    results.append(res)
    acc_rid = rowids(accused_rows)

    # ─────────────────────────────────────────────────────────────────
    # 22. Victim (FK → CaseMaster) -> 16 rows (4x original 4)
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "Victim", [
        {"CaseMasterID": case_rid[0], "VictimName": "Prakash Naidu", "AgeYear": 45, "GenderID": 1, "VictimPolice": False},
        {"CaseMasterID": case_rid[1], "VictimName": "Lakshmi Devi",  "AgeYear": 62, "GenderID": 2, "VictimPolice": False},
        {"CaseMasterID": case_rid[2], "VictimName": "Ramesh Gowda",  "AgeYear": 38, "GenderID": 1, "VictimPolice": False},
        {"CaseMasterID": case_rid[3], "VictimName": "Anil Mehta",    "AgeYear": 52, "GenderID": 1, "VictimPolice": False},
        {"CaseMasterID": case_rid[4], "VictimName": "Master Rahul",  "AgeYear": 10, "GenderID": 1, "VictimPolice": False},
        {"CaseMasterID": case_rid[5], "VictimName": "Girish K",      "AgeYear": 34, "GenderID": 1, "VictimPolice": False},
        {"CaseMasterID": case_rid[6], "VictimName": "Swaminathan",   "AgeYear": 55, "GenderID": 1, "VictimPolice": False},
        {"CaseMasterID": case_rid[7], "VictimName": "Shalini Prasad","AgeYear": 28, "GenderID": 2, "VictimPolice": False},
        {"CaseMasterID": case_rid[8], "VictimName": "Aishwarya",     "AgeYear": 14, "GenderID": 2, "VictimPolice": False},
        {"CaseMasterID": case_rid[9], "VictimName": "Public Interest","AgeYear": None, "GenderID": None, "VictimPolice": False},
        {"CaseMasterID": case_rid[10], "VictimName": "Priya Sharma", "AgeYear": 35, "GenderID": 2, "VictimPolice": True},
        {"CaseMasterID": case_rid[11], "VictimName": "Karthik",      "AgeYear": 22, "GenderID": 1, "VictimPolice": False},
        {"CaseMasterID": case_rid[12], "VictimName": "ABC Corp",     "AgeYear": None, "GenderID": None, "VictimPolice": False},
        {"CaseMasterID": case_rid[13], "VictimName": "Somappa",      "AgeYear": 55, "GenderID": 1, "VictimPolice": False},
        {"CaseMasterID": case_rid[14], "VictimName": "Girija Bai",   "AgeYear": 45, "GenderID": 2, "VictimPolice": False},
        {"CaseMasterID": case_rid[15], "VictimName": "National Bank","AgeYear": None, "GenderID": None, "VictimPolice": False},
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # 23. ComplainantDetails (FK → CaseMaster, OccupationMaster, ReligionMaster, CasteMaster) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "ComplainantDetails", [
        {"CaseMasterID": case_rid[0], "ComplainantName": "Suresh Nair",    "AgeYear": 40, "OccupationID": occ_rid[1], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
        {"CaseMasterID": case_rid[1], "ComplainantName": "Lakshmi Devi",   "AgeYear": 62, "OccupationID": occ_rid[3], "ReligionID": rel_rid[0], "CasteID": caste_rid[1], "GenderID": 2},
        {"CaseMasterID": case_rid[2], "ComplainantName": "Ramesh Gowda",   "AgeYear": 38, "OccupationID": occ_rid[2], "ReligionID": rel_rid[0], "CasteID": caste_rid[1], "GenderID": 1},
        {"CaseMasterID": case_rid[3], "ComplainantName": "Anil Mehta",     "AgeYear": 52, "OccupationID": occ_rid[1], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
        {"CaseMasterID": case_rid[4], "ComplainantName": "Vikram Gowda",   "AgeYear": 42, "OccupationID": occ_rid[0], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
        {"CaseMasterID": case_rid[5], "ComplainantName": "Girish K",       "AgeYear": 34, "OccupationID": occ_rid[5], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
        {"CaseMasterID": case_rid[6], "ComplainantName": "Swaminathan",    "AgeYear": 55, "OccupationID": occ_rid[1], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
        {"CaseMasterID": case_rid[7], "ComplainantName": "Shalini Prasad", "AgeYear": 28, "OccupationID": occ_rid[8], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 2},
        {"CaseMasterID": case_rid[8], "ComplainantName": "Mother of Child","AgeYear": 38, "OccupationID": occ_rid[10], "ReligionID": rel_rid[0], "CasteID": caste_rid[1], "GenderID": 2},
        {"CaseMasterID": case_rid[9], "ComplainantName": "Abdul Hameed",   "AgeYear": 43, "OccupationID": occ_rid[13], "ReligionID": rel_rid[1], "CasteID": caste_rid[1], "GenderID": 1},
        {"CaseMasterID": case_rid[10], "ComplainantName": "Prasad Rao",     "AgeYear": 45, "OccupationID": occ_rid[13], "ReligionID": rel_rid[0], "CasteID": caste_rid[2], "GenderID": 1},
        {"CaseMasterID": case_rid[11], "ComplainantName": "Karthik",       "AgeYear": 22, "OccupationID": occ_rid[4], "ReligionID": rel_rid[0], "CasteID": caste_rid[1], "GenderID": 1},
        {"CaseMasterID": case_rid[12], "ComplainantName": "Security Head",  "AgeYear": 35, "OccupationID": occ_rid[5], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
        {"CaseMasterID": case_rid[13], "ComplainantName": "Somappa",       "AgeYear": 55, "OccupationID": occ_rid[0], "ReligionID": rel_rid[0], "CasteID": caste_rid[3], "GenderID": 1},
        {"CaseMasterID": case_rid[14], "ComplainantName": "Girija Bai",    "AgeYear": 45, "OccupationID": occ_rid[3], "ReligionID": rel_rid[0], "CasteID": caste_rid[2], "GenderID": 2},
        {"CaseMasterID": case_rid[15], "ComplainantName": "Bank Auditor",   "AgeYear": 50, "OccupationID": occ_rid[1], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # 24. ActSectionAssociation (FK → CaseMaster, Act, Section) -> 32 rows (4x original 8)
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "ActSectionAssociation", [
        # Case 1: IPC 302
        {"CaseMasterID": case_rid[0],  "ActID": act_rid[0], "SectionID": sec_rid[0], "ActOrderID": 1, "SectionOrderID": 1},
        # Case 2: IPC 392 + IPC 379
        {"CaseMasterID": case_rid[1],  "ActID": act_rid[0], "SectionID": sec_rid[3], "ActOrderID": 1, "SectionOrderID": 1},
        {"CaseMasterID": case_rid[1],  "ActID": act_rid[0], "SectionID": sec_rid[2], "ActOrderID": 1, "SectionOrderID": 2},
        # Case 3: IPC 379 + IPC 411
        {"CaseMasterID": case_rid[2],  "ActID": act_rid[0], "SectionID": sec_rid[2], "ActOrderID": 1, "SectionOrderID": 1},
        {"CaseMasterID": case_rid[2],  "ActID": act_rid[0], "SectionID": sec_rid[4], "ActOrderID": 1, "SectionOrderID": 2},
        # Case 4: IT 66C + IT 66D + IPC 420
        {"CaseMasterID": case_rid[3],  "ActID": act_rid[2], "SectionID": sec_rid[6], "ActOrderID": 1, "SectionOrderID": 1},
        {"CaseMasterID": case_rid[3],  "ActID": act_rid[2], "SectionID": sec_rid[7], "ActOrderID": 1, "SectionOrderID": 2},
        {"CaseMasterID": case_rid[3],  "ActID": act_rid[0], "SectionID": sec_rid[5], "ActOrderID": 2, "SectionOrderID": 1},
        # Case 5: IPC 363
        {"CaseMasterID": case_rid[4],  "ActID": act_rid[0], "SectionID": sec_rid[8], "ActOrderID": 1, "SectionOrderID": 1},
        # Case 6: IPC 326
        {"CaseMasterID": case_rid[5],  "ActID": act_rid[0], "SectionID": sec_rid[9], "ActOrderID": 1, "SectionOrderID": 1},
        # Case 7: IPC 395
        {"CaseMasterID": case_rid[6],  "ActID": act_rid[0], "SectionID": sec_rid[12], "ActOrderID": 1, "SectionOrderID": 1},
        # Case 8: IPC 498A + DPA 3
        {"CaseMasterID": case_rid[7],  "ActID": act_rid[0], "SectionID": sec_rid[13], "ActOrderID": 1, "SectionOrderID": 1},
        {"CaseMasterID": case_rid[7],  "ActID": act_rid[11], "SectionID": sec_rid[30], "ActOrderID": 2, "SectionOrderID": 1},
        # Case 9: POCSO 4
        {"CaseMasterID": case_rid[8],  "ActID": act_rid[3], "SectionID": sec_rid[19], "ActOrderID": 1, "SectionOrderID": 1},
        # Case 10: NDPS 20 + NDPS 22
        {"CaseMasterID": case_rid[9],  "ActID": act_rid[1], "SectionID": sec_rid[15], "ActOrderID": 1, "SectionOrderID": 1},
        {"CaseMasterID": case_rid[9],  "ActID": act_rid[1], "SectionID": sec_rid[16], "ActOrderID": 1, "SectionOrderID": 2},
        # Case 11: IPC 326 + IPC 392
        {"CaseMasterID": case_rid[10], "ActID": act_rid[0], "SectionID": sec_rid[9], "ActOrderID": 1, "SectionOrderID": 1},
        {"CaseMasterID": case_rid[10], "ActID": act_rid[0], "SectionID": sec_rid[3], "ActOrderID": 1, "SectionOrderID": 2},
        # Case 12: MVA 185 + MVA 184
        {"CaseMasterID": case_rid[11], "ActID": act_rid[6], "SectionID": sec_rid[24], "ActOrderID": 1, "SectionOrderID": 1},
        {"CaseMasterID": case_rid[11], "ActID": act_rid[6], "SectionID": sec_rid[25], "ActOrderID": 1, "SectionOrderID": 2},
        # Case 13: IT 66 + IT 66D
        {"CaseMasterID": case_rid[12], "ActID": act_rid[2], "SectionID": sec_rid[17], "ActOrderID": 1, "SectionOrderID": 1},
        {"CaseMasterID": case_rid[12], "ActID": act_rid[2], "SectionID": sec_rid[7], "ActOrderID": 1, "SectionOrderID": 2},
        # Case 14: IPC 302
        {"CaseMasterID": case_rid[13], "ActID": act_rid[0], "SectionID": sec_rid[0], "ActOrderID": 1, "SectionOrderID": 1},
        # Case 15: IPC 392 + IPC 379
        {"CaseMasterID": case_rid[14], "ActID": act_rid[0], "SectionID": sec_rid[3], "ActOrderID": 1, "SectionOrderID": 1},
        {"CaseMasterID": case_rid[14], "ActID": act_rid[0], "SectionID": sec_rid[2], "ActOrderID": 1, "SectionOrderID": 2},
        # Case 16: PMLA 3
        {"CaseMasterID": case_rid[15], "ActID": act_rid[9], "SectionID": sec_rid[29], "ActOrderID": 1, "SectionOrderID": 1},
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # 25. ArrestSurrender (FK → CaseMaster, State, District, Unit, Employee, Court, Accused) -> 12 rows
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "ArrestSurrender", [
        # Original 3 Arrests
        {"CaseMasterID": case_rid[0], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-03-18", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[0], "PoliceStationID": unit_rid[0], "IOID": emp_rid[1], "CourtID": court_rid[0], "AccusedMasterID": acc_rid[0], "IsAccused": True, "IsComplainantAccused": False},
        {"CaseMasterID": case_rid[0], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-03-18", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[0], "PoliceStationID": unit_rid[0], "IOID": emp_rid[1], "CourtID": court_rid[0], "AccusedMasterID": acc_rid[1], "IsAccused": True, "IsComplainantAccused": False},
        {"CaseMasterID": case_rid[2], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-06-01", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[1], "PoliceStationID": unit_rid[2], "IOID": emp_rid[3], "CourtID": court_rid[1], "AccusedMasterID": acc_rid[4], "IsAccused": True, "IsComplainantAccused": False},
        # Added 9 Arrests
        {"CaseMasterID": case_rid[4], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-07-05", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[0], "PoliceStationID": unit_rid[1], "IOID": emp_rid[6], "CourtID": court_rid[0], "AccusedMasterID": acc_rid[6], "IsAccused": True, "IsComplainantAccused": False},
        {"CaseMasterID": case_rid[5], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-07-20", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[0], "PoliceStationID": unit_rid[1], "IOID": emp_rid[6], "CourtID": court_rid[0], "AccusedMasterID": acc_rid[7], "IsAccused": True, "IsComplainantAccused": False},
        {"CaseMasterID": case_rid[6], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-08-05", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[4], "PoliceStationID": unit_rid[6], "IOID": emp_rid[7], "CourtID": court_rid[5], "AccusedMasterID": acc_rid[8], "IsAccused": True, "IsComplainantAccused": False},
        {"CaseMasterID": case_rid[6], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-08-05", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[4], "PoliceStationID": unit_rid[6], "IOID": emp_rid[7], "CourtID": court_rid[5], "AccusedMasterID": acc_rid[9], "IsAccused": True, "IsComplainantAccused": False},
        {"CaseMasterID": case_rid[7], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-08-15", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[4], "PoliceStationID": unit_rid[6], "IOID": emp_rid[8], "CourtID": court_rid[5], "AccusedMasterID": acc_rid[12], "IsAccused": True, "IsComplainantAccused": False},
        {"CaseMasterID": case_rid[8], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-08-25", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[5], "PoliceStationID": unit_rid[7], "IOID": emp_rid[9], "CourtID": court_rid[6], "AccusedMasterID": acc_rid[13], "IsAccused": True, "IsComplainantAccused": False},
        {"CaseMasterID": case_rid[9], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-09-05", "ArrestSurrenderStateId": state_rid[1], "ArrestSurrenderDistrictId": dist_rid[7], "PoliceStationID": unit_rid[8], "IOID": emp_rid[10], "CourtID": court_rid[8], "AccusedMasterID": acc_rid[14], "IsAccused": True, "IsComplainantAccused": False},
        {"CaseMasterID": case_rid[10], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-09-20", "ArrestSurrenderStateId": state_rid[1], "ArrestSurrenderDistrictId": dist_rid[7], "PoliceStationID": unit_rid[8], "IOID": emp_rid[11], "CourtID": court_rid[8], "AccusedMasterID": acc_rid[15], "IsAccused": True, "IsComplainantAccused": False},
        {"CaseMasterID": case_rid[11], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-09-28", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[0], "PoliceStationID": unit_rid[0], "IOID": emp_rid[0], "CourtID": court_rid[0], "AccusedMasterID": acc_rid[18], "IsAccused": True, "IsComplainantAccused": False},
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # 26. ChargesheetDetails (FK → CaseMaster, Employee) -> 4 rows (4x original 1)
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "ChargesheetDetails", [
        # Original 1 Chargesheet
        {"CaseMasterID": case_rid[2], "csdate": "2024-07-15 10:00:00", "cstype": "A", "PolicePersonID": emp_rid[2]},
        # Added 3 Chargesheets
        {"CaseMasterID": case_rid[4], "csdate": "2024-08-10 11:00:00", "cstype": "A", "PolicePersonID": emp_rid[6]},
        {"CaseMasterID": case_rid[9], "csdate": "2024-09-15 14:00:00", "cstype": "A", "PolicePersonID": emp_rid[10]},
        {"CaseMasterID": case_rid[11], "csdate": "2024-10-20 10:00:00", "cstype": "A", "PolicePersonID": emp_rid[0]},
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