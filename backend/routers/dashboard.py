from fastapi import APIRouter, Depends, Request
from schemas.dashboard import (
    DashboardStatsResponse, DistrictCrimeResponse, AlertResponse, TrendResponse
)
from core.database import get_datastore
from core.security import require_role
from datetime import datetime

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    request: Request,
    db=Depends(get_datastore),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    return DashboardStatsResponse(
        total_firs=5847,
        active_cases=312,
        high_risk_offender_count=47,
        active_alert_count=8,
        computed_at=datetime.utcnow()
    )


@router.get("/district-crimes", response_model=list[DistrictCrimeResponse])
async def get_district_crimes(
    timeframe: str = "30d",
    request: Request = None,
    db=Depends(get_datastore),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    return [
        DistrictCrimeResponse(district_id=1, district_name="Bengaluru Urban",
            total_firs=5847, active_cases=312, high_risk_count=47,
            dominant_crime_type="Robbery", lat=12.9716, lng=77.5946),
        DistrictCrimeResponse(district_id=2, district_name="Mysuru",
            total_firs=984, active_cases=45, high_risk_count=8,
            dominant_crime_type="Theft", lat=12.2958, lng=76.6394),
        DistrictCrimeResponse(district_id=3, district_name="Hubballi-Dharwad",
            total_firs=1420, active_cases=88, high_risk_count=12,
            dominant_crime_type="Assault", lat=15.3647, lng=75.1240),
    ]


@router.get("/alerts", response_model=list[AlertResponse])
async def get_active_alerts(
    limit: int = 10,
    request: Request = None,
    db=Depends(get_datastore),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    return [
        AlertResponse(alert_id=1, title="Robbery Spike — Bengaluru North",
            level="CRITICAL", details="+340% above 90-day average",
            district_name="Bengaluru Urban", crime_type="Robbery",
            spike_ratio=4.4, created_at=datetime.utcnow(), time_ago="2h ago"),
        AlertResponse(alert_id=2, title="Assault Cluster — Hubballi",
            level="WARNING", details="+85% above 90-day average",
            district_name="Hubballi-Dharwad", crime_type="Assault",
            spike_ratio=1.85, created_at=datetime.utcnow(), time_ago="7h ago"),
    ]


@router.get("/trends", response_model=list[TrendResponse])
async def get_crime_trends(
    request: Request = None,
    db=Depends(get_datastore),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    return [
        TrendResponse(crime_category="Robbery",
            weekly_counts=[10,20,14,30,24,34,40],
            bar_heights=[25,50,35,75,60,85,100],
            change_pct=12.0, trend="up", total_current=162, total_prior=144),
        TrendResponse(crime_category="Theft",
            weekly_counts=[30,26,20,22,20,18,20],
            bar_heights=[75,65,50,55,50,45,50],
            change_pct=-2.0, trend="down", total_current=156, total_prior=159),
        TrendResponse(crime_category="Assault",
            weekly_counts=[10,12,10,16,14,24,28],
            bar_heights=[25,30,25,40,35,60,70],
            change_pct=5.0, trend="up", total_current=114, total_prior=108),
        TrendResponse(crime_category="Vehicle Crime",
            weekly_counts=[40,32,28,20,16,14,10],
            bar_heights=[100,80,70,50,40,35,25],
            change_pct=-15.0, trend="down", total_current=160, total_prior=188),
        TrendResponse(crime_category="Burglary",
            weekly_counts=[16,18,14,20,16,18,16],
            bar_heights=[40,45,35,50,40,45,40],
            change_pct=0.0, trend="flat", total_current=118, total_prior=118),
    ]
