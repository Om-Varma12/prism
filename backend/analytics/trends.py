from datetime import datetime
from typing import Optional, Literal

DISTRICT_CENTROIDS = {
    "Bengaluru Urban":  {"lat": 12.9716, "lng": 77.5946},
    "Mysuru":           {"lat": 12.2958, "lng": 76.6394},
    "Dakshina Kannada": {"lat": 12.8703, "lng": 74.8428},
    "Belagavi":         {"lat": 15.8497, "lng": 74.4977},
    "Ballari":          {"lat": 15.1394, "lng": 76.9214},
    "Kalaburagi":       {"lat": 17.3297, "lng": 76.8343},
    "Hubballi-Dharwad": {"lat": 15.3647, "lng": 75.1240},
    "Shivamogga":       {"lat": 13.9299, "lng": 75.5681},
    "Tumakuru":         {"lat": 13.3379, "lng": 77.1173},
    "Hassan":           {"lat": 13.0033, "lng": 76.1004},
}

TREND_CATEGORIES = {
    "Robbery":       ["Robbery", "Chain Snatching"],
    "Theft":         ["Theft", "Burglary"],
    "Assault":       ["Murder", "Attempt to Murder", "Assault"],
    "Vehicle Crime": ["Vehicle Theft"],
    "Cyber Crime":   ["Online Fraud", "Cyber Crime"],
}

# Karnataka Festival Calendar (dynamic calculation)
def get_festival_dates(year: int) -> dict:
    """
    Calculate festival dates dynamically for a given year.
    
    Args:
        year: Year to calculate festivals for
        
    Returns:
        Dictionary of festival names with their dates
    """
    from datetime import date
    
    # Fixed date festivals
    festivals = {
        "Republic Day": date(year, 1, 26),
        "Independence Day": date(year, 8, 15),
        "Christmas": date(year, 12, 25),
        "Makara Sankranti": date(year, 1, 14),  # Solar festival
    }
    
    # Religious festivals (simplified calculations - can be enhanced with proper libraries)
    # Note: These are approximate dates. For production, consider using libraries like 'holidays'
    # or proper lunar calendar calculations for religious festivals.
    
    # Ugadi (Kannada New Year) - typically March/April
    festivals["Ugadi"] = date(year, 4, 9) if year == 2024 else date(year, 4, 9)
    
    # Ganesh Chaturthi - 4th day of waxing moon in Bhadrapada (typically September)
    festivals["Ganesh Chaturthi"] = date(year, 9, 7) if year == 2024 else date(year, 9, 19)
    
    # Dasara (Dussehra) - 10th day of Navratri (typically October)
    festivals["Dasara"] = date(year, 10, 12) if year == 2024 else date(year, 10, 2)
    
    # Diwali - varies based on lunar calendar (typically October/November)
    festivals["Diwali"] = date(year, 11, 1) if year == 2024 else date(year, 10, 20)
    
    # Eid dates (approximate - these vary based on moon sighting)
    # Can be enhanced with proper Islamic calendar calculation
    festivals["Eid al-Fitr"] = date(year, 4, 10) if year == 2024 else date(year, 3, 30)
    festivals["Eid al-Adha"] = date(year, 6, 17) if year == 2024 else date(year, 6, 6)
    
    # Convert to required format
    return {
        name: {
            "date": festival_date.strftime("%Y-%m-%d"),
            "month": festival_date.month,
            "day": festival_date.day
        }
        for name, festival_date in festivals.items()
    }

def get_current_festival_calendar() -> dict:
    """Get festival calendar for current year."""
    from datetime import datetime
    current_year = datetime.now().year
    return get_festival_dates(current_year)

# Keep old constant for backward compatibility (deprecated)
FESTIVAL_CALENDAR = get_current_festival_calendar()

Granularity = Literal["month", "week"]


def normalize(counts: list[int]) -> list[int]:
    max_val = max(counts) if max(counts) > 0 else 1
    return [int((c / max_val) * 100) for c in counts]

def compute_trend(current: int, prior: int) -> tuple[float, str]:
    if prior == 0:
        if current > 0:
            return (100.0, "up")
        return (0.0, "flat")
    change = ((current - prior) / prior) * 100
    trend = "up" if change > 2 else "down" if change < -2 else "flat"
    return (round(change, 1), trend)

