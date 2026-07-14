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

# Karnataka Festival Calendar (static dates for 2024-2025)
FESTIVAL_CALENDAR = {
    "Dasara": {"date": "2024-10-12", "month": 10, "day": 12},
    "Diwali": {"date": "2024-11-01", "month": 11, "day": 1},
    "Ugadi": {"date": "2024-04-09", "month": 4, "day": 9},
    "Makara Sankranti": {"date": "2025-01-14", "month": 1, "day": 14},
    "Ganesh Chaturthi": {"date": "2024-09-07", "month": 9, "day": 7},
    "Eid al-Fitr": {"date": "2024-04-10", "month": 4, "day": 10},
    "Eid al-Adha": {"date": "2024-06-17", "month": 6, "day": 17},
    "Christmas": {"date": "2024-12-25", "month": 12, "day": 25},
    "Republic Day": {"date": "2025-01-26", "month": 1, "day": 26},
    "Independence Day": {"date": "2024-08-15", "month": 8, "day": 15},
}

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
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                if granularity == "month":
                    period_key = date_obj.strftime("%Y-%m")
                else:  # week
                    # Get ISO week number
                    period_key = f"{date_obj.year}-W{date_obj.isocalendar()[1]:02d}"
                
                grouped[period_key][crime_type] += 1
            except ValueError:
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
    ) -> dict:
        """
        Compute crime count comparison for festival window vs baseline.
        
        Args:
            incident_data: List of incident dictionaries with date
            festival_name: Name of festival from FESTIVAL_CALENDAR
        
        Returns:
            Dictionary with event_window_count, baseline_window_count, percentage_change
        """
        if festival_name not in FESTIVAL_CALENDAR:
            return {
                "event_window_count": 0,
                "baseline_window_count": 0,
                "percentage_change": 0.0,
            }

        festival = FESTIVAL_CALENDAR[festival_name]
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
