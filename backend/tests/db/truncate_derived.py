"""
PRISM — Truncate Derived Tables
================================
Deletes all rows from Drishti-derived tables:
- dashboard_stats
- crime_alerts
- risk_scores
- conversations
- audit_logs

These tables have no FK dependencies on source tables, so they can be
truncated independently without affecting the main KSP schema.

HOW TO RUN:
  Hit GET /db/tests/truncate_derived while your FastAPI dev server is running.

  ⚠️  WARNING: This deletes ALL rows from derived tables permanently.
      Use only in local dev / test environments.
"""

from fastapi import Request, APIRouter
from core.database import get_datastore

router = APIRouter(prefix="/db", tags=["truncate-derived"])


def truncate_table(datastore, table_name: str) -> dict:
    """
    Fetches all rows from a table and deletes them by ROWID.
    Catalyst DataStore doesn't have a native TRUNCATE — we fetch all
    row IDs and delete in bulk.
    """
    try:
        table = datastore.table(table_name)

        row_ids = []
        next_token = None

        while True:
            response = table.get_paged_rows(
                next_token=next_token,
                max_rows=200
            )
            
            rows = response.get("data", [])

            for row in rows:
                if "ROWID" in row:
                    row_ids.append(int(row["ROWID"]))

            if not response.get("more_records", False):
                break

            next_token = response.get("next_token")

        if not row_ids:
            print(f"    {table_name}: already empty")
            return {"table": table_name, "status": "empty", "deleted": 0}

        deleted = 0
        for row_id in row_ids:
            table.delete_row(row_id)
            deleted += 1

        print(f"     {table_name}: deleted {deleted} rows")
        return {"table": table_name, "status": "ok", "deleted": deleted}

    except Exception as e:
        print(f"    {table_name}: FAILED — {str(e)}")
        return {"table": table_name, "status": "error", "error": str(e)}


@router.get("/tests/truncate-derived")
def truncate_derived(request: Request):
    """
    Clears all rows from derived tables.
    Hit GET /db/tests/truncate-derived to run.

      DESTRUCTIVE — deletes all derived table data. Dev/test only.
    """
    ds = get_datastore(request)
    results = []

    print("\n========== PRISM DERIVED TABLES TRUNCATION ==========")
    print("  WARNING: Deleting all rows from derived tables")
    print("===================================================\n")

    # Truncate all derived tables
    for table in [
        "audit_logs",
        "conversations",
        "risk_scores",
        "crime_alerts",
        "dashboard_stats",
    ]:
        results.append(truncate_table(ds, table))

    # Summary
    total_deleted = sum(r.get("deleted", 0) for r in results)
    success_count = sum(1 for r in results if r["status"] in ("ok", "empty"))
    failed = [r for r in results if r["status"] == "error"]

    print(f"\n========== TRUNCATION COMPLETE ==========")
    print(f" Tables processed: {success_count}/{len(results)}")
    print(f"  Total rows deleted: {total_deleted}")
    if failed:
        print(f" Failed tables: {[r['table'] for r in failed]}")
    print("=========================================\n")

    return {
        "status": "complete",
        "tables_processed": success_count,
        "total_rows_deleted": total_deleted,
        "failed": failed,
        "results": results
    }
