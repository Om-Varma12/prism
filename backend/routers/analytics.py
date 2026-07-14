"""
Analytics & Patterns API routes.

These endpoints provide statistical intelligence for crime patterns,
including hotspot clustering, trend analysis, and offender risk scoring.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends

from core.database import get_zcql, get_cache
from core.security import require_role
from schemas.analytics import (
    CrimeAlertResponse,
    FestivalCalendarResponse,
    HotspotClusterResponse,
    OffenderRiskResponse,
    SocioeconomicResponse,
    TrendDataResponse,
)


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _empty_hotspot_response() -> HotspotClusterResponse:
    """Return an empty hotspot response for error cases."""
    from schemas.analytics import HotspotFilters
    return HotspotClusterResponse(
        clusters=[],
        total_incidents=0,
        filters=HotspotFilters(),
        generated_at=datetime.utcnow(),
    )


def _empty_trend_response() -> TrendDataResponse:
    """Return an empty trend response for error cases."""
    from schemas.analytics import TrendFilters, TrendGranularity
    return TrendDataResponse(
        data=[],
        filters=TrendFilters(granularity="month"),
        total_count=0,
        generated_at=datetime.utcnow(),
    )


def _empty_offender_risk_response() -> OffenderRiskResponse:
    """Return an empty offender risk response for error cases."""
    from schemas.analytics import OffenderRiskFilters
    return OffenderRiskResponse(
        offenders=[],
        total_count=0,
        page=1,
        page_size=20,
        filters=OffenderRiskFilters(),
        generated_at=datetime.utcnow(),
    )


@router.get("/hotspots", response_model=HotspotClusterResponse)
async def get_hotspots(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    district: Optional[str] = None,
    zcql=Depends(get_zcql),
    cache=Depends(get_cache),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Get spatial crime hotspots using DBSCAN clustering.
    
    Returns cluster centroids, point counts, bounding radius, and dominant crime type.
    Results are cached for 5 minutes based on filter combination.
    """
    try:
        from analytics.hotspot import HotspotAnalyzer
        from schemas.analytics import HotspotFilters
        
        # Build cache key from filter combination
        cache_key = f"hotspots:{date_from or 'all'}:{date_to or 'all'}:{district or 'all'}"
        
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            import json
            return HotspotClusterResponse(**json.loads(cached_data))
        
        # Build ZCQL query to fetch incident data
        # Note: Using LIMIT to respect 300-row limit
        query = """
            SELECT
                CaseMaster.latitude,
                CaseMaster.longitude,
                CrimeSubHead.CrimeHeadName as crime_type,
                District.DistrictName as district
            FROM CaseMaster
            LEFT JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
            LEFT JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
            LEFT JOIN District ON Unit.DistrictID = District.ROWID
            WHERE CaseMaster.latitude IS NOT NULL
            AND CaseMaster.longitude IS NOT NULL
        """
        
        # Add optional filters
        if date_from:
            query += f" AND CaseMaster.IncidentFromDate >= '{date_from}'"
        if date_to:
            query += f" AND CaseMaster.IncidentFromDate <= '{date_to}'"
        if district:
            query += f" AND District.DistrictName = '{district}'"
        
        query += " LIMIT 300"
        
        # Execute query
        result = zcql.execute_query(query)
        rows = result if isinstance(result, list) else []
        
        # Convert to incident data format
        incident_data = []
        for row in rows:
            incident_data.append({
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
                "crime_type": row.get("crime_type"),
                "district": row.get("district"),
            })
        
        # Perform DBSCAN clustering
        analyzer = HotspotAnalyzer(eps_km=1.0, min_samples=5)
        clusters = analyzer.analyze_hotspots(incident_data)
        
        # Convert to response format
        from schemas.analytics import HotspotCluster
        cluster_objects = [
            HotspotCluster(
                cluster_id=c["cluster_id"],
                centroid_lat=c["centroid_lat"],
                centroid_lng=c["centroid_lng"],
                point_count=c["point_count"],
                radius_km=c["radius_km"],
                dominant_crime_type=c["dominant_crime_type"],
                district=c["district"],
            )
            for c in clusters
        ]
        
        response = HotspotClusterResponse(
            clusters=cluster_objects,
            total_incidents=len(incident_data),
            filters=HotspotFilters(
                date_from=date_from,
                date_to=date_to,
                district=district,
            ),
            generated_at=datetime.utcnow(),
        )
        
        # Cache the response for 5 minutes (300 seconds)
        import json
        cache.set(cache_key, json.dumps(response.model_dump()), 300)
        
        return response
    except Exception as exc:
        print(f"[Warning] Failed to get hotspots: {exc}")
        return _empty_hotspot_response()


