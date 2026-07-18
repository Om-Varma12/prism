"""
Analytics & Patterns API routes.

These endpoints provide statistical intelligence for crime patterns,
including hotspot clustering, trend analysis, and offender risk scoring.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends

from core.database import get_zcql, get_cache_segment
from core.security import require_role
from services.cache_service import CacheService, generate_cache_key
from schemas.analytics import (
    CrimeAlertResponse,
    FestivalCalendarResponse,
    HotspotClusterResponse,
    OffenderRiskResponse,
    SocioeconomicResponse,
    TrendDataResponse,
)


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def convert_month_to_date_range(month_str: str) -> tuple[str, str]:
    """
    Convert month string (YYYY-MM) to date range (YYYY-MM-01 to YYYY-MM-last_day)
    
    Args:
        month_str: Month in format 'YYYY-MM'
        
    Returns:
        Tuple of (date_from, date_to) in 'YYYY-MM-DD' format
    """
    try:
        # Parse the month string
        dt = datetime.strptime(month_str, '%Y-%m')
        
        # First day of the month
        date_from = dt.strftime('%Y-%m-%d')
        
        # Last day of the month
        # Go to first day of next month, then subtract one day
        if dt.month == 12:
            next_month = dt.replace(year=dt.year + 1, month=1, day=1)
        else:
            next_month = dt.replace(month=dt.month + 1, day=1)
        
        last_day = next_month - timedelta(days=1)
        date_to = last_day.strftime('%Y-%m-%d')
        
        return date_from, date_to
    except ValueError:
        # If conversion fails, return as-is (might already be full date)
        return month_str, month_str


def validate_and_convert_date(date_str: Optional[str]) -> Optional[str]:
    """
    Validate and convert date string to proper format.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Properly formatted date string or None if invalid
    """
    if not date_str:
        return None
    
    try:
        # If already in YYYY-MM-DD format, validate and return
        if len(date_str) == 10 and date_str.count('-') == 2:
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        
        # If in YYYY-MM format, convert to range
        if len(date_str) == 7 and date_str.count('-') == 1:
            date_from, _ = convert_month_to_date_range(date_str)
            return date_from
        
        # Try to parse as datetime and format back
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
        
    except ValueError:
        # Log warning and return None
        print(f"[Warning] Invalid date format: {date_str}")
        return None


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
    cache_segment=Depends(get_cache_segment),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Get spatial crime hotspots using DBSCAN clustering.
    
    Returns cluster centroids, point counts, bounding radius, and dominant crime type.
    Results are cached for 24 hours based on filter combination.
    """
    cache = CacheService(cache_segment)
    
    try:
        from analytics.hotspot import HotspotAnalyzer
        from schemas.analytics import HotspotFilters
        
        # Convert month-only dates to full date ranges
        if date_from and len(date_from) == 7:  # YYYY-MM format
            date_from, _ = convert_month_to_date_range(date_from)
        if date_to and len(date_to) == 7:  # YYYY-MM format
            _, date_to = convert_month_to_date_range(date_to)
        
        # Generate cache key from filter combination
        cache_key = generate_cache_key("analytics:hotspots", date_from, date_to, district)
        
        # Try to get from cache first
        cached_hotspots = cache.get(cache_key)
        if cached_hotspots:
            print(f"[Cache] Hit for hotspots with filters: {date_from}, {date_to}, {district}")
            return HotspotClusterResponse(**cached_hotspots)
        
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
        print(f"[DEBUG] ZCQL returned {len(rows)} rows")
        
        # if rows:
        #     print("[DEBUG] FIRST RAW ROW:", rows[0])
            
        # Convert to incident data format
        incident_data = []
        for row in rows:
            case_master = row.get("CaseMaster", {})
            crime_sub_head = row.get("CrimeSubHead", {})
            district_data = row.get("District", {})

            incident_data.append({
                "latitude": case_master.get("latitude"),
                "longitude": case_master.get("longitude"),
                "crime_type": crime_sub_head.get("CrimeHeadName"),
                "district": district_data.get("DistrictName"),
            })
        print(f"[DEBUG] Incident data: {len(incident_data)} records")
        
        # Perform DBSCAN clustering
        analyzer = HotspotAnalyzer(eps_km=10.0, min_samples=2)
        clusters = analyzer.analyze_hotspots(incident_data)
        print(f"[DEBUG] DBSCAN generated {len(clusters)} clusters")
        
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
        
        # Cache the response for 24 hours
        cache.put(cache_key, response.model_dump(), expiry_in_hours=24)
        print(f"[Cache] Stored hotspots with filters: {date_from}, {date_to}, {district}")
        
        return response
    except Exception as exc:
        print(f"[Warning] Failed to get hotspots: {exc}")
        return _empty_hotspot_response()


