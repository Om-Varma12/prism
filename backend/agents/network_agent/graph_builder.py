"""
Co-accused graph builder for the Network Explorer.
"""
from collections import defaultdict, deque
from datetime import datetime, timedelta
from itertools import combinations
from typing import Any, Optional

from schemas.network import DensestNode, GraphEdge, GraphMetadata, GraphNode, GraphResponse, GraphView
from agents.network_agent.centrality import CentralityComputer


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
        nodes_by_id: dict[str, GraphNode] = {}
        case_groups: dict[str, list[str]] = defaultdict(list)
        case_incidents: dict[str, int] = {}

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

            if not case_row_id:
                continue

            node_key = accused_id or self._to_int(row_id) or abs(hash(f"{name}:{case_row_id}"))
            node_id = f"accused_{node_key}"

            incident_date = self._value(
                row, "CaseMaster", "IncidentFromDate", "IncidentFromDate"
            )
            district = self._value(row, "District", "DistrictName", "DistrictName")

            if node_id not in nodes_by_id:
                nodes_by_id[node_id] = GraphNode(
                    id=node_id,
                    label=str(name),
                    type="accused",
                    accused_id=int(node_key),
                    age=self._to_int(self._value(row, "Accused", "AgeYear", "AgeYear")),
                    gender=self._gender_label(
                        self._value(row, "Accused", "GenderID", "GenderID")
                    ),
                    fir_count=0,
                    is_absconding=False,
                    risk_score=0,
                    primary_district=str(district) if district else None,
                    last_seen_date=str(incident_date) if incident_date else None,
                    size=8,
                    color="#3B6FE8",
                )

            node = nodes_by_id[node_id]
            node.fir_count += 1
            node.risk_score = min(100, node.fir_count * 20)
            node.size = min(24, 8 + node.fir_count * 2)
            node.color = self._risk_color(node.risk_score)
            if incident_date and self._is_newer_date(str(incident_date), node.last_seen_date):
                node.last_seen_date = str(incident_date)
            if district and not node.primary_district:
                node.primary_district = str(district)

            if node_id not in case_groups[case_row_id]:
                case_groups[case_row_id].append(node_id)
            if case_master_id:
                case_incidents[case_row_id] = case_master_id

        edges_by_pair: dict[tuple[str, str], GraphEdge] = {}
        for case_id, node_ids in case_groups.items():
            if len(node_ids) < 2:
                continue

            incident_id = case_incidents.get(case_id)
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
                if incident_id and incident_id not in edge.incidents:
                    edge.incidents.append(incident_id)

        nodes = list(nodes_by_id.values())
        edges = list(edges_by_pair.values())
        
        # Apply view-specific filtering
        if view == "repeat":
            # Filter to only repeat offenders (2+ FIRs)
            repeat_node_ids = {node.id for node in nodes if node.fir_count >= 2}
            nodes = [node for node in nodes if node.id in repeat_node_ids]
            # Filter edges to only connect repeat offenders
            edges = [
                edge for edge in edges
                if edge.source in repeat_node_ids and edge.target in repeat_node_ids
            ]
        
        # Compute centrality metrics and attach to nodes
        CentralityComputer.attach_centrality_to_nodes(nodes, edges)

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
        
        if crime_type:
            where_clauses.append(f"CrimeSubHead.CrimeHeadName = '{crime_type}'")
        
        if district:
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
                Accused.ROWID,
                Accused.AccusedMasterID,
                Accused.AccusedName,
                Accused.AgeYear,
                Accused.GenderID,
                Accused.CaseMasterID,
                CaseMaster.ROWID,
                CaseMaster.CaseMasterID,
                CaseMaster.CrimeNo,
                CaseMaster.IncidentFromDate,
                CrimeSubHead.CrimeHeadName,
                Unit.UnitName,
                District.DistrictName
            FROM CaseMaster
            INNER JOIN Accused ON CaseMaster.ROWID = Accused.CaseMasterID
            LEFT JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
            LEFT JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
            LEFT JOIN District ON Unit.DistrictID = District.ROWID
            {where_sql}
            LIMIT 1000
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

    def _attach_degree_scores(self, nodes: list[GraphNode], edges: list[GraphEdge]) -> None:
        degree_by_id: dict[str, int] = defaultdict(int)
        for edge in edges:
            degree_by_id[edge.source] += edge.strength
            degree_by_id[edge.target] += edge.strength

        max_degree = max(degree_by_id.values(), default=1)
        for node in nodes:
            degree = degree_by_id.get(node.id, 0)
            node.centrality_score = round(degree / max_degree, 3) if max_degree else 0
            node.size = max(node.size, min(28, 8 + degree * 2))

    def _densest_node(self, nodes: list[GraphNode]) -> DensestNode | None:
        if not nodes:
            return None
        node = max(nodes, key=lambda item: item.centrality_score)
        return DensestNode(
            id=node.id,
            name=node.label,
            centrality_score=node.centrality_score,
        )

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
