"""
PRISM — Derived Table Data Insertion
====================================
Inserts sample data into Drishti-derived tables:
- dashboard_stats
- crime_alerts
- risk_scores
- conversations
- audit_logs

Uses Table API (insert_rows) instead of ZCQL for proper datetime handling.
JSON columns are inserted as VarChar strings since Catalyst DataStore
doesn't support JSON datatype directly.
"""

from fastapi import Request, APIRouter
from core.database import get_datastore
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/db", tags=["derived-insertion"])


@router.get("/tests/insert-derived-data")
async def insert_derived_data(request: Request):
    """Insert sample data into all derived tables."""
    ds = get_datastore(request)
    
    results = {"status": "ok", "tables": {}}
    
    # 1. dashboard_stats
    try:
        district_crime_json = json.dumps([
            {"district_id": 1, "district_name": "Bengaluru Urban", "total_firs": 156},
            {"district_id": 2, "district_name": "Mysuru", "total_firs": 89},
            {"district_id": 3, "district_name": "Dakshina Kannada", "total_firs": 67}
        ])
        
        trend_sparklines_json = json.dumps([
            {
                "crime_category": "Crimes Against Body",
                "weekly_counts": [12, 15, 8, 10, 14, 11, 9],
                "bar_heights": [0.8, 1.0, 0.53, 0.67, 0.93, 0.73, 0.6],
                "change_pct": 15.5,
                "trend": "up",
                "total_current": 79,
                "total_prior": 68
            },
            {
                "crime_category": "Crimes Against Property",
                "weekly_counts": [20, 18, 22, 19, 25, 21, 23],
                "bar_heights": [0.8, 0.72, 0.88, 0.76, 1.0, 0.84, 0.92],
                "change_pct": -5.2,
                "trend": "down",
                "total_current": 148,
                "total_prior": 156
            }
        ])
        
        table = ds.table("dashboard_stats")
        stats_rows = []
        for i in range(1, 13):
            now = datetime.utcnow() - timedelta(days=i)
            stats_rows.append({
                "stat_id": i,
                "computed_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "total_firs": 312 + i * 5,
                "active_cases": 89 + i * 2,
                "high_risk_offender_count": 15 + i,
                "active_alert_count": 4 + i,
                "district_crime_json": district_crime_json,
                "trend_sparklines_json": trend_sparklines_json
            })
        table.insert_rows(stats_rows)
        results["tables"]["dashboard_stats"] = f"inserted {len(stats_rows)} rows"
    except Exception as e:
        results["tables"]["dashboard_stats"] = f"failed: {str(e)}"
    
    # 2. crime_alerts
    try:
        alert_messages = [
            "Robbery up 340% in Bengaluru North",
            "Theft up 150% in Mysuru Central",
            "Vehicle theft spike in Bengaluru South",
            "Chain snatching increase in Mangalore",
            "Murder rate increase in Dharwad",
            "Cyber fraud spike in Udupi",
            "Drug trafficking alert in Belagavi",
            "Domestic violence rise in Kalaburagi",
            "Assault cases increase in Vijayawada",
            "Kidnapping trend in Visakhapatnam",
            "Burglary spike in Chennai",
            "Arms smuggling alert in Mumbai"
        ]
        severities = ["HIGH", "MEDIUM", "HIGH", "MEDIUM", "HIGH", "MEDIUM", "HIGH", "MEDIUM", "HIGH", "MEDIUM", "HIGH", "MEDIUM"]
        
        alerts = []
        for i in range(1, 13):
            alerts.append({
                "alert_id": i,
                "created_at": (datetime.utcnow() - timedelta(hours=i*2)).strftime("%Y-%m-%d %H:%M:%S"),
                "district_id": None,
                "crime_sub_head_id": None,
                "spike_ratio": round(2.0 + (i % 5) * 0.5, 1),
                "severity": severities[i-1],
                "alert_message": alert_messages[i-1],
                "is_acknowledged": 0 if i % 3 != 0 else 1
            })
        
        table = ds.table("crime_alerts")
        table.insert_rows(alerts)
        results["tables"]["crime_alerts"] = f"inserted {len(alerts)} rows"
    except Exception as e:
        results["tables"]["crime_alerts"] = f"failed: {str(e)}"
    
    # 3. risk_scores
    try:
        names = ["Ramesh Kumar", "Syed Abdul", "Mohan Singh", "Prakash Reddy", "Anil Mehta", "Vikram Gowda", "Girish K", "Shalini Prasad", "Vikas M", "Suresh Nair", "Lakshmi Devi", "Ramesh Gowda"]
        mo_tags = ["Serial robbery offender", "Vehicle theft specialist", "Property crime repeat offender", "Armed robbery suspect", "Cyber fraud perpetrator", "Kidnapping specialist", "Assault repeat offender", "Domestic violence accused", "Child abuse offender", "Murder suspect", "Chain snatcher", "Vehicle thief"]
        
        risk_scores = []
        for i in range(1, 13):
            risk_scores.append({
                "risk_score_id": i,
                "accused_name": names[i-1],
                "accused_age": 25 + (i % 20),
                "gender_id": 1 if i % 2 != 0 else 2,
                "fir_count": 2 + (i % 5),
                "district_ids": json.dumps([1, 2, 3][:i % 3 + 1]),
                "crime_types": json.dumps([5, 8, 12][:i % 3 + 1]),
                "is_absconding": 1 if i % 3 != 0 else 0,
                "gravity_avg": round(5.0 + (i % 5), 1),
                "risk_score": 65 + (i % 30),
                "mo_tag": mo_tags[i-1],
                "computed_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        table = ds.table("risk_scores")
        table.insert_rows(risk_scores)
        results["tables"]["risk_scores"] = f"inserted {len(risk_scores)} rows"
    except Exception as e:
        results["tables"]["risk_scores"] = f"failed: {str(e)}"
    
    # 4. conversations
    try:
        user_queries = [
            "Show me crime trends for Bengaluru",
            "List all high-risk offenders",
            "Find cases involving Ramesh Kumar",
            "Show district-wise crime statistics",
            "What are the recent theft cases?",
            "Show me murder cases from last month",
            "List all cyber fraud incidents",
            "Find kidnapping cases in Mysuru",
            "Show vehicle theft trends",
            "List assault cases in Bengaluru",
            "Find domestic violence complaints",
            "Show drug trafficking alerts"
        ]
        
        conversations = []
        for i in range(1, 13):
            conversations.append({
                "conversation_id": i,
                "user_id": f"user_{(i % 3) + 1}23",
                "session_id": f"session_{(i % 4) + 1:03d}",
                "role": "user",
                "content": user_queries[i-1],
                "sql_generated": None,
                "created_at": (datetime.utcnow() - timedelta(minutes=i*5)).strftime("%Y-%m-%d %H:%M:%S")
            })
            conversations.append({
                "conversation_id": i + 12,
                "user_id": f"user_{(i % 3) + 1}23",
                "session_id": f"session_{(i % 4) + 1:03d}",
                "role": "assistant",
                "content": f"Based on the query '{user_queries[i-1]}', here are the relevant results from the database.",
                "sql_generated": f"SELECT * FROM CaseMaster WHERE ...",
                "created_at": (datetime.utcnow() - timedelta(minutes=i*5 - 1)).strftime("%Y-%m-%d %H:%M:%S")
            })
        
        table = ds.table("conversations")
        table.insert_rows(conversations)
        results["tables"]["conversations"] = f"inserted {len(conversations)} rows"
    except Exception as e:
        results["tables"]["conversations"] = f"failed: {str(e)}"
    
    # 5. audit_logs
    try:
        endpoints = [
            "/api/dashboard/stats",
            "/api/dashboard/district-crimes",
            "/api/dashboard/alerts",
            "/api/chat/query",
            "/api/dashboard/trends",
            "/api/cases/list",
            "/api/offenders/list",
            "/api/alerts/acknowledge",
            "/api/reports/generate",
            "/api/analytics/crime-map",
            "/api/analytics/trend-analysis",
            "/api/users/profile"
        ]
        roles = ["analyst", "supervisor", "investigator", "admin"]
        
        audit_logs = []
        for i in range(1, 13):
            audit_logs.append({
                "log_id": i,
                "user_id": f"user_{(i % 3) + 1}23",
                "user_role": roles[i % 4],
                "endpoint": endpoints[i % len(endpoints)],
                "query_text": f"Query {i}: {endpoints[i % len(endpoints)]} access",
                "tables_accessed": "CaseMaster, dashboard_stats",
                "ip_address": "127.0.0.1",
                "created_at": (datetime.utcnow() - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S")
            })
        
        table = ds.table("audit_logs")
        table.insert_rows(audit_logs)
        results["tables"]["audit_logs"] = f"inserted {len(audit_logs)} rows"
    except Exception as e:
        results["tables"]["audit_logs"] = f"failed: {str(e)}"
    
    return results
