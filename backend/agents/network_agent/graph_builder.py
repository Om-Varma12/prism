"""
Co-accused graph builder for the Network Explorer.
"""
from collections import defaultdict, deque
from datetime import datetime, timedelta
from itertools import combinations
from typing import Any, Optional

from schemas.network import DensestNode, EdgeIncident, GraphEdge, GraphMetadata, GraphNode, GraphResponse, GraphView
from agents.network_agent.centrality import CentralityComputer
from agents.network_agent.community_detection import CommunityDetector


def jaro_winkler_similarity(s1: str, s2: str) -> float:
    s1 = s1.strip().lower()
    s2 = s2.strip().lower()
    if s1 == s2:
        return 1.0
    
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0
    
    match_bound = max(len1, len2) // 2 - 1
    if match_bound < 0:
        match_bound = 0
        
    s1_matches = [False] * len1
    s2_matches = [False] * len2
    
    matches = 0
    for i in range(len1):
        start = max(0, i - match_bound)
        end = min(len2, i + match_bound + 1)
        for j in range(start, end):
            if not s2_matches[j] and s1[i] == s2[j]:
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break
                
    if matches == 0:
        return 0.0
        
    t = 0
    k = 0
    for i in range(len1):
        if s1_matches[i]:
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                t += 1
            k += 1
            
    t = t // 2
    
    jaro = (matches / len1 + matches / len2 + (matches - t) / matches) / 3.0
    
    prefix = 0
    for i in range(min(4, len1, len2)):
        if s1[i] == s2[i]:
            prefix += 1
        else:
            break
            
    return jaro + prefix * 0.1 * (1.0 - jaro)


