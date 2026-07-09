"""
PRISM — Update Alert Acknowledgment Status
============================================
Updates 5 most recent alerts to is_acknowledged = false to make them active.
"""

from fastapi import Request, APIRouter
import zcatalyst_sdk
from datetime import datetime, timedelta
from core.database import get_datastore, get_zcql

router = APIRouter(prefix="/db", tags=["alerts"])


@router.get("/test/update-alerts-acknowledgment")
def update_alerts_acknowledgment(request: Request):
    """Update 5 most recent alerts to is_acknowledged = false."""
    try:
        zcql = get_zcql(request)
        datastore = get_datastore(request)
        
        # Step 1: Get current alerts ordered by created_at DESC
        query = """
            SELECT ROWID, is_acknowledged, created_at 
            FROM crime_alerts 
            ORDER BY created_at DESC 
            LIMIT 5
        """
        result = zcql.execute_query(query)
        
        if not result:
            return {"status": "error", "message": "No alerts found in crime_alerts table"}
        
        alerts = result[0].get('crime_alerts', result[0])
        print(f"Found {len(alerts)} alerts to update")
        
        # Step 2: Update each alert to is_acknowledged = false
        table = datastore.table('crime_alerts')
        updated_count = 0
        
        for alert in alerts:
            row_id = alert.get('ROWID')
            current_status = alert.get('is_acknowledged')
            
            if current_status is None or current_status == 1:
                # Update the row
                update_data = {
                    'ROWID': row_id,
                    'is_acknowledged': 0
                }
                table.update_row(update_data)
                updated_count += 1
                print(f"  Updated alert ROWID {row_id}: is_acknowledged = 0")
            else:
                print(f"  Skipped alert ROWID {row_id}: already 0")
        
        return {
            "status": "success",
            "message": f"Updated {updated_count} alerts to is_acknowledged = false",
            "updated_count": updated_count
        }
        
    except Exception as e:
        print(f"Error updating alerts: {e}")
        return {"status": "error", "message": str(e)}
