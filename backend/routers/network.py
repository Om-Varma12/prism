"""
Network Explorer API routes.

These endpoints are scaffolded with valid response shapes first so the frontend
can integrate against a stable contract while graph construction is built out.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends

from agents.network_agent.graph_builder import NetworkGraphBuilder
from core.database import get_zcql
from core.security import require_role
from schemas.network import (
    AccusedProfileResponse,
    DensestNode,
    GraphMetadata,
    GraphResponse,
    GraphView,
    SearchResponse,
)


router = APIRouter(prefix="/api/network", tags=["network"])


def _empty_graph_response() -> GraphResponse:
    return GraphResponse(
        nodes=[],
        edges=[],
        metadata=GraphMetadata(
            total_nodes=0,
            total_edges=0,
            largest_cluster_size=0,
            num_clusters=0,
            repeat_offender_count=0,
            densest_node=DensestNode(),
            generated_at=datetime.utcnow(),
        ),
    )


@router.get("/graph", response_model=GraphResponse)
async def get_network_graph(
    crime_type: Optional[str] = None,
    district: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    view: GraphView = "all",
    zcql=Depends(get_zcql),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Return the co-accused network graph.

    Builds the co-accused graph from Catalyst data with optional filters.
    Filters are applied as ZCQL WHERE clauses to limit the result set.
    """
    try:
        return NetworkGraphBuilder(zcql).build_graph(
            crime_type=crime_type,
            district=district,
            date_from=date_from,
            date_to=date_to,
            view=view,
        )
    except Exception as exc:
        print(f"[Warning] Failed to build network graph: {exc}")
        return _empty_graph_response()


