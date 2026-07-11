# PRISM — Network Explorer Page: Complete Specification

> The Network Explorer is where investigators **visualize criminal networks, detect gangs,
> identify repeat offenders, and understand relationships between accused persons**.
>
> This page turns raw FIR data into an interactive force-directed graph that reveals
> hidden structures in crime networks that Excel spreadsheets never could.

---

## What This Page Shows (At a Glance)

```
┌─────────────────────────────────────────────────────────┐
│  NETWORK EXPLORER                                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Filters Panel]        [Force-Directed Graph]         │
│  ──────────────         ──────────────────────         │
│  • Search by name       • Nodes:                        │
│  • Crime type filter      - Red circles: Accused       │
│  • District filter        - Grey squares: Incidents    │
│  • Date range            - Blue diamonds: Locations    │
│  • Legend               • Edges:                        │
│    (node types)          - Thickness = strength        │
│                          - Color = relationship type   │
│                                                         │
│                        [Node Detail Panel]             │
│                        ──────────────────              │
│                        • Accused name, age, gender    │
│                        • Risk score 0-100             │
│                        • Appears in N FIRs            │
│                        • Connected to X people        │
│                        • Gang cluster #N              │
│                        • [View Full Profile]          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Core concept:** Every accused person is a NODE. Every co-appearance in an FIR creates an EDGE.
The graph reveals which offenders work together, which territories they control, and which ones are central figures (hubs).

---

## The Three Network Views (Tabs)

Users toggle between three visualizations of the same underlying graph:

### View 1: "All Connections" (default)
- Shows every node and edge
- Highest density but most informative
- Best for exploratory pattern hunting
- Might look cluttered for large cities, but reflects reality of complex networks

### View 2: "Gang Clusters"
- Same graph, but nodes are colored by community detection result (Louvain algorithm)
- Each cluster outlined with a dashed circle + label ("Cluster #3 — Suspected Gang")
- Shows 5-8 largest clusters clearly
- Edges outside clusters (cross-cluster links) highlighted in different color
- Best for "who are the organized groups?"

### View 3: "Repeat Offenders"
- Filters graph to only show accused with 2+ FIRs
- Highlights repeat offenders and their networks
- Edges show co-appearance counts (thicker = more FIRs together)
- Best for "who keeps getting arrested?"

---

## What Happens On-Screen (User Interactions)

1. **Page loads** → Backend computes full graph (co-accused network)
2. **User types in search box** → Filter nodes by name (fuzzy match), graph re-renders
3. **User clicks crime type dropdown** → Filter nodes to those in selected crime category only
4. **User clicks a district filter** → Show only accused active in that district
5. **User clicks a node** → Right panel pops in with accused profile card
6. **User drags date range slider** → Re-fetch graph for only FIRs in that period
7. **User clicks "Gang Clusters" tab** → Re-color nodes by community, add cluster labels
8. **User hovers over edge** → Tooltip shows "co-accused in 3 FIRs" or similar

---

## Core Data Structures

### Node (Accused Person)

```typescript
interface GraphNode {
  id: string;                    // "accused_2001" (from AccusedMasterID)
  label: string;                 // "Abdul Rauf Khan"
  type: "accused" | "incident" | "location";
  
  // Accused-specific properties
  age?: number;
  gender?: "M" | "F" | "T";
  fir_count?: number;            // appears in N FIRs
  is_absconding?: boolean;       // no ArrestSurrender record
  risk_score?: number;           // 0-100
  gang_cluster?: number;         // which cluster (from Louvain)
  primary_district?: string;
  last_seen_date?: string;
  
  // Rendering hints
  size: number;                  // node radius (based on fir_count)
  color: string;                 // red for high risk, orange for medium, etc.
  x?: number;                    // force layout coordinates (D3 sets these)
  y?: number;
}

