"""
Graph centrality metrics for the Network Explorer.

Computes degree, weighted degree, and centrality scores for graph nodes
to identify key figures in criminal networks.
"""
from typing import Dict, List

from schemas.network import DensestNode, GraphEdge, GraphNode


class CentralityComputer:
    """Computes centrality metrics for graph nodes."""

    @staticmethod
    def compute_degree_scores(nodes: List[GraphNode], edges: List[GraphEdge]) -> Dict[str, float]:
        """
        Compute normalized degree centrality for each node.
        
        Degree is weighted by edge strength (number of co-appearances).
        Returns a mapping of node_id to centrality_score (0-1).
        """
        degree_by_id: Dict[str, int] = {}
        
        for edge in edges:
            degree_by_id[edge.source] = degree_by_id.get(edge.source, 0) + edge.strength
            degree_by_id[edge.target] = degree_by_id.get(edge.target, 0) + edge.strength
        
        # Normalize to 0-1 range
        max_degree = max(degree_by_id.values(), default=1)
        
        centrality_scores: Dict[str, float] = {}
        for node in nodes:
            degree = degree_by_id.get(node.id, 0)
            centrality_scores[node.id] = round(degree / max_degree, 3) if max_degree else 0
        
        return centrality_scores

    @staticmethod
    def attach_centrality_to_nodes(nodes: List[GraphNode], edges: List[GraphEdge]) -> None:
        """
        Attach centrality scores and adjust node sizes based on degree.
        
        Modifies nodes in-place to add centrality_score and update size.
        """
        degree_by_id: Dict[str, int] = {}
        
        for edge in edges:
            degree_by_id[edge.source] = degree_by_id.get(edge.source, 0) + edge.strength
            degree_by_id[edge.target] = degree_by_id.get(edge.target, 0) + edge.strength
        
        max_degree = max(degree_by_id.values(), default=1)
        
        for node in nodes:
            degree = degree_by_id.get(node.id, 0)
            node.centrality_score = round(degree / max_degree, 3) if max_degree else 0
            # Increase node size based on degree, capped at 28
            node.size = max(node.size, min(28, 8 + degree * 2))

    @staticmethod
    def find_densest_node(nodes: List[GraphNode]) -> DensestNode | None:
        """
        Find the node with the highest centrality score.
        
        Returns a DensestNode object with the most connected node's details.
        """
        if not nodes:
            return None
        
        node = max(nodes, key=lambda item: item.centrality_score)
        return DensestNode(
            id=node.id,
            name=node.label,
            centrality_score=node.centrality_score,
        )
