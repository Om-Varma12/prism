"""
Network Explorer API routes.

These endpoints are scaffolded with valid response shapes first so the frontend
can integrate against a stable contract while graph construction is built out.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends

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
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Return the co-accused network graph.

    Step 2 intentionally returns an empty but valid graph. Later steps will use
    the query parameters above to build and filter a live graph from Catalyst.
    """
    return _empty_graph_response()


@router.get("/profile/{accused_id}", response_model=AccusedProfileResponse)
async def get_accused_profile(
    accused_id: int,
    user=Depends(require_role(["investigator", "analyst", "supervisor"])),
):
    """
    Return a single accused profile.

    This is a placeholder response until the profile query layer is added.
    """
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
