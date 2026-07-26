"""
PRISM — Insert New Data Route (20 Rows Per Table)
=================================================
Inserts exactly 20 rows in each of the following tables:
  - dashboard_stats
  - crime_alerts
  - risk_scores
  - conversations
  - audit_logs
  - CaseMaster

Key rules:
  - All date/datetime columns are within 7 days of current UTC time.
  - Foreign keys in CaseMaster are resolved dynamically from existing master rows.
  - Uses direct ZCQL V2 INSERT statements executed via zcql.execute_query().
  - Primary key IDs are computed from MAX(id_col) + 1 to avoid conflicts.
"""

from fastapi import Request, APIRouter, Depends
from datetime import datetime, timedelta
import json
from typing import Optional, List
from core.database import get_zcql

router = APIRouter(prefix="/db", tags=["new-data-insertion"])


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _to_int(val) -> Optional[int]:
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _value(row: dict, table: str, column: str, flat_key: str):
    """Extract values from nested Catalyst ZCQL query results."""
    nested = row.get(table)
    if isinstance(nested, dict) and column in nested:
        return nested[column]
    if flat_key in row:
        return row[flat_key]
    qualified = f"{table}.{column}"
    if qualified in row:
        return row[qualified]
    prefixed = f"{table}_{column}"
    if prefixed in row:
        return row[prefixed]
    return row.get(column)


def _get_rids(zcql, table: str, cols: List[str] = None, limit: int = 20) -> List[dict]:
    """Fetch rows from a table and return them as plain dicts."""
    cols_str = ", ".join(cols) if cols else "ROWID"
    try:
        rows = zcql.execute_query(f"SELECT {cols_str} FROM {table} LIMIT {limit}") or []
        return rows
    except Exception:
        return []


def _get_max_id(zcql, table: str, id_col: str, fallback: int = 300) -> int:
    """Return MAX(id_col) + 1 for the given table to avoid primary key conflicts."""
    try:
        res = zcql.execute_query(f"SELECT MAX({id_col}) FROM {table}") or []
        if not res:
            return fallback
        row = res[0]
        max_val = None
        for k, v in row.items():
            if isinstance(v, dict):
                for ik, iv in v.items():
                    if "MAX" in ik:
                        max_val = _to_int(iv)
                        break
            elif "MAX" in k:
                max_val = _to_int(v)
                break
        return (max_val or 0) + 1
    except Exception:
        return fallback


