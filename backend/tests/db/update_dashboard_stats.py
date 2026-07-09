"""
PRISM — Update Dashboard Stats Alert Count
============================================
Updates dashboard_stats.active_alert_count to match actual unacknowledged alerts.
"""

from fastapi import Request, APIRouter
import zcatalyst_sdk
from datetime import datetime, timedelta
from core.database import get_datastore, get_zcql

router = APIRouter(prefix="/db", tags=["dashboard-stats"])


@router.get("/test/update-dashboard-stats")
def update_dashboard_stats(request: Request):
    """Update dashboard_stats.active_alert_count to match actual unacknowledged alerts."""
    try:
        zcql = get_zcql(request)
        datastore = get_datastore(request)
        
        # Step 1: Count unacknowledged alerts
        query = """
            SELECT COUNT(ROWID) as count 
            FROM crime_alerts 
            WHERE is_acknowledged = 0 OR is_acknowledged IS NULL
        """
        result = zcql.execute_query(query)
        
        if not result:
            unacknowledged_count = 0
        else:
            unacknowledged_count = result[0].get('count', 0)
        
        print(f"Unacknowledged alerts count: {unacknowledged_count}")
        
        # Step 2: Update the most recent dashboard_stats row
        query = """
            SELECT ROWID, active_alert_count, computed_at 
            FROM dashboard_stats 
            ORDER BY computed_at DESC 
            LIMIT 1
        """
        result = zcql.execute_query(query)
        
        if not result:
            return {"status": "error", "message": "No dashboard_stats row found"}
        
        stats_row = result[0].get('dashboard_stats', result[0])
        stats_row_id = stats_row.get('ROWID')
        old_count = stats_row.get('active_alert_count', 0)
        
        print(f"Current dashboard_stats.active_alert_count: {old_count}")
        print(f"Updating to: {unacknowledged_count}")
        
        # Step 3: Update the row (only update active_alert_count, keep existing computed_at)
        table = datastore.table('dashboard_stats')
        update_data = {
            'ROWID': stats_row_id,
            'active_alert_count': unacknowledged_count
        }
        table.update_row(update_data)
        
        return {
            "status": "success",
            "message": f"Updated dashboard_stats.active_alert_count from {old_count} to {unacknowledged_count}",
            "old_count": old_count,
            "new_count": unacknowledged_count
        }
        
    except Exception as e:
        print(f"Error updating dashboard_stats: {e}")
        return {"status": "error", "message": str(e)}