interface GraphEdge {
  source: string;                // node id
  target: string;                // node id
  type: "co_accused" | "location_overlap" | "temporal_proximity";
  strength: number;              // how many times co-appeared (1-N)
  incidents: number[];           // CaseMasterIDs that created this edge
  
  // Rendering
  thickness: number;             // based on strength (1-5px)
  color: string;                 // red for organized crime suspects, grey for casual
}
```

---

## Backend Architecture

### Three Layers

**Layer 1: Graph Construction** — Happens at request time OR on schedule
- Query `Accused` → get all accused across all FIRs
- Query co-accused relationships (same FIR)
- Compute fuzzy name matching to resolve repeat offenders
- Build NetworkX graph object in Python

**Layer 2: Graph Analysis** — Happens on the graph object
- Louvain community detection (identify gangs)
- Centrality metrics (who's the kingpin)
- Shortest paths (connections between any two people)
- Subgraph extraction (filter by crime type, district, date)

**Layer 3: Serialization** — Convert NetworkX → JSON for frontend
- Nodes array: `[{id, label, type, ...}, ...]`
- Edges array: `[{source, target, strength, type}, ...]`
- Metadata: `{max_risk_score, cluster_count, top_10_nodes_by_centrality}`

---

## Backend — API Endpoints

### Endpoint 1: Get Full Graph

**Route:** `GET /api/network/graph`

**Query parameters:**
```
crime_type: string (optional)    # filter to CrimeSubHeadID
district: string (optional)       # filter to district name
date_from: ISO date (optional)   # filter by IncidentFromDate
date_to: ISO date (optional)
view: "all" | "clusters" | "repeat" (default: "all")
```

**Response:**
```typescript
{
  nodes: GraphNode[],
  edges: GraphEdge[],
  metadata: {
    total_nodes: number,
    total_edges: number,
    largest_cluster_size: number,
    num_clusters: number,
    densest_node: {name, centrality_score},
    generated_at: ISO datetime
  }
}
```

**Backend file:** `backend/routers/network.py`

```python
@router.get("/api/network/graph", response_model=GraphResponse)
async def get_network_graph(
    crime_type: Optional[str] = None,
    district: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    view: str = "all",
    db=Depends(get_db),
    user=Depends(require_role(["analyst", "supervisor"]))  # more restrictive than chat
):
    """
    Constructs co-accused network graph from FIR data.
    
    Filters by crime type, district, date if provided.
    Applies Louvain community detection.
    Returns serialized NetworkX graph ready for D3 rendering.
    """
    pass
```

**Backend logic file:** `backend/agents/network_agent/agent.py`

This is where the heavy lifting happens:

```python
class NetworkAgent:
    def __init__(self, db):
        self.db = db
        self.graph = nx.Graph()
    
    def build_graph(self, filters: GraphFilters) -> nx.Graph:
        """
        1. Query accused persons matching filters
        2. Find co-accused relationships (same FIR)
        3. Fuzzy-match to resolve repeat offenders
        4. Add to NetworkX graph
        5. Return graph
        """
        pass
    
    def detect_communities(self) -> Dict[int, int]:
        """
        Run Louvain algorithm on the graph.
        Return node_id → cluster_id mapping.
        """
        pass
    
    def compute_centrality(self) -> Dict[int, float]:
        """
        Betweenness centrality for each node.
        High centrality = kingpin/hub in network.
        """
        pass
    
    def serialize(self) -> GraphResponse:
        """
        Convert NetworkX graph to JSON response object.
        """
        pass
