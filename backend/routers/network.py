"""
Network Explorer API routes.

These endpoints are scaffolded with valid response shapes first so the frontend
can integrate against a stable contract while graph construction is built out.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends

from agents.network_agent.graph_builder import NetworkGraphBuilder
from core.database import get_zcql, get_cache_segment
from core.security import require_role
from services.cache_service import CacheService, generate_cache_key
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
    cache_segment=Depends(get_cache_segment),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Return the co-accused network graph.

    Builds the co-accused graph from Catalyst data with optional filters.
    Filters are applied as ZCQL WHERE clauses to limit the result set.
    """
    cache = CacheService(cache_segment)
    
    # Check cache
    cache_key = generate_cache_key("network:graph", crime_type, district, date_from, date_to, view)
    cached_graph = cache.get(cache_key)
    if cached_graph:
        print(f"[Cache] Hit for network graph with filters: {crime_type}, {district}")
        return GraphResponse(**cached_graph)
    
    try:
        response = NetworkGraphBuilder(zcql).build_graph(
            crime_type=crime_type,
            district=district,
            date_from=date_from,
            date_to=date_to,
            view=view,
        )
        
        # Cache the response for 6 hours
        cache.put(cache_key, response.model_dump(), expiry_in_hours=6)
        print(f"[Cache] Stored network graph with filters: {crime_type}, {district}")
        
        return response
    except Exception as exc:
        print(f"[Warning] Failed to build network graph: {exc}")
        return _empty_graph_response()