@router.get("/emerging-clusters", response_model=CrimeAlertResponse)
async def get_emerging_clusters(
    zcql=Depends(get_zcql),
    user=Depends(require_role(["analyst", "supervisor"])),
):
    """
    Get emerging crime clusters from the crime_alerts table.
    
    Returns unacknowledged, high-severity alerts where crime rate is significantly
    above historical baseline (spike_ratio > 2.0).
    """
    try:
        # TODO: Implement emerging clusters logic in Step 3
        from schemas.analytics import CrimeAlert
        return CrimeAlertResponse(
            alerts=[],
            total_alerts=0,
            generated_at=datetime.utcnow(),
        )
    except Exception as exc:
        print(f"[Warning] Failed to get emerging clusters: {exc}")
        from schemas.analytics import CrimeAlert
        return CrimeAlertResponse(
            alerts=[],
            total_alerts=0,
            generated_at=datetime.utcnow(),
        )


@router.get("/trends", response_model=TrendDataResponse)
async def get_trends(
    granularity: str = "month",
    crime_type: Optional[str] = None,
    district: Optional[str] = None,
    zcql=Depends(get_zcql),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Get crime trend analysis with time-series aggregation.
    
    Returns historical data and forecasted values for the next 30 days.
    Forecasted data is visually distinct from historical data.
    """
    try:
        # TODO: Implement trend aggregation logic in Step 4
        # TODO: Integrate forecast data in Step 6
        return _empty_trend_response()
    except Exception as exc:
        print(f"[Warning] Failed to get trends: {exc}")
        return _empty_trend_response()


@router.get("/festival-calendar", response_model=FestivalCalendarResponse)
async def get_festival_calendar(
    zcql=Depends(get_zcql),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Get seasonal event comparisons for Karnataka festivals.
    
    Returns crime rate in ±7-day window around festivals vs yearly baseline.
    """
    try:
        # TODO: Implement festival calendar logic in Step 4
        return FestivalCalendarResponse(
            comparisons=[],
            generated_at=datetime.utcnow(),
        )
    except Exception as exc:
        print(f"[Warning] Failed to get festival calendar: {exc}")
        return FestivalCalendarResponse(
            comparisons=[],
            generated_at=datetime.utcnow(),
        )


@router.get("/offender-risk", response_model=OffenderRiskResponse)
async def get_offender_risk(
    district: Optional[str] = None,
    min_risk_score: Optional[float] = None,
    is_absconding: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
    zcql=Depends(get_zcql),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Get offender risk scores from the risk_scores table.
    
    Returns sortable, filterable list of offenders with risk scores,
    MO tags, absconding status, and FIR count.
    """
    try:
        # TODO: Implement offender risk logic in Step 7
        return _empty_offender_risk_response()
    except Exception as exc:
        print(f"[Warning] Failed to get offender risk: {exc}")
        return _empty_offender_risk_response()


@router.get("/socioeconomic", response_model=SocioeconomicResponse)
async def get_socioeconomic(
    zcql=Depends(get_zcql),
    user=Depends(require_role(["analyst", "supervisor"])),
):
    """
    Get district-level socioeconomic indicators.
    
    Returns literacy rate, urbanization percentage, and population
    for Karnataka districts. Role-gated to Analyst/Supervisor only.
    """
    try:
        # TODO: Implement socioeconomic data logic in Step 8
        return SocioeconomicResponse(
            districts=[],
            generated_at=datetime.utcnow(),
        )
    except Exception as exc:
        print(f"[Warning] Failed to get socioeconomic data: {exc}")
        return SocioeconomicResponse(
            districts=[],
            generated_at=datetime.utcnow(),
        )