```

---

### Endpoint 2: Get Accused Profile

**Route:** `GET /api/network/profile/{accused_id}`

**Response:**
```typescript
{
  accused_id: number;
  name: string;
  age: number;
  gender: string;
  fir_count: number;                 // total FIRs this person appears in
  firs: Array<{
    case_master_id: number,
    crime_type: string,
    date: ISO date,
    district: string,
    status: "Under Investigation" | "Charge Sheeted" | "Closed"
  }>;
  co_accused: Array<{               // who they typically work with
    name: string,
    times_together: number,          // number of shared FIRs
    risk_score: number
  }>;
  crime_types: Array<{              // what crimes they're known for
    name: string,
    count: number
  }>;
  modus_operandi: string;            // LLM-extracted MO summary
  risk_score: number;
  gang_cluster: number;
  is_absconding: boolean;
  last_seen_date: string;
}
```

**Backend file:** `backend/routers/network.py` (add)

```python
@router.get("/api/network/profile/{accused_id}", response_model=AccusedProfileResponse)
async def get_accused_profile(
    accused_id: int,
    db=Depends(get_db),
    user=Depends(require_role(["analyst", "supervisor"]))
):
    """
    Full profile of an accused person including their criminal history,
    associates, risk scoring, and gang affiliation.
    """
    pass
```

---

### Endpoint 3: Search Accused

**Route:** `GET /api/network/search`

**Query parameters:**
```
q: string          # search term (name, partial name)
limit: int = 10    # max results to return
```

**Response:**
```typescript
{
  results: Array<{
    accused_id: number,
    name: string,
    fir_count: number,
    risk_score: number,
    last_fir_date: string
  }>
}
```

**Backend file:** `backend/routers/network.py` (add)

```python
@router.get("/api/network/search", response_model=SearchResponse)
async def search_accused(
    q: str,
    limit: int = 10,
    db=Depends(get_db),
    user=Depends(require_role(["analyst", "supervisor"]))
):
    """
    Fuzzy search across accused names.
    Returns top matches ranked by fir_count (most active offenders first).
    """
    pass
```

---

## Frontend Architecture

### File Structure

```
frontend/src/
├── pages/NetworkExplorer/
│   └── index.tsx                    # main page component
├── components/network/
│   ├── NetworkGraph.tsx             # D3 force-directed graph
│   ├── FilterPanel.tsx              # left sidebar with filters
│   ├── NodeDetailPanel.tsx          # right sidebar with profile
│   ├── ClusterLabel.tsx             # labels for gang clusters
│   └── LegendPanel.tsx              # node type legend
├── services/network.service.ts      # API calls
├── hooks/useNetworkGraph.ts         # graph data hook
└── types/network.ts                 # TypeScript interfaces
```

### Main Component: `NetworkExplorer/index.tsx`

```typescript
export default function NetworkExplorer() {
  // State
  const [view, setView] = useState<'all' | 'clusters' | 'repeat'>('all');
  const [filters, setFilters] = useState<GraphFilters>({
    crime_type: null,
    district: null,
    date_from: null,
    date_to: null,
  });
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // Data fetching
  const { nodes, edges, metadata, loading, error } = useNetworkGraph(filters, view);

  return (
    <div className="flex h-full gap-4">
      {/* Left: Filter Panel */}
      <FilterPanel filters={filters} onFiltersChange={setFilters} />

      {/* Center: Graph Canvas */}
      <div className="flex-1">
        <div className="mb-4 flex gap-2">
          <button onClick={() => setView('all')} className={view === 'all' ? 'active' : ''}>
            All Connections
          </button>
          <button onClick={() => setView('clusters')} className={view === 'clusters' ? 'active' : ''}>
            Gang Clusters
          </button>
          <button onClick={() => setView('repeat')} className={view === 'repeat' ? 'active' : ''}>
            Repeat Offenders
          </button>
        </div>
        
        <NetworkGraph
          nodes={nodes}
          edges={edges}
          selectedNodeId={selectedNodeId}
          onNodeClick={setSelectedNodeId}
          view={view}
          metadata={metadata}
        />
      </div>

      {/* Right: Detail Panel */}
      {selectedNodeId && (
        <NodeDetailPanel accusedId={parseInt(selectedNodeId)} />
      )}
    </div>
  );
}
```

---

### Component 2: `FilterPanel.tsx`

```typescript
interface FilterPanelProps {
  filters: GraphFilters;
  onFiltersChange: (filters: GraphFilters) => void;
}

