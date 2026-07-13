"""
PRISM — Seed Populate Network Data (Interconnected Criminal Networks & 1-Year Range)
================================================================================
This script seeds a rich network of interconnected cases and accused to show:
  1. Multi-gang structures (Gang Alpha, Gang Beta, Gang Gamma)
  2. Bridge nodes connecting different gangs (e.g., Rajeev Hegde)
  3. Real Karnataka districts and police stations
  4. Spread across 1 full year to simulate chronological data collection
  5. Correct mapping of CaseStatus (Under Investigation -> Absconding, Charge Sheeted -> Arrested)

FK RULES: All FK columns require the ROWID of the parent row, NOT a hardcoded integer.
  Always resolve ROWIDs from the database before using them in child inserts.
"""

from fastapi import Request, APIRouter
import zcatalyst_sdk
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/db", tags=["populate_network"])


def get_datastore(req: Request):
    catalyst_app = zcatalyst_sdk.initialize(req=req)
    return catalyst_app.datastore()


def get_zcql(req: Request):
    catalyst_app = zcatalyst_sdk.initialize(req=req)
    return catalyst_app.zcql()


def fetch_first_rowid(zcql, table_name: str) -> int | None:
    """Fetch the ROWID of the first row in a table."""
    try:
        query = f"SELECT ROWID FROM {table_name} LIMIT 1"
        rows = zcql.execute_query(query)
        if isinstance(rows, list) and rows:
            nested = rows[0].get(table_name, rows[0])
            rid = nested.get("ROWID")
            return int(rid) if rid else None
    except Exception as e:
        print(f"[Populate] Could not fetch first row from {table_name}: {e}")
    return None


def fetch_existing(zcql, table_name: str, name_col: str) -> dict[str, int]:
    """Fetch existing records and return {name: rowid} map."""
    try:
        query = f"SELECT ROWID, {name_col} FROM {table_name} LIMIT 300"
        rows = zcql.execute_query(query)
        result = {}
        for r in (rows if isinstance(rows, list) else []):
            nested = r.get(table_name, r)
            rowid = nested.get("ROWID")
            name = nested.get(name_col)
            if rowid and name:
                result[str(name)] = int(rowid)
        return result
    except Exception as e:
        print(f"[Populate] Could not fetch existing from {table_name}: {e}")
        return {}


def insert_batch(datastore, table_name: str, rows: list[dict]) -> list[dict]:
    """Insert a list of rows and return them with their assigned ROWIDs."""
    if not rows:
        return []
    try:
        table = datastore.table(table_name)
        response = table.insert_rows(rows)
        return response if isinstance(response, list) else []
    except Exception as e:
        print(f"[Populate Error] {table_name} batch insert failed: {e}")
        return []


def resolve_or_insert(zcql, ds, table_name: str, name_col: str, name_value: str, insert_row: dict) -> int | None:
    """Resolve ROWID by name, or insert if not found. Returns the ROWID."""
    existing = fetch_existing(zcql, table_name, name_col)
    rid = existing.get(name_value)
    if rid:
        return rid
    inserted = insert_batch(ds, table_name, [insert_row])
    if inserted:
        return int(inserted[0]["ROWID"])
    return None


