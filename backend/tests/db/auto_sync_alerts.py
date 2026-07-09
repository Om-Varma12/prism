"""
PRISM — Auto-Sync Dashboard Stats Alert Count
============================================
Automatically syncs dashboard_stats.active_alert_count with actual unacknowledged alerts from crime_alerts.
This should be called periodically (e.g., every 5 minutes) to keep the KPI card accurate.
"""

from fastapi import Request, APIRouter
import zcatalyst_sdk
from datetime import datetime, timedelta
from core.database import get_datastore, get_zcql

router = APIRouter(prefix="/db", tags=["auto-sync"])


def sync_alert_count(zcql, datastore):
    """Reusable function to sync alert count. Can be called from endpoint or scheduler."""
    try:
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
        
        print(f"[Auto-Sync] Unacknowledged alerts count: {unacknowledged_count}")
        
        # Step 2: Get current dashboard_stats row
        query = """
            SELECT ROWID, active_alert_count, computed_at 
            FROM dashboard_stats 
            ORDER BY computed_at DESC 
            LIMIT 1
        """
        result = zcql.execute_query(query)
        
        if not result:
            print("[Auto-Sync] No dashboard_stats row found")
            return {"status": "error", "message": "No dashboard_stats row found"}
        
        stats_row = result[0].get('dashboard_stats', result[0])
        stats_row_id = stats_row.get('ROWID')
        old_count = stats_row.get('active_alert_count', 0)
        
        print(f"[Auto-Sync] Current dashboard_stats.active_alert_count: {old_count}")
        
        # Step 3: Update if count changed
        if old_count != unacknowledged_count:
            print(f"[Auto-Sync] Updating to: {unacknowledged_count}")
            table = datastore.table('dashboard_stats')
            update_data = {
                'ROWID': stats_row_id,
                'active_alert_count': unacknowledged_count
            }
            table.update_row(update_data)
            
            print(f"[Auto-Sync] Synced from {old_count} to {unacknowledged_count}")
            return {
                "status": "success",
                "old_count": old_count,
                "new_count": unacknowledged_count,
                "synced": True
            }
        else:
            print(f"[Auto-Sync] No change needed (count: {unacknowledged_count})")
            return {
                "status": "success",
                "old_count": old_count,
                "new_count": unacknowledged_count,
                "synced": False
            }
        
    except Exception as e:
        print(f"[Auto-Sync] Error: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/test/auto-sync-alerts")
def auto_sync_alerts(request: Request):
    """Manual trigger for auto-sync (for testing)."""
    zcql = get_zcql(request)
    datastore = get_datastore(request)
    result = sync_alert_count(zcql, datastore)
    
    if result["status"] == "success":
        if result["synced"]:
            return {
                "status": "success",
                "message": f"Synced dashboard_stats.active_alert_count from {result['old_count']} to {result['new_count']}",
                "old_count": result["old_count"],
                "new_count": result["new_count"],
                "synced": True
            }
        else:
            return {
                "status": "success",
                "message": f"No sync needed (count already: {result['new_count']})",
                "old_count": result["old_count"],
                "new_count": result["new_count"],
                "synced": False
            }
    else:
        return result