export function FilterPanel({ filters, onFiltersChange }: FilterPanelProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const { results: searchResults, loading: searching } = useSearchAccused(searchQuery);

  return (
    <div className="w-64 bg-panel border-l border-tactical p-4 flex flex-col gap-4 overflow-y-auto">
      <div>
        <label className="block text-xs text-on-surface-variant mb-2 uppercase">
          Search by Name
        </label>
        <input
          type="text"
          placeholder="Type accused name..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-surface border border-tactical rounded px-2 py-1 text-sm"
        />
        {searching && <span className="text-xs text-on-surface-variant">Searching...</span>}
        {searchResults.map((result) => (
          <div key={result.accused_id} className="text-xs mt-2 p-2 bg-surface rounded cursor-pointer">
            {result.name} ({result.fir_count} FIRs)
          </div>
        ))}
      </div>

      <div>
        <label className="block text-xs text-on-surface-variant mb-2 uppercase">
          Crime Type
        </label>
        <select
          value={filters.crime_type || ''}
          onChange={(e) =>
            onFiltersChange({ ...filters, crime_type: e.target.value || null })
          }
          className="w-full bg-surface border border-tactical rounded px-2 py-1 text-sm"
        >
          <option value="">All Crime Types</option>
          <option value="Murder">Murder</option>
          <option value="Robbery">Robbery</option>
          <option value="Theft">Theft</option>
          {/* ... more options ... */}
        </select>
      </div>

      <div>
        <label className="block text-xs text-on-surface-variant mb-2 uppercase">
          District
        </label>
        <select
          value={filters.district || ''}
          onChange={(e) =>
            onFiltersChange({ ...filters, district: e.target.value || null })
          }
          className="w-full bg-surface border border-tactical rounded px-2 py-1 text-sm"
        >
          <option value="">All Districts</option>
          <option value="Bengaluru Urban">Bengaluru Urban</option>
          <option value="Mysuru">Mysuru</option>
          {/* ... more districts ... */}
        </select>
      </div>

      <div>
        <label className="block text-xs text-on-surface-variant mb-2 uppercase">
          Date Range
        </label>
        <input
          type="date"
          value={filters.date_from || ''}
          onChange={(e) =>
            onFiltersChange({ ...filters, date_from: e.target.value || null })
          }
          className="w-full bg-surface border border-tactical rounded px-2 py-1 text-sm mb-2"
        />
        <input
          type="date"
          value={filters.date_to || ''}
          onChange={(e) =>
            onFiltersChange({ ...filters, date_to: e.target.value || null })
          }
          className="w-full bg-surface border border-tactical rounded px-2 py-1 text-sm"
        />
      </div>

      <div className="mt-auto pt-4 border-t border-tactical">
        <h4 className="text-xs text-on-surface-variant uppercase mb-2">Legend</h4>
        <div className="space-y-2 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-error"></div>
            <span>High Risk (70-100)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-orange-500"></div>
            <span>Medium Risk (40-69)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-primary-container"></div>
            <span>Low Risk (0-39)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

### Component 3: `NetworkGraph.tsx` (D3 Force-Directed)

This is the most complex component. It uses D3.js force simulation.

```typescript
interface NetworkGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNodeId: string | null;
  onNodeClick: (nodeId: string) => void;
  view: 'all' | 'clusters' | 'repeat';
  metadata: GraphMetadata;
}

export function NetworkGraph({
  nodes,
  edges,
  selectedNodeId,
  onNodeClick,
  view,
  metadata,
}: NetworkGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [simulation, setSimulation] = useState<d3.Simulation<any, undefined> | null>(null);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    // Create force simulation
    const sim = d3
      .forceSimulation(nodes)
      .force(
        'link',
        d3
          .forceLink(edges)
          .id((d: any) => d.id)
          .distance((d: any) => Math.max(50, 200 / Math.sqrt(d.strength)))
          .strength(0.5)
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius((d: any) => d.size + 5));

    // D3 rendering code here...
    // This is a lot of SVG / canvas manipulation

    setSimulation(sim);

    return () => {
      sim.stop();
    };
  }, [nodes, edges, view]);

  return (
    <svg
      ref={svgRef}
      className="w-full h-full bg-[#050608]"
      style={{ cursor: 'grab' }}
    />
  );
}
```

---

### Component 4: `NodeDetailPanel.tsx`

```typescript
interface NodeDetailPanelProps {
  accusedId: number;
}

export function NodeDetailPanel({ accusedId }: NodeDetailPanelProps) {
  const { profile, loading } = useAccusedProfile(accusedId);

  if (loading) return <div className="p-4">Loading...</div>;
  if (!profile) return <div className="p-4">Not found</div>;

  return (
    <div className="w-80 bg-panel border-l border-tactical p-4 overflow-y-auto">
      <h2 className="text-lg font-bold text-on-surface mb-4">{profile.name}</h2>

      {/* Risk Score */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-on-surface-variant uppercase">Risk Score</span>
          <span className={`text-lg font-bold ${
            profile.risk_score >= 70 ? 'text-error' :
            profile.risk_score >= 40 ? 'text-orange-500' :
            'text-primary-container'
          }`}>
            {profile.risk_score}
          </span>
        </div>
        <div className="w-full h-2 bg-surface rounded-full overflow-hidden">
          <div
            className={`h-full ${
              profile.risk_score >= 70 ? 'bg-error' :
              profile.risk_score >= 40 ? 'bg-orange-500' :
              'bg-primary-container'
            }`}
            style={{ width: `${profile.risk_score}%` }}
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-2 mb-4 text-sm">
        <div>
          <span className="text-xs text-on-surface-variant">Age</span>
          <div className="text-on-surface">{profile.age}</div>
        </div>
        <div>
          <span className="text-xs text-on-surface-variant">Gender</span>
          <div className="text-on-surface">{profile.gender}</div>
        </div>
        <div>
          <span className="text-xs text-on-surface-variant">FIRs</span>
          <div className="text-on-surface">{profile.fir_count}</div>
        </div>
        <div>
          <span className="text-xs text-on-surface-variant">Status</span>
          <div className={profile.is_absconding ? 'text-error' : 'text-primary'}>
            {profile.is_absconding ? 'Absconding' : 'Arrested'}
          </div>
        </div>
      </div>

      {/* Co-accused */}
      <div className="mb-4">
        <h3 className="text-xs text-on-surface-variant uppercase mb-2">Associates</h3>
        <div className="space-y-2">
          {profile.co_accused.map((coAcc) => (
            <div key={coAcc.name} className="text-xs p-2 bg-surface rounded">
              <div className="text-on-surface font-bold">{coAcc.name}</div>
              <div className="text-on-surface-variant">{coAcc.times_together} shared FIRs</div>
            </div>
          ))}
        </div>
      </div>

      {/* Crime Types */}
      <div className="mb-4">
        <h3 className="text-xs text-on-surface-variant uppercase mb-2">Crime Types</h3>
        <div className="space-y-1 text-xs">
          {profile.crime_types.map((ct) => (
            <div key={ct.name} className="flex justify-between">
              <span>{ct.name}</span>
              <span className="text-on-surface-variant">{ct.count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* MO */}
      {profile.modus_operandi && (
        <div className="mb-4 p-3 bg-surface rounded">
          <h3 className="text-xs text-on-surface-variant uppercase mb-2">Modus Operandi</h3>
          <p className="text-xs text-on-surface">{profile.modus_operandi}</p>
        </div>
      )}

      {/* FIRs Timeline */}
      <div>
        <h3 className="text-xs text-on-surface-variant uppercase mb-2">Recent FIRs</h3>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {profile.firs.slice(0, 5).map((fir) => (
            <div key={fir.case_master_id} className="text-xs p-2 bg-surface rounded border border-tactical">
              <div className="text-on-surface font-mono">{fir.case_master_id}</div>
              <div className="text-on-surface-variant">{fir.crime_type}</div>
              <div className="text-on-surface-variant text-xs">{new Date(fir.date).toLocaleDateString()}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## Complete API Summary for Network Explorer

| Endpoint | Method | Purpose |
|---|---|---|
| `GET /api/network/graph` | GET | Full co-accused graph (all nodes + edges) with filtering |
| `GET /api/network/profile/{accused_id}` | GET | Full profile of one accused person |
| `GET /api/network/search` | GET | Fuzzy search accused by name |

---

## Implementation Roadmap

```
Phase 1: Backend Graph Construction (Days 1-3)
  ├── build_graph() — query Accused + co-accused relationships
  ├── entity_resolver — fuzzy match for repeat offenders
  ├── Endpoint 1 & 2 & 3 stubbed with hardcoded data
  └── Louvain community detection working on test data

Phase 2: Frontend Graph Rendering (Days 4-6)
  ├── D3 force-directed layout working
  ├── Node/edge rendering
  ├── Hover tooltips
  └── Click to select node

Phase 3: Frontend Interactions (Days 7-8)
  ├── Filter panel fully functional
  ├── View toggle (all/clusters/repeat)
  ├── Detail panel population
  └── Search autocomplete

Phase 4: Polish & Optimization (Days 9-10)
  ├── Performance tuning (graph too slow?)
  ├── Caching large graphs in localStorage
  ├── Error handling
  └── Loading states
```

---

## Key Technical Challenges

1. **Performance:** Graph with 500+ nodes = slow D3 simulation. Solution: Use `simulation.tick(300)` to pre-compute 300 iterations before rendering.

2. **Name matching:** "Abdul Rauf Khan" vs "A. Rauf Khan" vs "Rauf Khan A" = 3 different rows in Accused table but same person. Solution: Use rapidfuzz token_sort_ratio > 85 + age within 2 years + same gender.

3. **Clustering on large networks:** Louvain algorithm is O(n log n) but can be slow. Solution: Cache results in Redis, re-run only on Cron schedule, not per-request.

4. **D3 in React:** D3 mutates DOM directly. React also mutates DOM. They fight. Solution: D3 updates SVG contents, React only manages the container + interaction state.

---

## Files to Create

```
backend/
├── routers/network.py                    ← CREATE
├── agents/network_agent/
│   ├── agent.py                         ← CREATE
│   ├── graph_builder.py                 ← CREATE (build_graph)
│   ├── entity_resolver.py               ← CREATE (fuzzy matching)
│   ├── community_detection.py           ← CREATE (Louvain)
│   └── centrality.py                    ← CREATE (betweenness, degree)

frontend/src/
├── pages/NetworkExplorer/index.tsx      ← CREATE
├── components/network/
│   ├── NetworkGraph.tsx                 ← CREATE (D3 graph)
│   ├── FilterPanel.tsx                  ← CREATE
│   ├── NodeDetailPanel.tsx              ← CREATE
│   └── LegendPanel.tsx                  ← CREATE
├── services/network.service.ts          ← CREATE
├── hooks/useNetworkGraph.ts             ← CREATE
└── types/network.ts                     ← CREATE
```

---

## Next Steps

1. **Clarify scope with stakeholders** — How many nodes is "acceptable"? 500? 2000? This determines caching strategy.

2. **Start with Backend Graph Construction** — Get co-accused relationships working before touching D3.

3. **Test with seed data** — Use the 4 demo FIRs to verify entity resolution finds "Abdul Rauf Khan" appears twice.

4. **Stub frontend with mock data** — Render a 10-node graph with D3 using hardcoded data before wiring the API.

5. **Wire endpoints one by one** — Get graph endpoint working, then profile endpoint, then search.
