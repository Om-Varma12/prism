"""
Add metadata columns to conversations table for storing full response data.

This script adds the following columns to the conversations table:
- table_data_json: JSON string containing table data
- entities_json: JSON string containing mentioned entities
- follow_ups_json: JSON string containing follow-up suggestions
- sources_json: JSON string containing data sources
- scanned_records: Integer count of scanned records
"""
from fastapi import Request, APIRouter
from core.database import get_zcql

router = APIRouter(prefix="/api/db", tags=["schema"])


@router.get("/tests/add-conversation-metadata-columns")
async def add_conversation_metadata_columns(request: Request):
    """Add metadata columns to conversations table."""
    zcql = get_zcql(request)
    
    results = {"status": "ok", "columns_added": [], "errors": []}
    
    # Add columns using ALTER TABLE
    columns = [
        "ADD COLUMN table_data_json TEXT",
        "ADD COLUMN entities_json TEXT", 
        "ADD COLUMN follow_ups_json TEXT",
        "ADD COLUMN sources_json TEXT",
        "ADD COLUMN scanned_records INTEGER"
    ]
    
    for column_sql in columns:
        try:
            query = f"ALTER TABLE conversations {column_sql}"
            zcql.execute_query(query)
            column_name = column_sql.split()[-1]
            results["columns_added"].append(column_name)
        except Exception as e:
            # Column might already exist, check error message
            error_msg = str(e).lower()
            if "duplicate" in error_msg or "already exists" in error_msg:
                column_name = column_sql.split()[-1]
                results["columns_added"].append(f"{column_name} (already exists)")
            else:
                results["errors"].append(f"{column_sql}: {str(e)}")
    
    return results