@router.get("/emerging-clusters", response_model=CrimeAlertResponse)
async def get_emerging_clusters(
    zcql=Depends(get_zcql),
    cache_segment=Depends(get_cache_segment),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Get emerging crime clusters from the crime_alerts table.
    
    Returns unacknowledged, high-severity alerts where crime rate is significantly
    above historical baseline (spike_ratio > 2.0). Results are cached for 6 hours.
    """
    cache = CacheService(cache_segment)
    
    try:
        from schemas.analytics import CrimeAlert
        
        # Build cache key with hourly granularity
        cache_key = generate_cache_key("analytics:emerging", datetime.utcnow().strftime('%Y%m%d%H'))
        
        # Try to get from cache first
        cached_alerts = cache.get(cache_key)
        if cached_alerts:
            print(f"[Cache] Hit for emerging clusters")
            return CrimeAlertResponse(**cached_alerts)
        
        # Query crime_alerts table for unacknowledged, high-severity alerts
        query = """
            SELECT
                crime_alerts.ROWID as alert_id,
                CrimeSubHead.CrimeHeadName as crime_type,
                District.DistrictName as district,
                crime_alerts.spike_ratio,
                crime_alerts.created_at as detected_at,
                crime_alerts.is_acknowledged as acknowledged,
                crime_alerts.severity
            FROM crime_alerts
            LEFT JOIN CrimeSubHead ON crime_alerts.crime_sub_head_id = CrimeSubHead.ROWID
            LEFT JOIN District ON crime_alerts.district_id = District.ROWID
            WHERE crime_alerts.is_acknowledged = 0
            AND crime_alerts.severity = 'HIGH'
            ORDER BY crime_alerts.spike_ratio DESC
            LIMIT 50
        """
        
        # Execute query
        result = zcql.execute_query(query)
        rows = result if isinstance(result, list) else []
        print(f"[DEBUG] Emerging clusters query returned {len(rows)} rows")
        
        # Show sample row for debugging
        if rows:
            print(f"[DEBUG] Sample emerging cluster row: {rows[0]}")
        
        # Convert to response format
        alerts = []
        for row in rows:
            # Handle nested ZCQL response structure
            crime_alerts = row.get("crime_alerts", {})
            crime_sub_head = row.get("CrimeSubHead", {})
            district_data = row.get("District", {})
            
            # Extract with proper None handling
            crime_type_raw = crime_sub_head.get("CrimeHeadName")
            district_raw = district_data.get("DistrictName")
            
            # Use "Unknown" for None values to satisfy Pydantic string type
            crime_type = crime_type_raw if crime_type_raw else "Unknown"
            district = district_raw if district_raw else "Unknown"
            
            spike_ratio = row.get("spike_ratio") or crime_alerts.get("spike_ratio", 0.0)
            
            print(f"[DEBUG] Processed alert: crime_type={crime_type} (raw={crime_type_raw}), district={district} (raw={district_raw}), spike_ratio={spike_ratio}")
            
            alerts.append(CrimeAlert(
                alert_id=row.get("alert_id") or crime_alerts.get("ROWID"),
                crime_type=crime_type,
                district=district,
                spike_ratio=spike_ratio,
                baseline_count=row.get("baseline_count"),  # Will be None since column doesn't exist
                current_count=row.get("current_count"),  # Will be None since column doesn't exist
                detected_at=row.get("detected_at") or crime_alerts.get("created_at"),
                acknowledged=bool(row.get("acknowledged", 0) or crime_alerts.get("is_acknowledged", 0)),
                severity=row.get("severity") or crime_alerts.get("severity", "HIGH"),
            ))
        
        response = CrimeAlertResponse(
            alerts=alerts,
            total_alerts=len(alerts),
            generated_at=datetime.utcnow(),
        )
        
        # Cache the response for 6 hours
        cache.put(cache_key, response.model_dump(), expiry_in_hours=6)
        print(f"[Cache] Stored emerging clusters")
        
        return response
    except Exception as exc:
        print(f"[Warning] Failed to get emerging clusters: {exc}")
        from schemas.analytics import CrimeAlert
        return CrimeAlertResponse(
            alerts=[],
            total_alerts=0,
            generated_at=datetime.utcnow(),
        )


@router.get("/test/insert-crime-alerts")
async def insert_test_crime_alerts(
    zcql=Depends(get_zcql),
):
    """
    Insert sample crime alerts for testing emerging clusters.
    """
    try:
        # Get sample crime types and districts
        crime_types_query = "SELECT ROWID, CrimeHeadName FROM CrimeSubHead LIMIT 5"
        crime_types_result = zcql.execute_query(crime_types_query)
        crime_types = crime_types_result if isinstance(crime_types_result, list) else []
        
        districts_query = "SELECT ROWID, DistrictName FROM District LIMIT 5"
        districts_result = zcql.execute_query(districts_query)
        districts = districts_result if isinstance(districts_result, list) else []
        
        print(f"[DEBUG] Crime types: {crime_types}")
        print(f"[DEBUG] Districts: {districts}")
        
        if not crime_types or not districts:
            return {"status": "error", "message": "No crime types or districts found"}
        
        # Insert sample alerts with valid foreign keys
        from datetime import datetime, timedelta
        sample_alerts = [
            {
                "district_id": int(districts[0].get("District", {}).get("ROWID", 0)),
                "crime_sub_head_id": int(crime_types[0].get("CrimeSubHead", {}).get("ROWID", 0)),
                "spike_ratio": 3.5,
                "severity": "HIGH",
                "alert_message": f"{crime_types[0].get('CrimeSubHead', {}).get('CrimeHeadName')} up 350% in {districts[0].get('District', {}).get('DistrictName')}",
                "is_acknowledged": 0,
                "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "district_id": int(districts[1].get("District", {}).get("ROWID", 0)),
                "crime_sub_head_id": int(crime_types[1].get("CrimeSubHead", {}).get("ROWID", 0)),
                "spike_ratio": 4.2,
                "severity": "HIGH",
                "alert_message": f"{crime_types[1].get('CrimeSubHead', {}).get('CrimeHeadName')} up 420% in {districts[1].get('District', {}).get('DistrictName')}",
                "is_acknowledged": 0,
                "created_at": (datetime.utcnow() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "district_id": int(districts[2].get("District", {}).get("ROWID", 0)),
                "crime_sub_head_id": int(crime_types[2].get("CrimeSubHead", {}).get("ROWID", 0)),
                "spike_ratio": 2.8,
                "severity": "HIGH",
                "alert_message": f"{crime_types[2].get('CrimeSubHead', {}).get('CrimeHeadName')} up 280% in {districts[2].get('District', {}).get('DistrictName')}",
                "is_acknowledged": 0,
                "created_at": (datetime.utcnow() - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
            },
        ]
        
        inserted_count = 0
        for alert in sample_alerts:
            insert_query = f"""
                INSERT INTO crime_alerts (district_id, crime_sub_head_id, spike_ratio, severity, alert_message, is_acknowledged, created_at)
                VALUES ({alert['district_id']}, {alert['crime_sub_head_id']}, {alert['spike_ratio']}, '{alert['severity']}', '{alert['alert_message']}', {alert['is_acknowledged']}, '{alert['created_at']}')
            """
            try:
                zcql.execute_query(insert_query)
                inserted_count += 1
                print(f"[DEBUG] Inserted alert: {alert['alert_message']}")
            except Exception as e:
                print(f"[DEBUG] Failed to insert alert: {e}")
        
        return {
            "status": "success",
            "message": f"Inserted {inserted_count} sample crime alerts",
            "inserted_count": inserted_count
        }
    except Exception as exc:
        print(f"[Warning] Failed to insert test crime alerts: {exc}")
        return {"status": "error", "message": str(exc)}


@router.get("/test/clean-crime-alerts")
async def clean_crime_alerts(
    zcql=Depends(get_zcql),
):
    """
    Delete all crime_alerts for testing purposes.
    """
    try:
        # Delete all crime_alerts (simpler approach for testing)
        delete_query = "DELETE FROM crime_alerts"
        result = zcql.execute_query(delete_query)
        
        return {
            "status": "success",
            "message": "Deleted all crime alerts"
        }
    except Exception as exc:
        print(f"[Warning] Failed to clean crime alerts: {exc}")
        return {"status": "error", "message": str(exc)}


@router.get("/trends", response_model=TrendDataResponse)
async def get_trends(
    granularity: str = "month",
    crime_type: Optional[str] = None,
    district: Optional[str] = None,
    zcql=Depends(get_zcql),
    cache_segment=Depends(get_cache_segment),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Get crime trend analysis with time-series aggregation.
    
    Returns historical data and forecasted values for the next 30 days.
    Forecasted data is visually distinct from historical data.
    Results are cached for 12 hours based on filter combination.
    """
    cache = CacheService(cache_segment)
    
    try:
        from analytics.trends import TrendAggregator
        from schemas.analytics import TrendFilters
        
        # Validate granularity
        if granularity not in ["month", "week"]:
            granularity = "month"
        
        # Generate cache key from filter combination
        cache_key = generate_cache_key("analytics:trends", granularity, crime_type, district)
        
        # Try to get from cache first
        cached_trends = cache.get(cache_key)
        if cached_trends:
            print(f"[Cache] Hit for trends with filters: {granularity}, {crime_type}, {district}")
            return TrendDataResponse(**cached_trends)
        
        # Build ZCQL query to fetch incident data
        query = """
            SELECT
                CaseMaster.IncidentFromDate as date,
                CrimeSubHead.CrimeHeadName as crime_type,
                District.DistrictName as district
            FROM CaseMaster
            LEFT JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
            LEFT JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
            LEFT JOIN District ON Unit.DistrictID = District.ROWID
            WHERE CaseMaster.IncidentFromDate IS NOT NULL
        """
        
        # Add optional filters
        if crime_type:
            query += f" AND CrimeSubHead.CrimeHeadName = '{crime_type}'"
        if district:
            query += f" AND District.DistrictName = '{district}'"
        
        query += " LIMIT 300"
        
        # Execute query
        result = zcql.execute_query(query)
        rows = result if isinstance(result, list) else []
        print(f"[DEBUG] Trends query returned {len(rows)} rows")
        
        # Show sample row for debugging
        if rows:
            print(f"[DEBUG] Sample row: {rows[0]}")
        
        # Convert to incident data format
        incident_data = []
        for row in rows:
            case_master = row.get("CaseMaster", {})
            crime_sub_head = row.get("CrimeSubHead", {})
            district_data = row.get("District", {})

            incident_data.append({
                "date": case_master.get("IncidentFromDate"),
                "crime_type": crime_sub_head.get("CrimeHeadName"),
                "district": district_data.get("DistrictName"),
            })
        print(f"[DEBUG] Incident data: {len(incident_data)} records")
        
        # Perform trend aggregation
        aggregator = TrendAggregator()
        aggregated_data = aggregator.aggregate_trends(incident_data, granularity)
        print(f"[DEBUG] Aggregated data: {len(aggregated_data)} points")
        
        # Convert historical data to response format
        from schemas.analytics import TrendPoint
        trend_points = [
            TrendPoint(
                date=d["date"],
                count=d["count"],
                is_forecast=False,
            )
            for d in aggregated_data
        ]
        
        # Fetch forecast data from crime_forecasts table (optional - may not exist)
        forecast_rows = []
        try:
            forecast_query = """
                SELECT
                    crime_category,
                    forecast_date,
                    predicted_value,
                    lower_bound,
                    upper_bound
                FROM crime_forecasts
                ORDER BY forecast_date ASC
                LIMIT 150
            """
            
            forecast_result = zcql.execute_query(forecast_query)
            forecast_rows = forecast_result if isinstance(forecast_result, list) else []
            print(f"[DEBUG] Forecast query returned {len(forecast_rows)} rows")
        except Exception as e:
            print(f"[DEBUG] Forecast query failed: {e}")
            forecast_rows = []
        
        # Convert forecast data to response format
        forecast_groups = {}
        for row in forecast_rows:
            # Handle both flat and nested ZCQL response structures
            crime_category = row.get("crime_category")
            if not crime_category:
                # Try nested structure
                crime_category = row.get("crime_forecasts", {}).get("crime_category")
            
            # Only include forecasts that match the crime_type filter (if specified)
            if crime_type and crime_category != crime_type:
                continue
            
            # Format date based on granularity
            forecast_date = row.get("forecast_date")
            if not forecast_date:
                forecast_date = row.get("crime_forecasts", {}).get("forecast_date")
            
            if forecast_date:
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(forecast_date, "%Y-%m-%d")
                    if granularity == "month":
                        period_key = date_obj.strftime("%Y-%m")
                    else:  # week
                        period_key = f"{date_obj.year}-W{date_obj.isocalendar()[1]:02d}"
                    
                    predicted_value = row.get("predicted_value")
                    if predicted_value is None:
                        predicted_value = row.get("crime_forecasts", {}).get("predicted_value", 0.0)
                    
                    lower_bound = row.get("lower_bound")
                    if lower_bound is None:
                        lower_bound = row.get("crime_forecasts", {}).get("lower_bound", 0.0)
                    
                    upper_bound = row.get("upper_bound")
                    if upper_bound is None:
                        upper_bound = row.get("crime_forecasts", {}).get("upper_bound", 0.0)
                    
                    if period_key not in forecast_groups:
                        forecast_groups[period_key] = {
                            "count": 0.0,
                            "lower_bound": 0.0,
                            "upper_bound": 0.0
                        }
                    
                    forecast_groups[period_key]["count"] += float(predicted_value or 0.0)
                    if lower_bound is not None:
                        forecast_groups[period_key]["lower_bound"] += float(lower_bound)
                    if upper_bound is not None:
                        forecast_groups[period_key]["upper_bound"] += float(upper_bound)
                except ValueError as e:
                    print(f"[DEBUG] Failed to parse forecast date '{forecast_date}': {e}")
                    continue
        
        for period_key, vals in forecast_groups.items():
            trend_points.append(TrendPoint(
                date=period_key,
                count=int(round(vals["count"])),
                is_forecast=True,
                lower_bound=int(round(vals["lower_bound"])) if vals["lower_bound"] else None,
                upper_bound=int(round(vals["upper_bound"])) if vals["upper_bound"] else None,
            ))
        
        # Sort all points by date
        trend_points.sort(key=lambda x: x.date)
        
        print(f"[DEBUG] Total trend points (historical + forecast): {len(trend_points)}")
        print(f"[DEBUG] Historical points: {len([p for p in trend_points if not p.is_forecast])}")
        print(f"[DEBUG] Forecast points: {len([p for p in trend_points if p.is_forecast])}")
        
        response = TrendDataResponse(
            data=trend_points,
            filters=TrendFilters(
                granularity=granularity,
                crime_type=crime_type,
                district=district,
            ),
            total_count=len(trend_points),
            generated_at=datetime.utcnow(),
        )
        
        # Cache the response for 12 hours
        cache.put(cache_key, response.model_dump(), expiry_in_hours=12)
        print(f"[Cache] Stored trends with filters: {granularity}, {crime_type}, {district}")
        
        return response
    except Exception as exc:
        print(f"[Warning] Failed to get trends: {exc}")
        return _empty_trend_response()


@router.get("/festival-calendar", response_model=FestivalCalendarResponse)
async def get_festival_calendar(
    crime_type: Optional[str] = None,
    district: Optional[str] = None,
    zcql=Depends(get_zcql),
    cache_segment=Depends(get_cache_segment),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Get seasonal event comparisons for Karnataka festivals.
    
    Returns crime rate in ±7-day window around festivals vs yearly baseline.
    Results are cached for 1 hour since festival dates are static.
    """
    cache = CacheService(cache_segment)
    from datetime import datetime, timedelta
    
    try:
        from analytics.trends import TrendAggregator, get_current_festival_calendar
        from schemas.analytics import SeasonalComparison
        
        print(f"[DEBUG] Festival calendar request - crime_type: {crime_type}, district: {district}")
        
        # Build cache key with filters
        cache_key = generate_cache_key("analytics:festival-calendar", crime_type, district)
        
        # Try to get from cache first
        cached_festival = cache.get(cache_key)
        if cached_festival:
            print(f"[Cache] Hit for festival calendar with filters: {crime_type}, {district}")
            return FestivalCalendarResponse(**cached_festival)
        
        # Build query with optional filters
        where_conditions = ["CaseMaster.IncidentFromDate IS NOT NULL"]
        if crime_type:
            where_conditions.append(f"CrimeSubHead.CrimeHeadName = '{crime_type}'")
        if district:
            where_conditions.append(f"District.DistrictName = '{district}'")
        
        query = f"""
            SELECT
                CaseMaster.IncidentFromDate as date,
                CrimeSubHead.CrimeHeadName as crime_type,
                District.DistrictName as district
            FROM CaseMaster
            LEFT JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
            LEFT JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
            LEFT JOIN District ON Unit.DistrictID = District.ROWID
            WHERE {' AND '.join(where_conditions)}
            LIMIT 300
        """
        
        # Execute query
        result = zcql.execute_query(query)
        rows = result if isinstance(result, list) else []
        print(f"[DEBUG] Festival query returned {len(rows)} rows")
        
        # Convert to incident data format
        incident_data = []
        for row in rows:
            # Handle nested ZCQL response structure
            case_master = row.get("CaseMaster", {})
            crime_sub_head = row.get("CrimeSubHead", {})
            district_data = row.get("District", {})
            
            date = case_master.get("IncidentFromDate")
            if not date:
                continue
            
            incident_data.append({
                "date": date,
                "crime_type": crime_sub_head.get("CrimeHeadName"),
                "district": district_data.get("DistrictName"),
            })
        print(f"[DEBUG] Processed {len(incident_data)} incident records")
        
        # Show sample incident data for debugging
        if incident_data:
            print(f"[DEBUG] Sample incident data: {incident_data[0]}")
        
        # Get dynamic festival calendar for current year
        festival_calendar = get_current_festival_calendar()
        print(f"[DEBUG] Using festival calendar: {list(festival_calendar.keys())}")
        
        # Compute seasonal comparisons for each festival
        aggregator = TrendAggregator()
        comparisons = []
        
        print(f"[DEBUG] Computing comparisons for {len(festival_calendar)} festivals")
        for festival_name, festival_info in festival_calendar.items():
            comparison = aggregator.compute_seasonal_comparison(
                incident_data, 
                festival_name,
                festival_calendar
            )
            
            print(f"[DEBUG] {festival_name}: event={comparison['event_window_count']}, baseline={comparison['baseline_window_count']}, change={comparison['percentage_change']}%")
            
            # Calculate window dates
            festival_date = datetime.strptime(festival_info["date"], "%Y-%m-%d")
            window_start = festival_date - timedelta(days=7)
            window_end = festival_date + timedelta(days=7)
            
            comparisons.append(SeasonalComparison(
                event_name=festival_name,
                event_date=festival_info["date"],
                window_start=window_start.strftime("%Y-%m-%d"),
                window_end=window_end.strftime("%Y-%m-%d"),
                event_window_count=comparison["event_window_count"],
                baseline_window_count=comparison["baseline_window_count"],
                percentage_change=comparison["percentage_change"],
            ))
        
        response = FestivalCalendarResponse(
            comparisons=comparisons,
            generated_at=datetime.utcnow(),
        )
        
        # Cache the response for 24 hours since festival dates are static
        cache.put(cache_key, response.model_dump(), expiry_in_hours=24)
        print(f"[Cache] Stored festival calendar with filters: {crime_type}, {district}")
        
        return response
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
    cache_segment=Depends(get_cache_segment),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Get offender risk scores from the risk_scores table.
    
    Returns sortable, filterable list of offenders with risk scores,
    MO tags, absconding status, and FIR count.
    Results are cached for 10 minutes based on filter combination.
    """
    cache = CacheService(cache_segment)
    try:
        from schemas.analytics import OffenderRisk, OffenderRiskFilters
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20
        
        # Build cache key from filter combination
        cache_key = generate_cache_key("analytics:offender-risk", district, min_risk_score, is_absconding, page, page_size)
        
        # Try to get from cache first
        cached_risk = cache.get(cache_key)
        if cached_risk:
            print(f"[Cache] Hit for offender risk with filters: {district}, {min_risk_score}")
            return OffenderRiskResponse(**cached_risk)
        
        # Build ZCQL query to fetch risk_scores data
        query = """
            SELECT
                ROWID,
                accused_name,
                risk_score,
                mo_tag,
                district_ids,
                is_absconding,
                fir_count
            FROM risk_scores
            WHERE 1=1
        """
        
        # Add optional filters
        if district:
            # district_ids is stored as JSON array, need to check if district is in the array
            query += f" AND district_ids LIKE '%{district}%'"
        if min_risk_score is not None:
            query += f" AND risk_score >= {min_risk_score}"
        if is_absconding is not None:
            is_absconding_val = "TRUE" if is_absconding else "FALSE"
            query += f" AND is_absconding = {is_absconding_val}"
        
        # Add sorting (default: risk_score DESC)
        query += " ORDER BY risk_score DESC"
        
        # Add pagination
        offset = (page - 1) * page_size
        query += f" LIMIT {page_size} OFFSET {offset}"
        
        # Execute query
        result = zcql.execute_query(query)
        rows = result if isinstance(result, list) else []
        
        # Convert to response format
        offenders = []
        for row in rows:
            # Parse district_ids from JSON if it's a string
            district_ids = row.get("district_ids", "[]")
            if isinstance(district_ids, str):
                try:
                    import json
                    district_ids = json.loads(district_ids)
                except:
                    district_ids = []
            
            offenders.append(OffenderRisk(
                accused_id=row.get("ROWID"),
                accused_name=row.get("accused_name", "Unknown"),
                risk_score=row.get("risk_score", 0.0),
                mo_tag=row.get("mo_tag"),
                district_ids=district_ids if isinstance(district_ids, list) else [],
                is_absconding=row.get("is_absconding", False),
                fir_count=row.get("fir_count", 0),
            ))
        
        # Get total count for pagination (without LIMIT/OFFSET)
        count_query = """
            SELECT COUNT(*) as total
            FROM risk_scores
            WHERE 1=1
        """
        
        if district:
            count_query += f" AND district_ids LIKE '%{district}%'"
        if min_risk_score is not None:
            count_query += f" AND risk_score >= {min_risk_score}"
        if is_absconding is not None:
            is_absconding_val = "TRUE" if is_absconding else "FALSE"
            count_query += f" AND is_absconding = {is_absconding_val}"
        
        count_result = zcql.execute_query(count_query)
        total_count = count_result[0].get("total", 0) if count_result else 0
        
        response = OffenderRiskResponse(
            offenders=offenders,
            total_count=total_count,
            page=page,
            page_size=page_size,
            filters=OffenderRiskFilters(
                district=district,
                min_risk_score=min_risk_score,
                is_absconding=is_absconding,
            ),
            generated_at=datetime.utcnow(),
        )
        
        # Cache the response for 4 hours
        cache.put(cache_key, response.model_dump(), expiry_in_hours=4)
        print(f"[Cache] Stored offender risk with filters: {district}, {min_risk_score}")
        
        return response
    except Exception as exc:
        print(f"[Warning] Failed to get offender risk: {exc}")
        return _empty_offender_risk_response()


@router.get("/socioeconomic", response_model=SocioeconomicResponse)
async def get_socioeconomic(
    zcql=Depends(get_zcql),
    cache_segment=Depends(get_cache_segment),
    user=Depends(require_role(["analyst", "supervisor"])),
):
    """
    Get district-level socioeconomic indicators.
    
    Returns literacy rate, urbanization percentage, and population
    for Karnataka districts. Role-gated to Analyst/Supervisor only.
    Server-side enforcement - Investigators receive 403.
    Results are cached for 24 hours since data is static.
    """
    cache = CacheService(cache_segment)
    
    try:
        from schemas.analytics import DistrictSocioeconomic
        import json
        import os
        
        # Build cache key
        cache_key = generate_cache_key("analytics:socioeconomic", "district-data")
        
        # Try to get from cache first
        cached_socio = cache.get(cache_key)
        if cached_socio:
            print(f"[Cache] Hit for socioeconomic data")
            return SocioeconomicResponse(**cached_socio)
        
        # Load static socioeconomic data from JSON file
        json_path = os.path.join(os.path.dirname(__file__), "..", "data", "district_socioeconomic.json")
        
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"[Warning] Socioeconomic data file not found at {json_path}")
            return SocioeconomicResponse(
                districts=[],
                generated_at=datetime.utcnow(),
            )
        
        # Convert to response format
        districts = [
            DistrictSocioeconomic(
                district=d["district"],
                literacy_rate=d["literacy_rate"],
                urbanization_percentage=d["urbanization_percentage"],
                population=d["population"],
            )
            for d in data.get("districts", [])
        ]
        
        response = SocioeconomicResponse(
            districts=districts,
            generated_at=datetime.utcnow(),
        )
        
        # Cache the response for 24 hours since data is static
        cache.put(cache_key, response.model_dump(), expiry_in_hours=24)
        print(f"[Cache] Stored socioeconomic data")
        
        return response
    except Exception as exc:
        print(f"[Warning] Failed to get socioeconomic data: {exc}")
        return SocioeconomicResponse(
            districts=[],
            generated_at=datetime.utcnow(),
        )


@router.get("/test/insert-forecasts")
async def insert_test_forecasts(
    zcql=Depends(get_zcql),
):
    """
    Test route to insert sample forecast data into crime_forecasts table.
    This is for development/testing purposes only.
    """
    try:
        # Generate sample forecast data for next 30 days
        crime_categories = ["Murder", "Theft", "Robbery", "Assault", "Vehicle Theft"]
        base_date = datetime.now()
        
        inserted_count = 0
        
        for category in crime_categories:
            for day_offset in range(30):  # 30 days forecast
                forecast_date = base_date + timedelta(days=day_offset)
                
                # Generate realistic forecast values
                base_value = {
                    "Murder": 2,
                    "Theft": 15,
                    "Robbery": 8,
                    "Assault": 12,
                    "Vehicle Theft": 6
                }[category]
                
                # Add some variation
                predicted_value = base_value + (day_offset % 5) - 2
                lower_bound = max(0, predicted_value - 3)
                upper_bound = predicted_value + 3
                
                # ZCQL INSERT statement
                insert_query = f"""
                    INSERT INTO crime_forecasts (
                        crime_category, 
                        forecast_date, 
                        predicted_value, 
                        lower_bound, 
                        upper_bound, 
                        generated_at, 
                        forecast_days
                    ) VALUES (
                        '{category}',
                        '{forecast_date.strftime('%Y-%m-%d')}',
                        {predicted_value},
                        {lower_bound},
                        {upper_bound},
                        '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}',
                        30
                    )
                """
                
                zcql.execute_query(insert_query)
                inserted_count += 1
        
        return {
            "success": True,
            "message": f"Successfully inserted {inserted_count} forecast records",
            "categories": crime_categories,
            "days_forecasted": 30,
            "total_records": inserted_count
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to insert forecasts: {str(e)}"
        }
