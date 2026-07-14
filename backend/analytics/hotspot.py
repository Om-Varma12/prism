"""
Hotspot clustering using DBSCAN for spatial crime analysis.

This module provides the HotspotAnalyzer class that performs spatial clustering
on crime incident coordinates to identify crime hotspots.
"""
from typing import Optional
from datetime import datetime
import numpy as np
from sklearn.cluster import DBSCAN


class HotspotAnalyzer:
    """
    Analyzes spatial crime data to identify hotspots using DBSCAN clustering.
    
    Clusters crime incidents based on geographic proximity and computes
    cluster statistics including centroid, radius, and dominant crime type.
    """

    def __init__(self, eps_km: float = 1.0, min_samples: int = 5):
        """
        Initialize the HotspotAnalyzer.
        
        Args:
            eps_km: Maximum distance between two samples for one to be considered
                   as in the neighborhood of the other (in kilometers).
                   Default: 1.0 km (approx 0.01 degrees latitude/longitude).
            min_samples: Minimum number of samples in a neighborhood for a point
                        to be considered as a core point. Default: 5.
        """
        self.eps_km = eps_km
        self.min_samples = min_samples
        # Convert km to approximate degrees (roughly 1 degree = 111 km)
        self.eps_deg = eps_km / 111.0

    def analyze_hotspots(
        self,
        incident_data: list[dict],
    ) -> list[dict]:
        """
        Perform DBSCAN clustering on incident data.
        
        Args:
            incident_data: List of incident dictionaries with keys:
                          - latitude: float
                          - longitude: float
                          - crime_type: str
                          - district: str (optional)
        
        Returns:
            List of cluster dictionaries with keys:
            - cluster_id: int
            - centroid_lat: float
            - centroid_lng: float
            - point_count: int
            - radius_km: float
            - dominant_crime_type: str
            - district: str (optional)
        """
        if not incident_data:
            return []

        # Extract coordinates and metadata
        coordinates = []
        metadata = []
        for incident in incident_data:
            lat = incident.get("latitude")
            lng = incident.get("longitude")
            if lat is not None and lng is not None:
                coordinates.append([lat, lng])
                metadata.append({
                    "crime_type": incident.get("crime_type", "Unknown"),
                    "district": incident.get("district"),
                })

        if len(coordinates) < self.min_samples:
            return []

        # Perform DBSCAN clustering
        coords_array = np.array(coordinates)
        dbscan = DBSCAN(eps=self.eps_deg, min_samples=self.min_samples)
        labels = dbscan.fit_predict(coords_array)

        # Group points by cluster
        clusters = {}
        for i, label in enumerate(labels):
            if label == -1:  # Noise point
                continue
            if label not in clusters:
                clusters[label] = {
                    "points": [],
                    "crime_types": [],
                    "districts": [],
                }
            clusters[label]["points"].append(coords_array[i])
            clusters[label]["crime_types"].append(metadata[i]["crime_type"])
            if metadata[i]["district"]:
                clusters[label]["districts"].append(metadata[i]["district"])

        # Compute cluster statistics
        results = []
        for cluster_id, cluster_data in clusters.items():
            points = np.array(cluster_data["points"])
            crime_types = cluster_data["crime_types"]
            districts = cluster_data["districts"]

            # Calculate centroid
            centroid = np.mean(points, axis=0)
            centroid_lat = float(centroid[0])
            centroid_lng = float(centroid[1])

            # Calculate radius (maximum distance from centroid to any point in cluster)
            distances = np.sqrt(np.sum((points - centroid) ** 2, axis=1))
            radius_deg = np.max(distances) if len(distances) > 0 else 0
            radius_km = radius_deg * 111.0

            # Calculate dominant crime type
            dominant_crime_type = self._get_dominant_crime_type(crime_types)

            # Get district (most common district in cluster)
            district = self._get_most_common(districts) if districts else None

            results.append({
                "cluster_id": int(cluster_id),
                "centroid_lat": centroid_lat,
                "centroid_lng": centroid_lng,
                "point_count": len(points),
                "radius_km": radius_km,
                "dominant_crime_type": dominant_crime_type,
                "district": district,
            })

        # Sort by point count (descending)
        results.sort(key=lambda x: x["point_count"], reverse=True)

        return results

    def _get_dominant_crime_type(self, crime_types: list[str]) -> str:
        """
        Get the most common crime type in the cluster.
        
        Args:
            crime_types: List of crime type strings.
        
        Returns:
            The most common crime type, or "Unknown" if empty.
        """
        if not crime_types:
            return "Unknown"
        return self._get_most_common(crime_types)

    def _get_most_common(self, items: list[str]) -> str:
        """
        Get the most common item in a list.
        
        Args:
            items: List of strings.
        
        Returns:
            The most common string, or the first item if all are unique.
        """
        if not items:
            return None
        from collections import Counter
        counter = Counter(items)
        return counter.most_common(1)[0][0]
