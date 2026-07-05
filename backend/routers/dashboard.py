from fastapi import APIRouter, Depends, Request
from schemas.dashboard import (
    DashboardStatsResponse, DistrictCrimeResponse, AlertResponse, TrendResponse
)
from core.database import get_datastore, get_zcql
from core.security import require_role
from datetime import datetime, timedelta
from analytics.trends import (
    DISTRICT_CENTROIDS, TREND_CATEGORIES, normalize, compute_trend, format_time_ago
)
from collections import defaultdict, Counter

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    request: Request,
    zcql=Depends(get_zcql),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    try:
        query = "SELECT * FROM dashboard_stats ORDER BY computed_at DESC LIMIT 1"
        result = zcql.execute_query(query)
        print(f"Dashboard stats query result: {result}")
        if result and len(result) > 0:
            # ZCQL returns data nested under table name key
            row_data = result[0].get('dashboard_stats', result[0])
            return DashboardStatsResponse(**row_data)
    except Exception as e:
        print(f"Dashboard stats query error: {e}")
        pass
    
    # Fallback: compute on-the-fly if table doesn't exist
    try:
        query = "SELECT COUNT(CaseMasterID) as total FROM CaseMaster"
        result = zcql.execute_query(query)
        print(f"Total FIRs query result: {result}")
        total_firs = result[0]["total"] if result else 0
        
        query = """
            SELECT COUNT(CaseMaster.CaseMasterID) as active 
            FROM CaseMaster 
            INNER JOIN CaseStatusMaster ON CaseMaster.CaseStatusID = CaseStatusMaster.ROWID 
            WHERE CaseStatusMaster.CaseStatusName = 'Under Investigation'
        """
        result = zcql.execute_query(query)
        print(f"Active cases query result: {result}")
        active_cases = result[0]["active"] if result else 0
    except Exception as e:
        print(f"Fallback query error: {e}")
        total_firs = 0
        active_cases = 0
    
    print(f"Final stats - total_firs: {total_firs}, active_cases: {active_cases}")
    return DashboardStatsResponse(
        total_firs=total_firs,
        active_cases=active_cases,
        high_risk_offender_count=0,
        active_alert_count=0,
        computed_at=datetime.utcnow()
    )


