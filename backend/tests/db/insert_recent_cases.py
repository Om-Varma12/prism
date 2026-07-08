"""
PRISM — Insert Recent CaseMaster Records for Dashboard Testing
================================================================
Inserts Units, Employees, and CaseMaster records for Belagavi and Kalaburagi
districts to show points on the dashboard map.
"""

from fastapi import Request, APIRouter
import zcatalyst_sdk
from datetime import datetime, timedelta
from core.database import get_datastore, get_zcql

router = APIRouter(prefix="/db", tags=["recent-cases"])


def insert(datastore, table_name: str, rows: list[dict]) -> tuple[dict, list[dict]]:
    """Insert rows and return (result_summary, inserted_rows_with_rowids)."""
    try:
        table = datastore.table(table_name)
        response = table.insert_rows(rows)
        inserted = response if isinstance(response, list) else []
        print(f"  {table_name}: inserted {len(inserted)} rows")
        return {"table": table_name, "status": "ok", "count": len(inserted)}, inserted
    except Exception as e:
        print(f"    {table_name}: FAILED — {e}")
        return {"table": table_name, "status": "error", "error": str(e)}, []


@router.get("/test/insert-recent-cases")
def insert_recent_cases(request: Request):
    """Insert Units, Employees, and CaseMaster records for Belagavi and Kalaburagi districts."""
    ds = get_datastore(request)
    zcql = get_zcql(request)
    results = []

    print("\n========== INSERTING UNITS, EMPLOYEES, AND CASEMASTER RECORDS ==========\n")

    # Fetch District ROWIDs
    try:
        district_query = "SELECT ROWID, DistrictName FROM District WHERE DistrictName IN ('Belagavi', 'Kalaburagi')"
        district_result = zcql.execute_query(district_query)
        district_map = {row.get("District", {}).get("DistrictName"): row.get("District", {}).get("ROWID") for row in district_result}
        print(f"Districts found: {district_map}")
    except Exception as e:
        print(f"Error fetching districts: {e}")
        return {"status": "error", "message": str(e)}

    # Fetch State ROWID for Karnataka
    try:
        state_query = "SELECT ROWID, StateName FROM State WHERE StateName = 'Karnataka'"
        state_result = zcql.execute_query(state_query)
        karnataka_state_rid = state_result[0].get("State", {}).get("ROWID") if state_result else None
        print(f"Karnataka State ROWID: {karnataka_state_rid}")
    except Exception as e:
        print(f"Error fetching state: {e}")
        return {"status": "error", "message": str(e)}

    # Fetch UnitType ROWID for Police Station
    try:
        unittype_query = "SELECT ROWID, UnitTypeName FROM UnitType WHERE UnitTypeName = 'Police Station'"
        unittype_result = zcql.execute_query(unittype_query)
        police_station_type_rid = unittype_result[0].get("UnitType", {}).get("ROWID") if unittype_result else None
        print(f"Police Station UnitType ROWID: {police_station_type_rid}")
    except Exception as e:
        print(f"Error fetching unit type: {e}")
        return {"status": "error", "message": str(e)}

    # Fetch Rank ROWIDs
    try:
        rank_query = "SELECT ROWID, RankName FROM Rank WHERE RankName IN ('Sub Inspector', 'Inspector')"
        rank_result = zcql.execute_query(rank_query)
        rank_map = {row.get("Rank", {}).get("RankName"): row.get("Rank", {}).get("ROWID") for row in rank_result}
        print(f"Ranks found: {rank_map}")
    except Exception as e:
        print(f"Error fetching ranks: {e}")
        return {"status": "error", "message": str(e)}

    # Fetch Designation ROWIDs
    try:
        desig_query = "SELECT ROWID, DesignationName FROM Designation WHERE DesignationName IN ('Station House Officer', 'Investigating Officer')"
        desig_result = zcql.execute_query(desig_query)
        desig_map = {row.get("Designation", {}).get("DesignationName"): row.get("Designation", {}).get("ROWID") for row in desig_result}
        print(f"Designations found: {desig_map}")
    except Exception as e:
        print(f"Error fetching designations: {e}")
        return {"status": "error", "message": str(e)}

    # Fetch Court ROWID for Belagavi
    try:
        court_query = "SELECT ROWID, CourtName FROM Court WHERE CourtName = 'Belagavi Sessions Court'"
        court_result = zcql.execute_query(court_query)
        belagavi_court_rid = court_result[0].get("Court", {}).get("ROWID") if court_result else None
        print(f"Belagavi Court ROWID: {belagavi_court_rid}")
    except Exception as e:
        print(f"Error fetching court: {e}")
        return {"status": "error", "message": str(e)}

    # Fetch existing ROWIDs for foreign key reference tables
    try:
        casecat_query = "SELECT ROWID, LookupValue FROM CaseCategory WHERE LookupValue = 'FIR'"
        casecat_result = zcql.execute_query(casecat_query)
        casecat_map = {row.get("CaseCategory", {}).get("LookupValue"): row.get("CaseCategory", {}).get("ROWID") for row in casecat_result}
        print(f"CaseCategory ROWIDs: {casecat_map}")
    except Exception as e:
        print(f"Error fetching case category: {e}")
        return {"status": "error", "message": str(e)}

    try:
        gravity_query = "SELECT ROWID, LookupValue FROM GravityOffence WHERE LookupValue IN ('Heinous', 'Serious')"
        gravity_result = zcql.execute_query(gravity_query)
        gravity_map = {row.get("GravityOffence", {}).get("LookupValue"): row.get("GravityOffence", {}).get("ROWID") for row in gravity_result}
        print(f"GravityOffence ROWIDs: {gravity_map}")
    except Exception as e:
        print(f"Error fetching gravity offence: {e}")
        return {"status": "error", "message": str(e)}

    try:
        crimehead_query = "SELECT ROWID, CrimeGroupName FROM CrimeHead WHERE CrimeGroupName IN ('Crimes Against Body', 'Crimes Against Property', 'Crimes Against Women')"
        crimehead_result = zcql.execute_query(crimehead_query)
        crimehead_map = {row.get("CrimeHead", {}).get("CrimeGroupName"): row.get("CrimeHead", {}).get("ROWID") for row in crimehead_result}
        print(f"CrimeHead ROWIDs: {crimehead_map}")
    except Exception as e:
        print(f"Error fetching crime head: {e}")
        return {"status": "error", "message": str(e)}

    try:
        csh_query = "SELECT ROWID, CrimeHeadName FROM CrimeSubHead WHERE CrimeHeadName IN ('Murder', 'Theft', 'Chain Snatching', 'Robbery')"
        csh_result = zcql.execute_query(csh_query)
        csh_map = {row.get("CrimeSubHead", {}).get("CrimeHeadName"): row.get("CrimeSubHead", {}).get("ROWID") for row in csh_result}
        print(f"CrimeSubHeads found: {csh_map}")
    except Exception as e:
        print(f"Error fetching crime subheads: {e}")
        return {"status": "error", "message": str(e)}

    try:
        status_query = "SELECT ROWID, CaseStatusName FROM CaseStatusMaster WHERE CaseStatusName IN ('Under Investigation', 'Charge Sheeted')"
        status_result = zcql.execute_query(status_query)
        status_map = {row.get("CaseStatusMaster", {}).get("CaseStatusName"): row.get("CaseStatusMaster", {}).get("ROWID") for row in status_result}
        print(f"CaseStatus found: {status_map}")
    except Exception as e:
        print(f"Error fetching case status: {e}")
        return {"status": "error", "message": str(e)}

    # Insert Units for Belagavi and Kalaburagi
    belagavi_district_rid = district_map.get("Belagavi")
    kalaburagi_district_rid = district_map.get("Kalaburagi")

    if not belagavi_district_rid or not kalaburagi_district_rid:
        return {"status": "error", "message": "District ROWIDs not found for Belagavi or Kalaburagi"}

    unit_rows = [
        {"UnitID": 17, "UnitName": "Belagavi Town Police Station", "TypeID": police_station_type_rid, "ParentUnit": None, "NationalityID": 1, "StateID": karnataka_state_rid, "DistrictID": belagavi_district_rid, "Active": True},
        {"UnitID": 18, "UnitName": "Belagavi Rural PS", "TypeID": police_station_type_rid, "ParentUnit": None, "NationalityID": 1, "StateID": karnataka_state_rid, "DistrictID": belagavi_district_rid, "Active": True},
        {"UnitID": 19, "UnitName": "Kalaburagi City PS", "TypeID": police_station_type_rid, "ParentUnit": None, "NationalityID": 1, "StateID": karnataka_state_rid, "DistrictID": kalaburagi_district_rid, "Active": True},
        {"UnitID": 20, "UnitName": "Kalaburagi Rural PS", "TypeID": police_station_type_rid, "ParentUnit": None, "NationalityID": 1, "StateID": karnataka_state_rid, "DistrictID": kalaburagi_district_rid, "Active": True},
    ]

    res, inserted_units = insert(ds, "Unit", unit_rows)
    results.append(res)
    unit_rid_map = {row["UnitName"]: row["ROWID"] for row in inserted_units}
    print(f"New Unit ROWIDs: {unit_rid_map}")

    # Insert Employees for new Units
    emp_rows = [
        {"EmployeeID": 17, "KGID": "KG2001117", "FirstName": "Ramesh Kumar", "EmployeeDOB": "1985-03-15", "GenderID": 1, "BloodGroupID": 2, "PhysicallyChallenged": False, "AppointmentDate": "2008-06-01", "DistrictID": belagavi_district_rid, "UnitID": unit_rid_map.get("Belagavi Town Police Station"), "RankID": rank_map.get("Inspector"), "DesignationID": desig_map.get("Station House Officer")},
        {"EmployeeID": 18, "KGID": "KG2001118", "FirstName": "Priya Sharma", "EmployeeDOB": "1990-07-22", "GenderID": 2, "BloodGroupID": 1, "PhysicallyChallenged": False, "AppointmentDate": "2013-09-15", "DistrictID": belagavi_district_rid, "UnitID": unit_rid_map.get("Belagavi Town Police Station"), "RankID": rank_map.get("Sub Inspector"), "DesignationID": desig_map.get("Investigating Officer")},
        {"EmployeeID": 19, "KGID": "KG2001119", "FirstName": "Mohammed Farooq", "EmployeeDOB": "1982-11-08", "GenderID": 1, "BloodGroupID": 3, "PhysicallyChallenged": False, "AppointmentDate": "2005-03-20", "DistrictID": belagavi_district_rid, "UnitID": unit_rid_map.get("Belagavi Rural PS"), "RankID": rank_map.get("Inspector"), "DesignationID": desig_map.get("Station House Officer")},
        {"EmployeeID": 20, "KGID": "KG2001120", "FirstName": "Anitha Reddy", "EmployeeDOB": "1993-05-30", "GenderID": 2, "BloodGroupID": 4, "PhysicallyChallenged": False, "AppointmentDate": "2016-11-01", "DistrictID": belagavi_district_rid, "UnitID": unit_rid_map.get("Belagavi Rural PS"), "RankID": rank_map.get("Sub Inspector"), "DesignationID": desig_map.get("Investigating Officer")},
        {"EmployeeID": 21, "KGID": "KG2001121", "FirstName": "Suresh Patil", "EmployeeDOB": "1988-12-05", "GenderID": 1, "BloodGroupID": 2, "PhysicallyChallenged": False, "AppointmentDate": "2011-04-10", "DistrictID": kalaburagi_district_rid, "UnitID": unit_rid_map.get("Kalaburagi City PS"), "RankID": rank_map.get("Inspector"), "DesignationID": desig_map.get("Station House Officer")},
        {"EmployeeID": 22, "KGID": "KG2001122", "FirstName": "Vikram Singh", "EmployeeDOB": "1984-01-20", "GenderID": 1, "BloodGroupID": 3, "PhysicallyChallenged": False, "AppointmentDate": "2006-08-15", "DistrictID": kalaburagi_district_rid, "UnitID": unit_rid_map.get("Kalaburagi City PS"), "RankID": rank_map.get("Sub Inspector"), "DesignationID": desig_map.get("Investigating Officer")},
        {"EmployeeID": 23, "KGID": "KG2001123", "FirstName": "Deepa N", "EmployeeDOB": "1991-09-18", "GenderID": 2, "BloodGroupID": 1, "PhysicallyChallenged": False, "AppointmentDate": "2014-05-12", "DistrictID": kalaburagi_district_rid, "UnitID": unit_rid_map.get("Kalaburagi Rural PS"), "RankID": rank_map.get("Inspector"), "DesignationID": desig_map.get("Station House Officer")},
        {"EmployeeID": 24, "KGID": "KG2001124", "FirstName": "Ramesh Chandra", "EmployeeDOB": "1980-05-25", "GenderID": 1, "BloodGroupID": 2, "PhysicallyChallenged": False, "AppointmentDate": "2002-12-01", "DistrictID": kalaburagi_district_rid, "UnitID": unit_rid_map.get("Kalaburagi Rural PS"), "RankID": rank_map.get("Sub Inspector"), "DesignationID": desig_map.get("Investigating Officer")},
    ]

    res, inserted_emps = insert(ds, "Employee", emp_rows)
    results.append(res)
    emp_rid_map = {row["KGID"]: row["ROWID"] for row in inserted_emps}
    print(f"New Employee ROWIDs: {emp_rid_map}")

    # Generate recent dates (within last 30 days from 2026-07-08)
    base_date = datetime(2026, 7, 8)
    case_dates = [
        (base_date - timedelta(days=3)).strftime("%Y-%m-%d"),  # 2026-07-05
        (base_date - timedelta(days=8)).strftime("%Y-%m-%d"),  # 2026-06-30
        (base_date - timedelta(days=13)).strftime("%Y-%m-%d"), # 2026-06-25
        (base_date - timedelta(days=18)).strftime("%Y-%m-%d"), # 2026-06-20
        (base_date - timedelta(days=23)).strftime("%Y-%m-%d"), # 2026-06-15
    ]

    # Get max existing CaseMasterID to avoid conflicts
    try:
        case_query = "SELECT MAX(CaseMasterID) as max_id FROM CaseMaster"
        case_result = zcql.execute_query(case_query)
        max_id = case_result[0].get("CaseMaster", {}).get("MAX(CaseMasterID)", 0) if case_result else 0
        next_id = (int(max_id) if max_id else 0) + 1
    except:
        next_id = 100  # Fallback

    # CaseMaster records for Belagavi and Kalaburagi
    case_rows = [
        # Belagavi cases
        {
            "CaseMasterID": next_id,
            "CrimeNo": f"10443010012026000{next_id}",
            "CaseNo": f"2026000{next_id}",
            "CrimeRegisteredDate": case_dates[0],
            "PolicePersonID": emp_rid_map.get("KG2001117"),
            "PoliceStationID": unit_rid_map.get("Belagavi Town Police Station"),
            "CaseCategoryID": casecat_map.get("FIR"),
            "GravityOffenceID": gravity_map.get("Serious"),
            "CrimeMajorHeadID": crimehead_map.get("Crimes Against Property"),
            "CrimeMinorHeadID": csh_map.get("Theft"),
            "CaseStatusID": status_map.get("Under Investigation"),
            "CourtID": belagavi_court_rid,
            "IncidentFromDate": f"{case_dates[0]} 14:30:00",
            "IncidentToDate": f"{case_dates[0]} 15:00:00",
            "InfoReceivedPSDate": f"{case_dates[0]} 15:30:00",
            "latitude": 15.8607,
            "longitude": 74.5069,
            "BriefFacts": "On 05-07-2026 at 14:30 hrs, a theft was reported from a shop in Belagavi Town."
        },
        {
            "CaseMasterID": next_id + 1,
            "CrimeNo": f"10443010022026000{next_id + 1}",
            "CaseNo": f"2026000{next_id + 1}",
            "CrimeRegisteredDate": case_dates[1],
            "PolicePersonID": emp_rid_map.get("KG2001118"),
            "PoliceStationID": unit_rid_map.get("Belagavi Town Police Station"),
            "CaseCategoryID": casecat_map.get("FIR"),
            "GravityOffenceID": gravity_map.get("Heinous"),
            "CrimeMajorHeadID": crimehead_map.get("Crimes Against Body"),
            "CrimeMinorHeadID": csh_map.get("Murder"),
            "CaseStatusID": status_map.get("Under Investigation"),
            "CourtID": belagavi_court_rid,
            "IncidentFromDate": f"{case_dates[1]} 21:00:00",
            "IncidentToDate": f"{case_dates[1]} 21:30:00",
            "InfoReceivedPSDate": f"{case_dates[1]} 22:00:00",
            "latitude": 15.8607,
            "longitude": 74.5069,
            "BriefFacts": "On 30-06-2026 at 21:00 hrs, a murder was reported in Belagavi rural area."
        },
        {
            "CaseMasterID": next_id + 2,
            "CrimeNo": f"10443010032026000{next_id + 2}",
            "CaseNo": f"2026000{next_id + 2}",
            "CrimeRegisteredDate": case_dates[2],
            "PolicePersonID": emp_rid_map.get("KG2001119"),
            "PoliceStationID": unit_rid_map.get("Belagavi Rural PS"),
            "CaseCategoryID": casecat_map.get("FIR"),
            "GravityOffenceID": gravity_map.get("Serious"),
            "CrimeMajorHeadID": crimehead_map.get("Crimes Against Women"),
            "CrimeMinorHeadID": csh_map.get("Chain Snatching"),
            "CaseStatusID": status_map.get("Charge Sheeted"),
            "CourtID": belagavi_court_rid,
            "IncidentFromDate": f"{case_dates[2]} 10:00:00",
            "IncidentToDate": f"{case_dates[2]} 10:15:00",
            "InfoReceivedPSDate": f"{case_dates[2]} 10:45:00",
            "latitude": 15.7500,
            "longitude": 74.4500,
            "BriefFacts": "On 25-06-2026 at 10:00 hrs, chain snatching reported near Belagavi rural market."
        },
        # Kalaburagi cases
        {
            "CaseMasterID": next_id + 3,
            "CrimeNo": f"10443010042026000{next_id + 3}",
            "CaseNo": f"2026000{next_id + 3}",
            "CrimeRegisteredDate": case_dates[3],
            "PolicePersonID": emp_rid_map.get("KG2001121"),
            "PoliceStationID": unit_rid_map.get("Kalaburagi City PS"),
            "CaseCategoryID": casecat_map.get("FIR"),
            "GravityOffenceID": gravity_map.get("Serious"),
            "CrimeMajorHeadID": crimehead_map.get("Crimes Against Property"),
            "CrimeMinorHeadID": csh_map.get("Theft"),
            "CaseStatusID": status_map.get("Under Investigation"),
            "CourtID": None,
            "IncidentFromDate": f"{case_dates[3]} 16:00:00",
            "IncidentToDate": f"{case_dates[3]} 16:30:00",
            "InfoReceivedPSDate": f"{case_dates[3]} 17:00:00",
            "latitude": 17.3400,
            "longitude": 76.8400,
            "BriefFacts": "On 20-06-2026 at 16:00 hrs, a theft was reported from a shop in Kalaburagi City."
        },
        {
            "CaseMasterID": next_id + 4,
            "CrimeNo": f"10443010052026000{next_id + 4}",
            "CaseNo": f"2026000{next_id + 4}",
            "CrimeRegisteredDate": case_dates[4],
            "PolicePersonID": emp_rid_map.get("KG2001122"),
            "PoliceStationID": unit_rid_map.get("Kalaburagi City PS"),
            "CaseCategoryID": casecat_map.get("FIR"),
            "GravityOffenceID": gravity_map.get("Heinous"),
            "CrimeMajorHeadID": crimehead_map.get("Crimes Against Body"),
            "CrimeMinorHeadID": csh_map.get("Robbery"),
            "CaseStatusID": status_map.get("Under Investigation"),
            "CourtID": None,
            "IncidentFromDate": f"{case_dates[4]} 20:00:00",
            "IncidentToDate": f"{case_dates[4]} 20:30:00",
            "InfoReceivedPSDate": f"{case_dates[4]} 21:00:00",
            "latitude": 17.3400,
            "longitude": 76.8400,
            "BriefFacts": "On 15-06-2026 at 20:00 hrs, armed robbery reported at Kalaburagi City residence."
        },
    ]

    res, inserted_cases = insert(ds, "CaseMaster", case_rows)
    results.append(res)

    print(f"\n========== SUMMARY ==========")
    print(f"Inserted {len(inserted_units)} Units")
    print(f"Inserted {len(inserted_emps)} Employees")
    print(f"Inserted {len(inserted_cases)} CaseMaster records")
    print(f"Date range: {case_dates[-1]} to {case_dates[0]}")
    print(f"============================\n")

    return {
        "status": "ok",
        "units_inserted": len(inserted_units),
        "employees_inserted": len(inserted_emps),
        "cases_inserted": len(inserted_cases),
        "date_range": {"from": case_dates[-1], "to": case_dates[0]},
        "results": results
    }
