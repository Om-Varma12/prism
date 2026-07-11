# Network Explorer Implementation Steps

This plan turns the current mocked `NetworkExplorerScreen` into a live co-accused network feature backed by Catalyst ZCQL data. Each step is intended to be a small, reviewable commit with a concrete user-visible or architectural outcome.

## Current Baseline

- The frontend already has `frontend/src/components/NetworkExplorerScreen.tsx`, but it uses hardcoded nodes, edges, filters, and suspect profiles from `mockData.ts`.
- There is no `backend/routers/network.py` mounted in `backend/main.py`.
- There are no network-specific schemas, services, hooks, or backend graph-agent modules in the actual codebase.
- The feature spec expects three views: all connections, gang clusters, and repeat offenders.
- The live data source should be Catalyst ZCQL over `CaseMaster`, `Accused`, `Unit`, `District`, `CrimeSubHead`, `ArrestSurrender`, and optionally `risk_scores`.

---

## Step 1: Add Shared Network Data Contracts

**Commit message:** `feat(network): add graph response contracts`

**Do:**
- Create backend Pydantic schemas for graph nodes, edges, metadata, filters, accused profiles, and search responses.
- Create matching frontend TypeScript types for graph responses, filters, profile details, and search results.
- Keep field names aligned with the spec: `nodes`, `edges`, `metadata`, `risk_score`, `fir_count`, `gang_cluster`, `is_absconding`.

**Achieves:**
- Establishes the API contract before implementation.
- Prevents frontend/backend drift while the feature is built in parallel.

---

## Step 2: Create Network Router With Safe Stub Endpoints

**Commit message:** `feat(network): scaffold network api routes`

**Do:**
- Add `backend/routers/network.py`.
- Implement stubbed versions of:
  - `GET /api/network/graph`
  - `GET /api/network/profile/{accused_id}`
  - `GET /api/network/search`
- Mount the router in `backend/main.py`.
- Use the same `require_role` dependency pattern as dashboard/chat for now.

**Achieves:**
- Gives the frontend stable endpoints immediately.
- Allows API integration work before full graph construction is ready.

---

## Step 3: Build Basic Co-Accused Graph Querying

**Commit message:** `feat(network): build co-accused graph from zcql`

**Do:**
- Create `backend/agents/network_agent/graph_builder.py`.
- Query accused rows joined to `CaseMaster`, `CrimeSubHead`, `Unit`, and `District`.
- Group accused by `CaseMaster.ROWID`.
- Create one node per accused row initially.
- Create one `co_accused` edge for each pair of accused in the same FIR.
- Aggregate repeated co-appearances into edge `strength`.

**Achieves:**
- Replaces hardcoded graph data with actual FIR-derived relationships.
- Produces the core intelligence structure: people connected by shared cases.

---

## Step 4: Add Graph Filtering

**Commit message:** `feat(network): support graph filters`

**Do:**
- Support `crime_type`, `district`, `date_from`, `date_to`, and `view` query params in `/api/network/graph`.
- Translate filters into ZCQL-safe `WHERE` clauses.
- Keep date filtering on `CaseMaster.IncidentFromDate`.
- Add conservative limits or default date windows if graph size becomes too large.

**Achieves:**
- Makes the graph useful for investigation slices instead of one huge global view.
- Enables frontend filter controls to affect live graph data.

---

## Step 5: Add Network Metrics and Serialization

**Commit message:** `feat(network): compute graph metrics`

**Do:**
- Add `backend/agents/network_agent/centrality.py`.
- Compute degree, weighted degree, and a simple centrality score from the built graph.
- Add node rendering hints: `size`, `color`, `risk_score`, `fir_count`, and `primary_district`.
- Fill response metadata: total nodes, total edges, densest node, generated timestamp.

**Achieves:**
- Makes the graph visually meaningful, not just connected.
- Enables "kingpin" and "hub" style interpretation from graph structure.

---

## Step 6: Implement Repeat Offender View

**Commit message:** `feat(network): add repeat offender graph view`

**Do:**
- Make `view=repeat` return only accused identities with 2+ FIR appearances.
- Preserve edges among repeat offenders.
- Add metadata counts for repeat offenders and filtered edges.
- Ensure the endpoint returns an empty-but-valid graph when there are no repeat offenders.

**Achieves:**
- Delivers one of the three required tabs with real backend behavior.
- Helps investigators focus on recurring offenders instead of one-off cases.

---

## Step 7: Add Community Detection for Gang Clusters

**Commit message:** `feat(network): detect gang clusters`

**Do:**
- Create `backend/agents/network_agent/community_detection.py`.
- Start with a dependency-light connected-components fallback if a Louvain package is not available.
- Assign `gang_cluster` IDs to nodes.
- Make `view=clusters` return clustered nodes and cluster metadata.
- Keep the implementation swappable so Louvain can replace the fallback later.

**Achieves:**
- Delivers the second major investigative view.
- Surfaces suspected groups even before advanced graph analytics are tuned.

---

## Step 8: Build Accused Profile Endpoint