@router.get("/district-crimes", response_model=list[DistrictCrimeResponse])
async def get_district_crimes(
    timeframe: str = "30d",
    request: Request = None,
    zcql=Depends(get_zcql),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    timeframe_days = {"24h": 1, "7d": 7, "30d": 30}
    days = timeframe_days.get(timeframe, 30)
    since = datetime.utcnow() - timedelta(days=days)
    since_str = since.strftime("%Y-%m-%d %H:%M:%S")
    
    query = f"""
        SELECT 
            District.DistrictName,
            COUNT(CaseMaster.ROWID) as total_firs,
            CrimeSubHead.CrimeSubHeadName as crime_type
        FROM CaseMaster
        INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
        INNER JOIN District ON Unit.DistrictID = District.ROWID
        LEFT JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
        WHERE CaseMaster.IncidentFromDate >= '{since_str}'
        GROUP BY District.DistrictName, CrimeSubHead.CrimeSubHeadName
    """
    
    try:
        result = zcql.execute_query(query)
    except Exception:
        result = []
    
    district_stats = defaultdict(lambda: {"total_firs": 0, "crime_types": []})
    
    for row in result:
        d_name = row.get("DistrictName", "Unknown")
        district_stats[d_name]["total_firs"] += row.get("total_firs", 0)
        crime_type = row.get("crime_type")
        if crime_type:
            district_stats[d_name]["crime_types"].append(crime_type)
    
    results = []
    for d_name, d_data in district_stats.items():
        centroid = DISTRICT_CENTROIDS.get(d_name, {"lat": 15.0, "lng": 76.0})
        dominant = Counter(d_data["crime_types"]).most_common(1)
        dominant_type = dominant[0][0] if dominant else "Unknown"
        results.append(DistrictCrimeResponse(
            district_id=hash(d_name) % 1000,
            district_name=d_name,
            total_firs=d_data["total_firs"],
            active_cases=0,
            high_risk_count=0,
            dominant_crime_type=dominant_type,
            lat=centroid["lat"],
            lng=centroid["lng"]
        ))
    
    return sorted(results, key=lambda x: x.total_firs, reverse=True)


@router.get("/alerts", response_model=list[AlertResponse])
async def get_active_alerts(
    limit: int = 10,
    request: Request = None,
    zcql=Depends(get_zcql),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    try:
        query = f"""
            SELECT 
                crime_alerts.ROWID as alert_id,
                crime_alerts.severity,
                crime_alerts.spike_ratio,
                crime_alerts.created_at,
                crime_alerts.is_acknowledged,
                District.DistrictName,
                CrimeSubHead.CrimeSubHeadName
            FROM crime_alerts
            LEFT JOIN District ON crime_alerts.district_id = District.ROWID
            LEFT JOIN CrimeSubHead ON crime_alerts.crime_sub_head_id = CrimeSubHead.ROWID
            WHERE crime_alerts.is_acknowledged = false OR crime_alerts.is_acknowledged IS NULL
            ORDER BY 
                CASE WHEN crime_alerts.severity = 'HIGH' THEN 0 ELSE 1 END,
                crime_alerts.created_at DESC
            LIMIT {limit}
        """
        result = zcql.execute_query(query)
    except Exception:
        result = []
    
    results = []
    for row in result:
        level = "CRITICAL" if row.get("severity") == "HIGH" else "WARNING"
        created_at = row.get("created_at", datetime.utcnow())
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                created_at = datetime.utcnow()
        
        created_at_naive = created_at
        if hasattr(created_at_naive, 'tzinfo') and created_at_naive.tzinfo is not None:
            created_at_naive = created_at_naive.replace(tzinfo=None)
        
        spike_ratio = row.get("spike_ratio", 1.0)
        results.append(AlertResponse(
            alert_id=row.get("alert_id", 0),
            title=f"{row.get('CrimeSubHeadName', 'Crime')} Spike — {row.get('DistrictName', 'Unknown')}",
            level=level,
            details=f"+{int((spike_ratio - 1) * 100)}% above 90-day average",
            district_name=row.get("DistrictName", "Unknown"),
            crime_type=row.get("CrimeSubHeadName", "Unknown"),
            spike_ratio=spike_ratio,
            created_at=created_at,
            time_ago=format_time_ago(created_at_naive)
        ))
    
    return results


@router.get("/trends", response_model=list[TrendResponse])
async def get_crime_trends(
    request: Request = None,
    zcql=Depends(get_zcql),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    try:
        query = "SELECT trend_sparklines_json FROM dashboard_stats ORDER BY computed_at DESC LIMIT 1"
        result = zcql.execute_query(query)
        if result and len(result) > 0:
            trend_json = result[0].get("trend_sparklines_json")
            if trend_json:
                import json
                trend_data = json.loads(trend_json) if isinstance(trend_json, str) else trend_json
                return [TrendResponse(**t) for t in trend_data]
    except Exception:
        pass
    
    # Fallback: compute on-the-fly using ZCQL
    results = []
    now = datetime.utcnow()
    prior_30d_start = (now - timedelta(days=60)).strftime("%Y-%m-%d %H:%M:%S")
    current_30d_start = (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        query = f"""
            SELECT CrimeSubHead.CrimeSubHeadName, COUNT(CaseMaster.ROWID) as count
            FROM CaseMaster
            LEFT JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
            WHERE CaseMaster.IncidentFromDate >= '{prior_30d_start}'
            GROUP BY CrimeSubHead.CrimeSubHeadName
        """
        result = zcql.execute_query(query)
        
        crime_counts = {row.get("CrimeSubHeadName", "Unknown"): row.get("count", 0) for row in result}
    except Exception:
        crime_counts = {}
    
    for category, sub_head_names in TREND_CATEGORIES.items():
        current_30d = sum(crime_counts.get(name, 0) for name in sub_head_names)
        prior_30d = 0  # Would need separate query for prior period
        
        change_pct, trend = compute_trend(current_30d, prior_30d)
        
        weekly_counts = [current_30d // 7] * 7
        bar_heights = normalize(weekly_counts)
        
        results.append(TrendResponse(
            crime_category=category,
            weekly_counts=weekly_counts,
            bar_heights=bar_heights,
            change_pct=change_pct,
            trend=trend,
            total_current=current_30d,
            total_prior=prior_30d
        ))
    
    return results
