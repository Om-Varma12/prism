"""
Community detection for the Network Explorer.

Implements connected components as a fallback for gang cluster detection.
This can be replaced with Louvain algorithm when available.
"""
from collections import deque
from typing import Dict, List, Set

from schemas.network import GraphEdge, GraphNode



class CommunityDetector:
    """Detects communities (gang clusters) using a modularity-optimizing Louvain-like algorithm."""

    @staticmethod
    def detect_clusters(nodes: List[GraphNode], edges: List[GraphEdge]) -> Dict[str, int]:
        """
        Assign cluster IDs to nodes using a modularity optimization (Louvain) method.
        
        Optimizes modularity (Q) by greedily shifting nodes to neighboring communities.
        Returns a mapping of node_id to cluster_id.
        """
        if not nodes:
            return {}
        
        # Build adjacency matrix with weights (edge strength)
        adj: Dict[str, Dict[str, float]] = {node.id: {} for node in nodes}
        node_degrees: Dict[str, float] = {node.id: 0.0 for node in nodes}
        m = 0.0
        
        for edge in edges:
            weight = float(edge.strength or 1.0)
            adj[edge.source][edge.target] = weight
            adj[edge.target][edge.source] = weight
            node_degrees[edge.source] += weight
            node_degrees[edge.target] += weight
            m += weight
            
        if m == 0.0:
            # If no edges exist, each node is in its own cluster
            return {node.id: idx for idx, node in enumerate(nodes)}
            
        # Initial partition: each node in its own community
        community_of: Dict[str, str] = {node.id: node.id for node in nodes}
        
        # Track total weight in each community
        tot: Dict[str, float] = {node.id: node_degrees[node.id] for node in nodes}
        
        # Louvain first-phase greedy local modularity optimization
        improved = True
        max_iterations = 20
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            for node in nodes:
                node_id = node.id
                c_old = community_of[node_id]
                k_i = node_degrees[node_id]
                
                # Find neighboring communities
                neighborhood_communities: Dict[str, float] = {}
                for neighbor, weight in adj[node_id].items():
                    c_neigh = community_of[neighbor]
                    neighborhood_communities[c_neigh] = neighborhood_communities.get(c_neigh, 0.0) + weight
                    
                # Compute best community to move to
                best_community = c_old
                best_delta_q = 0.0
                
                # Cost of removing node i from c_old
                k_i_in_old = neighborhood_communities.get(c_old, 0.0)
                delta_q_remove = -k_i_in_old / m + ((tot[c_old] - k_i) * k_i) / (2.0 * m * m)
                
                for c_new, k_i_in_new in neighborhood_communities.items():
                    if c_new == c_old:
                        continue
                    
                    # Benefit of adding node i to c_new
                    delta_q_add = k_i_in_new / m - (tot[c_new] * k_i) / (2.0 * m * m)
                    
                    delta_q = delta_q_remove + delta_q_add
                    if delta_q > best_delta_q:
                        best_delta_q = delta_q
                        best_community = c_new
                        
                # If a better community was found, move the node
                if best_community != c_old:
                    community_of[node_id] = best_community
                    tot[c_old] -= k_i
                    tot[best_community] += k_i
                    improved = True
                    
        # Normalize community IDs to integers starting from 0
        unique_comms = sorted(list(set(community_of.values())))
        comm_to_idx = {comm: idx for idx, comm in enumerate(unique_comms)}
        
        return {node_id: comm_to_idx[comm] for node_id, comm in community_of.items()}

    @staticmethod
    def assign_clusters_to_nodes(nodes: List[GraphNode], edges: List[GraphEdge]) -> None:
        """
        Assign gang_cluster IDs to nodes in-place.
        """
        node_to_cluster = CommunityDetector.detect_clusters(nodes, edges)
        
        for node in nodes:
            node.gang_cluster = node_to_cluster.get(node.id)

    @staticmethod
    def get_cluster_metadata(nodes: List[GraphNode]) -> Dict[int, int]:
        """
        Get metadata about cluster sizes.
        """
        cluster_sizes: Dict[int, int] = {}
        
        for node in nodes:
            if node.gang_cluster is not None:
                cluster_sizes[node.gang_cluster] = cluster_sizes.get(node.gang_cluster, 0) + 1
        
        return cluster_sizes