class NetworkGraphBuilder:
    """Builds a basic co-accused graph from Catalyst ZCQL results."""

    def __init__(self, zcql):
        self.zcql = zcql

    def build_graph(
        self,
        crime_type: Optional[str] = None,
        district: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        view: GraphView = "all",
    ) -> GraphResponse:
        # Apply default date window if no date filters provided (last 90 days)
        if not date_from and not date_to:
            date_to = datetime.utcnow().strftime("%Y-%m-%d")
            date_from = (datetime.utcnow() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        rows = self._fetch_accused_rows(crime_type, district, date_from, date_to)
        
        # ─── Step 1: Entity Resolution (Fuzzy Matching) ───
        resolved_nodes: list[GraphNode] = []
        node_id_mapping: dict[str, str] = {}
        
        def find_matching_node(name: str, age: Optional[int], gender: str, accused_id: Optional[int]) -> Optional[GraphNode]:
            if accused_id:
                for node in resolved_nodes:
                    if node.accused_id == accused_id:
                        return node
            
            for node in resolved_nodes:
                if gender and gender != "Unknown" and node.gender and node.gender != "Unknown":
                    if gender != node.gender:
                        continue
                if age is not None and node.age is not None:
                    if abs(age - node.age) > 5:
                        continue
                if jaro_winkler_similarity(name, node.label) >= 0.88:
                    return node
            return None

        case_groups: dict[str, list[str]] = defaultdict(list)
        case_incidents: dict[str, tuple[int, str | None]] = {}  # case_row_id -> (case_master_id, crime_no)
        absconding_by_resolved_id: dict[str, bool] = {}
        crime_types_by_resolved_id: dict[str, set[int]] = defaultdict(set)  # Track crime types per node

        for row in rows:
            accused_id = self._to_int(
                self._value(row, "Accused", "AccusedMasterID", "AccusedMasterID")
            )
            row_id = self._value(row, "Accused", "ROWID", "ROWID")
            case_master_id = self._to_int(
                self._value(row, "CaseMaster", "CaseMasterID", "CaseMasterID")
            )
            case_row_id = str(
                self._value(row, "CaseMaster", "ROWID", "CaseMaster_ROWID")
                or self._value(row, "Accused", "CaseMasterID", "CaseMasterID")
                or case_master_id
                or ""
            )
            name = (
                self._value(row, "Accused", "AccusedName", "AccusedName")
                or "Unknown accused"
            )
            age = self._to_int(self._value(row, "Accused", "AgeYear", "AgeYear"))
            gender_val = self._value(row, "Accused", "GenderID", "GenderID")
            gender = self._gender_label(gender_val) or "Unknown"
            
            # Check absconding status via presence of ArrestSurrender
            # Note: ArrestSurrender is not joined in the main query to stay within 4-join limit
            # We'll check absconding status separately for each unique accused
            is_row_absconding = True  # Default to absconding, will be updated if arrest found

            # Get crime type ID for filtering
            crime_type_id = self._to_int(self._value(row, "CaseMaster", "CrimeMinorHeadID", "CrimeMinorHeadID"))

            if not case_row_id:
                continue

            matched_node = find_matching_node(name, age, gender, accused_id)
            
            if matched_node:
                resolved_id = matched_node.id
                # Always update accused_id if current row has one
                if accused_id:
                    matched_node.accused_id = accused_id
                if matched_node.age is None and age is not None:
                    matched_node.age = age
                if (matched_node.gender is None or matched_node.gender == "Unknown") and gender != "Unknown":
                    matched_node.gender = gender
            else:
                node_key = accused_id or self._to_int(row_id) or abs(hash(f"{name}:{case_row_id}"))
                resolved_id = f"accused_{node_key}"
                
                incident_date = self._value(
                    row, "CaseMaster", "IncidentFromDate", "IncidentFromDate"
                )
                district_name = self._value(row, "District", "DistrictName", "DistrictName")
                
                matched_node = GraphNode(
                    id=resolved_id,
                    label=str(name),
                    type="accused",
                    accused_id=accused_id,
                    age=age,
                    gender=gender,
                    fir_count=0,
                    is_absconding=False,
                    risk_score=0,
                    primary_district=str(district_name) if district_name else None,
                    last_seen_date=str(incident_date) if incident_date else None,
                    size=8,
                    color="#3B6FE8",
                )
                resolved_nodes.append(matched_node)
            
            row_key = str(row_id or f"{name}:{case_row_id}")
            node_id_mapping[row_key] = resolved_id
            
            incident_date = self._value(row, "CaseMaster", "IncidentFromDate", "IncidentFromDate")
            if incident_date and self._is_newer_date(str(incident_date), matched_node.last_seen_date):
                matched_node.last_seen_date = str(incident_date)
            
            district_name = self._value(row, "District", "DistrictName", "DistrictName")
            if district_name and not matched_node.primary_district:
                matched_node.primary_district = str(district_name)

            absconding_by_resolved_id[resolved_id] = absconding_by_resolved_id.get(resolved_id, False) or is_row_absconding

            # Track crime types for this node
            if crime_type_id:
                crime_types_by_resolved_id[resolved_id].add(crime_type_id)

            if resolved_id not in case_groups[case_row_id]:
                case_groups[case_row_id].append(resolved_id)
            if case_master_id and case_row_id not in case_incidents:
                crime_no = str(self._value(row, "CaseMaster", "CrimeNo", "CrimeNo") or "")
                case_incidents[case_row_id] = (case_master_id, crime_no or None)

        # Update node summaries
        for node in resolved_nodes:
            node.fir_count = sum(1 for cid, nids in case_groups.items() if node.id in nids)
            node.is_absconding = absconding_by_resolved_id.get(node.id, False)
            node.risk_score = min(100, node.fir_count * 20)
            node.size = min(24, 8 + node.fir_count * 2)
            node.color = self._risk_color(node.risk_score)

        edges_by_pair: dict[tuple[str, str], GraphEdge] = {}
        for case_id, node_ids in case_groups.items():
            if len(node_ids) < 2:
                continue

            incident_tuple = case_incidents.get(case_id)
            for source, target in combinations(sorted(node_ids), 2):
                pair = (source, target)
                if pair not in edges_by_pair:
                    edges_by_pair[pair] = GraphEdge(
                        source=source,
                        target=target,
                        type="co_accused",
                        strength=0,
                        incidents=[],
                        thickness=1,
                        color="#44474f",
                    )

                edge = edges_by_pair[pair]
                edge.strength += 1
                edge.thickness = min(5, 1 + edge.strength)
                edge.color = "#ffb4ab" if edge.strength > 1 else "#44474f"
                if incident_tuple:
                    case_master_id, crime_no = incident_tuple
                    existing_ids = {inc.case_master_id for inc in edge.incidents}
                    if case_master_id not in existing_ids:
                        edge.incidents.append(EdgeIncident(case_master_id=case_master_id, crime_no=crime_no))

        nodes = resolved_nodes
        edges = list(edges_by_pair.values())
        
        # Assign gang clusters before view filtering so cluster sizes are available
        CommunityDetector.assign_clusters_to_nodes(nodes, edges)

        # Apply view-specific filtering
        if view == "repeat":
            repeat_node_ids = {node.id for node in nodes if node.fir_count >= 2}
            nodes = [node for node in nodes if node.id in repeat_node_ids]
            edges = [
                edge for edge in edges
                if edge.source in repeat_node_ids and edge.target in repeat_node_ids
            ]
        elif view == "clusters":
            # Keep only nodes that belong to a gang cluster of size >= 2
            cluster_sizes = CommunityDetector.get_cluster_metadata(nodes)
            gang_node_ids = {
                node.id for node in nodes
                if node.gang_cluster is not None and cluster_sizes.get(node.gang_cluster, 0) >= 2
            }
            nodes = [node for node in nodes if node.id in gang_node_ids]
            edges = [
                edge for edge in edges
                if edge.source in gang_node_ids and edge.target in gang_node_ids
            ]
        
        # Apply crime type filtering (post-processing, since CrimeSubHead can't be joined in main query
        # without exceeding ZCQL's 4-join limit).
        # IMPORTANT: CaseMaster.CrimeMinorHeadID stores CrimeSubHead.ROWID (the physical PK),
        # NOT CrimeSubHead.CrimeSubHeadID (the logical/small int column). We must select ROWID.
        if crime_type:
            crime_type_query = f"""
                SELECT CrimeSubHead.ROWID
                FROM CrimeSubHead
                WHERE CrimeSubHead.CrimeHeadName = '{crime_type}'
                LIMIT 100
            """
            try:
                crime_type_result = self.zcql.execute_query(crime_type_query)
                target_crime_type_ids = [
                    self._to_int(self._value(row, "CrimeSubHead", "ROWID", "ROWID"))
                    for row in (crime_type_result if isinstance(crime_type_result, list) else [])
                ]
                target_crime_type_ids = [cid for cid in target_crime_type_ids if cid is not None]
                print(f"[DEBUG] Crime type '{crime_type}' resolved to ROWIDs: {target_crime_type_ids}")

                if target_crime_type_ids:
                    # Filter nodes by crime type using tracked crime_types_by_resolved_id
                    nodes = [
                        node for node in nodes
                        if node.id in crime_types_by_resolved_id
                        and any(ctid in target_crime_type_ids for ctid in crime_types_by_resolved_id[node.id])
                    ]
                    # Filter edges to only include connections between filtered nodes
                    node_ids_set = {node.id for node in nodes}
                    edges = [
                        edge for edge in edges
                        if edge.source in node_ids_set and edge.target in node_ids_set
                    ]
            except Exception as exc:
                print(f"[Warning] Failed to filter by crime type: {exc}")
        
        # Community detection already ran above before view filtering.
        # Re-run only if the node list has changed (crime_type or view filter was applied).
        if crime_type or view in ("repeat", "clusters"):
            CommunityDetector.assign_clusters_to_nodes(nodes, edges)
        
        # Compute centrality metrics and attach to nodes
        CentralityComputer.attach_centrality_to_nodes(nodes, edges)

        # Update risk scores based on crime count, flight risk (absconding), and network centrality
        for node in nodes:
            centrality = getattr(node, "centrality_score", 0.0) or 0.0
            node.risk_score = min(100, (node.fir_count * 15) + (35 if node.is_absconding else 0) + int(centrality * 50))
            node.color = self._risk_color(node.risk_score)

        return GraphResponse(
            nodes=nodes,
            edges=edges,
            metadata=GraphMetadata(
                total_nodes=len(nodes),
                total_edges=len(edges),
                largest_cluster_size=self._largest_connected_component_size(nodes, edges),
                num_clusters=self._connected_component_count(nodes, edges),
                repeat_offender_count=sum(1 for node in nodes if node.fir_count >= 2),
                densest_node=CentralityComputer.find_densest_node(nodes),
                generated_at=datetime.utcnow(),
            ),
        )

    def _fetch_accused_rows(
        self,
        crime_type: Optional[str] = None,
        district: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        where_clauses = []
        
        # Note: crime_type filtering removed due to ZCQL 4-join limit
        # Crime type can be filtered client-side or via a separate query
        
        if district:
            # Filter by District.DistrictName
            where_clauses.append(f"District.DistrictName = '{district}'")
        
        if date_from:
            where_clauses.append(f"CaseMaster.IncidentFromDate >= '{date_from}'")
        
        if date_to:
            where_clauses.append(f"CaseMaster.IncidentFromDate <= '{date_to}'")
        
        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)
        
        query = f"""
            SELECT
                Accused.ROWID as Accused_ROWID,
                Accused.AccusedMasterID,
                Accused.AccusedName,
                Accused.AgeYear,
                Accused.GenderID,
                Accused.CaseMasterID,
                CaseMaster.ROWID as CaseMaster_ROWID,
                CaseMaster.CaseMasterID,
                CaseMaster.CrimeNo,
                CaseMaster.IncidentFromDate,
                CaseMaster.CrimeMinorHeadID,
                Unit.UnitName,
                District.DistrictName
            FROM CaseMaster
            INNER JOIN Accused ON CaseMaster.ROWID = Accused.CaseMasterID
            LEFT JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
            LEFT JOIN District ON Unit.DistrictID = District.ROWID
            {where_sql}
            LIMIT 300
        """
        result = self.zcql.execute_query(query)
        return result if isinstance(result, list) else []

    def _attach_degree_scores(self, nodes: list[GraphNode], edges: list[GraphEdge]) -> None:
        """Deprecated: Use CentralityComputer.attach_centrality_to_nodes instead."""
        CentralityComputer.attach_centrality_to_nodes(nodes, edges)

    def _densest_node(self, nodes: list[GraphNode]) -> DensestNode | None:
        """Deprecated: Use CentralityComputer.find_densest_node instead."""
        return CentralityComputer.find_densest_node(nodes)

    def _value(
        self,
        row: dict[str, Any],
        table: str,
        column: str,
        flat_key: str,
    ) -> Any:
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

    def _to_int(self, value: Any) -> int | None:
        if value in (None, ""):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _gender_label(self, gender_id: Any) -> str | None:
        if gender_id in (None, ""):
            return None
        mapping = {"1": "M", "2": "F", "3": "T", 1: "M", 2: "F", 3: "T"}
        return mapping.get(gender_id, str(gender_id))

    def _risk_color(self, risk_score: float) -> str:
        if risk_score >= 70:
            return "#ffb4ab"
        if risk_score >= 40:
            return "#ffb86b"
        return "#3B6FE8"

    def _is_newer_date(self, candidate: str, current: str | None) -> bool:
        if not current:
            return True
        return candidate > current

    def _connected_component_count(
        self, nodes: list[GraphNode], edges: list[GraphEdge]
    ) -> int:
        return len(self._connected_component_sizes(nodes, edges))

    def _largest_connected_component_size(
        self, nodes: list[GraphNode], edges: list[GraphEdge]
    ) -> int:
        return max(self._connected_component_sizes(nodes, edges), default=0)

    def _connected_component_sizes(
        self, nodes: list[GraphNode], edges: list[GraphEdge]
    ) -> list[int]:
        if not nodes:
            return []

        adjacency: dict[str, set[str]] = {node.id: set() for node in nodes}
        for edge in edges:
            adjacency.setdefault(edge.source, set()).add(edge.target)
            adjacency.setdefault(edge.target, set()).add(edge.source)

        seen: set[str] = set()
        sizes: list[int] = []
        for node_id in adjacency:
            if node_id in seen:
                continue
            size = 0
            queue: deque[str] = deque([node_id])
            seen.add(node_id)
            while queue:
                current = queue.popleft()
                size += 1
                for neighbor in adjacency[current]:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        queue.append(neighbor)
            sizes.append(size)
        return sizes