@router.get("/profile/{accused_id}", response_model=AccusedProfileResponse)
async def get_accused_profile(
    accused_id: int,
    row_id: Optional[int] = None,
    zcql=Depends(get_zcql),
    cache_segment=Depends(get_cache_segment),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Return a single accused profile with FIR history, associates, and risk scoring.
    
    Can query by either accused_id (AccusedMasterID) or row_id (Accused.ROWID).
    """
    cache = CacheService(cache_segment)
    
    # Check cache
    cache_key = generate_cache_key("network:profile", accused_id, row_id or 'default')
    cached_profile = cache.get(cache_key)
    if cached_profile:
        print(f"[Cache] Hit for accused profile: {accused_id}")
        return AccusedProfileResponse(**cached_profile)
    
    try:
        # Use row_id if provided; fall back to accused_id
        # accused_id may be 0 when the caller only knows the row_id (no AccusedMasterID)
        if row_id is not None:
            where_clause = f"Accused.ROWID = {row_id}"
        elif accused_id and accused_id != 0:
            where_clause = f"Accused.AccusedMasterID = {accused_id}"
        else:
            return AccusedProfileResponse(
                accused_id=None,
                row_id=row_id,
                name="Unknown accused",
                fir_count=0,
                firs=[],
                co_accused=[],
                crime_types=[],
                risk_score=0,
                is_absconding=False,
            )
        
        # Query accused basic info with FIR history (max 3 joins)
        # ZCQL: use ROWID for PK joins, max 4 joins total
        accused_query = f"""
            SELECT
                Accused.AccusedMasterID,
                Accused.ROWID as Accused_ROWID,
                Accused.AccusedName,
                Accused.AgeYear,
                Accused.GenderID,
                CaseMaster.CaseMasterID,
                CaseMaster.CrimeNo,
                CaseMaster.IncidentFromDate,
                CrimeSubHead.CrimeHeadName,
                Unit.UnitName
            FROM CaseMaster
            INNER JOIN Accused ON CaseMaster.ROWID = Accused.CaseMasterID
            LEFT JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
            LEFT JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
            WHERE {where_clause}
            LIMIT 300
        """
        accused_result = zcql.execute_query(accused_query)
        accused_rows = accused_result if isinstance(accused_result, list) else []
        
        if not accused_rows:
            return AccusedProfileResponse(
                accused_id=accused_id if accused_id and accused_id != 0 else None,
                row_id=row_id,
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
        
        # Check absconding status in a separate query (to stay within 4-join limit)
        # Only meaningful if we have an AccusedMasterID
        resolved_accused_id = _to_int(_value(first_row, "Accused", "AccusedMasterID", "AccusedMasterID")) or (accused_id if accused_id and accused_id != 0 else None)
        resolved_row_id = _to_int(_value(first_row, "Accused", "Accused_ROWID", "Accused_ROWID")) or row_id
        arrest_query = f"""
            SELECT ArrestSurrenderID
            FROM ArrestSurrender
            WHERE ArrestSurrender.AccusedMasterID = {resolved_accused_id}
            LIMIT 1
        """ if resolved_accused_id else None
        try:
            if arrest_query:
                arrest_result = zcql.execute_query(arrest_query)
                is_absconding = not (arrest_result and isinstance(arrest_result, list) and len(arrest_result) > 0)
            else:
                is_absconding = True
        except Exception:
            is_absconding = True
        
        # Build FIR summary list
        firs = []
        crime_type_counts = {}
        last_seen_date = None
        
        for row in accused_rows:
            case_master_id = _to_int(_value(row, "CaseMaster", "CaseMasterID", "CaseMasterID"))
            crime_no = _value(row, "CaseMaster", "CrimeNo", "CrimeNo")
            incident_date = _value(row, "CaseMaster", "IncidentFromDate", "IncidentFromDate")
            crime_type = _value(row, "CrimeSubHead", "CrimeHeadName", "CrimeHeadName")
            unit_name = _value(row, "Unit", "UnitName", "UnitName")
            
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
                    "district": unit_name,  # Use UnitName as location identifier
                    "status": "Under Investigation" if is_absconding else "Charge Sheeted"
                })
        
        # Build crime types summary
        crime_types = [
            {"name": ct, "count": count}
            for ct, count in crime_type_counts.items()
        ]
        
        # Query co-accused with times together
        # ZCQL does not support table aliases in FROM/JOIN — get all case IDs for this accused
        # then fetch co-accused for each case separately to avoid alias syntax errors
        case_ids = list({r_fir["case_master_id"] for r_fir in firs if r_fir.get("case_master_id")})
        co_accused_counts: dict = {}
        for cid in case_ids[:20]:  # cap at 20 cases to stay within ZCQL limits
            try:
                co_q = f"""
                    SELECT Accused.AccusedMasterID, Accused.AccusedName
                    FROM CaseMaster
                    INNER JOIN Accused ON CaseMaster.ROWID = Accused.CaseMasterID
                    WHERE CaseMaster.CaseMasterID = {cid}
                    LIMIT 50
                """
                co_rows = zcql.execute_query(co_q)
                for co_row in (co_rows if isinstance(co_rows, list) else []):
                    co_id = _to_int(_value(co_row, "Accused", "AccusedMasterID", "AccusedMasterID"))
                    co_name = _value(co_row, "Accused", "AccusedName", "AccusedName") or "Unknown"
                    if co_id and co_id != accused_id:
                        if co_id not in co_accused_counts:
                            co_accused_counts[co_id] = {"name": co_name, "count": 0}
                        co_accused_counts[co_id]["count"] += 1
            except Exception:
                pass
        co_accused_query = None  # signal that we've already built co_accused below
        # Build co_accused list from the co_accused_counts dict populated above
        co_accused = [
            {
                "name": info["name"],
                "times_together": info["count"],
                "risk_score": min(100, info["count"] * 20),
            }
            for info in sorted(co_accused_counts.values(), key=lambda x: x["count"], reverse=True)[:10]
        ]
        
        # Calculate risk score (fallback: based on FIR count and absconding status)
        fir_count = len(firs)
        risk_score = min(100, fir_count * 15 + (35 if is_absconding else 0))
        
        return AccusedProfileResponse(
            accused_id=resolved_accused_id,
            row_id=resolved_row_id,
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
        
        # Cache the response for 2 hours
        cache.put(cache_key, response.model_dump(), expiry_in_hours=2)
        print(f"[Cache] Stored accused profile: {accused_id}")
        
        return response
    except Exception as exc:
        print(f"[Warning] Failed to build accused profile: {exc}")
        import traceback
        traceback.print_exc()
        return AccusedProfileResponse(
            accused_id=accused_id if accused_id and accused_id != 0 else None,
            row_id=row_id,
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
    crime_type: Optional[str] = None,
    district: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    zcql=Depends(get_zcql),
    cache_segment=Depends(get_cache_segment),
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Search accused persons by name with wildcard matching.
    
    Results are ranked by FIR count and latest FIR date.
    Optional filters (crime_type, district, date_from, date_to) can be applied.
    """
    cache = CacheService(cache_segment)
    
    # Check cache
    cache_key = generate_cache_key("network:search", q, limit, crime_type, district, date_from, date_to)
    cached_search = cache.get(cache_key)
    if cached_search:
        print(f"[Cache] Hit for search: {q}")
        return SearchResponse(**cached_search)
    
    try:
        if not q or len(q.strip()) < 2:
            return SearchResponse(results=[])
        
        search_term = q.strip()
        
        # Build WHERE clauses for filters
        where_clauses = []
        if crime_type:
            # IMPORTANT: CaseMaster.CrimeMinorHeadID stores CrimeSubHead.ROWID (the physical PK),
            # NOT CrimeSubHead.CrimeSubHeadID. We must query ROWID to get matching values.
            crime_type_query = f"""
                SELECT CrimeSubHead.ROWID
                FROM CrimeSubHead
                WHERE CrimeSubHead.CrimeHeadName = '{crime_type}'
                LIMIT 100
            """
            try:
                crime_type_result = zcql.execute_query(crime_type_query)
                crime_type_ids = [
                    _to_int(_value(row, "CrimeSubHead", "ROWID", "ROWID"))
                    for row in (crime_type_result if isinstance(crime_type_result, list) else [])
                ]
                crime_type_ids = [cid for cid in crime_type_ids if cid is not None]
                if crime_type_ids:
                    where_clauses.append(f"CaseMaster.CrimeMinorHeadID IN ({','.join(map(str, crime_type_ids))})") 
            except Exception:
                pass
        
        if district:
            where_clauses.append(f"District.DistrictName = '{district}'")
        
        if date_from:
            where_clauses.append(f"CaseMaster.IncidentFromDate >= '{date_from}'")
        
        if date_to:
            where_clauses.append(f"CaseMaster.IncidentFromDate <= '{date_to}'")
        
        # Add name filter to WHERE clauses
        safe_term = search_term.replace("'", "''")
        where_clauses.append(f"Accused.AccusedName LIKE '*{safe_term}*'")
        
        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)
        
        # Query accused with FIR count and latest FIR date
        # ZCQL: use * wildcard (not %), no complex aggregates in search
        search_query = f"""
            SELECT
                Accused.ROWID as Accused_ROWID,
                Accused.AccusedMasterID,
                Accused.AccusedName,
                Accused.AgeYear,
                CaseMaster.IncidentFromDate
            FROM CaseMaster
            INNER JOIN Accused ON CaseMaster.ROWID = Accused.CaseMasterID
            LEFT JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
            LEFT JOIN District ON Unit.DistrictID = District.ROWID
            {where_sql}
            LIMIT {min(limit * 20, 300)}
        """
        
        result = zcql.execute_query(search_query)
        rows = result if isinstance(result, list) else []
        
        # Deduplicate rows by AccusedMasterID (or ROWID as fallback) and aggregate FIR count
        seen_ids: dict = {}
        for row in rows:
            acc_id = _to_int(_value(row, "Accused", "AccusedMasterID", "AccusedMasterID"))
            row_id_val = _to_int(_value(row, "Accused", "ROWID", "Accused_ROWID"))
            # Use AccusedMasterID as dedup key when available, otherwise use ROWID
            key = acc_id if acc_id is not None else row_id_val
            if key is None:
                continue
            name = _value(row, "Accused", "AccusedName", "AccusedName") or "Unknown"
            incident_date = _value(row, "CaseMaster", "IncidentFromDate", "IncidentFromDate")
            if key not in seen_ids:
                seen_ids[key] = {
                    "name": name,
                    "fir_count": 0,
                    "last_fir_date": None,
                    "accused_id": acc_id,
                    "row_id": row_id_val,
                }
            seen_ids[key]["fir_count"] += 1
            if incident_date and (
                not seen_ids[key]["last_fir_date"]
                or str(incident_date) > str(seen_ids[key]["last_fir_date"])
            ):
                seen_ids[key]["last_fir_date"] = incident_date

        # Sort by fir_count descending, take top `limit`
        sorted_results = sorted(seen_ids.items(), key=lambda kv: kv[1]["fir_count"], reverse=True)[:limit]

        # Check absconding status for the search results to compute risk score consistently
        accused_ids_to_check = [info["accused_id"] for _key, info in sorted_results if info["accused_id"]]
        absconding_map = {}
        if accused_ids_to_check:
            try:
                ids_str = ",".join(map(str, accused_ids_to_check))
                arrest_query = f"""
                    SELECT ArrestSurrenderID, AccusedMasterID
                    FROM ArrestSurrender
                    WHERE ArrestSurrender.AccusedMasterID IN ({ids_str})
                """
                arrest_result = zcql.execute_query(arrest_query)
                arrest_rows = arrest_result if isinstance(arrest_result, list) else []
                arrested_ids = {
                    _to_int(_value(r, "ArrestSurrender", "AccusedMasterID", "AccusedMasterID"))
                    for r in arrest_rows
                }
                for acc_id in accused_ids_to_check:
                    absconding_map[acc_id] = acc_id not in arrested_ids
            except Exception:
                # Default all to absconding (flight risk) if query fails
                for acc_id in accused_ids_to_check:
                    absconding_map[acc_id] = True
        
        results = []
        for _key, info in sorted_results:
            acc_id = info["accused_id"]
            is_absconding = absconding_map.get(acc_id, True) if acc_id else True
            risk_score = min(100, info["fir_count"] * 15 + (35 if is_absconding else 0))
            results.append({
                "accused_id": acc_id,
                "row_id": info["row_id"],
                "name": info["name"],
                "fir_count": info["fir_count"],
                "risk_score": risk_score,
                "last_fir_date": info["last_fir_date"],
            })

        # Cache the response for 1 hour
        cache.put(cache_key, {"results": results}, expiry_in_hours=1)
        print(f"[Cache] Stored search results: {q}")

        return SearchResponse(results=results)
    except Exception as exc:
        print(f"[Warning] Failed to search accused: {exc}")
        return SearchResponse(results=[])
