"""
Community detection for the Network Explorer.

Implements connected components as a fallback for gang cluster detection.
This can be replaced with Louvain algorithm when available.
"""
from collections import deque
from typing import Dict, List, Set

from schemas.network import GraphEdge, GraphNode


class CommunityDetector:
    """Detects communities (gang clusters) in the graph using connected components."""

    @staticmethod
    def detect_clusters(nodes: List[GraphNode], edges: List[GraphEdge]) -> Dict[str, int]:
        """
        Assign cluster IDs to nodes using connected components algorithm.
        
        Each connected component is treated as a potential gang cluster.
        Returns a mapping of node_id to cluster_id.
        
        This is a lightweight fallback that can be replaced with Louvain
        for more sophisticated community detection.
        """
        if not nodes:
            return {}
        
        # Build adjacency list
        adjacency: Dict[str, Set[str]] = {node.id: set() for node in nodes}
        for edge in edges:
            adjacency.setdefault(edge.source, set()).add(edge.target)
            adjacency.setdefault(edge.target, set()).add(edge.source)
        
        # Find connected components using BFS
        seen: Set[str] = set()
        cluster_id = 0
        node_to_cluster: Dict[str, int] = {}
        
        for node_id in adjacency:
            if node_id in seen:
                continue
            
            # BFS to find all nodes in this component
            queue: deque[str] = deque([node_id])
            seen.add(node_id)
            
            while queue:
                current = queue.popleft()
                node_to_cluster[current] = cluster_id
                
                for neighbor in adjacency[current]:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        queue.append(neighbor)
            
            cluster_id += 1
        
        return node_to_cluster

    @staticmethod
    def assign_clusters_to_nodes(nodes: List[GraphNode], edges: List[GraphEdge]) -> None:
        """
        Assign gang_cluster IDs to nodes in-place.
        
        Uses connected components as a simple clustering algorithm.
        """
        node_to_cluster = CommunityDetector.detect_clusters(nodes, edges)
        
        for node in nodes:
            node.gang_cluster = node_to_cluster.get(node.id)

    @staticmethod
    def get_cluster_metadata(nodes: List[GraphNode]) -> Dict[int, int]:
        """
        Get metadata about cluster sizes.
        
        Returns a mapping of cluster_id to number of nodes in that cluster.
        """
        cluster_sizes: Dict[int, int] = {}
        
        for node in nodes:
            if node.gang_cluster is not None:
                cluster_sizes[node.gang_cluster] = cluster_sizes.get(node.gang_cluster, 0) + 1
        
        return cluster_sizes
