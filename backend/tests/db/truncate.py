"""
Drishti — Truncate All Tables
================================
Deletes all rows from every table in reverse FK dependency order.
Child tables must be cleared before parent tables to avoid FK violations.

TRUNCATION ORDER (reverse of insertion order):
  Derived tables first (no FKs to source), then child → parent.

  1. audit_logs           (derived, no FK)
  2. conversations        (derived, no FK)
  3. risk_scores          (derived, no FK)
  4. crime_alerts         (derived, FK → District, CrimeSubHead — clear first anyway)
  5. dashboard_stats      (derived, no FK)
  6. ChargesheetDetails   (FK → CaseMaster, Employee)
  7. ArrestSurrender      (FK → CaseMaster, Accused, Employee, Court, State, District, Unit)
  8. ActSectionAssociation(FK → CaseMaster, Act, Section)
  9. ComplainantDetails   (FK → CaseMaster, OccupationMaster, ReligionMaster, CasteMaster)
  10. Victim              (FK → CaseMaster)
  11. Accused             (FK → CaseMaster)
  12. CaseMaster          (FK → Employee, Unit, CaseCategory, GravityOffence, CrimeHead, CrimeSubHead, CaseStatusMaster, Court)
  13. CrimeHeadActSection (FK → CrimeHead, Act)
  14. Section             (FK → Act)
  15. Act                 (no FK — but Section depends on it)
  16. CrimeSubHead        (FK → CrimeHead)
  17. CrimeHead           (no FK)
  18. CaseStatusMaster    (no FK)
  19. CasteMaster         (no FK)
  20. ReligionMaster      (no FK)
  21. OccupationMaster    (no FK)
  22. ChargesheetDetails  already done above
  23. Employee            (FK → District, Unit, Rank, Designation)
  24. Designation         (no FK)
  25. Rank                (no FK)
  26. Court               (FK → District, State)
  27. Unit                (FK → UnitType, State, District)
  28. UnitType            (no FK)
  29. CaseCategory        (no FK)
  30. GravityOffence      (no FK)
  31. District            (FK → State)
  32. State               (no FK)

HOW TO RUN:
  Hit GET /test/truncate while your FastAPI dev server is running.

  ⚠️  WARNING: This deletes ALL rows from ALL tables permanently.
      Use only in local dev / test environments.
      Never run against production data.
"""

from fastapi import FastAPI, Request, APIRouter
import zcatalyst_sdk

router = APIRouter(
    prefix="/db",
    tags=["truncate"]
)


def get_datastore(req: Request):
    """Initialize Catalyst SDK and return datastore instance."""
    catalyst_app = zcatalyst_sdk.initialize(req=req)
    return catalyst_app.datastore()


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


@router.get("/test/truncate")
def truncate_all(request: Request):
    """
    Clears all rows from all Drishti tables in safe FK order.
    Hit GET /test/truncate to run.

      DESTRUCTIVE — deletes everything. Dev/test only.
    """
    ds = get_datastore(request)
    results = []

    print("\n========== PRISM TABLE TRUNCATION ==========")
    print("  WARNING: Deleting all rows from all tables")
    print("===============================================\n")

    # ─────────────────────────────────────────────────────────────────
    # PHASE 1: Derived / platform tables (no FKs to source tables)
    # Clear these first — they reference source tables loosely
    # ─────────────────────────────────────────────────────────────────
    print("Phase 1: Derived tables")
    for table in [
        "audit_logs",
        "conversations",
        "risk_scores",
        "crime_alerts",
        "dashboard_stats",
    ]:
        results.append(truncate_table(ds, table))

    # ─────────────────────────────────────────────────────────────────
    # PHASE 2: Deepest child tables of CaseMaster
    # These depend on CaseMaster and must go before it
    # ─────────────────────────────────────────────────────────────────
    print("\n Phase 2: CaseMaster children ")
    for table in [
        "ChargesheetDetails",    # FK → CaseMaster, Employee
        "ArrestSurrender",       # FK → CaseMaster, Accused, Employee, Court, State, District, Unit
        "ActSectionAssociation", # FK → CaseMaster, Act, Section
        "ComplainantDetails",    # FK → CaseMaster, OccupationMaster, ReligionMaster, CasteMaster
        "Victim",                # FK → CaseMaster
        "Accused",               # FK → CaseMaster (must come after ArrestSurrender which refs Accused)
    ]:
        results.append(truncate_table(ds, table))

    # ─────────────────────────────────────────────────────────────────
    # PHASE 3: CaseMaster itself
    # All children cleared — now safe to clear the parent
    # ─────────────────────────────────────────────────────────────────
    print("\n Phase 3: CaseMaster (central table) ")
    results.append(truncate_table(ds, "CaseMaster"))

    # ─────────────────────────────────────────────────────────────────
    # PHASE 4: Legal classification tables
    # CrimeHeadActSection depends on CrimeHead and Act
    # Section depends on Act
    # CrimeSubHead depends on CrimeHead
    # ─────────────────────────────────────────────────────────────────
    print("\n Phase 4: Legal classification tables ")
    for table in [
        "CrimeHeadActSection",  # FK → CrimeHead, Act — must go before both
        "Section",              # FK → Act
        "ActSectionAssociation",# already cleared in Phase 2 — safe to re-attempt
        "Act",                  # no FK — but Section depends on it
        "CrimeSubHead",         # FK → CrimeHead
        "CrimeHead",            # no FK — CrimeSubHead + CrimeHeadActSection depend on it
    ]:
        results.append(truncate_table(ds, table))

    # ─────────────────────────────────────────────────────────────────
    # PHASE 5: Lookup tables
    # Referenced by ComplainantDetails and CaseMaster — now safe
    # ─────────────────────────────────────────────────────────────────
    print("\n Phase 5: Lookup / reference tables ")
    for table in [
        "CaseStatusMaster",   # referenced by CaseMaster.CaseStatusID
        "CaseCategory",       # referenced by CaseMaster.CaseCategoryID
        "GravityOffence",     # referenced by CaseMaster.GravityOffenceID
        "CasteMaster",        # referenced by ComplainantDetails.CasteID
        "ReligionMaster",     # referenced by ComplainantDetails.ReligionID
        "OccupationMaster",   # referenced by ComplainantDetails.OccupationID
    ]:
        results.append(truncate_table(ds, table))

    # ─────────────────────────────────────────────────────────────────
    # PHASE 6: Employee and its dependencies
    # Employee is referenced by CaseMaster and ArrestSurrender (cleared)
    # Employee itself depends on District, Unit, Rank, Designation
    # ─────────────────────────────────────────────────────────────────
    print("\n Phase 6: Employee tables ")
    for table in [
        "Employee",      # FK → District, Unit, Rank, Designation
        "Designation",   # no FK
        "Rank",          # no FK
    ]:
        results.append(truncate_table(ds, table))

    # ─────────────────────────────────────────────────────────────────
    # PHASE 7: Geography tables
    # Court depends on District and State
    # Unit depends on UnitType, State, District
    # District depends on State
    # ─────────────────────────────────────────────────────────────────
    print("\n Phase 7: Geography & org tables ")
    for table in [
        "Court",      # FK → District, State
        "Unit",       # FK → UnitType, State, District
        "UnitType",   # no FK
        "District",   # FK → State
        "State",      # no FK — root of geography hierarchy
    ]:
        results.append(truncate_table(ds, table))

    # ─────────────────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────────────────
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