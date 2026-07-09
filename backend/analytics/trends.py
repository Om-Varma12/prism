from datetime import datetime

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