# ──────────────────────────────────────────────────────────────────────────────
# Route
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/tests/insert-new-data")
def insert_new_data(request: Request, zcql=Depends(get_zcql)):
    results = {"status": "ok", "inserted": {}, "errors": []}
    now = datetime.utcnow()

    # ── 1. Resolve foreign key ROWIDs from master tables ────────────────────
    def rids(rows, table, col="ROWID"):
        return [r for r in [_to_int(_value(row, table, col, col)) for row in rows] if r]

    dist_rows   = _get_rids(zcql, "District", ["ROWID"])
    emp_rows    = _get_rids(zcql, "Employee", ["ROWID"])
    unit_rows   = _get_rids(zcql, "Unit", ["ROWID"])
    cat_rows    = _get_rids(zcql, "CaseCategory", ["ROWID"])
    grav_rows   = _get_rids(zcql, "GravityOffence", ["ROWID"])
    csh_rows    = _get_rids(zcql, "CrimeSubHead", ["ROWID", "CrimeHeadID"])
    status_rows = _get_rids(zcql, "CaseStatusMaster", ["ROWID"])
    court_rows  = _get_rids(zcql, "Court", ["ROWID"])

    district_rids = rids(dist_rows, "District")
    emp_rids      = rids(emp_rows, "Employee")
    station_rids  = rids(unit_rows, "Unit")
    casecat_rids  = rids(cat_rows, "CaseCategory")
    gravity_rids  = rids(grav_rows, "GravityOffence")
    csh_rids      = rids(csh_rows, "CrimeSubHead")
    ch_rids       = rids(csh_rows, "CrimeSubHead", "CrimeHeadID")
    status_rids   = rids(status_rows, "CaseStatusMaster")
    court_rids    = rids(court_rows, "Court")

    def pick(lst, i):
        return lst[i % len(lst)] if lst else "NULL"

    # ── 2. Get starting IDs ─────────────────────────────────────────────────
    base_stat    = _get_max_id(zcql, "dashboard_stats",   "stat_id",           fallback=500)
    base_alert   = _get_max_id(zcql, "crime_alerts",      "alert_id",          fallback=500)
    base_risk    = _get_max_id(zcql, "risk_scores",       "risk_score_id",     fallback=500)
    base_conv    = _get_max_id(zcql, "conversations",     "conversation_id",   fallback=500)
    base_log     = _get_max_id(zcql, "audit_logs",        "log_id",            fallback=500)
    base_case    = _get_max_id(zcql, "CaseMaster",        "CaseMasterID",      fallback=500)

    # ── 3. Data pools ───────────────────────────────────────────────────────
    # Kept deliberately short to fit within VarChar column max-length.
    # (insert_derived_data.py bypasses this via DataStore SDK; ZCQL INSERT enforces it.)
    DIST_JSONS = [
        '[{"d":1,"n":"Bengaluru","firs":210}]',
        '[{"d":2,"n":"Mysuru","firs":120}]',
        '[{"d":3,"n":"Mangaluru","firs":75}]',
        '[{"d":4,"n":"Belagavi","firs":95}]',
        '[{"d":5,"n":"Dharwad","firs":62}]',
        '[{"d":6,"n":"Udupi","firs":48}]',
        '[{"d":7,"n":"Kalaburagi","firs":83}]',
    ]
    TREND_JSONS = [
        '[{"cat":"Body","wk":[14,16,9,12],"pct":12.4,"t":"up"}]',
        '[{"cat":"Property","wk":[22,19,25,21],"pct":-3.1,"t":"dn"}]',
        '[{"cat":"Women","wk":[8,10,7,9],"pct":5.2,"t":"up"}]',
        '[{"cat":"Cyber","wk":[5,7,4,6],"pct":8.0,"t":"up"}]',
        '[{"cat":"Narcotics","wk":[3,4,3,5],"pct":2.1,"t":"up"}]',
        '[{"cat":"Traffic","wk":[11,12,10,13],"pct":-1.5,"t":"dn"}]',
        '[{"cat":"Arms","wk":[2,3,2,4],"pct":10.0,"t":"up"}]',
    ]

    ALERT_MSGS = [
        "Armed robbery spike in Bengaluru East",
        "Vehicle theft increase in Mysuru North",
        "Cyber fraud surge in Hubballi",
        "Chain snatching rise in Mangaluru South",
        "Drug trafficking alert near Belagavi border",
        "Grievous hurt cases spike in Udupi town",
        "Kidnapping trend reported in Kalaburagi rural",
        "Dacoity attempt foiled in Dharwad",
        "Murder rate rise in Hassan district",
        "Online fraud spike targeting senior citizens in Bengaluru",
        "Extortion calls spike in Vijayawada",
        "Domestic violence surge in Bengaluru North",
        "Arms smuggling alert near Karnataka-Goa border",
        "Stalking complaints rise in Koramangala area",
        "Drunken driving spike near Mysuru highway",
        "Hacking incidents targeting IT companies in Whitefield",
        "Money laundering alert — multiple shell firms detected",
        "Rioting incidents near communal hotspot in Kalaburagi",
        "Wildlife poaching alert in Bandipur reserve area",
        "Tax evasion ring busted in Mangaluru port area",
    ]

    ACCUSED_NAMES = [
        "Karan Singh", "Vijay Gowda", "Arjun Prasad", "Sunil Naik",
        "Rajesh Gowda", "Abdul Rahaman", "Srinivas Reddy", "Mohammed Ashiq",
        "Deepak Rao", "Praveen Kumar", "Ravi Nayak", "Harish Kamath",
        "Jagdish Shetty", "Vinod Hegde", "Santosh Bhat", "Murugan S",
        "Lakshman Rao", "Girish Patil", "Ramakrishna T", "Suresh Joshi",
    ]
    MO_TAGS = [
        "Repeat burglary offender", "Vehicle snatcher", "Assault prime accused",
        "Drug peddler suspect", "Illegal weapons possessor", "Cyber crime organizer",
        "Kidnapping specialist", "Property fraud perpetrator", "Serial chain snatcher",
        "Money laundering intermediary", "Domestic violence repeat offender",
        "Dacoity gang leader", "Arms smuggling suspect", "Stalking accused",
        "Drunk driving repeat offender", "Ransomware deployer", "Wildlife poacher",
        "Tax evasion mastermind", "Extortion ring coordinator", "Online fraud organizer",
    ]

    USER_QUERIES = [
        "Show me crime trends for Bengaluru last 7 days",
        "List all absconding offenders in Mysuru district",
        "What are the top crime hotspots right now?",
        "Show high-risk offenders in Belagavi",
        "Find all murder cases filed this week",
        "Show vehicle theft trend for July 2026",
        "List all cyber fraud incidents reported recently",
        "Find kidnapping cases in Kalaburagi",
        "Show district-wise crime breakdown",
        "List assault cases filed in Bengaluru this month",
        "Find domestic violence complaints in Dharwad",
        "Show drug trafficking alerts near Karnataka border",
        "Which police stations have most FIRs this week?",
        "Show robbery trend for last 7 days",
        "List all gang clusters in the network graph",
        "Find cases involving Chain Snatching this week",
        "Show crime heatmap for Mangaluru",
        "List accused persons with risk score above 80",
        "Show pending trial cases in Bengaluru courts",
        "Find all dacoity cases from this month",
    ]
    ASST_REPLIES = [
        "Here are the crime trends for Bengaluru over the past 7 days.",
        "Found 8 absconding offenders registered in Mysuru district.",
        "The top 5 hotspots are Koramangala, Indiranagar, Whitefield, Jayanagar, MG Road.",
        "Identified 4 high-risk offenders in Belagavi district.",
        "3 murder FIRs were filed this week across Karnataka.",
        "Vehicle theft has increased 18% compared to the previous week.",
        "12 cyber fraud cases filed this week. Most involve OTP-based fraud.",
        "2 kidnapping cases found in Kalaburagi district.",
        "District-wise breakdown fetched from 6 active districts.",
        "Found 9 assault FIRs in Bengaluru this month.",
        "6 domestic violence complaints registered in Dharwad this week.",
        "3 drug trafficking alerts active near the Karnataka–Goa border.",
        "Cubbon Park PS leads with 14 FIRs registered this week.",
        "Robbery FIRs up 22% compared to the same period last week.",
        "Identified 3 active gang clusters in the network graph.",
        "5 chain snatching cases found. Most occurred in morning hours.",
        "Crime heatmap generated for Mangaluru covering 4 hotspot zones.",
        "Found 7 accused persons with risk score above 80.",
        "15 cases currently in pending trial status across Bengaluru courts.",
        "Found 2 dacoity cases registered this month in Dharwad and Kalaburagi.",
    ]

    ENDPOINTS = [
        "/api/network/graph", "/api/analytics/trends", "/api/chat/query",
        "/api/dashboard/stats", "/api/analytics/hotspots", "/api/network/profile",
        "/api/analytics/festival-calendar", "/api/network/search", "/api/dashboard/alerts",
        "/api/cases/list", "/api/offenders/risk-scores", "/api/analytics/crime-map",
        "/api/network/crime-types", "/api/reports/generate", "/api/users/profile",
        "/api/dashboard/district-crimes", "/api/analytics/emerging-clusters",
        "/api/alerts/acknowledge", "/api/network/clusters", "/api/cases/chargesheet",
    ]
    ROLES = ["investigator", "analyst", "supervisor", "admin"]
    USER_IDS = ["user_101", "user_202", "user_303", "user_404", "user_505"]

    BRIEF_FACTS = [
        "Theft of gold chain reported by pedestrian near bus stand.",
        "Burglary at residential house — jewelry and cash stolen.",
        "Vehicle theft from shopping mall parking lot.",
        "Local vendor found murdered near market area.",
        "Kidnapping of school child for ransom by unknown persons.",
        "Drunken driving incident causing road accident and minor injuries.",
        "Armed robbery at jewellery shop by masked persons.",
        "Cyber fraud — victim defrauded of Rs 1.5 lakh via OTP sharing.",
        "Drug possession case — suspect held with contraband substances.",
        "Domestic violence complaint lodged by victim against spouse.",
        "Extortion call received by shopkeeper from unknown number.",
        "Chain snatching by two-wheeler riding accused near school.",
        "Dacoity at petrol bunk — four masked accused fled with cash.",
        "Assault with iron rod on complainant outside a bar.",
        "Arms recovery — illegal country-made pistol found on accused.",
        "Hacking of corporate email account — ransom demanded.",
        "Wildlife poaching — accused caught with animal skins in vehicle.",
        "Money laundering case — multiple suspicious transactions traced.",
        "Rioting and stone pelting near disputed property in town.",
        "Stalking complaint by working woman — accused arrested.",
    ]

    LATS = [
        12.9716, 12.2958, 12.8698, 15.8607, 12.9352, 13.3408, 15.4589,
        13.0827, 14.4673, 12.3012, 17.3400, 16.5062, 12.8231, 14.1625,
        15.3647, 13.6288, 12.9165, 12.3547, 14.8201, 13.2468,
    ]
    LONS = [
        77.5946, 76.6394, 77.6408, 74.5069, 77.6245, 74.7421, 75.0078,
        80.2707, 75.9198, 76.6288, 76.8400, 80.6480, 77.4952, 75.3200,
        75.1240, 74.8347, 77.6801, 77.5612, 74.3892, 77.8120,
    ]

    # ── 4. Build query lists ─────────────────────────────────────────────────
    tables_queries = {}

    # A. dashboard_stats (20 rows)
    qs = []
    for i in range(20):
        dt = (now - timedelta(days=i % 7, hours=(i % 12) + 1)).strftime("%Y-%m-%d %H:%M:%S")
        dist_j  = DIST_JSONS[i % len(DIST_JSONS)]
        trend_j = TREND_JSONS[i % len(TREND_JSONS)]
        qs.append(f"""
            INSERT INTO dashboard_stats (
                stat_id, computed_at, total_firs, active_cases,
                high_risk_offender_count, active_alert_count,
                district_crime_json, trend_sparklines_json
            ) VALUES (
                {base_stat + i}, '{dt}', {380 + i * 6}, {95 + i * 2},
                {22 + i}, {4 + (i % 8)},
                '{dist_j}', '{trend_j}'
            )
        """)
    tables_queries["dashboard_stats"] = qs

    # B. crime_alerts (20 rows)
    qs = []
    for i in range(20):
        dt = (now - timedelta(days=i % 7, hours=(i % 10) + 1)).strftime("%Y-%m-%d %H:%M:%S")
        severity = "HIGH" if i % 3 != 1 else "MEDIUM"
        dist_val = pick(district_rids, i)
        csh_val  = pick(csh_rids, i)
        qs.append(f"""
            INSERT INTO crime_alerts (
                alert_id, created_at, district_id, crime_sub_head_id,
                spike_ratio, severity, alert_message, is_acknowledged
            ) VALUES (
                {base_alert + i}, '{dt}', {dist_val}, {csh_val},
                {round(2.1 + i * 0.15, 2)}, '{severity}',
                '{ALERT_MSGS[i]}', {1 if i % 5 == 0 else 0}
            )
        """)
    tables_queries["crime_alerts"] = qs

    # C. risk_scores (20 rows)
    qs = []
    for i in range(20):
        dt = (now - timedelta(days=i % 7, hours=(i % 8) + 2)).strftime("%Y-%m-%d %H:%M:%S")
        qs.append(f"""
            INSERT INTO risk_scores (
                risk_score_id, accused_name, accused_age, gender_id,
                fir_count, district_ids, crime_types, is_absconding,
                gravity_avg, risk_score, mo_tag, computed_at
            ) VALUES (
                {base_risk + i}, '{ACCUSED_NAMES[i]}', {20 + i * 2}, {1 if i % 2 == 0 else 2},
                {2 + (i % 6)}, '[{pick(district_rids, i)}, {pick(district_rids, i+1)}]',
                '[{pick(csh_rids, i)}, {pick(csh_rids, i+2)}]',
                {1 if i % 3 != 0 else 0},
                {round(4.0 + (i % 5) * 0.4, 1)}, {60 + (i % 4) * 10 + i},
                '{MO_TAGS[i]}', '{dt}'
            )
        """)
    tables_queries["risk_scores"] = qs

    # D. conversations (20 rows — alternating user/assistant pairs)
    qs = []
    for i in range(20):
        dt = (now - timedelta(days=i % 7, minutes=(i % 30) * 10 + 5)).strftime("%Y-%m-%d %H:%M:%S")
        user_id = USER_IDS[i % len(USER_IDS)]
        session_id = f"session_new_{(i // 2) + 1:03d}"
        if i % 2 == 0:
            role = "user"
            content = USER_QUERIES[i % len(USER_QUERIES)].replace("'", "''")
            sql_gen = "NULL"
        else:
            role = "assistant"
            content = ASST_REPLIES[i % len(ASST_REPLIES)].replace("'", "''")
            sql_gen = f"'SELECT CaseMaster.ROWID FROM CaseMaster LIMIT 50'"
        qs.append(f"""
            INSERT INTO conversations (
                conversation_id, user_id, session_id, role,
                content, sql_generated, created_at
            ) VALUES (
                {base_conv + i}, '{user_id}', '{session_id}', '{role}',
                '{content}', {sql_gen}, '{dt}'
            )
        """)
    tables_queries["conversations"] = qs

    # E. audit_logs (20 rows)
    qs = []
    for i in range(20):
        dt = (now - timedelta(days=i % 7, hours=(i % 11) + 1)).strftime("%Y-%m-%d %H:%M:%S")
        endpoint = ENDPOINTS[i % len(ENDPOINTS)]
        user_id  = USER_IDS[i % len(USER_IDS)]
        role     = ROLES[i % len(ROLES)]
        query_text = f"Accessing {endpoint} — audit log entry {base_log + i}"
        qs.append(f"""
            INSERT INTO audit_logs (
                log_id, user_id, user_role, endpoint,
                query_text, tables_accessed, ip_address, created_at
            ) VALUES (
                {base_log + i}, '{user_id}', '{role}', '{endpoint}',
                '{query_text}', 'CaseMaster, dashboard_stats, crime_alerts',
                '192.168.1.{50 + (i % 50)}', '{dt}'
            )
        """)
    tables_queries["audit_logs"] = qs

    # F. CaseMaster (20 rows)
    qs = []
    for i in range(20):
        reg_date = (now - timedelta(days=i % 7)).strftime("%Y-%m-%d")
        inc_from = (now - timedelta(days=i % 7, hours=5)).strftime("%Y-%m-%d %H:%M:%S")
        inc_to   = (now - timedelta(days=i % 7, hours=4)).strftime("%Y-%m-%d %H:%M:%S")
        info_rec = (now - timedelta(days=i % 7, hours=3)).strftime("%Y-%m-%d %H:%M:%S")
        case_id  = base_case + i
        qs.append(f"""
            INSERT INTO CaseMaster (
                CaseMasterID, CrimeNo, CaseNo, CrimeRegisteredDate,
                PolicePersonID, PoliceStationID, CaseCategoryID, GravityOffenceID,
                CrimeMajorHeadID, CrimeMinorHeadID, CaseStatusID, CourtID,
                IncidentFromDate, IncidentToDate, InfoReceivedPSDate,
                latitude, longitude, BriefFacts
            ) VALUES (
                {case_id}, '1044301001202600{case_id:04d}', '202600{case_id:04d}', '{reg_date}',
                {pick(emp_rids, i)}, {pick(station_rids, i)}, {pick(casecat_rids, i)}, {pick(gravity_rids, i)},
                {pick(ch_rids, i)}, {pick(csh_rids, i)}, {pick(status_rids, i)}, {pick(court_rids, i)},
                '{inc_from}', '{inc_to}', '{info_rec}',
                {LATS[i]}, {LONS[i]}, '{BRIEF_FACTS[i]}'
            )
        """)
    tables_queries["CaseMaster"] = qs

    # ── 5. Execute all queries ───────────────────────────────────────────────
    for table_name, queries in tables_queries.items():
        inserted_count = 0
        for q in queries:
            try:
                zcql.execute_query(q)
                inserted_count += 1
            except Exception as e:
                results["errors"].append(
                    f"[{table_name}] FAILED: {str(e)[:200]}"
                )
        results["inserted"][table_name] = f"inserted {inserted_count}/{len(queries)} rows"
        print(f"[insert-new-data] {table_name}: {inserted_count}/{len(queries)}")

    return results