@router.get("/test/populate_network_data")
def populate_network_data(request: Request):
    ds = get_datastore(request)
    zcql = get_zcql(request)
    logs = []

    logs.append("Starting network-explorer data population...")

    # ─────────────────────────────────────────────────────────────────
    # 1. Resolve State (Karnataka) - already exists from initial seed
    # ─────────────────────────────────────────────────────────────────
    existing_states = fetch_existing(zcql, "State", "StateName")
    karnataka_rowid = existing_states.get("Karnataka")
    if not karnataka_rowid:
        inserted = insert_batch(ds, "State", [
            {"StateID": 101, "StateName": "Karnataka", "NationalityID": 1, "Active": True}
        ])
        if inserted:
            karnataka_rowid = int(inserted[0]["ROWID"])
            logs.append(f"Inserted State: Karnataka (ROWID: {karnataka_rowid})")
        else:
            logs.append("Failed to insert/resolve State: Karnataka")
            return {"status": "error", "logs": logs}
    else:
        logs.append(f"Resolved State: Karnataka (ROWID: {karnataka_rowid})")

    # ─────────────────────────────────────────────────────────────────
    # 2. Resolve Districts
    # ─────────────────────────────────────────────────────────────────
    district_names = ["Bengaluru North", "Bengaluru South", "Mysuru Central", "Belagavi", "Mangalore", "Dharwad"]
    existing_districts = fetch_existing(zcql, "District", "DistrictName")
    district_map = {}
    districts_to_insert = []

    for idx, dname in enumerate(district_names):
        rid = existing_districts.get(dname)
        if rid:
            district_map[dname] = rid
        else:
            districts_to_insert.append({
                "DistrictID": 201 + idx,
                "DistrictName": dname,
                "StateID": karnataka_rowid,
                "Active": True
            })

    if districts_to_insert:
        inserted = insert_batch(ds, "District", districts_to_insert)
        for r in inserted:
            dname = r.get("DistrictName")
            rid = int(r.get("ROWID"))
            district_map[dname] = rid

    if not district_map:
        logs.append("No districts resolved — cannot continue")
        return {"status": "error", "logs": logs}

    logs.append(f"Resolved Districts: {list(district_map.keys())}")

    # ─────────────────────────────────────────────────────────────────
    # 3a. Resolve UnitType (TypeID FK → UnitType.ROWID)
    # ─────────────────────────────────────────────────────────────────
    existing_unit_types = fetch_existing(zcql, "UnitType", "UnitTypeName")
    unit_type_rowid = existing_unit_types.get("Police Station")
    if not unit_type_rowid:
        inserted = insert_batch(ds, "UnitType", [
            {"UnitTypeID": 401, "UnitTypeName": "Police Station", "CityDistState": "City", "Hierarchy": 3, "Active": True}
        ])
        if inserted:
            unit_type_rowid = int(inserted[0]["ROWID"])
            logs.append(f"Inserted UnitType: Police Station (ROWID: {unit_type_rowid})")
        else:
            logs.append("Failed to insert/resolve UnitType")
            return {"status": "error", "logs": logs}
    else:
        logs.append(f"Resolved UnitType: Police Station (ROWID: {unit_type_rowid})")

    # ─────────────────────────────────────────────────────────────────
    # 3b. Resolve Police Stations (Units)
    # ─────────────────────────────────────────────────────────────────
    unit_map = {}
    existing_units = fetch_existing(zcql, "Unit", "UnitName")
    units_to_insert = []

    for idx, (dname, drid) in enumerate(district_map.items()):
        uname = f"{dname} PS"
        rid = existing_units.get(uname)
        if rid:
            unit_map[uname] = rid
        else:
            units_to_insert.append({
                "UnitID": 301 + idx,
                "UnitName": uname,
                "TypeID": unit_type_rowid,    # ← ROWID of UnitType, not hardcoded 1
                "DistrictID": drid,
                "StateID": karnataka_rowid,
                "Active": True
            })

    if units_to_insert:
        inserted = insert_batch(ds, "Unit", units_to_insert)
        for r in inserted:
            uname = r.get("UnitName")
            rid = int(r.get("ROWID"))
            unit_map[uname] = rid

    if not unit_map:
        logs.append("No units resolved or inserted — cannot generate cases without a police station")
        return {"status": "error", "logs": logs}

    logs.append(f"Resolved Units: {list(unit_map.keys())}")

    # ─────────────────────────────────────────────────────────────────
    # 4. Resolve CrimeHead and CrimeSubHead
    # ─────────────────────────────────────────────────────────────────
    existing_crime_heads = fetch_existing(zcql, "CrimeHead", "CrimeGroupName")
    body_head_rid = existing_crime_heads.get("Crimes Against Body")
    prop_head_rid = existing_crime_heads.get("Crimes Against Property")

    heads_to_insert = []
    if not body_head_rid:
        heads_to_insert.append({"CrimeHeadID": 401, "CrimeGroupName": "Crimes Against Body", "Active": True})
    if not prop_head_rid:
        heads_to_insert.append({"CrimeHeadID": 402, "CrimeGroupName": "Crimes Against Property", "Active": True})

    if heads_to_insert:
        inserted = insert_batch(ds, "CrimeHead", heads_to_insert)
        for r in inserted:
            gname = r.get("CrimeGroupName")
            rid = int(r.get("ROWID"))
            if gname == "Crimes Against Body":
                body_head_rid = rid
            elif gname == "Crimes Against Property":
                prop_head_rid = rid

    if not body_head_rid or not prop_head_rid:
        logs.append("Failed to resolve CrimeHead ROWIDs")
        return {"status": "error", "logs": logs}

    existing_subheads = fetch_existing(zcql, "CrimeSubHead", "CrimeHeadName")
    subhead_map = {}
    subheads_needed = {
        "Murder": body_head_rid,
        "Robbery": prop_head_rid,
        "Chain Snatching": prop_head_rid,
        "Vehicle Theft": prop_head_rid
    }
    subheads_to_insert = []

    for idx, (shname, parent_rid) in enumerate(subheads_needed.items()):
        rid = existing_subheads.get(shname)
        if rid:
            subhead_map[shname] = rid
        else:
            subheads_to_insert.append({
                "CrimeSubHeadID": 501 + idx,
                "CrimeHeadID": parent_rid,
                "CrimeHeadName": shname,
                "SeqID": idx + 1
            })

    if subheads_to_insert:
        inserted = insert_batch(ds, "CrimeSubHead", subheads_to_insert)
        for r in inserted:
            shname = r.get("CrimeHeadName")
            rid = int(r.get("ROWID"))
            subhead_map[shname] = rid

    logs.append(f"Resolved CrimeSubHeads: {list(subhead_map.keys())}")

    # ─────────────────────────────────────────────────────────────────
    # 5. Resolve CaseStatusMaster
    # ─────────────────────────────────────────────────────────────────
    existing_statuses = fetch_existing(zcql, "CaseStatusMaster", "CaseStatusName")
    status_map = {}
    statuses_to_insert = []

    for idx, sname in enumerate(["Under Investigation", "Charge Sheeted"]):
        rid = existing_statuses.get(sname)
        if rid:
            status_map[sname] = rid
        else:
            statuses_to_insert.append({"CaseStatusID": 601 + idx, "CaseStatusName": sname})

    if statuses_to_insert:
        inserted = insert_batch(ds, "CaseStatusMaster", statuses_to_insert)
        for r in inserted:
            sname = r.get("CaseStatusName")
            rid = int(r.get("ROWID"))
            status_map[sname] = rid

    logs.append(f"Resolved CaseStatuses: {list(status_map.keys())}")

    # ─────────────────────────────────────────────────────────────────
    # 6. Resolve CaseCategory (FK → CaseCategory.ROWID)
    # ─────────────────────────────────────────────────────────────────
    existing_categories = fetch_existing(zcql, "CaseCategory", "LookupValue")
    case_category_rowid = existing_categories.get("FIR")
    if not case_category_rowid:
        inserted = insert_batch(ds, "CaseCategory", [{"CaseCategoryID": 701, "LookupValue": "FIR"}])
        if inserted:
            case_category_rowid = int(inserted[0]["ROWID"])
        else:
            logs.append("Failed to resolve CaseCategory")
            return {"status": "error", "logs": logs}
    logs.append(f"Resolved CaseCategory: FIR (ROWID: {case_category_rowid})")

    # ─────────────────────────────────────────────────────────────────
    # 7. Resolve GravityOffence (FK → GravityOffence.ROWID)
    #    Column name is LookupValue (same pattern as CaseCategory)
    # ─────────────────────────────────────────────────────────────────
    existing_gravity = fetch_existing(zcql, "GravityOffence", "LookupValue")
    gravity_rowid = existing_gravity.get("Serious")
    if not gravity_rowid and existing_gravity:
        gravity_rowid = list(existing_gravity.values())[0]  # Fall back to any existing one
    if not gravity_rowid:
        inserted = insert_batch(ds, "GravityOffence", [{"GravityOffenceID": 801, "LookupValue": "Serious"}])
        if inserted:
            gravity_rowid = int(inserted[0]["ROWID"])
        else:
            logs.append("Failed to resolve GravityOffence — will omit from CaseMaster inserts")
    logs.append(f"Resolved GravityOffence ROWID: {gravity_rowid}")

    # ─────────────────────────────────────────────────────────────────
    # 8. Resolve Employee (PolicePersonID FK → Employee.ROWID)
    # ─────────────────────────────────────────────────────────────────
    employee_rowid = fetch_first_rowid(zcql, "Employee")
    if not employee_rowid:
        # Need Rank and Designation first for Employee FK
        rank_rowid = fetch_first_rowid(zcql, "Rank")
        if not rank_rowid:
            inserted = insert_batch(ds, "Rank", [{"RankID": 901, "RankName": "Inspector", "Hierarchy": 2, "Active": True}])
            rank_rowid = int(inserted[0]["ROWID"]) if inserted else None

        desig_rowid = fetch_first_rowid(zcql, "Designation")
        if not desig_rowid:
            inserted = insert_batch(ds, "Designation", [{"DesignationID": 902, "DesignationName": "Station House Officer", "Active": True, "SortOrder": 1}])
            desig_rowid = int(inserted[0]["ROWID"]) if inserted else None

        first_district = list(district_map.values())[0]
        first_unit = list(unit_map.values())[0]

        if rank_rowid and desig_rowid:
            inserted = insert_batch(ds, "Employee", [{
                "EmployeeID": 1001,
                "KGID": "KG9001001",
                "FirstName": "Rajesh Kumar",
                "EmployeeDOB": "1985-03-15",
                "GenderID": 1,
                "BloodGroupID": 1,
                "PhysicallyChallenged": False,
                "AppointmentDate": "2008-06-01",
                "DistrictID": first_district,
                "UnitID": first_unit,
                "RankID": rank_rowid,
                "DesignationID": desig_rowid
            }])
            employee_rowid = int(inserted[0]["ROWID"]) if inserted else None

    logs.append(f"Resolved Employee (PolicePersonID) ROWID: {employee_rowid}")

    # ─────────────────────────────────────────────────────────────────
    # 9. Resolve Court (CourtID FK → Court.ROWID) — optional, can be None
    # ─────────────────────────────────────────────────────────────────
    court_rowid = fetch_first_rowid(zcql, "Court")
    if not court_rowid:
        inserted = insert_batch(ds, "Court", [{"CourtID": 1001, "CourtName": "City Civil Court Bengaluru", "CourtTypeID": 1, "DistrictID": list(district_map.values())[0]}])
        court_rowid = int(inserted[0]["ROWID"]) if inserted else None
    logs.append(f"Resolved Court ROWID: {court_rowid}")

    # ─────────────────────────────────────────────────────────────────
    # 10. Gang definitions
    # ─────────────────────────────────────────────────────────────────
    gang_alpha  = ["Syed Imran", "Abdul Rauf Khan", "Vikram Gowda", "Ravi Kumar B", "Venkatesh Prasad"]
    gang_beta   = ["Suresh Kumar", "Mahesh Gowda", "Ramesh Nayak", "Anand Murthy", "Somesh Shettar"]
    gang_gamma  = ["Kiran Hegde", "Vijay Mallya", "Nirav Modi", "Mehuli Ghosh", "Sanjay Dutt"]
    bridge_ab   = "Rajeev Hegde"
    bridge_bg   = "Praveen Kumar"
    bridge_ag   = "Shekhar Sen"
    lone_wolves = ["Pradeep Rao", "Nithin Dev", "Sunil Shetty"]

    # ─────────────────────────────────────────────────────────────────
    # 11. Build 40 cases spread over past 365 days
    # ─────────────────────────────────────────────────────────────────
    now = datetime.utcnow()
    total_cases = 40
    dates = sorted([
        now - timedelta(days=int((365 / total_cases) * i) + random.randint(-4, 4))
        for i in range(total_cases)
    ])

    unit_names   = list(unit_map.keys())
    subhead_names = list(subhead_map.keys())

    case_master_inserts   = []
    case_accused_plan     = []  # List of (case_id, accused_names, status_name)

    for i in range(total_cases):
        # track case_id as index; store crime_no for mapping back after insert
        crime_no = f"NET{now.strftime('%Y%m%d%H%M%S')}{i:03d}"
        case_no  = f"C-NET-{i:04d}"
        incident_date   = dates[i].strftime("%Y-%m-%d %H:%M:%S")
        reg_date        = (dates[i] + timedelta(hours=random.randint(2, 24))).strftime("%Y-%m-%d %H:%M:%S")
        unit_name       = random.choice(unit_names)
        unit_rid        = unit_map[unit_name]
        crime_sh_name   = random.choice(subhead_names)
        subhead_rid     = subhead_map[crime_sh_name]
        is_body_crime   = crime_sh_name == "Murder"
        major_head_rid  = body_head_rid if is_body_crime else prop_head_rid
        status_name     = "Charge Sheeted" if (i % 5 < 3) else "Under Investigation"
        status_rid      = status_map.get(status_name)

        row = {
            # No CaseMasterID — let Catalyst auto-assign to avoid DUPLICATE_VALUE on re-runs
            "CrimeNo":             crime_no,
            "CaseNo":              case_no,
            "CrimeRegisteredDate": reg_date,
            "IncidentFromDate":    incident_date,
            "PoliceStationID":     unit_rid,
            "CaseCategoryID":      case_category_rowid,
            "CrimeMajorHeadID":    major_head_rid,
            "CrimeMinorHeadID":    subhead_rid,
            "BriefFacts":          f"Seeded incident for {crime_sh_name} in {unit_name}.",
            "latitude":            12.9 + random.uniform(-0.2, 0.2),
            "longitude":           77.5 + random.uniform(-0.2, 0.2),
        }
        # Only add FK columns if we successfully resolved the ROWIDs
        if employee_rowid:
            row["PolicePersonID"] = employee_rowid
        if gravity_rowid:
            row["GravityOffenceID"] = gravity_rowid
        if status_rid:
            row["CaseStatusID"] = status_rid
        if court_rowid and (i % 5 < 3):  # Only charge-sheeted cases get a court
            row["CourtID"] = court_rowid

        case_master_inserts.append(row)

        # Assign accused based on case index
        if i < 12:
            names = random.sample(gang_alpha, min(random.choice([2, 3, 4]), len(gang_alpha)))
        elif i < 24:
            names = random.sample(gang_beta, min(random.choice([2, 3, 4]), len(gang_beta)))
        elif i < 33:
            names = random.sample(gang_gamma, min(random.choice([2, 3]), len(gang_gamma)))
        elif i in (33, 34):
            names = [bridge_ab, random.choice(gang_alpha), random.choice(gang_beta)]
        elif i in (35, 36):
            names = [bridge_bg, random.choice(gang_beta), random.choice(gang_gamma)]
        elif i in (37, 38):
            names = [bridge_ag, random.choice(gang_alpha), random.choice(gang_gamma)]
        else:
            names = random.sample(lone_wolves, min(random.choice([1, 2]), len(lone_wolves)))

        case_accused_plan.append((crime_no, names, status_name, incident_date))

    # Insert CaseMaster in batches of 20 (ZCQL insert limit safety)
    inserted_cases = []
    for batch_start in range(0, len(case_master_inserts), 20):
        batch = case_master_inserts[batch_start:batch_start + 20]
        result = insert_batch(ds, "CaseMaster", batch)
        inserted_cases.extend(result)

    logs.append(f"Inserted {len(inserted_cases)} CaseMaster records")

    # Build CrimeNo → ROWID map (CrimeNo is unique per insert run, safe to use as key)
    case_rowid_map = {r.get("CrimeNo"): int(r.get("ROWID")) for r in inserted_cases}

    # ─────────────────────────────────────────────────────────────────
    # 12. Insert Accused rows
    # ─────────────────────────────────────────────────────────────────
    accused_inserts  = []
    accused_meta     = []   # (case_id, consistent_master_id, name, status_name, incident_date)

    for crime_no_key, acc_names, status_name, incident_date in case_accused_plan:
        case_rowid = case_rowid_map.get(crime_no_key)
        if not case_rowid:
            continue
        for idx, name in enumerate(acc_names):
            accused_inserts.append({
                # No AccusedMasterID — let Catalyst auto-assign to avoid duplicates on re-run
                "CaseMasterID":    case_rowid,
                "AccusedName":     name,
                "AgeYear":         random.randint(22, 52),
                "GenderID":        random.choice([1, 1, 1, 2]),
                "PersonID":        f"A{idx + 1}"
            })
            accused_meta.append((crime_no_key, case_rowid, name, status_name, incident_date))

    inserted_accused = []
    for batch_start in range(0, len(accused_inserts), 20):
        batch = accused_inserts[batch_start:batch_start + 20]
        result = insert_batch(ds, "Accused", batch)
        inserted_accused.extend(result)

    logs.append(f"Inserted {len(inserted_accused)} Accused records")

    # Build (case_rowid, accused_name) → Accused ROWID
    accused_rowid_map = {}
    for r in inserted_accused:
        cm_rowid  = int(r.get("CaseMasterID"))
        acc_name  = r.get("AccusedName")
        rid       = int(r.get("ROWID"))
        accused_rowid_map[(cm_rowid, acc_name)] = rid

    # ─────────────────────────────────────────────────────────────────
    # 13. Insert ArrestSurrender for Charge Sheeted cases
    # ─────────────────────────────────────────────────────────────────
    arrest_inserts  = []
    arrest_counter  = 9000

    for crime_no_key, case_rowid, name, status_name, incident_date in accused_meta:
        if status_name != "Charge Sheeted":
            continue
        accused_rowid = accused_rowid_map.get((case_rowid, name))
        if not accused_rowid:
            continue

        inc_dt      = datetime.strptime(incident_date, "%Y-%m-%d %H:%M:%S")
        arrest_date = (inc_dt + timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d")
        arrest_counter += 1

        row = {
            # No ArrestSurrenderID — let Catalyst auto-assign to avoid duplicates on re-run
            "CaseMasterID":              case_rowid,
            "AccusedMasterID":           accused_rowid,
            "ArrestSurrenderDate":       arrest_date,
            "ArrestSurrenderStateId":    karnataka_rowid,
            "ArrestSurrenderDistrictId": random.choice(list(district_map.values())),
            "PoliceStationID":           random.choice(list(unit_map.values())),
            "IsAccused":                 True
        }
        if employee_rowid:
            row["IOID"] = employee_rowid
        if court_rowid:
            row["CourtID"] = court_rowid

        arrest_inserts.append(row)

    inserted_arrests = []
    for batch_start in range(0, len(arrest_inserts), 20):
        batch = arrest_inserts[batch_start:batch_start + 20]
        result = insert_batch(ds, "ArrestSurrender", batch)
        inserted_arrests.extend(result)

    logs.append(f"Inserted {len(inserted_arrests)} ArrestSurrender records")
    logs.append("Network-explorer data population complete!")

    return {
        "status": "success",
        "summary": {
            "cases":   len(inserted_cases),
            "accused": len(inserted_accused),
            "arrests": len(inserted_arrests),
        },
        "logs": logs
    }
