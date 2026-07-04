from fastapi import APIRouter, Depends, Request
from schemas.dashboard import (
    DashboardStatsResponse, DistrictCrimeResponse, AlertResponse, TrendResponse
)
from core.database import get_datastore
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
    db=Depends(get_datastore),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    try:
        table = db.table("dashboard_stats")
        rows = table.get_paged_rows().rows
        if rows:
            latest = sorted(rows, key=lambda r: r.get("computed_at", ""), reverse=True)[0]
            return DashboardStatsResponse(**latest)
    except Exception:
        pass
    
    # Fallback: compute on-the-fly if table doesn't exist
    case_table = db.table("CaseMaster")
    all_cases = case_table.get_paged_rows().rows
    total_firs = len(all_cases)
    
    status_table = db.table("CaseStatusMaster")
    status_map = {row["ROWID"]: row["CaseStatusName"] for row in status_table.get_paged_rows().rows}
    active_cases = sum(1 for c in all_cases if status_map.get(c.get("CaseStatusID")) == "Under Investigation")
    
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
    db=Depends(get_datastore),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    timeframe_days = {"24h": 1, "7d": 7, "30d": 30}
    days = timeframe_days.get(timeframe, 30)
    since = datetime.utcnow() - timedelta(days=days)
    
    case_table = db.table("CaseMaster")
    all_cases = case_table.get_paged_rows().rows
    
    unit_table = db.table("Unit")
    units = {row["ROWID"]: row for row in unit_table.get_paged_rows().rows}
    
    district_table = db.table("District")
    districts = {row["ROWID"]: row for row in district_table.get_paged_rows().rows}
    
    crime_sub_head_table = db.table("CrimeSubHead")
    crime_sub_heads = {row["ROWID"]: row for row in crime_sub_head_table.get_paged_rows().rows}
    
    district_stats = defaultdict(lambda: {"total_firs": 0, "crime_types": []})
    
    for case in all_cases:
        incident_date = case.get("IncidentFromDate")
        if incident_date and isinstance(incident_date, str):
            try:
                case_date = datetime.fromisoformat(incident_date.replace('Z', '+00:00'))
                # Normalize to naive for comparison with naive `since`
                if case_date.tzinfo is not None:
                    case_date = case_date.replace(tzinfo=None)
                if case_date < since:
                    continue
            except (ValueError, TypeError):
                continue
        
        unit = units.get(case.get("PoliceStationID"))
        if not unit:
            continue
        dist = districts.get(unit.get("DistrictID"))
        if not dist:
            continue
        d_name = dist.get("DistrictName", "Unknown")
        district_stats[d_name]["total_firs"] += 1
        csh = crime_sub_heads.get(case.get("CrimeMinorHeadID"))
        if csh:
            district_stats[d_name]["crime_types"].append(csh.get("CrimeSubHeadName", ""))
    
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
    db=Depends(get_datastore),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    try:
        alerts_table = db.table("crime_alerts")
        rows = alerts_table.get_paged_rows().rows
        
        district_table = db.table("District")
        districts = {row["ROWID"]: row for row in district_table.get_paged_rows().rows}
        
        crime_sub_head_table = db.table("CrimeSubHead")
        crime_sub_heads = {row["ROWID"]: row for row in crime_sub_head_table.get_paged_rows().rows}
        
        unacknowledged = [r for r in rows if not r.get("is_acknowledged", False)]
        # Step 1: newest first; Step 2: stable-sort severity (HIGH=0 first) — Python sort is stable
        unacknowledged.sort(key=lambda r: str(r.get("created_at", "")), reverse=True)
        unacknowledged.sort(key=lambda r: 0 if r.get("severity") == "HIGH" else 1)

        
        results = []
        for row in unacknowledged[:limit]:
            dist = districts.get(row.get("district_id"))
            csh = crime_sub_heads.get(row.get("crime_sub_head_id"))
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
            results.append(AlertResponse(
                alert_id=row.get("ROWID", 0),
                title=f"{csh.get('CrimeSubHeadName', 'Crime')} Spike — {dist.get('DistrictName', 'Unknown')}" if csh and dist else "Crime Spike",
                level=level,
                details=f"+{int((row.get('spike_ratio', 1) - 1) * 100)}% above 90-day average",
                district_name=dist.get("DistrictName", "Unknown") if dist else "Unknown",
                crime_type=csh.get("CrimeSubHeadName", "Unknown") if csh else "Unknown",
                spike_ratio=row.get("spike_ratio", 1.0),
                created_at=created_at,
                time_ago=format_time_ago(created_at_naive)
            ))
        
        return results
    except Exception:
        return []


@router.get("/trends", response_model=list[TrendResponse])
async def get_crime_trends(
    request: Request = None,
    db=Depends(get_datastore),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    try:
        table = db.table("dashboard_stats")
        rows = table.get_paged_rows().rows
        if rows:
            latest = sorted(rows, key=lambda r: r.get("computed_at", ""), reverse=True)[0]
            trend_json = latest.get("trend_sparklines_json")
            if trend_json:
                import json
                trend_data = json.loads(trend_json) if isinstance(trend_json, str) else trend_json
                return [TrendResponse(**t) for t in trend_data]
    except Exception:
        pass
    
    # Fallback: compute on-the-fly
    case_table = db.table("CaseMaster")
    all_cases = case_table.get_paged_rows().rows
    
    crime_sub_head_table = db.table("CrimeSubHead")
    crime_sub_heads = {row["ROWID"]: row for row in crime_sub_head_table.get_paged_rows().rows}

    def safe_parse_date(val) -> datetime | None:
        if not val or not isinstance(val, str):
            return None
        try:
            return datetime.fromisoformat(val.replace('Z', '+00:00'))
        except ValueError:
            return None
    
    results = []
    now = datetime.utcnow()
    for category, sub_head_names in TREND_CATEGORIES.items():
        sub_head_ids = [rid for rid, r in crime_sub_heads.items() if r.get("CrimeSubHeadName") in sub_head_names]
        
        category_cases = [c for c in all_cases if c.get("CrimeMinorHeadID") in sub_head_ids]
        
        current_30d = 0
        prior_30d = 0
        for c in category_cases:
            dt = safe_parse_date(c.get("IncidentFromDate"))
            if dt is None:
                continue
            # Make offset-naive for comparison
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            age_days = (now - dt).days
            if age_days <= 30:
                current_30d += 1
            elif 30 < age_days <= 60:
                prior_30d += 1
        
        change_pct, trend = compute_trend(current_30d, prior_30d)
        
        # Distribute evenly across 7 weeks as approximation
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