def format_time_ago(created_at: datetime) -> str:
    diff = datetime.utcnow() - created_at
    hours = int(diff.total_seconds() / 3600)
    if hours < 1:
        return f"{int(diff.total_seconds() / 60)}m ago"
    if hours < 24:
        return f"{hours}h ago"
    return f"{diff.days}d ago"


class TrendAggregator:
    """
    Aggregates crime data by time period (month/week) for trend analysis.
    """

    def __init__(self):
        pass

    def aggregate_trends(
        self,
        incident_data: list[dict],
        granularity: Granularity = "month",
    ) -> list[dict]:
        """
        Aggregate incident data by time period.
        
        Args:
            incident_data: List of incident dictionaries with date and crime_type
            granularity: 'month' or 'week'
        
        Returns:
            List of aggregated data points with date, count, crime_type
        """
        if not incident_data:
            return []

        # Group by date period and crime type
        from collections import defaultdict
        grouped = defaultdict(lambda: defaultdict(int))
        
        for incident in incident_data:
            date_str = incident.get("date")
            crime_type = incident.get("crime_type", "Unknown")
            
            if not date_str:
                continue
            
            # Parse date and format based on granularity
            try:
                # Try parsing with time component first
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # Fall back to date-only format
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                
                if granularity == "month":
                    period_key = date_obj.strftime("%Y-%m")
                else:  # week
                    # Get ISO week number
                    period_key = f"{date_obj.year}-W{date_obj.isocalendar()[1]:02d}"
                
                grouped[period_key][crime_type] += 1
            except ValueError as e:
                print(f"[DEBUG] Date parsing failed for '{date_str}': {e}")
                continue

        # Convert to list of data points
        results = []
        for period_key, crime_counts in grouped.items():
            for crime_type, count in crime_counts.items():
                results.append({
                    "date": period_key,
                    "count": count,
                    "crime_type": crime_type,
                })

        # Sort by date
        results.sort(key=lambda x: x["date"])

        return results

    def compute_seasonal_comparison(
        self,
        incident_data: list[dict],
        festival_name: str,
        festival_calendar: dict = None,
    ) -> dict:
        """
        Compute crime count comparison for festival window vs baseline.
        
        Args:
            incident_data: List of incident dictionaries with date
            festival_name: Name of festival
            festival_calendar: Optional festival calendar (uses current year if not provided)
        
        Returns:
            Dictionary with event_window_count, baseline_window_count, percentage_change
        """
        if festival_calendar is None:
            festival_calendar = get_current_festival_calendar()
        
        if festival_name not in festival_calendar:
            return {
                "event_window_count": 0,
                "baseline_window_count": 0,
                "percentage_change": 0.0,
            }

        festival = festival_calendar[festival_name]
        festival_date = datetime.strptime(festival["date"], "%Y-%m-%d")
        
        # Calculate ±7-day window around festival
        from datetime import timedelta
        window_start = festival_date - timedelta(days=7)
        window_end = festival_date + timedelta(days=7)
        
        # Count crimes in event window
        event_window_count = 0
        for incident in incident_data:
            date_str = incident.get("date")
            if not date_str:
                continue
            try:
                incident_date = datetime.strptime(date_str, "%Y-%m-%d")
                if window_start <= incident_date <= window_end:
                    event_window_count += 1
            except ValueError:
                continue
        
        # Calculate baseline (same 14-day window in different month)
        # Use month-3 as baseline (e.g., October festival → July baseline)
        baseline_start = window_start.replace(month=((window_start.month - 4) % 12) + 1)
        baseline_end = window_end.replace(month=((window_end.month - 4) % 12) + 1)
        
        baseline_window_count = 0
        for incident in incident_data:
            date_str = incident.get("date")
            if not date_str:
                continue
            try:
                incident_date = datetime.strptime(date_str, "%Y-%m-%d")
                if baseline_start <= incident_date <= baseline_end:
                    baseline_window_count += 1
            except ValueError:
                continue
        
        # Calculate percentage change
        if baseline_window_count == 0:
            percentage_change = 100.0 if event_window_count > 0 else 0.0
        else:
            percentage_change = ((event_window_count - baseline_window_count) / baseline_window_count) * 100
        
        return {
            "event_window_count": event_window_count,
            "baseline_window_count": baseline_window_count,
            "percentage_change": round(percentage_change, 1),
        }
