"""
PRISM — Seed Data Insertion (ROWID-aware, 4x Scale, Explicit IDs)
================================================================
Catalyst DataStore FK columns require the internal ROWID of the referenced row,
NOT the custom ID value you supply. This script:
  1. Inserts each parent table first
  2. Reads back the assigned ROWIDs from the response
  3. Uses those ROWIDs in all child FK columns
  4. Scale: 4 times the original dataset (16 Cases, 24 Accused, etc.)
  5. Explicit IDs: Populates unique primary key columns (StateID, DistrictID, etc.) starting from 1.
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

    print("\n========== PRISM SEED DATA INSERTION (4X SCALE, EXPLICIT IDs) ==========\n")

    # ─────────────────────────────────────────────────────────────────
    # 1. State (no FK) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, state_rows = insert(ds, "State", [
        {"StateID": 1,  "StateName": "Karnataka",      "NationalityID": 1, "Active": True},
        {"StateID": 2,  "StateName": "Tamil Nadu",     "NationalityID": 1, "Active": True},
        {"StateID": 3,  "StateName": "Andhra Pradesh", "NationalityID": 1, "Active": True},
        {"StateID": 4,  "StateName": "Maharashtra",    "NationalityID": 1, "Active": True},
        {"StateID": 5,  "StateName": "Kerala",         "NationalityID": 1, "Active": True},
        {"StateID": 6,  "StateName": "Telangana",      "NationalityID": 1, "Active": True},
        {"StateID": 7,  "StateName": "Goa",            "NationalityID": 1, "Active": True},
        {"StateID": 8,  "StateName": "Gujarat",        "NationalityID": 1, "Active": True},
        {"StateID": 9,  "StateName": "Rajasthan",      "NationalityID": 1, "Active": True},
        {"StateID": 10, "StateName": "Madhya Pradesh", "NationalityID": 1, "Active": True},
        {"StateID": 11, "StateName": "Uttar Pradesh",  "NationalityID": 1, "Active": True},
        {"StateID": 12, "StateName": "Bihar",          "NationalityID": 1, "Active": True},
        {"StateID": 13, "StateName": "West Bengal",    "NationalityID": 1, "Active": True},
        {"StateID": 14, "StateName": "Odisha",         "NationalityID": 1, "Active": True},
        {"StateID": 15, "StateName": "Punjab",         "NationalityID": 1, "Active": True},
        {"StateID": 16, "StateName": "Haryana",        "NationalityID": 1, "Active": True},
    ])
    results.append(res)
    state_rid = rowids(state_rows)

    # ─────────────────────────────────────────────────────────────────
    # 2. District (FK → State) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, district_rows = insert(ds, "District", [
        {"DistrictID": 1,  "DistrictName": "Bengaluru Urban",  "StateID": state_rid[0],  "Active": True},
        {"DistrictID": 2,  "DistrictName": "Mysuru",           "StateID": state_rid[0],  "Active": True},
        {"DistrictID": 3,  "DistrictName": "Dakshina Kannada", "StateID": state_rid[0],  "Active": True},
        {"DistrictID": 4,  "DistrictName": "Belagavi",         "StateID": state_rid[0],  "Active": True},
        {"DistrictID": 5,  "DistrictName": "Dharwad",          "StateID": state_rid[0],  "Active": True},
        {"DistrictID": 6,  "DistrictName": "Udupi",            "StateID": state_rid[0],  "Active": True},
        {"DistrictID": 7,  "DistrictName": "Kalaburagi",       "StateID": state_rid[0],  "Active": True},
        {"DistrictID": 8,  "DistrictName": "Chennai",          "StateID": state_rid[1],  "Active": True},
        {"DistrictID": 9,  "DistrictName": "Madurai",          "StateID": state_rid[1],  "Active": True},
        {"DistrictID": 10, "DistrictName": "Coimbatore",       "StateID": state_rid[1],  "Active": True},
        {"DistrictID": 11, "DistrictName": "Vijayawada",       "StateID": state_rid[2],  "Active": True},
        {"DistrictID": 12, "DistrictName": "Visakhapatnam",    "StateID": state_rid[2],  "Active": True},
        {"DistrictID": 13, "DistrictName": "Mumbai City",      "StateID": state_rid[3],  "Active": True},
        {"DistrictID": 14, "DistrictName": "Pune",             "StateID": state_rid[3],  "Active": True},
        {"DistrictID": 15, "DistrictName": "Nagpur",           "StateID": state_rid[3],  "Active": True},
        {"DistrictID": 16, "DistrictName": "North Goa",        "StateID": state_rid[6],  "Active": True},
    ])
    results.append(res)
    dist_rid = rowids(district_rows)

    # ─────────────────────────────────────────────────────────────────
    # 3. UnitType (no FK) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, unittype_rows = insert(ds, "UnitType", [
        {"UnitTypeID": 1,  "UnitTypeName": "Police Station",         "CityDistState": "City",     "Hierarchy": 3, "Active": True},
        {"UnitTypeID": 2,  "UnitTypeName": "Circle Office",          "CityDistState": "District", "Hierarchy": 2, "Active": True},
        {"UnitTypeID": 3,  "UnitTypeName": "District Armed Reserve", "CityDistState": "District", "Hierarchy": 2, "Active": True},
        {"UnitTypeID": 4,  "UnitTypeName": "District HQ",            "CityDistState": "District", "Hierarchy": 1, "Active": True},
        {"UnitTypeID": 5,  "UnitTypeName": "Traffic Police Station", "CityDistState": "City",     "Hierarchy": 3, "Active": True},
        {"UnitTypeID": 6,  "UnitTypeName": "Cyber Crime PS",         "CityDistState": "City",     "Hierarchy": 3, "Active": True},
        {"UnitTypeID": 7,  "UnitTypeName": "CID",                    "CityDistState": "State",    "Hierarchy": 1, "Active": True},
        {"UnitTypeID": 8,  "UnitTypeName": "Crime Branch",           "CityDistState": "District", "Hierarchy": 2, "Active": True},
        {"UnitTypeID": 9,  "UnitTypeName": "Anti-Narcotics Cell",    "CityDistState": "State",    "Hierarchy": 2, "Active": True},
        {"UnitTypeID": 10, "UnitTypeName": "Railway Police Station", "CityDistState": "City",     "Hierarchy": 3, "Active": True},
        {"UnitTypeID": 11, "UnitTypeName": "Women Police Station",   "CityDistState": "City",     "Hierarchy": 3, "Active": True},
        {"UnitTypeID": 12, "UnitTypeName": "Special Branch",         "CityDistState": "District", "Hierarchy": 2, "Active": True},
        {"UnitTypeID": 13, "UnitTypeName": "Intelligence Wing",      "CityDistState": "State",    "Hierarchy": 1, "Active": True},
        {"UnitTypeID": 14, "UnitTypeName": "KSRP Battalion",         "CityDistState": "State",    "Hierarchy": 2, "Active": True},
        {"UnitTypeID": 15, "UnitTypeName": "Training School",        "CityDistState": "State",    "Hierarchy": 2, "Active": True},
        {"UnitTypeID": 16, "UnitTypeName": "Dog Squad Unit",         "CityDistState": "District", "Hierarchy": 3, "Active": True},
    ])
    results.append(res)
    ut_rid = rowids(unittype_rows)

    # ─────────────────────────────────────────────────────────────────
    # 4. Unit (FK → UnitType, State, District) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, unit_rows = insert(ds, "Unit", [
        {"UnitID": 1,  "UnitName": "Cubbon Park Police Station",      "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0], "Active": True},
        {"UnitID": 2,  "UnitName": "Koramangala Police Station",      "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0], "Active": True},
        {"UnitID": 3,  "UnitName": "Mysuru City Police Station",      "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[1], "Active": True},
        {"UnitID": 4,  "UnitName": "Mangaluru Central Police Station", "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[2], "Active": True},
        {"UnitID": 5,  "UnitName": "Jayanagar Police Station",        "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0], "Active": True},
        {"UnitID": 6,  "UnitName": "Indiranagar Police Station",      "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0], "Active": True},
        {"UnitID": 7,  "UnitName": "Dharwad Town Police Station",      "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[4], "Active": True},
        {"UnitID": 8,  "UnitName": "Udupi Town Police Station",        "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[5], "Active": True},
        {"UnitID": 9,  "UnitName": "Chennai Central Police Station",  "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[1], "DistrictID": dist_rid[7], "Active": True},
        {"UnitID": 10, "UnitName": "Coimbatore Town Police Station",   "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[1], "DistrictID": dist_rid[9], "Active": True},
        {"UnitID": 11, "UnitName": "Vijayawada Town Police Station",   "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[2], "DistrictID": dist_rid[10], "Active": True},
        {"UnitID": 12, "UnitName": "Mumbai Central Police Station",    "TypeID": ut_rid[0], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[3], "DistrictID": dist_rid[12], "Active": True},
        {"UnitID": 13, "UnitName": "Bengaluru Cyber Crime PS",        "TypeID": ut_rid[5], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0], "Active": True},
        {"UnitID": 14, "UnitName": "Bengaluru Circle Office",         "TypeID": ut_rid[1], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[0], "Active": True},
        {"UnitID": 15, "UnitName": "Mysuru Circle Office",            "TypeID": ut_rid[1], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[1], "Active": True},
        {"UnitID": 16, "UnitName": "Mangaluru DAR Unit",              "TypeID": ut_rid[2], "ParentUnit": None, "NationalityID": 1, "StateID": state_rid[0], "DistrictID": dist_rid[2], "Active": True},
    ])
    results.append(res)
    unit_rid = rowids(unit_rows)

    # ─────────────────────────────────────────────────────────────────
    # 5. Court (FK → District, State) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, court_rows = insert(ds, "Court", [
        {"CourtID": 1,  "CourtName": "City Civil Court Bengaluru",     "DistrictID": dist_rid[0],  "StateID": state_rid[0], "Active": True},
        {"CourtID": 2,  "CourtName": "Mysuru District Sessions Court", "DistrictID": dist_rid[1],  "StateID": state_rid[0], "Active": True},
        {"CourtID": 3,  "CourtName": "DK District Court Mangaluru",    "DistrictID": dist_rid[2],  "StateID": state_rid[0], "Active": True},
        {"CourtID": 4,  "CourtName": "Belagavi Sessions Court",        "DistrictID": dist_rid[3],  "StateID": state_rid[0], "Active": True},
        {"CourtID": 5,  "CourtName": "High Court of Karnataka",        "DistrictID": dist_rid[0],  "StateID": state_rid[0], "Active": True},
        {"CourtID": 6,  "CourtName": "Dharwad District Court",         "DistrictID": dist_rid[4],  "StateID": state_rid[0], "Active": True},
        {"CourtID": 7,  "CourtName": "Udupi District Court",           "DistrictID": dist_rid[5],  "StateID": state_rid[0], "Active": True},
        {"CourtID": 8,  "CourtName": "Kalaburagi Sessions Court",       "DistrictID": dist_rid[6],  "StateID": state_rid[0], "Active": True},
        {"CourtID": 9,  "CourtName": "Chennai High Court",             "DistrictID": dist_rid[7],  "StateID": state_rid[1], "Active": True},
        {"CourtID": 10, "CourtName": "Madurai Sessions Court",         "DistrictID": dist_rid[8],  "StateID": state_rid[1], "Active": True},
        {"CourtID": 11, "CourtName": "Coimbatore District Court",      "DistrictID": dist_rid[9],  "StateID": state_rid[1], "Active": True},
        {"CourtID": 12, "CourtName": "Vijayawada Sessions Court",      "DistrictID": dist_rid[10], "StateID": state_rid[2], "Active": True},
        {"CourtID": 13, "CourtName": "Visakhapatnam District Court",   "DistrictID": dist_rid[11], "StateID": state_rid[2], "Active": True},
        {"CourtID": 14, "CourtName": "Mumbai High Court",              "DistrictID": dist_rid[12], "StateID": state_rid[3], "Active": True},
        {"CourtID": 15, "CourtName": "Pune Sessions Court",             "DistrictID": dist_rid[13], "StateID": state_rid[3], "Active": True},
        {"CourtID": 16, "CourtName": "Nagpur Sessions Court",           "DistrictID": dist_rid[14], "StateID": state_rid[3], "Active": True},
    ])
    results.append(res)
    court_rid = rowids(court_rows)

    # ─────────────────────────────────────────────────────────────────
    # 6. Rank (no FK) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, rank_rows = insert(ds, "Rank", [
        {"RankID": 1,  "RankName": "Constable",                      "Hierarchy": 5, "Active": True},
        {"RankID": 2,  "RankName": "Head Constable",                 "Hierarchy": 4, "Active": True},
        {"RankID": 3,  "RankName": "Sub Inspector",                  "Hierarchy": 3, "Active": True},
        {"RankID": 4,  "RankName": "Inspector",                      "Hierarchy": 2, "Active": True},
        {"RankID": 5,  "RankName": "Assistant Sub Inspector",        "Hierarchy": 3, "Active": True},
        {"RankID": 6,  "RankName": "Deputy Superintendent",          "Hierarchy": 2, "Active": True},
        {"RankID": 7,  "RankName": "Superintendent of Police",       "Hierarchy": 1, "Active": True},
        {"RankID": 8,  "RankName": "Deputy Inspector General",       "Hierarchy": 1, "Active": True},
        {"RankID": 9,  "RankName": "Inspector General of Police",    "Hierarchy": 1, "Active": True},
        {"RankID": 10, "RankName": "Additional Director General",    "Hierarchy": 1, "Active": True},
        {"RankID": 11, "RankName": "Director General of Police",     "Hierarchy": 1, "Active": True},
        {"RankID": 12, "RankName": "Senior Constable",               "Hierarchy": 4, "Active": True},
        {"RankID": 13, "RankName": "Head Constable Grade II",        "Hierarchy": 4, "Active": True},
        {"RankID": 14, "RankName": "Assistant Inspector",            "Hierarchy": 3, "Active": True},
        {"RankID": 15, "RankName": "Sub-Divisional Officer",         "Hierarchy": 2, "Active": True},
        {"RankID": 16, "RankName": "Circle Inspector",               "Hierarchy": 2, "Active": True},
    ])
    results.append(res)
    rank_rid = rowids(rank_rows)

    # ─────────────────────────────────────────────────────────────────
    # 7. Designation (no FK) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, desig_rows = insert(ds, "Designation", [
        {"DesignationID": 1,  "DesignationName": "Station House Officer",       "Active": True, "SortOrder": 1},
        {"DesignationID": 2,  "DesignationName": "Investigating Officer",       "Active": True, "SortOrder": 2},
        {"DesignationID": 3,  "DesignationName": "Station Writer",              "Active": True, "SortOrder": 3},
        {"DesignationID": 4,  "DesignationName": "Beat Officer",                "Active": True, "SortOrder": 4},
        {"DesignationID": 5,  "DesignationName": "Assistant Investigating Officer", "Active": True, "SortOrder": 5},
        {"DesignationID": 6,  "DesignationName": "Duty Officer",                "Active": True, "SortOrder": 6},
        {"DesignationID": 7,  "DesignationName": "Law and Order Officer",       "Active": True, "SortOrder": 7},
        {"DesignationID": 8,  "DesignationName": "Crime Branch Chief",          "Active": True, "SortOrder": 8},
        {"DesignationID": 9,  "DesignationName": "Reader to SP",                "Active": True, "SortOrder": 9},
        {"DesignationID": 10, "DesignationName": "Public Relations Officer",    "Active": True, "SortOrder": 10},
        {"DesignationID": 11, "DesignationName": "Wireless Operator",           "Active": True, "SortOrder": 11},
        {"DesignationID": 12, "DesignationName": "Cyber Analyst",               "Active": True, "SortOrder": 12},
        {"DesignationID": 13, "DesignationName": "Forensic Expert",             "Active": True, "SortOrder": 13},
        {"DesignationID": 14, "DesignationName": "Dog Squad In-charge",         "Active": True, "SortOrder": 14},
        {"DesignationID": 15, "DesignationName": "Armourer",                    "Active": True, "SortOrder": 15},
        {"DesignationID": 16, "DesignationName": "Guard Commander",             "Active": True, "SortOrder": 16},
    ])
    results.append(res)
    desig_rid = rowids(desig_rows)

    # ─────────────────────────────────────────────────────────────────
    # 8. Employee (FK → District, Unit, Rank, Designation) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, emp_rows = insert(ds, "Employee", [
        {"EmployeeID": 1,  "KGID": "KG2001101", "FirstName": "Rajesh Kumar",       "EmployeeDOB": "1985-03-15", "GenderID": 1, "BloodGroupID": 2, "PhysicallyChallenged": False, "AppointmentDate": "2008-06-01", "DistrictID": dist_rid[0],  "UnitID": unit_rid[0],  "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"EmployeeID": 2,  "KGID": "KG2001102", "FirstName": "Priya Sharma",        "EmployeeDOB": "1990-07-22", "GenderID": 2, "BloodGroupID": 1, "PhysicallyChallenged": False, "AppointmentDate": "2013-09-15", "DistrictID": dist_rid[0],  "UnitID": unit_rid[0],  "RankID": rank_rid[2], "DesignationID": desig_rid[1]},
        {"EmployeeID": 3,  "KGID": "KG2001103", "FirstName": "Mohammed Farooq",     "EmployeeDOB": "1982-11-08", "GenderID": 1, "BloodGroupID": 3, "PhysicallyChallenged": False, "AppointmentDate": "2005-03-20", "DistrictID": dist_rid[1],  "UnitID": unit_rid[2],  "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"EmployeeID": 4,  "KGID": "KG2001104", "FirstName": "Anitha Reddy",        "EmployeeDOB": "1993-05-30", "GenderID": 2, "BloodGroupID": 4, "PhysicallyChallenged": False, "AppointmentDate": "2016-11-01", "DistrictID": dist_rid[1],  "UnitID": unit_rid[2],  "RankID": rank_rid[2], "DesignationID": desig_rid[1]},
        {"EmployeeID": 5,  "KGID": "KG2001105", "FirstName": "Suresh Patil",        "EmployeeDOB": "1988-12-05", "GenderID": 1, "BloodGroupID": 2, "PhysicallyChallenged": False, "AppointmentDate": "2011-04-10", "DistrictID": dist_rid[0],  "UnitID": unit_rid[0],  "RankID": rank_rid[0], "DesignationID": desig_rid[3]},
        {"EmployeeID": 6,  "KGID": "KG2001106", "FirstName": "Vikram Singh",        "EmployeeDOB": "1984-01-20", "GenderID": 1, "BloodGroupID": 3, "PhysicallyChallenged": False, "AppointmentDate": "2006-08-15", "DistrictID": dist_rid[0],  "UnitID": unit_rid[1],  "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"EmployeeID": 7,  "KGID": "KG2001107", "FirstName": "Deepa N",             "EmployeeDOB": "1991-09-18", "GenderID": 2, "BloodGroupID": 1, "PhysicallyChallenged": False, "AppointmentDate": "2014-05-12", "DistrictID": dist_rid[0],  "UnitID": unit_rid[1],  "RankID": rank_rid[2], "DesignationID": desig_rid[1]},
        {"EmployeeID": 8,  "KGID": "KG2001108", "FirstName": "Ramesh Chandra",      "EmployeeDOB": "1980-05-25", "GenderID": 1, "BloodGroupID": 2, "PhysicallyChallenged": False, "AppointmentDate": "2002-12-01", "DistrictID": dist_rid[4],  "UnitID": unit_rid[6],  "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"EmployeeID": 9,  "KGID": "KG2001109", "FirstName": "Kavitha Murthy",      "EmployeeDOB": "1987-10-31", "GenderID": 2, "BloodGroupID": 4, "PhysicallyChallenged": False, "AppointmentDate": "2009-02-15", "DistrictID": dist_rid[4],  "UnitID": unit_rid[6],  "RankID": rank_rid[2], "DesignationID": desig_rid[1]},
        {"EmployeeID": 10, "KGID": "KG2001110", "FirstName": "Jayaram Bhat",        "EmployeeDOB": "1978-04-14", "GenderID": 1, "BloodGroupID": 3, "PhysicallyChallenged": False, "AppointmentDate": "2001-09-20", "DistrictID": dist_rid[5],  "UnitID": unit_rid[7],  "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"EmployeeID": 11, "KGID": "KG2001111", "FirstName": "Abdul Hameed",        "EmployeeDOB": "1983-08-08", "GenderID": 1, "BloodGroupID": 1, "PhysicallyChallenged": False, "AppointmentDate": "2007-06-15", "DistrictID": dist_rid[7],  "UnitID": unit_rid[8],  "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"EmployeeID": 12, "KGID": "KG2001112", "FirstName": "Meenakshi Sundaram",  "EmployeeDOB": "1992-06-11", "GenderID": 2, "BloodGroupID": 2, "PhysicallyChallenged": False, "AppointmentDate": "2015-08-01", "DistrictID": dist_rid[7],  "UnitID": unit_rid[8],  "RankID": rank_rid[2], "DesignationID": desig_rid[1]},
        {"EmployeeID": 13, "KGID": "KG2001113", "FirstName": "Sanjay G",            "EmployeeDOB": "1989-11-22", "GenderID": 1, "BloodGroupID": 4, "PhysicallyChallenged": False, "AppointmentDate": "2012-10-15", "DistrictID": dist_rid[10], "UnitID": unit_rid[10], "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"EmployeeID": 14, "KGID": "KG2001114", "FirstName": "Sunita K",            "EmployeeDOB": "1986-07-07", "GenderID": 2, "BloodGroupID": 1, "PhysicallyChallenged": False, "AppointmentDate": "2010-03-25", "DistrictID": dist_rid[12], "UnitID": unit_rid[11], "RankID": rank_rid[3], "DesignationID": desig_rid[0]},
        {"EmployeeID": 15, "KGID": "KG2001115", "FirstName": "Prasad Rao",          "EmployeeDOB": "1981-02-28", "GenderID": 1, "BloodGroupID": 2, "PhysicallyChallenged": False, "AppointmentDate": "2004-11-10", "DistrictID": dist_rid[0],  "UnitID": unit_rid[0],  "RankID": rank_rid[1], "DesignationID": desig_rid[2]},
        {"EmployeeID": 16, "KGID": "KG2001116", "FirstName": "Vinay Kumar",         "EmployeeDOB": "1995-04-19", "GenderID": 1, "BloodGroupID": 3, "PhysicallyChallenged": False, "AppointmentDate": "2018-09-01", "DistrictID": dist_rid[0],  "UnitID": unit_rid[0],  "RankID": rank_rid[0], "DesignationID": desig_rid[3]},
    ])
    results.append(res)
    emp_rid = rowids(emp_rows)

    # ─────────────────────────────────────────────────────────────────
    # 9. CaseCategory (no FK) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, casecat_rows = insert(ds, "CaseCategory", [
        {"CaseCategoryID": 1,  "LookupValue": "FIR"},
        {"CaseCategoryID": 2,  "LookupValue": "UDR"},
        {"CaseCategoryID": 3,  "LookupValue": "PAR"},
        {"CaseCategoryID": 4,  "LookupValue": "Zero FIR"},
        {"CaseCategoryID": 5,  "LookupValue": "NCR"},
        {"CaseCategoryID": 6,  "LookupValue": "Missing Report"},
        {"CaseCategoryID": 7,  "LookupValue": "Petty Case"},
        {"CaseCategoryID": 8,  "LookupValue": "Preventive Case"},
        {"CaseCategoryID": 9,  "LookupValue": "NCR-Petty"},
        {"CaseCategoryID": 10, "LookupValue": "UDR-Accidental"},
        {"CaseCategoryID": 11, "LookupValue": "UDR-Suicide"},
        {"CaseCategoryID": 12, "LookupValue": "UDR-Suspicious"},
        {"CaseCategoryID": 13, "LookupValue": "Juvenile Case"},
        {"CaseCategoryID": 14, "LookupValue": "Sessions Case"},
        {"CaseCategoryID": 15, "LookupValue": "Special Court Case"},
        {"CaseCategoryID": 16, "LookupValue": "Lok Adalat Case"},
    ])
    results.append(res)
    casecat_rid = rowids(casecat_rows)

    # ─────────────────────────────────────────────────────────────────
    # 10. GravityOffence (no FK) -> 12 rows
    # ─────────────────────────────────────────────────────────────────
    res, gravity_rows = insert(ds, "GravityOffence", [
        {"GravityOffenceID": 1,  "LookupValue": "Heinous"},
        {"GravityOffenceID": 2,  "LookupValue": "Serious"},
        {"GravityOffenceID": 3,  "LookupValue": "Non-Heinous"},
        {"GravityOffenceID": 4,  "LookupValue": "Minor"},
        {"GravityOffenceID": 5,  "LookupValue": "Petty"},
        {"GravityOffenceID": 6,  "LookupValue": "Moderate"},
        {"GravityOffenceID": 7,  "LookupValue": "Critical"},
        {"GravityOffenceID": 8,  "LookupValue": "Extremely Heinous"},
        {"GravityOffenceID": 9,  "LookupValue": "High Severity"},
        {"GravityOffenceID": 10, "LookupValue": "Low Severity"},
        {"GravityOffenceID": 11, "LookupValue": "Medium Severity"},
        {"GravityOffenceID": 12, "LookupValue": "Statutory"},
    ])
    results.append(res)
    gravity_rid = rowids(gravity_rows)

    # ─────────────────────────────────────────────────────────────────
    # 11. CrimeHead (no FK) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, crimehead_rows = insert(ds, "CrimeHead", [
        {"CrimeHeadID": 1,  "CrimeGroupName": "Crimes Against Body",     "Active": True},
        {"CrimeHeadID": 2,  "CrimeGroupName": "Crimes Against Property", "Active": True},
        {"CrimeHeadID": 3,  "CrimeGroupName": "Crimes Against Women",    "Active": True},
        {"CrimeHeadID": 4,  "CrimeGroupName": "Cyber Crimes",            "Active": True},
        {"CrimeHeadID": 5,  "CrimeGroupName": "White Collar Crimes",     "Active": True},
        {"CrimeHeadID": 6,  "CrimeGroupName": "Narcotics Offenses",      "Active": True},
        {"CrimeHeadID": 7,  "CrimeGroupName": "Public Order Offenses",   "Active": True},
        {"CrimeHeadID": 8,  "CrimeGroupName": "Traffic Violations",      "Active": True},
        {"CrimeHeadID": 9,  "CrimeGroupName": "Economic Offenses",       "Active": True},
        {"CrimeHeadID": 10, "CrimeGroupName": "Environmental Crimes",    "Active": True},
        {"CrimeHeadID": 11, "CrimeGroupName": "Juvenile Delinquency",    "Active": True},
        {"CrimeHeadID": 12, "CrimeGroupName": "Election Offenses",       "Active": True},
        {"CrimeHeadID": 13, "CrimeGroupName": "Arms Act Cases",          "Active": True},
        {"CrimeHeadID": 14, "CrimeGroupName": "National Security Offenses", "Active": True},
        {"CrimeHeadID": 15, "CrimeGroupName": "Excise Act Cases",        "Active": True},
        {"CrimeHeadID": 16, "CrimeGroupName": "Government Property Damage", "Active": True},
    ])
    results.append(res)
    ch_rid = rowids(crimehead_rows)

    # ─────────────────────────────────────────────────────────────────
    # 12. CrimeSubHead (FK → CrimeHead) -> 32 rows
    # ─────────────────────────────────────────────────────────────────
    res, csh_rows = insert(ds, "CrimeSubHead", [
        {"CrimeSubHeadID": 1,  "CrimeHeadID": ch_rid[0], "CrimeHeadName": "Murder",            "SeqID": 1},
        {"CrimeSubHeadID": 2,  "CrimeHeadID": ch_rid[0], "CrimeHeadName": "Attempt to Murder", "SeqID": 2},
        {"CrimeSubHeadID": 3,  "CrimeHeadID": ch_rid[1], "CrimeHeadName": "Robbery",           "SeqID": 1},
        {"CrimeSubHeadID": 4,  "CrimeHeadID": ch_rid[1], "CrimeHeadName": "Chain Snatching",   "SeqID": 2},
        {"CrimeSubHeadID": 5,  "CrimeHeadID": ch_rid[1], "CrimeHeadName": "Vehicle Theft",     "SeqID": 3},
        {"CrimeSubHeadID": 6,  "CrimeHeadID": ch_rid[1], "CrimeHeadName": "Burglary",          "SeqID": 4},
        {"CrimeSubHeadID": 7,  "CrimeHeadID": ch_rid[2], "CrimeHeadName": "Harassment",        "SeqID": 1},
        {"CrimeSubHeadID": 8,  "CrimeHeadID": ch_rid[3], "CrimeHeadName": "Online Fraud",      "SeqID": 1},
        {"CrimeSubHeadID": 9,  "CrimeHeadID": ch_rid[0], "CrimeHeadName": "Kidnapping",        "SeqID": 3},
        {"CrimeSubHeadID": 10, "CrimeHeadID": ch_rid[0], "CrimeHeadName": "Grievous Hurt",     "SeqID": 4},
        {"CrimeSubHeadID": 11, "CrimeHeadID": ch_rid[0], "CrimeHeadName": "Assault",           "SeqID": 5},
        {"CrimeSubHeadID": 12, "CrimeHeadID": ch_rid[1], "CrimeHeadName": "Theft",             "SeqID": 5},
        {"CrimeSubHeadID": 13, "CrimeHeadID": ch_rid[1], "CrimeHeadName": "Extortion",         "SeqID": 6},
        {"CrimeSubHeadID": 14, "CrimeHeadID": ch_rid[1], "CrimeHeadName": "Dacoity",           "SeqID": 7},
        {"CrimeSubHeadID": 15, "CrimeHeadID": ch_rid[2], "CrimeHeadName": "Dowry Death",       "SeqID": 2},
        {"CrimeSubHeadID": 16, "CrimeHeadID": ch_rid[2], "CrimeHeadName": "Domestic Violence", "SeqID": 3},
        {"CrimeSubHeadID": 17, "CrimeHeadID": ch_rid[2], "CrimeHeadName": "Stalking",          "SeqID": 4},
        {"CrimeSubHeadID": 18, "CrimeHeadID": ch_rid[3], "CrimeHeadName": "Hacking",           "SeqID": 2},
        {"CrimeSubHeadID": 19, "CrimeHeadID": ch_rid[3], "CrimeHeadName": "Phishing",          "SeqID": 3},
        {"CrimeSubHeadID": 20, "CrimeHeadID": ch_rid[3], "CrimeHeadName": "Identity Theft",    "SeqID": 4},
        {"CrimeSubHeadID": 21, "CrimeHeadID": ch_rid[4], "CrimeHeadName": "Corporate Fraud",   "SeqID": 1},
        {"CrimeSubHeadID": 22, "CrimeHeadID": ch_rid[4], "CrimeHeadName": "Money Laundering",  "SeqID": 2},
        {"CrimeSubHeadID": 23, "CrimeHeadID": ch_rid[5], "CrimeHeadName": "Drug Possession",   "SeqID": 1},
        {"CrimeSubHeadID": 24, "CrimeHeadID": ch_rid[5], "CrimeHeadName": "Drug Trafficking",  "SeqID": 2},
        {"CrimeSubHeadID": 25, "CrimeHeadID": ch_rid[6], "CrimeHeadName": "Rioting",           "SeqID": 1},
        {"CrimeSubHeadID": 26, "CrimeHeadID": ch_rid[6], "CrimeHeadName": "Unlawful Assembly", "SeqID": 2},
        {"CrimeSubHeadID": 27, "CrimeHeadID": ch_rid[7], "CrimeHeadName": "Drunken Driving",   "SeqID": 1},
        {"CrimeSubHeadID": 28, "CrimeHeadID": ch_rid[7], "CrimeHeadName": "Reckless Driving",  "SeqID": 2},
        {"CrimeSubHeadID": 29, "CrimeHeadID": ch_rid[8], "CrimeHeadName": "Tax Evasion",       "SeqID": 1},
        {"CrimeSubHeadID": 30, "CrimeHeadID": ch_rid[8], "CrimeHeadName": "Smuggling",         "SeqID": 2},
        {"CrimeSubHeadID": 31, "CrimeHeadID": ch_rid[9], "CrimeHeadName": "Wildlife Poaching", "SeqID": 1},
        {"CrimeSubHeadID": 32, "CrimeHeadID": ch_rid[12],"CrimeHeadName": "Arms Smuggling",   "SeqID": 1},
    ])
    results.append(res)
    csh_rid = rowids(csh_rows)

    # ─────────────────────────────────────────────────────────────────
    # 13. Act (no FK) -> 16 rows (Primary key is ActCode, a string)
    # ─────────────────────────────────────────────────────────────────
    res, act_rows = insert(ds, "Act", [
        {"ActCode": "IPC",          "ActDescription": "Indian Penal Code, 1860",                               "ShortName": "IPC",          "Active": True},
        {"ActCode": "NDPS",         "ActDescription": "Narcotic Drugs and Psychotropic Substances Act, 1985",  "ShortName": "NDPS",         "Active": True},
        {"ActCode": "IT Act",       "ActDescription": "Information Technology Act, 2000",                      "ShortName": "IT Act",       "Active": True},
        {"ActCode": "POCSO",        "ActDescription": "Protection of Children from Sexual Offences Act, 2012", "ShortName": "POCSO",        "Active": True},
        {"ActCode": "Arms Act",     "ActDescription": "Arms Act, 1959",                                        "ShortName": "Arms Act",     "Active": True},
        {"ActCode": "PCA",          "ActDescription": "Prevention of Corruption Act, 1988",                    "ShortName": "PCA",          "Active": True},
        {"ActCode": "MVA",          "ActDescription": "Motor Vehicles Act, 1988",                              "ShortName": "MVA",          "Active": True},
        {"ActCode": "Excise Act",   "ActDescription": "Excise Act, 1965",                                      "ShortName": "Excise Act",   "Active": True},
        {"ActCode": "WPA",          "ActDescription": "Wildlife Protection Act, 1972",                         "ShortName": "WPA",          "Active": True},
        {"ActCode": "PMLA",         "ActDescription": "Prevention of Money Laundering Act, 2002",              "ShortName": "PMLA",         "Active": True},
        {"ActCode": "ECA",          "ActDescription": "Essential Commodities Act, 1955",                      "ShortName": "ECA",          "Active": True},
        {"ActCode": "DPA",          "ActDescription": "Dowry Prohibition Act, 1961",                           "ShortName": "DPA",          "Active": True},
        {"ActCode": "DVA",          "ActDescription": "Domestic Violence Act, 2005",                           "ShortName": "DVA",          "Active": True},
        {"ActCode": "CRA",          "ActDescription": "Copyright Act, 1957",                                   "ShortName": "CRA",          "Active": True},
        {"ActCode": "Passport Act", "ActDescription": "Passport Act, 1967",                                    "ShortName": "Passport Act", "Active": True},
        {"ActCode": "EDA",          "ActDescription": "Epidemic Diseases Act, 1897",                           "ShortName": "EDA",          "Active": True},
    ])
    results.append(res)
    act_rid = rowids(act_rows)

    # ─────────────────────────────────────────────────────────────────
    # 14. Section (FK → Act) -> 32 rows (Primary key is SectionCode)
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
    # 15. CrimeHeadActSection (FK → CrimeHead, Act) -> 16 rows
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
    # 16. OccupationMaster (no FK) -> 20 rows
    # ─────────────────────────────────────────────────────────────────
    res, occ_rows = insert(ds, "OccupationMaster", [
        {"OccupationID": 1,  "OccupationName": "Farmer"},
        {"OccupationID": 2,  "OccupationName": "Government Employee"},
        {"OccupationID": 3,  "OccupationName": "Business"},
        {"OccupationID": 4,  "OccupationName": "Daily Wage Worker"},
        {"OccupationID": 5,  "OccupationName": "Student"},
        {"OccupationID": 6,  "OccupationName": "Software Engineer"},
        {"OccupationID": 7,  "OccupationName": "Doctor"},
        {"OccupationID": 8,  "OccupationName": "Lawyer"},
        {"OccupationID": 9,  "OccupationName": "Teacher"},
        {"OccupationID": 10, "OccupationName": "Driver"},
        {"OccupationID": 11, "OccupationName": "Housewife"},
        {"OccupationID": 12, "OccupationName": "Unemployed"},
        {"OccupationID": 13, "OccupationName": "Retired"},
        {"OccupationID": 14, "OccupationName": "Police Personnel"},
        {"OccupationID": 15, "OccupationName": "IT Analyst"},
        {"OccupationID": 16, "OccupationName": "Security Guard"},
        {"OccupationID": 17, "OccupationName": "Electrician"},
        {"OccupationID": 18, "OccupationName": "Plumber"},
        {"OccupationID": 19, "OccupationName": "Shopkeeper"},
        {"OccupationID": 20, "OccupationName": "Artist"},
    ])
    results.append(res)
    occ_rid = rowids(occ_rows)

    # ─────────────────────────────────────────────────────────────────
    # 17. ReligionMaster (no FK) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, rel_rows = insert(ds, "ReligionMaster", [
        {"ReligionID": 1,  "ReligionName": "Hindu"},
        {"ReligionID": 2,  "ReligionName": "Muslim"},
        {"ReligionID": 3,  "ReligionName": "Christian"},
        {"ReligionID": 4,  "ReligionName": "Jain"},
        {"ReligionID": 5,  "ReligionName": "Sikh"},
        {"ReligionID": 6,  "ReligionName": "Buddhist"},
        {"ReligionID": 7,  "ReligionName": "Parsi"},
        {"ReligionID": 8,  "ReligionName": "Jewish"},
        {"ReligionID": 9,  "ReligionName": "Tribal Religion"},
        {"ReligionID": 10, "ReligionName": "Bahai"},
        {"ReligionID": 11, "ReligionName": "Atheist"},
        {"ReligionID": 12, "ReligionName": "Agnostic"},
        {"ReligionID": 13, "ReligionName": "Spiritualist"},
        {"ReligionID": 14, "ReligionName": "Humanist"},
        {"ReligionID": 15, "ReligionName": "Other"},
        {"ReligionID": 16, "ReligionName": "Not Disclosed"},
    ])
    results.append(res)
    rel_rid = rowids(rel_rows)

    # ─────────────────────────────────────────────────────────────────
    # 18. CasteMaster (no FK) -> 16 rows (CasteMaster uses lowercase 'caste_master_id')
    # ─────────────────────────────────────────────────────────────────
    res, caste_rows = insert(ds, "CasteMaster", [
        {"caste_master_id": 1,  "caste_master_name": "General"},
        {"caste_master_id": 2,  "caste_master_name": "OBC"},
        {"caste_master_id": 3,  "caste_master_name": "SC"},
        {"caste_master_id": 4,  "caste_master_name": "ST"},
        {"caste_master_id": 5,  "caste_master_name": "Lingayat"},
        {"caste_master_id": 6,  "caste_master_name": "Vokkaliga"},
        {"caste_master_id": 7,  "caste_master_name": "Kuruba"},
        {"caste_master_id": 8,  "caste_master_name": "Madiga"},
        {"caste_master_id": 9,  "caste_master_name": "Chalavadi"},
        {"caste_master_id": 10, "caste_master_name": "Billava"},
        {"caste_master_id": 11, "caste_master_name": "Bunt"},
        {"caste_master_id": 12, "caste_master_name": "Mogaveera"},
        {"caste_master_id": 13, "caste_master_name": "Idiga"},
        {"caste_master_id": 14, "caste_master_name": "Devanga"},
        {"caste_master_id": 15, "caste_master_name": "Sadar"},
        {"caste_master_id": 16, "caste_master_name": "Nayaka"},
    ])
    results.append(res)
    caste_rid = rowids(caste_rows)

    # ─────────────────────────────────────────────────────────────────
    # 19. CaseStatusMaster (no FK) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, status_rows = insert(ds, "CaseStatusMaster", [
        {"CaseStatusID": 1,  "CaseStatusName": "Under Investigation"},
        {"CaseStatusID": 2,  "CaseStatusName": "Charge Sheeted"},
        {"CaseStatusID": 3,  "CaseStatusName": "Referred to Court"},
        {"CaseStatusID": 4,  "CaseStatusName": "Closed"},
        {"CaseStatusID": 5,  "CaseStatusName": "Stayed by High Court"},
        {"CaseStatusID": 6,  "CaseStatusName": "Compromised"},
        {"CaseStatusID": 7,  "CaseStatusName": "Convicted"},
        {"CaseStatusID": 8,  "CaseStatusName": "Acquitted"},
        {"CaseStatusID": 9,  "CaseStatusName": "Abated (Accused Dead)"},
        {"CaseStatusID": 10, "CaseStatusName": "Quashed"},
        {"CaseStatusID": 11, "CaseStatusName": "Pending Trial"},
        {"CaseStatusID": 12, "CaseStatusName": "Transfer to other PS"},
        {"CaseStatusID": 13, "CaseStatusName": "Reopened"},
        {"CaseStatusID": 14, "CaseStatusName": "Untraceable (FR-C)"},
        {"CaseStatusID": 15, "CaseStatusName": "False Case (FR-B)"},
        {"CaseStatusID": 16, "CaseStatusName": "Mistake of Fact (FR-G)"},
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
            "CaseMasterID": 1,
            "CrimeNo": "104430100120240001", "CaseNo": "202400001", "CrimeRegisteredDate": "2024-03-15",
            "PolicePersonID": emp_rid[0], "PoliceStationID": unit_rid[0], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[0], "CrimeMajorHeadID": ch_rid[0], "CrimeMinorHeadID": csh_rid[0],
            "CaseStatusID": status_rid[0], "CourtID": court_rid[0], "IncidentFromDate": "2024-03-14 22:30:00",
            "IncidentToDate": "2024-03-14 23:00:00", "InfoReceivedPSDate": "2024-03-15 01:15:00",
            "latitude": 12.9716, "longitude": 77.5946,
            "BriefFacts": "On 14-03-2024 at approximately 22:30 hrs, the complainant Suresh Nair reported that his neighbour was found dead in his residence near Cubbon Park. The victim had multiple stab wounds on the chest."
        },
        {
            "CaseMasterID": 2,
            "CrimeNo": "104430100120240002", "CaseNo": "202400002", "CrimeRegisteredDate": "2024-04-02",
            "PolicePersonID": emp_rid[1], "PoliceStationID": unit_rid[0], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[1], "CrimeMajorHeadID": ch_rid[1], "CrimeMinorHeadID": csh_rid[3],
            "CaseStatusID": status_rid[0], "CourtID": None, "IncidentFromDate": "2024-04-02 08:15:00",
            "IncidentToDate": "2024-04-02 08:20:00", "InfoReceivedPSDate": "2024-04-02 09:00:00",
            "latitude": 12.9352, "longitude": 77.6245,
            "BriefFacts": "On 02-04-2024 at 08:15 hrs, complainant Lakshmi Devi reported that two persons on a two-wheeler snatched her gold chain valued at Rs 45,000 near Koramangala market."
        },
        {
            "CaseMasterID": 3,
            "CrimeNo": "104430100320240001", "CaseNo": "202400001", "CrimeRegisteredDate": "2024-05-20",
            "PolicePersonID": emp_rid[2], "PoliceStationID": unit_rid[2], "CaseCategoryID": casecat_rid[0],
            "GravityOffenceID": gravity_rid[1], "CrimeMajorHeadID": ch_rid[1], "CrimeMinorHeadID": csh_rid[4],
            "CaseStatusID": status_rid[1], "CourtID": court_rid[1], "IncidentFromDate": "2024-05-19 23:45:00",
            "IncidentToDate": "2024-05-20 00:30:00", "InfoReceivedPSDate": "2024-05-20 07:00:00",
            "latitude": 12.2958, "longitude": 76.6394,
            "BriefFacts": "On 19-05-2024, complainant Ramesh Gowda reported that his Honda City car was stolen from the parking area of Mysuru Palace Road. It was found abandoned in Bannimantap."
        },
        {
            "CaseMasterID": 4,
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
            "CaseMasterID": 5,
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
            "CaseMasterID": 6,
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
            "CaseMasterID": 7,
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
            "CaseMasterID": 8,
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
            "CaseMasterID": 9,
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
            "CaseMasterID": 10,
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
            "CaseMasterID": 11,
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
            "CaseMasterID": 12,
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
            "CaseMasterID": 13,
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
            "CaseMasterID": 14,
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
            "CaseMasterID": 15,
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
            "CaseMasterID": 16,
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
    # 21. Accused (FK → CaseMaster) -> 24 rows
    # ─────────────────────────────────────────────────────────────────
    res, accused_rows = insert(ds, "Accused", [
        # Case 1 (murder)
        {"AccusedMasterID": 1,  "CaseMasterID": case_rid[0], "AccusedName": "Abdul Rauf Khan",              "AgeYear": 31, "GenderID": 1, "PersonID": "A1"},
        {"AccusedMasterID": 2,  "CaseMasterID": case_rid[0], "AccusedName": "Syed Imran",                   "AgeYear": 27, "GenderID": 1, "PersonID": "A2"},
        # Case 2 (chain snatching)
        {"AccusedMasterID": 3,  "CaseMasterID": case_rid[1], "AccusedName": "Abdul Rauf Khan",              "AgeYear": 31, "GenderID": 1, "PersonID": "A1"},
        # Case 3 (vehicle theft)
        {"AccusedMasterID": 4,  "CaseMasterID": case_rid[2], "AccusedName": "Venkatesh Prasad",             "AgeYear": 24, "GenderID": 1, "PersonID": "A1"},
        {"AccusedMasterID": 5,  "CaseMasterID": case_rid[2], "AccusedName": "Ravi Kumar B",                 "AgeYear": 22, "GenderID": 1, "PersonID": "A2"},
        # Case 4 (cyber fraud)
        {"AccusedMasterID": 6,  "CaseMasterID": case_rid[3], "AccusedName": "Unknown — Under Investigation","AgeYear": None,"GenderID": None,"PersonID": "A1"},
        # Case 5 (kidnapping)
        {"AccusedMasterID": 7,  "CaseMasterID": case_rid[4], "AccusedName": "Vikram Gowda",                 "AgeYear": 35, "GenderID": 1, "PersonID": "A1"},
        # Case 6 (grievous hurt)
        {"AccusedMasterID": 8,  "CaseMasterID": case_rid[5], "AccusedName": "Raju Naik",                    "AgeYear": 29, "GenderID": 1, "PersonID": "A1"},
        # Case 7 (dacoity)
        {"AccusedMasterID": 9,  "CaseMasterID": case_rid[6], "AccusedName": "Someshwara Rao",               "AgeYear": 41, "GenderID": 1, "PersonID": "A1"},
        {"AccusedMasterID": 10, "CaseMasterID": case_rid[6], "AccusedName": "Kishore Kumar",                "AgeYear": 30, "GenderID": 1, "PersonID": "A2"},
        {"AccusedMasterID": 11, "CaseMasterID": case_rid[6], "AccusedName": "Dinesh Naik",                  "AgeYear": 28, "GenderID": 1, "PersonID": "A3"},
        {"AccusedMasterID": 12, "CaseMasterID": case_rid[6], "AccusedName": "Mohan Lal",                    "AgeYear": 33, "GenderID": 1, "PersonID": "A4"},
        # Case 8 (DV)
        {"AccusedMasterID": 13, "CaseMasterID": case_rid[7], "AccusedName": "Harish Prasad",                "AgeYear": 32, "GenderID": 1, "PersonID": "A1"},
        # Case 9 (POCSO)
        {"AccusedMasterID": 14, "CaseMasterID": case_rid[8], "AccusedName": "Vikas M",                      "AgeYear": 45, "GenderID": 1, "PersonID": "A1"},
        # Case 10 (drugs)
        {"AccusedMasterID": 15, "CaseMasterID": case_rid[9], "AccusedName": "Peter D'Souza",                "AgeYear": 26, "GenderID": 1, "PersonID": "A1"},
        # Case 11 (rioting)
        {"AccusedMasterID": 16, "CaseMasterID": case_rid[10], "AccusedName": "Rakesh K",                    "AgeYear": 23, "GenderID": 1, "PersonID": "A1"},
        {"AccusedMasterID": 17, "CaseMasterID": case_rid[10], "AccusedName": "Santosh G",                   "AgeYear": 25, "GenderID": 1, "PersonID": "A2"},
        {"AccusedMasterID": 18, "CaseMasterID": case_rid[10], "AccusedName": "Manju N",                     "AgeYear": 22, "GenderID": 1, "PersonID": "A3"},
        # Case 12 (traffic)
        {"AccusedMasterID": 19, "CaseMasterID": case_rid[11], "AccusedName": "Rajeev Hegde",                "AgeYear": 38, "GenderID": 1, "PersonID": "A1"},
        # Case 13 (hacking)
        {"AccusedMasterID": 20, "CaseMasterID": case_rid[12], "AccusedName": "Karan Johar",                 "AgeYear": 24, "GenderID": 1, "PersonID": "A1"},
        # Case 14 (UDR)
        {"AccusedMasterID": 21, "CaseMasterID": case_rid[13], "AccusedName": "Unknown",                     "AgeYear": None,"GenderID": None,"PersonID": "A1"},
        # Case 15 (zero FIR)
        {"AccusedMasterID": 22, "CaseMasterID": case_rid[14], "AccusedName": "Shankar Lal",                 "AgeYear": 29, "GenderID": 1, "PersonID": "A1"},
        # Case 16 (PMLA)
        {"AccusedMasterID": 23, "CaseMasterID": case_rid[15], "AccusedName": "Vijay Mallya Jr",             "AgeYear": 48, "GenderID": 1, "PersonID": "A1"},
    ])
    results.append(res)
    acc_rid = rowids(accused_rows)

    # ─────────────────────────────────────────────────────────────────
    # 22. Victim (FK → CaseMaster) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "Victim", [
        {"VictimMasterID": 1,  "CaseMasterID": case_rid[0], "VictimName": "Prakash Naidu", "AgeYear": 45, "GenderID": 1, "VictimPolice": False},
        {"VictimMasterID": 2,  "CaseMasterID": case_rid[1], "VictimName": "Lakshmi Devi",  "AgeYear": 62, "GenderID": 2, "VictimPolice": False},
        {"VictimMasterID": 3,  "CaseMasterID": case_rid[2], "VictimName": "Ramesh Gowda",  "AgeYear": 38, "GenderID": 1, "VictimPolice": False},
        {"VictimMasterID": 4,  "CaseMasterID": case_rid[3], "VictimName": "Anil Mehta",    "AgeYear": 52, "GenderID": 1, "VictimPolice": False},
        {"VictimMasterID": 5,  "CaseMasterID": case_rid[4], "VictimName": "Master Rahul",  "AgeYear": 10, "GenderID": 1, "VictimPolice": False},
        {"VictimMasterID": 6,  "CaseMasterID": case_rid[5], "VictimName": "Girish K",      "AgeYear": 34, "GenderID": 1, "VictimPolice": False},
        {"VictimMasterID": 7,  "CaseMasterID": case_rid[6], "VictimName": "Swaminathan",   "AgeYear": 55, "GenderID": 1, "VictimPolice": False},
        {"VictimMasterID": 8,  "CaseMasterID": case_rid[7], "VictimName": "Shalini Prasad","AgeYear": 28, "GenderID": 2, "VictimPolice": False},
        {"VictimMasterID": 9,  "CaseMasterID": case_rid[8], "VictimName": "Aishwarya",     "AgeYear": 14, "GenderID": 2, "VictimPolice": False},
        {"VictimMasterID": 10, "CaseMasterID": case_rid[9], "VictimName": "Public Interest","AgeYear": None, "GenderID": None, "VictimPolice": False},
        {"VictimMasterID": 11, "CaseMasterID": case_rid[10], "VictimName": "Priya Sharma", "AgeYear": 35, "GenderID": 2, "VictimPolice": True},
        {"VictimMasterID": 12, "CaseMasterID": case_rid[11], "VictimName": "Karthik",      "AgeYear": 22, "GenderID": 1, "VictimPolice": False},
        {"VictimMasterID": 13, "CaseMasterID": case_rid[12], "VictimName": "ABC Corp",     "AgeYear": None, "GenderID": None, "VictimPolice": False},
        {"VictimMasterID": 14, "CaseMasterID": case_rid[13], "VictimName": "Somappa",      "AgeYear": 55, "GenderID": 1, "VictimPolice": False},
        {"VictimMasterID": 15, "CaseMasterID": case_rid[14], "VictimName": "Girija Bai",   "AgeYear": 45, "GenderID": 2, "VictimPolice": False},
        {"VictimMasterID": 16, "CaseMasterID": case_rid[15], "VictimName": "National Bank","AgeYear": None, "GenderID": None, "VictimPolice": False},
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # 23. ComplainantDetails (FK → CaseMaster, OccupationMaster, ReligionMaster, CasteMaster) -> 16 rows
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "ComplainantDetails", [
        {"ComplainantID": 1,  "CaseMasterID": case_rid[0], "ComplainantName": "Suresh Nair",    "AgeYear": 40, "OccupationID": occ_rid[1], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
        {"ComplainantID": 2,  "CaseMasterID": case_rid[1], "ComplainantName": "Lakshmi Devi",   "AgeYear": 62, "OccupationID": occ_rid[3], "ReligionID": rel_rid[0], "CasteID": caste_rid[1], "GenderID": 2},
        {"ComplainantID": 3,  "CaseMasterID": case_rid[2], "ComplainantName": "Ramesh Gowda",   "AgeYear": 38, "OccupationID": occ_rid[2], "ReligionID": rel_rid[0], "CasteID": caste_rid[1], "GenderID": 1},
        {"ComplainantID": 4,  "CaseMasterID": case_rid[3], "ComplainantName": "Anil Mehta",     "AgeYear": 52, "OccupationID": occ_rid[1], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
        {"ComplainantID": 5,  "CaseMasterID": case_rid[4], "ComplainantName": "Vikram Gowda",   "AgeYear": 42, "OccupationID": occ_rid[0], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
        {"ComplainantID": 6,  "CaseMasterID": case_rid[5], "ComplainantName": "Girish K",       "AgeYear": 34, "OccupationID": occ_rid[5], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
        {"ComplainantID": 7,  "CaseMasterID": case_rid[6], "ComplainantName": "Swaminathan",    "AgeYear": 55, "OccupationID": occ_rid[1], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
        {"ComplainantID": 8,  "CaseMasterID": case_rid[7], "ComplainantName": "Shalini Prasad", "AgeYear": 28, "OccupationID": occ_rid[8], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 2},
        {"ComplainantID": 9,  "CaseMasterID": case_rid[8], "ComplainantName": "Mother of Child","AgeYear": 38, "OccupationID": occ_rid[10], "ReligionID": rel_rid[0], "CasteID": caste_rid[1], "GenderID": 2},
        {"ComplainantID": 10, "CaseMasterID": case_rid[9], "ComplainantName": "Abdul Hameed",   "AgeYear": 43, "OccupationID": occ_rid[13], "ReligionID": rel_rid[1], "CasteID": caste_rid[1], "GenderID": 1},
        {"ComplainantID": 11, "CaseMasterID": case_rid[10], "ComplainantName": "Prasad Rao",     "AgeYear": 45, "OccupationID": occ_rid[13], "ReligionID": rel_rid[0], "CasteID": caste_rid[2], "GenderID": 1},
        {"ComplainantID": 12, "CaseMasterID": case_rid[11], "ComplainantName": "Karthik",       "AgeYear": 22, "OccupationID": occ_rid[4], "ReligionID": rel_rid[0], "CasteID": caste_rid[1], "GenderID": 1},
        {"ComplainantID": 13, "CaseMasterID": case_rid[12], "ComplainantName": "Security Head",  "AgeYear": 35, "OccupationID": occ_rid[5], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
        {"ComplainantID": 14, "CaseMasterID": case_rid[13], "ComplainantName": "Somappa",       "AgeYear": 55, "OccupationID": occ_rid[0], "ReligionID": rel_rid[0], "CasteID": caste_rid[3], "GenderID": 1},
        {"ComplainantID": 15, "CaseMasterID": case_rid[14], "ComplainantName": "Girija Bai",    "AgeYear": 45, "OccupationID": occ_rid[3], "ReligionID": rel_rid[0], "CasteID": caste_rid[2], "GenderID": 2},
        {"ComplainantID": 16, "CaseMasterID": case_rid[15], "ComplainantName": "Bank Auditor",   "AgeYear": 50, "OccupationID": occ_rid[1], "ReligionID": rel_rid[0], "CasteID": caste_rid[0], "GenderID": 1},
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # 24. ActSectionAssociation (FK → CaseMaster, Act, Section) -> 32 rows
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
        {"ArrestSurrenderID": 1,  "CaseMasterID": case_rid[0], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-03-18", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[0], "PoliceStationID": unit_rid[0], "IOID": emp_rid[1], "CourtID": court_rid[0], "AccusedMasterID": acc_rid[0], "IsAccused": True, "IsComplainantAccused": False},
        {"ArrestSurrenderID": 2,  "CaseMasterID": case_rid[0], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-03-18", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[0], "PoliceStationID": unit_rid[0], "IOID": emp_rid[1], "CourtID": court_rid[0], "AccusedMasterID": acc_rid[1], "IsAccused": True, "IsComplainantAccused": False},
        {"ArrestSurrenderID": 3,  "CaseMasterID": case_rid[2], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-06-01", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[1], "PoliceStationID": unit_rid[2], "IOID": emp_rid[3], "CourtID": court_rid[1], "AccusedMasterID": acc_rid[4], "IsAccused": True, "IsComplainantAccused": False},
        # Added 9 Arrests
        {"ArrestSurrenderID": 4,  "CaseMasterID": case_rid[4], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-07-05", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[0], "PoliceStationID": unit_rid[1], "IOID": emp_rid[6], "CourtID": court_rid[0], "AccusedMasterID": acc_rid[6], "IsAccused": True, "IsComplainantAccused": False},
        {"ArrestSurrenderID": 5,  "CaseMasterID": case_rid[5], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-07-20", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[0], "PoliceStationID": unit_rid[1], "IOID": emp_rid[6], "CourtID": court_rid[0], "AccusedMasterID": acc_rid[7], "IsAccused": True, "IsComplainantAccused": False},
        {"ArrestSurrenderID": 6,  "CaseMasterID": case_rid[6], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-08-05", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[4], "PoliceStationID": unit_rid[6], "IOID": emp_rid[7], "CourtID": court_rid[5], "AccusedMasterID": acc_rid[8], "IsAccused": True, "IsComplainantAccused": False},
        {"ArrestSurrenderID": 7,  "CaseMasterID": case_rid[6], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-08-05", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[4], "PoliceStationID": unit_rid[6], "IOID": emp_rid[7], "CourtID": court_rid[5], "AccusedMasterID": acc_rid[9], "IsAccused": True, "IsComplainantAccused": False},
        {"ArrestSurrenderID": 8,  "CaseMasterID": case_rid[7], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-08-15", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[4], "PoliceStationID": unit_rid[6], "IOID": emp_rid[8], "CourtID": court_rid[5], "AccusedMasterID": acc_rid[12], "IsAccused": True, "IsComplainantAccused": False},
        {"ArrestSurrenderID": 9,  "CaseMasterID": case_rid[8], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-08-25", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[5], "PoliceStationID": unit_rid[7], "IOID": emp_rid[9], "CourtID": court_rid[6], "AccusedMasterID": acc_rid[13], "IsAccused": True, "IsComplainantAccused": False},
        {"ArrestSurrenderID": 10, "CaseMasterID": case_rid[9], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-09-05", "ArrestSurrenderStateId": state_rid[1], "ArrestSurrenderDistrictId": dist_rid[7], "PoliceStationID": unit_rid[8], "IOID": emp_rid[10], "CourtID": court_rid[8], "AccusedMasterID": acc_rid[14], "IsAccused": True, "IsComplainantAccused": False},
        {"ArrestSurrenderID": 11, "CaseMasterID": case_rid[10], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-09-20", "ArrestSurrenderStateId": state_rid[1], "ArrestSurrenderDistrictId": dist_rid[7], "PoliceStationID": unit_rid[8], "IOID": emp_rid[11], "CourtID": court_rid[8], "AccusedMasterID": acc_rid[15], "IsAccused": True, "IsComplainantAccused": False},
        {"ArrestSurrenderID": 12, "CaseMasterID": case_rid[11], "ArrestSurrenderTypeID": 1, "ArrestSurrenderDate": "2024-09-28", "ArrestSurrenderStateId": state_rid[0], "ArrestSurrenderDistrictId": dist_rid[0], "PoliceStationID": unit_rid[0], "IOID": emp_rid[0], "CourtID": court_rid[0], "AccusedMasterID": acc_rid[18], "IsAccused": True, "IsComplainantAccused": False},
    ])
    results.append(res)

    # ─────────────────────────────────────────────────────────────────
    # 26. ChargesheetDetails (FK → CaseMaster, Employee) -> 4 rows
    # ─────────────────────────────────────────────────────────────────
    res, _ = insert(ds, "ChargesheetDetails", [
        # Original 1 Chargesheet
        {"CSID": 1, "CaseMasterID": case_rid[2], "csdate": "2024-07-15 10:00:00", "cstype": "A", "PolicePersonID": emp_rid[2]},
        # Added 3 Chargesheets
        {"CSID": 2, "CaseMasterID": case_rid[4], "csdate": "2024-08-10 11:00:00", "cstype": "A", "PolicePersonID": emp_rid[6]},
        {"CSID": 3, "CaseMasterID": case_rid[9], "csdate": "2024-09-15 14:00:00", "cstype": "A", "PolicePersonID": emp_rid[10]},
        {"CSID": 4, "CaseMasterID": case_rid[11], "csdate": "2024-10-20 10:00:00", "cstype": "A", "PolicePersonID": emp_rid[0]},
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