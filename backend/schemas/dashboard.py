from pydantic import BaseModel
from datetime import datetime


class DashboardStatsResponse(BaseModel):
    total_firs: int
    active_cases: int
    high_risk_offender_count: int
    active_alert_count: int
    computed_at: datetime


class DistrictCrimeResponse(BaseModel):
    district_id: int
    district_name: str
    total_firs: int
    active_cases: int
    high_risk_count: int
    dominant_crime_type: str
    lat: float
    lng: float


class AlertResponse(BaseModel):
    alert_id: int
    title: str
    level: str
    details: str
    district_name: str
    crime_type: str
    spike_ratio: float
    created_at: datetime
    time_ago: str


class SparklineWeek(BaseModel):
    week_label: str
    count: int


class TrendResponse(BaseModel):
    crime_category: str
    weekly_counts: list[int]
    bar_heights: list[int]
    change_pct: float
    trend: str
    total_current: int
    total_prior: int
