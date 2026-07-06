"""
PRISM — Insert Recent CaseMaster Records for Dashboard Testing
================================================================
Inserts 5 recent CaseMaster records with dates within last 30 days
for different Karnataka districts to test district markers on dashboard.
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
    """Insert 5 recent CaseMaster records for different Karnataka districts."""
    ds = get_datastore(request)
    zcql = get_zcql(request)
    results = []

    print("\n========== INSERTING RECENT CASEMASTER RECORDS ==========\n")

    # Fetch existing ROWIDs using ZCQL
    try:
        district_query = "SELECT ROWID, DistrictName FROM District WHERE DistrictName IN ('Bengaluru Urban', 'Mysuru', 'Dakshina Kannada', 'Belagavi', 'Kalaburagi')"
        district_result = zcql.execute_query(district_query)
        district_map = {row.get("District", {}).get("DistrictName"): row.get("District", {}).get("ROWID") for row in district_result}
        print(f"Districts found: {district_map}")
    except Exception as e:
        print(f"Error fetching districts: {e}")
        return {"status": "error", "message": str(e)}

    try:
        unit_query = "SELECT ROWID, UnitName FROM Unit"
        unit_result = zcql.execute_query(unit_query)
        unit_map = {row.get("Unit", {}).get("UnitName"): row.get("Unit", {}).get("ROWID") for row in unit_result}
        print(f"Units found: {len(unit_map)}")
    except Exception as e:
        print(f"Error fetching units: {e}")
        return {"status": "error", "message": str(e)}

    try:
        emp_query = "SELECT ROWID, KGID FROM Employee"
        emp_result = zcql.execute_query(emp_query)
        emp_map = {row.get("Employee", {}).get("KGID"): row.get("Employee", {}).get("ROWID") for row in emp_result}
        print(f"Employees found: {len(emp_map)}")
    except Exception as e:
        print(f"Error fetching employees: {e}")
        return {"status": "error", "message": str(e)}

    try:
        csh_query = "SELECT ROWID, CrimeHeadName FROM CrimeSubHead WHERE CrimeHeadName IN ('Murder', 'Vehicle Theft', 'Chain Snatching', 'Online Fraud', 'Robbery')"
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

    # Fetch ROWIDs for foreign key reference tables using name-based lookups
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
        crimehead_query = "SELECT ROWID, CrimeGroupName FROM CrimeHead WHERE CrimeGroupName IN ('Crimes Against Body', 'Crimes Against Property', 'Crimes Against Women', 'Cyber Crimes')"
        crimehead_result = zcql.execute_query(crimehead_query)
        crimehead_map = {row.get("CrimeHead", {}).get("CrimeGroupName"): row.get("CrimeHead", {}).get("ROWID") for row in crimehead_result}
        print(f"CrimeHead ROWIDs: {crimehead_map}")
    except Exception as e:
        print(f"Error fetching crime head: {e}")
        return {"status": "error", "message": str(e)}

    # Generate recent dates (within last 30 days from 2026-07-06)
    base_date = datetime(2026, 7, 6)
    case_dates = [
        (base_date - timedelta(days=5)).strftime("%Y-%m-%d"),  # 2026-07-01
        (base_date - timedelta(days=10)).strftime("%Y-%m-%d"), # 2026-06-26
        (base_date - timedelta(days=15)).strftime("%Y-%m-%d"), # 2026-06-21
        (base_date - timedelta(days=20)).strftime("%Y-%m-%d"), # 2026-06-16
        (base_date - timedelta(days=25)).strftime("%Y-%m-%d"), # 2026-06-11
    ]

    # Get max existing CaseMasterID to avoid conflicts
    try:
        case_query = "SELECT MAX(CaseMasterID) as max_id FROM CaseMaster"
        case_result = zcql.execute_query(case_query)
        max_id = case_result[0].get("CaseMaster", {}).get("MAX(CaseMasterID)", 0) if case_result else 0
        next_id = (int(max_id) if max_id else 0) + 1
    except:
        next_id = 100  # Fallback

    # CaseMaster records for 5 different districts
    case_rows = [
        {
            "CaseMasterID": next_id,
            "CrimeNo": f"10443010012026000{next_id}",
            "CaseNo": f"2026000{next_id}",
            "CrimeRegisteredDate": case_dates[0],
            "PolicePersonID": emp_map.get("KG2001101", 1),
            "PoliceStationID": unit_map.get("Cubbon Park Police Station", 1),
            "CaseCategoryID": casecat_map.get("FIR"),
            "GravityOffenceID": gravity_map.get("Heinous"),
            "CrimeMajorHeadID": crimehead_map.get("Crimes Against Body"),
            "CrimeMinorHeadID": csh_map.get("Murder"),
            "CaseStatusID": status_map.get("Under Investigation"),
            "CourtID": None,
            "IncidentFromDate": f"{case_dates[0]} 22:30:00",
            "IncidentToDate": f"{case_dates[0]} 23:00:00",
            "InfoReceivedPSDate": f"{case_dates[0]} 23:15:00",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "BriefFacts": "On 01-07-2026 at 22:30 hrs, a murder was reported near Cubbon Park area."
        },
        {
            "CaseMasterID": next_id + 1,
            "CrimeNo": f"10443010032026000{next_id + 1}",
            "CaseNo": f"2026000{next_id + 1}",
            "CrimeRegisteredDate": case_dates[1],
            "PolicePersonID": emp_map.get("KG2001103", 3),
            "PoliceStationID": unit_map.get("Mysuru City Police Station", 3),
            "CaseCategoryID": casecat_map.get("FIR"),
            "GravityOffenceID": gravity_map.get("Serious"),
            "CrimeMajorHeadID": crimehead_map.get("Crimes Against Property"),
            "CrimeMinorHeadID": csh_map.get("Vehicle Theft"),
            "CaseStatusID": status_map.get("Under Investigation"),
            "CourtID": None,
            "IncidentFromDate": f"{case_dates[1]} 14:00:00",
            "IncidentToDate": f"{case_dates[1]} 14:30:00",
            "InfoReceivedPSDate": f"{case_dates[1]} 15:00:00",
            "latitude": 12.2958,
            "longitude": 76.6394,
            "BriefFacts": "On 26-06-2026 at 14:00 hrs, a car theft was reported from Mysuru Palace Road."
        },
        {
            "CaseMasterID": next_id + 2,
            "CrimeNo": f"10443010042026000{next_id + 2}",
            "CaseNo": f"2026000{next_id + 2}",
            "CrimeRegisteredDate": case_dates[2],
            "PolicePersonID": emp_map.get("KG2001104", 4),
            "PoliceStationID": unit_map.get("Mangaluru Central Police Station", 4),
            "CaseCategoryID": casecat_map.get("FIR"),
            "GravityOffenceID": gravity_map.get("Serious"),
            "CrimeMajorHeadID": crimehead_map.get("Crimes Against Women"),
            "CrimeMinorHeadID": csh_map.get("Chain Snatching"),
            "CaseStatusID": status_map.get("Charge Sheeted"),
            "CourtID": None,
            "IncidentFromDate": f"{case_dates[2]} 10:15:00",
            "IncidentToDate": f"{case_dates[2]} 10:20:00",
            "InfoReceivedPSDate": f"{case_dates[2]} 10:45:00",
            "latitude": 12.8703,
            "longitude": 74.8428,
            "BriefFacts": "On 21-06-2026 at 10:15 hrs, chain snatching reported near Mangaluru market."
        },
        {
            "CaseMasterID": next_id + 3,
            "CrimeNo": f"10443010052026000{next_id + 3}",
            "CaseNo": f"2026000{next_id + 3}",
            "CrimeRegisteredDate": case_dates[3],
            "PolicePersonID": emp_map.get("KG2001106", 6),
            "PoliceStationID": unit_map.get("Indiranagar Police Station", 6),
            "CaseCategoryID": casecat_map.get("FIR"),
            "GravityOffenceID": gravity_map.get("Heinous"),
            "CrimeMajorHeadID": crimehead_map.get("Cyber Crimes"),
            "CrimeMinorHeadID": csh_map.get("Online Fraud"),
            "CaseStatusID": status_map.get("Under Investigation"),
            "CourtID": None,
            "IncidentFromDate": f"{case_dates[3]} 11:00:00",
            "IncidentToDate": f"{case_dates[3]} 12:30:00",
            "InfoReceivedPSDate": f"{case_dates[3]} 14:00:00",
            "latitude": 12.9789,
            "longitude": 77.5917,
            "BriefFacts": "On 16-06-2026, victim received fraudulent call posing as bank official."
        },
        {
            "CaseMasterID": next_id + 4,
            "CrimeNo": f"10443010072026000{next_id + 4}",
            "CaseNo": f"2026000{next_id + 4}",
            "CrimeRegisteredDate": case_dates[4],
            "PolicePersonID": emp_map.get("KG2001107", 7),
            "PoliceStationID": unit_map.get("Jayanagar Police Station", 5),
            "CaseCategoryID": casecat_map.get("FIR"),
            "GravityOffenceID": gravity_map.get("Serious"),
            "CrimeMajorHeadID": crimehead_map.get("Crimes Against Body"),
            "CrimeMinorHeadID": csh_map.get("Robbery"),
            "CaseStatusID": status_map.get("Under Investigation"),
            "CourtID": None,
            "IncidentFromDate": f"{case_dates[4]} 20:00:00",
            "IncidentToDate": f"{case_dates[4]} 20:15:00",
            "InfoReceivedPSDate": f"{case_dates[4]} 20:30:00",
            "latitude": 12.9352,
            "longitude": 77.6245,
            "BriefFacts": "On 11-06-2026 at 20:00 hrs, armed robbery reported at Jayanagar residence."
        },
    ]

    res, inserted = insert(ds, "CaseMaster", case_rows)
    results.append(res)

    print(f"\n========== SUMMARY ==========")
    print(f"Inserted {len(inserted)} recent CaseMaster records")
    print(f"Date range: {case_dates[-1]} to {case_dates[0]}")
    print(f"============================\n")

    return {
        "status": "ok",
        "inserted": len(inserted),
        "date_range": {"from": case_dates[-1], "to": case_dates[0]},
        "results": results
    }