@router.get("/profile/{accused_id}", response_model=AccusedProfileResponse)
async def get_accused_profile(
    accused_id: int,
    zcql=Depends(get_zcql),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Return a single accused profile with FIR history, associates, and risk scoring.
    """
    try:
        # Query accused basic info with FIR history
        accused_query = f"""
            SELECT
                Accused.AccusedMasterID,
                Accused.AccusedName,
                Accused.AgeYear,
                Accused.GenderID,
                CaseMaster.ROWID as CaseMaster_ROWID,
                CaseMaster.CaseMasterID,
                CaseMaster.CrimeNo,
                CaseMaster.IncidentFromDate,
                CrimeSubHead.CrimeHeadName,
                District.DistrictName,
                ArrestSurrender.ROWID as Arrest_ROWID
            FROM Accused
            INNER JOIN CaseMaster ON Accused.CaseMasterID = CaseMaster.ROWID
            LEFT JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
            LEFT JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
            LEFT JOIN District ON Unit.DistrictID = District.ROWID
            LEFT JOIN ArrestSurrender ON Accused.ROWID = ArrestSurrender.AccusedID
            WHERE Accused.AccusedMasterID = {accused_id}
            LIMIT 1000
        """
        accused_result = zcql.execute_query(accused_query)
        accused_rows = accused_result if isinstance(accused_result, list) else []
        
        if not accused_rows:
            return AccusedProfileResponse(
                accused_id=accused_id,
                name="Unknown accused",
                fir_count=0,
                firs=[],
                co_accused=[],
                crime_types=[],
                risk_score=0,
                is_absconding=False,
            )
        
        # Extract basic info from first row
        first_row = accused_rows[0]
        name = _value(first_row, "Accused", "AccusedName", "AccusedName") or "Unknown accused"
        age = _to_int(_value(first_row, "Accused", "AgeYear", "AgeYear"))
        gender_id = _value(first_row, "Accused", "GenderID", "GenderID")
        gender = _gender_label(gender_id)
        
        # Check if absconding (no arrest record)
        is_absconding = _value(first_row, "ArrestSurrender", "ROWID", "Arrest_ROWID") is None
        
        # Build FIR summary list
        firs = []
        crime_type_counts = {}
        last_seen_date = None
        
        for row in accused_rows:
            case_master_id = _to_int(_value(row, "CaseMaster", "CaseMasterID", "CaseMasterID"))
            crime_no = _value(row, "CaseMaster", "CrimeNo", "CrimeNo")
            incident_date = _value(row, "CaseMaster", "IncidentFromDate", "IncidentFromDate")
            crime_type = _value(row, "CrimeSubHead", "CrimeHeadName", "CrimeHeadName")
            district = _value(row, "District", "DistrictName", "DistrictName")
            
            if crime_type:
                crime_type_counts[crime_type] = crime_type_counts.get(crime_type, 0) + 1
            
            if incident_date and (not last_seen_date or incident_date > last_seen_date):
                last_seen_date = incident_date
            
            if case_master_id:
                firs.append({
                    "case_master_id": case_master_id,
                    "crime_no": crime_no,
                    "crime_type": crime_type,
                    "date": incident_date,
                    "district": district,
                    "status": "Under Investigation" if is_absconding else "Charge Sheeted"
                })
        
        # Build crime types summary
        crime_types = [
            {"name": ct, "count": count}
            for ct, count in crime_type_counts.items()
        ]
        
        # Query co-accused with times together
        co_accused_query = f"""
            SELECT
                a2.AccusedMasterID,
                a2.AccusedName,
                COUNT(DISTINCT cm.CaseMasterID) as times_together
            FROM Accused a1
            INNER JOIN CaseMaster cm ON a1.CaseMasterID = cm.ROWID
            INNER JOIN Accused a2 ON cm.ROWID = a2.CaseMasterID
            WHERE a1.AccusedMasterID = {accused_id}
            AND a2.AccusedMasterID != {accused_id}
            GROUP BY a2.AccusedMasterID, a2.AccusedName
            ORDER BY times_together DESC
            LIMIT 10
        """
        co_accused_result = zcql.execute_query(co_accused_query)
        co_accused_rows = co_accused_result if isinstance(co_accused_result, list) else []
        
        co_accused = []
        for row in co_accused_rows:
            co_name = _value(row, "a2", "AccusedName", "AccusedName") or "Unknown"
            times_together = _to_int(_value(row, "", "times_together", "times_together")) or 0
            co_accused.append({
                "name": co_name,
                "times_together": times_together,
                "risk_score": min(100, times_together * 20)  # Simple risk based on co-appearances
            })
        
        # Calculate risk score (fallback: based on FIR count and absconding status)
        fir_count = len(firs)
        risk_score = min(100, fir_count * 15 + (50 if is_absconding else 0))
        
        return AccusedProfileResponse(
            accused_id=accused_id,
            name=name,
            age=age,
            gender=gender,
            fir_count=fir_count,
            firs=firs,
            co_accused=co_accused,
            crime_types=crime_types,
            risk_score=risk_score,
            is_absconding=is_absconding,
            last_seen_date=last_seen_date,
            aliases=[],
        )
    except Exception as exc:
        print(f"[Warning] Failed to build accused profile: {exc}")
        return AccusedProfileResponse(
            accused_id=accused_id,
            name="Unknown accused",
            fir_count=0,
            firs=[],
            co_accused=[],
            crime_types=[],
            risk_score=0,
            is_absconding=False,
        )


def _value(row: dict, table: str, column: str, flat_key: str):
    """Helper to extract values from nested Catalyst query results."""
    nested = row.get(table)
    if isinstance(nested, dict) and column in nested:
        return nested[column]
    if flat_key in row:
        return row[flat_key]
    qualified = f"{table}.{column}"
    if qualified in row:
        return row[qualified]
    prefixed = f"{table}_{column}"
    if prefixed in row:
        return row[prefixed]
    return row.get(column)


def _to_int(value):
    """Helper to safely convert to int."""
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _gender_label(gender_id):
    """Helper to convert gender ID to label."""
    if gender_id in (None, ""):
        return None
    mapping = {"1": "M", "2": "F", "3": "T", 1: "M", 2: "F", 3: "T"}
    return mapping.get(gender_id, str(gender_id))


@router.get("/search", response_model=SearchResponse)
async def search_accused(
    q: str,
    limit: int = 10,
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Search accused persons by name.

    This returns no matches until the Catalyst-backed search implementation is
    added in the search step.
    """
    return SearchResponse(results=[])
