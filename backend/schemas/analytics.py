"""
Pydantic schemas for the Analytics & Patterns API.
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# Hotspot Map Schemas
class HotspotCluster(BaseModel):
    """A single spatial crime cluster from DBSCAN."""

    cluster_id: int
    centroid_lat: float
    centroid_lng: float
    point_count: int
    radius_km: float
    dominant_crime_type: Optional[str] = None
    district: Optional[str] = None


class HotspotFilters(BaseModel):
    """Optional filters for the hotspot endpoint."""

    date_from: Optional[str] = None
    date_to: Optional[str] = None
    district: Optional[str] = None


class HotspotClusterResponse(BaseModel):
    """Response body for GET /api/analytics/hotspots."""

    clusters: list[HotspotCluster]
    total_incidents: int
    filters: HotspotFilters
    generated_at: datetime


# Emerging Clusters Schemas
class CrimeAlert(BaseModel):
    """A single emerging crime cluster alert from crime_alerts table."""

    alert_id: int
    crime_type: str
    district: str
    spike_ratio: float
    baseline_count: int
    current_count: int
    detected_at: datetime
    acknowledged: bool = False
    severity: Literal["LOW", "MEDIUM", "HIGH"]


class CrimeAlertResponse(BaseModel):
    """Response body for GET /api/analytics/emerging-clusters."""

    alerts: list[CrimeAlert]
    total_alerts: int
    generated_at: datetime


# Trend Analysis Schemas
TrendGranularity = Literal["month", "week"]


class TrendPoint(BaseModel):
    """A single data point in a time series."""

    date: str
    count: int
    is_forecast: bool = False
    lower_bound: Optional[int] = None
    upper_bound: Optional[int] = None


class TrendFilters(BaseModel):
    """Optional filters for the trend endpoint."""

    granularity: TrendGranularity = "month"
    crime_type: Optional[str] = None
    district: Optional[str] = None


class TrendDataResponse(BaseModel):
    """Response body for GET /api/analytics/trends."""

    data: list[TrendPoint]
    filters: TrendFilters
    total_count: int
    generated_at: datetime


class SeasonalComparison(BaseModel):
    """Seasonal event comparison data."""

    event_name: str
    event_date: str
    window_start: str
    window_end: str
    event_window_count: int
    baseline_window_count: int
    percentage_change: float


class FestivalCalendarResponse(BaseModel):
    """Response body for GET /api/analytics/festival-calendar."""

    comparisons: list[SeasonalComparison]
    generated_at: datetime


# Offender Risk Board Schemas
class OffenderRisk(BaseModel):
    """A single offender from the risk_scores table."""

    accused_id: int
    accused_name: str
    risk_score: float
    mo_tag: Optional[str] = None
    district_ids: list[str] = Field(default_factory=list)
    is_absconding: bool = False
    fir_count: int


class OffenderRiskFilters(BaseModel):
    """Optional filters for the offender risk endpoint."""

    district: Optional[str] = None
    min_risk_score: Optional[float] = None
    is_absconding: Optional[bool] = None


class OffenderRiskResponse(BaseModel):
    """Response body for GET /api/analytics/offender-risk."""

    offenders: list[OffenderRisk]
    total_count: int
    page: int
    page_size: int
    filters: OffenderRiskFilters
    generated_at: datetime


# Sociological Data Schemas
class DistrictSocioeconomic(BaseModel):
    """Socioeconomic indicators for a district."""

    district: str
    literacy_rate: float
    urbanization_percentage: float
    population: int


class SocioeconomicResponse(BaseModel):
    """Response body for GET /api/analytics/socioeconomic."""

    districts: list[DistrictSocioeconomic]
    generated_at: datetime
