"""
Pydantic schemas for the Network Explorer API.
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


GraphView = Literal["all", "clusters", "repeat"]
NodeType = Literal["accused", "incident", "location"]
EdgeType = Literal["co_accused", "location_overlap", "temporal_proximity"]


class GraphFilters(BaseModel):
    """Optional filters accepted by the graph endpoint."""

    crime_type: Optional[str] = None
    district: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    view: GraphView = "all"


class GraphNode(BaseModel):
    """Serializable node rendered by the Network Explorer graph."""

    id: str
    label: str
    type: NodeType = "accused"
    accused_id: Optional[int] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    fir_count: int = 0
    is_absconding: bool = False
    risk_score: float = 0
    gang_cluster: Optional[int] = None
    primary_district: Optional[str] = None
    last_seen_date: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)
    size: float = 8
    color: str = "#3B6FE8"
    centrality_score: float = 0


class EdgeIncident(BaseModel):
    """A single FIR that justifies a co-accused edge connection."""

    case_master_id: int
    crime_no: Optional[str] = None


class GraphEdge(BaseModel):
    """Serializable edge between two graph nodes."""

    source: str
    target: str
    type: EdgeType = "co_accused"
    strength: int = 1
    incidents: list[EdgeIncident] = Field(default_factory=list)
    thickness: float = 1
    color: str = "#44474f"


class DensestNode(BaseModel):
    """Summary of the most connected node in a graph response."""

    id: Optional[str] = None
    name: Optional[str] = None
    centrality_score: float = 0


class GraphMetadata(BaseModel):
    """Graph-level metrics and generation details."""

    total_nodes: int
    total_edges: int
    largest_cluster_size: int = 0
    num_clusters: int = 0
    repeat_offender_count: int = 0
    densest_node: Optional[DensestNode] = None
    generated_at: datetime


class GraphResponse(BaseModel):
    """Response body for GET /api/network/graph."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]
    metadata: GraphMetadata


class AccusedFirSummary(BaseModel):
    """Single FIR entry shown inside an accused profile."""

    case_master_id: int
    crime_no: Optional[str] = None
    crime_type: Optional[str] = None
    date: Optional[str] = None
    district: Optional[str] = None
    status: Optional[str] = None


class CoAccusedSummary(BaseModel):
    """Known associate for an accused profile."""

    accused_id: Optional[int] = None
    name: str
    times_together: int
    risk_score: float = 0


class CrimeTypeSummary(BaseModel):
    """Crime-type count for an accused profile."""

    name: str
    count: int


class AccusedProfileResponse(BaseModel):
    """Response body for GET /api/network/profile/{accused_id}."""

    accused_id: int
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    fir_count: int
    firs: list[AccusedFirSummary] = Field(default_factory=list)
    co_accused: list[CoAccusedSummary] = Field(default_factory=list)
    crime_types: list[CrimeTypeSummary] = Field(default_factory=list)
    modus_operandi: Optional[str] = None
    risk_score: float = 0
    gang_cluster: Optional[int] = None
    is_absconding: bool = False
    last_seen_date: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    """Single accused search result."""

    accused_id: int
    name: str
    fir_count: int
    risk_score: float = 0
    last_fir_date: Optional[str] = None


class SearchResponse(BaseModel):
    """Response body for GET /api/network/search."""

    results: list[SearchResult]