**Commit message:** `feat(network): add accused profile endpoint`

**Do:**
- Implement `GET /api/network/profile/{accused_id}`.
- Return accused demographics, FIR history, crime type counts, district history, co-accused list, risk score, absconding status, and last seen date.
- Use `LEFT JOIN ArrestSurrender` for absconding detection.
- Use `risk_scores` if available, with a deterministic fallback score if not.

**Achieves:**
- Powers the right-side detail panel with real data.
- Lets a clicked graph node become an actionable investigator profile.

---

## Step 9: Build Accused Search Endpoint

**Commit message:** `feat(network): add accused search`

**Do:**
- Implement `GET /api/network/search?q=&limit=`.
- Search `Accused.AccusedName` using Catalyst-compatible wildcard matching.
- Rank results by FIR count and latest FIR date.
- Return compact results for autocomplete.

**Achieves:**
- Enables fast lookup by accused name.
- Makes the filter panel useful for targeted investigations.

---

## Step 10: Add Frontend Network API Layer

**Commit message:** `feat(network): add frontend network data hooks`

**Do:**
- Create `frontend/src/services/network.service.ts`.
- Create `frontend/src/hooks/useNetworkGraph.ts`.
- Add hooks for graph loading, profile loading, and accused search.
- Use React Query for caching and loading/error states, matching the dashboard pattern.

**Achieves:**
- Creates a clean frontend data boundary.
- Keeps network API calls out of the UI component.

---

## Step 11: Replace Mock Graph With Live Graph State

**Commit message:** `feat(network): wire explorer to live graph data`

**Do:**
- Refactor `NetworkExplorerScreen.tsx` to use `useNetworkGraph`.
- Keep the current tactical layout and visual language.
- Replace hardcoded nodes, connections, filters, and profile data with API-backed state.
- Keep a small local fallback only for empty/error states, not normal operation.

**Achieves:**
- Converts the page from demo-only mock UI to real product behavior.
- Preserves the existing look while changing the data source underneath.

---

## Step 12: Implement Real Graph Rendering Component

**Commit message:** `feat(network): render interactive force graph`

**Do:**
- Create `frontend/src/components/network/NetworkGraph.tsx`.
- Render nodes and edges from backend JSON.
- Support node click, edge hover tooltip, selected-node highlighting, connected-neighbor highlighting, zoom, and pan.
- Use SVG first; introduce D3 force simulation only if dependency and performance constraints are acceptable.

**Achieves:**
- Delivers the central feature experience: an interactive relationship graph.
- Makes graph structure legible through edge thickness, node size, and color.

---

## Step 13: Add Filter and Detail Panels

**Commit message:** `feat(network): add graph filters and profile panel`

**Do:**
- Create `FilterPanel`, `NodeDetailPanel`, and `LegendPanel` components under `frontend/src/components/network/`.
- Wire search, district, crime type, date range, and view tabs to graph refetching.
- Load profile data when a node is selected.
- Show FIR timeline, associates, crime mix, risk score, and absconding status in the detail panel.

**Achieves:**
- Completes the investigator workflow around the graph.
- Turns graph clicks into usable case intelligence.

---

## Step 14: Add Entity Resolution and Risk Improvements

**Commit message:** `feat(network): resolve repeated accused identities`

**Do:**
- Create `backend/agents/network_agent/entity_resolver.py`.
- Normalize accused names and merge likely duplicates using name similarity, age proximity, and gender.
- Keep a transparent `aliases` list on resolved nodes when multiple rows are merged.
- Improve risk scoring from `fir_count`, absconding status, gravity, and crime spread.

**Achieves:**
- Reduces duplicate nodes for the same person.
- Makes repeat-offender and gang-cluster views more accurate.

---

## Step 15: Test, Tune, and Document the Feature

**Commit message:** `test(network): cover graph api and explorer states`

**Do:**
- Add backend tests for graph construction, filters, repeat view, cluster assignment, search, and profile responses.
- Add frontend tests for loading, empty, error, filter, tab, and selected-profile states.
- Add lightweight docs for the network API and known performance limits.
- Run frontend build and backend tests before merging.

**Achieves:**
- Gives the feature a verification net.
- Documents what is live, what is approximated, and where future optimization belongs.

---

## Recommended Build Order

1. Finish Steps 1-5 first to get a live graph API.
2. Then implement Steps 10-13 to replace the mock UI.
3. Add Steps 6-9 as soon as the base graph is stable.
4. Save Step 14 for after live data exposes actual duplicate-name problems.
5. Use Step 15 throughout, but make it the final hardening commit before demo or deployment.

## Definition of Done

- Network Explorer no longer depends on `MOCK_SUSPECTS` for normal rendering.
- `/api/network/graph` returns real nodes and edges from Catalyst data.
- All three views work: all connections, gang clusters, repeat offenders.
- Clicking a node shows a real accused profile.
- Search and filters change the graph data.
- Empty, loading, and error states are handled cleanly.
- The feature builds successfully with `npm run build`.
