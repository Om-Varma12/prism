```
prism/
│
├── README.md
├── .gitignore
├── .catalystrc                            # Catalyst CLI project config
├── catalyst.json                          # Catalyst project metadata
├── TODO                                   # open tasks / roadmap notes
├── project-structure.md                   # this file
├── services-used.md                       # list of Catalyst services consumed
│
├── resources/                             # Catalyst API reference docs (offline)
│   ├── cache/                             # Cache service reference
│   ├── quickml/                           # Quick ML / LLM reference
│   ├── stratus/                           # Stratus object-storage reference
│   └── zcql/                              # ZCQL query language reference
│
├── implementations/                       # Feature-level design docs & specs
│   ├── analytics/
│   │   └── ANALYTICS_PAGE_SPEC.md
│   ├── chat-interface/
│   │   ├── PLAN.md
│   │   └── STEPS.md
│   ├── dashboard/
│   │   ├── DASHBOARD_SPEC.md
│   │   ├── PLAN.md
│   │   └── STEPS.md
│   └── network-explorer/
│       ├── NETWORK_EXPLORER_SPEC.md
│       ├── NETWORK_EXPLORER_SUMMARY.txt
│       └── STEPS.md
│
├── frontend/                              # Create React App + TypeScript
│   ├── package.json
│   ├── tsconfig.json
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── logo192.png
│   ├── DESIGN.md                          # frontend design guidelines & tokens
│   │
│   └── src/
│       ├── index.tsx                      # app entry point (ReactDOM.render)
│       ├── index.css                      # global styles & CSS variables
│       ├── App.tsx                        # top-level routing, page switching
│       ├── App.css                        # app-level styles
│       ├── App.test.tsx
│       ├── react-app-env.d.ts
│       ├── reportWebVitals.ts
│       ├── setupTests.ts
│       ├── logo.svg
│       │
│       ├── types.ts                       # shared TypeScript types (chat, sessions, etc.)
│       │
│       ├── types/                         # domain-specific TypeScript interfaces
│       │   ├── analytics.ts               # HotspotPoint, TrendData, RiskScore types
│       │   └── network.ts                 # GraphNode, GraphEdge, NetworkGraph types
│       │
│       ├── constants/
│       │   └── districtCoordinates.ts     # lat/lng for each Karnataka district
│       │
│       ├── data/
│       │   └── mockData.ts                # static mock data for dev/testing
│       │
│       ├── lib/
│       │   └── api-client.ts              # axios instance with base URL + headers
│       │
│       ├── hooks/                         # custom React hooks
│       │   ├── useChat.ts                 # session management, message send/receive, URL sync
│       │   ├── useChatQuery.ts            # React Query hooks for chat history & session messages
│       │   ├── useDashboardStats.ts       # dashboard KPI + trend data fetching
│       │   └── useNetworkGraph.ts         # criminal network graph data fetching
│       │
│       ├── services/                      # API call functions (not hooks)
│       │   ├── analytics.service.ts       # hotspots, trends, risk-board API calls
│       │   ├── chat.service.ts            # chat query & history API calls
│       │   ├── dashboard.service.ts       # dashboard stats & district crimes API calls
│       │   └── network.service.ts         # network graph API calls
│       │
│       ├── components/                    # screen-level & shared UI components
│       │   ├── LoginScreen.tsx            # login / auth landing page
│       │   ├── CommandDashboardScreen.tsx # main dashboard (KPIs, trends, map)
│       │   ├── ChatScreen.tsx             # intelligence chat (messages, table, SQL drawer)
│       │   ├── AnalyticsScreen.tsx        # analytics hub (hotspot, trend, risk-board tabs)
│       │   ├── NetworkExplorerScreen.tsx  # criminal network graph explorer
│       │   ├── Sidebar.tsx                # persistent left navigation bar
│       │   │
│       │   ├── analytics/
│       │   │   └── HotspotDetailsPanel.tsx  # slide-in panel for hotspot drill-down
│       │   │
│       │   ├── common/
│       │   │   ├── DateRangeSlider.tsx    # shared date-range slider control
│       │   │   └── DistrictFilter.tsx     # shared district dropdown filter
│       │   │
│       │   └── network/
│       │       └── NetworkGraph.tsx       # D3 force-directed criminal network graph
│       │
│       └── pages/                         # sub-page components (route fragments)
│           └── Analytics/
│               ├── index.tsx              # analytics page container / tab router
│               ├── HotspotMap.tsx         # Leaflet heatmap tab
│               ├── TrendAnalysis.tsx      # recharts trend analysis tab
│               └── OffenderRiskBoard.tsx  # offender risk scoring board tab
│
│
└── backend/                              # Python — FastAPI + Zoho Catalyst
    │
    ├── Dockerfile                         # for Catalyst AppSail deployment
    ├── app-config.json                    # AppSail start command config
    ├── requirements.txt                   # pip dependencies (legacy)
    ├── pyproject.toml                     # uv project config & dependencies
    ├── uv.lock                            # locked dependency graph (uv)
    ├── .env                               # local secrets (gitignored)
    ├── .env.example                       # env variable template
    ├── .catalystignore                    # files excluded from Catalyst deploy
    ├── .python-version                    # pinned Python version (for uv/pyenv)
    ├── docker-compose.yml                 # local dev stack
    ├── main.py                            # FastAPI app entry point, middleware, startup
    ├── BACKEND_DOCUMENTATION.md           # full backend API & architecture docs
    │
    ├── db/
    │   └── schema.md                      # ZCQL database schema reference (all tables & columns)
    │
    ├── core/                              # app-wide singletons & config
    │   ├── database.py                    # ZCQL client factory (get_zcql dependency)
    │   └── security.py                    # Catalyst auth token validation helpers
    │
    ├── schemas/                           # Pydantic request / response schemas
    │   ├── chat.py                        # ChatQueryRequest, ChatQueryResponse, SessionMessage, etc.
    │   ├── analytics.py                   # HotspotResponse, TrendResponse, RiskBoardResponse
    │   ├── dashboard.py                   # DashboardStats, DistrictCrimeResponse
    │   └── network.py                     # NetworkGraphResponse, NodeSchema, EdgeSchema
    │
    ├── routers/                           # FastAPI routers, one per domain
    │   ├── chat.py                        # POST /api/chat/query
    │   │                                  # GET  /api/chat/history
    │   │                                  # GET  /api/chat/messages?session_id=...
    │   │                                  # POST /api/chat/new-session
    │   │                                  # DELETE /api/chat/session/{id}
    │   ├── analytics.py                   # GET /api/analytics/hotspots
    │   │                                  # GET /api/analytics/trends
    │   │                                  # GET /api/analytics/risk-board
    │   ├── dashboard.py                   # GET /api/dashboard/stats
    │   │                                  # GET /api/dashboard/trends
    │   │                                  # GET /api/dashboard/district-crimes
    │   └── network.py                     # GET /api/network/graph
    │                                      # GET /api/network/node/{id}
    │
    ├── agents/                            # multi-agent intelligence pipeline
    │   ├── __init__.py
    │   │
    │   ├── router/                        # query classification & routing
    │   │   ├── agent.py                   # QueryRouterAgent — routes to sql/general/kannada
    │   │   └── prompts.py                 # router system + user prompt templates
    │   │
    │   ├── text_to_sql/                   # natural language → ZCQL
    │   │   ├── agent.py                   # TextToSQLAgent — LLM call + retry logic
    │   │   ├── schema_context.py          # full DB schema injected into LLM prompt
    │   │   ├── validator.py               # ZCQL query validation & auto-sanitisation
    │   │   └── prompts.py                 # system + user + retry prompt templates
    │   │
    │   ├── response_structurer/           # formats raw DB results into user response
    │   │   ├── agent.py                   # ResponseStructurer — LLM formats text + table
    │   │   └── prompts.py                 # structurer system + user prompt templates
    │   │
    │   ├── general_chat/                  # handles non-database conversational queries
    │   │   ├── agent.py                   # GeneralChatAgent — answers app/general questions
    │   │   └── prompts.py                 # general chat system + user prompt templates
    │   │
    │   ├── title_generator/               # generates session titles from first query
    │   │   ├── agent.py                   # TitleGeneratorAgent
    │   │   └── prompts.py                 # title generation prompt templates
    │   │
    │   └── network_agent/                 # criminal network graph analysis
    │       ├── graph_builder.py           # builds NetworkX graph from ZCQL data
    │       ├── community_detection.py     # Louvain community clustering
    │       └── centrality.py              # betweenness / degree centrality scores
    │
    ├── analytics/                         # standalone analytics computation modules
    │   ├── hotspot.py                     # DBSCAN geospatial crime hotspot clustering
    │   ├── trends.py                      # temporal aggregation + trend detection
    │   └── forecasting.py                 # Prophet time-series crime forecasting
    │
    ├── services/                          # external service wrappers
    │   ├── llm_client.py                  # Catalyst Quick ML LLM API wrapper
    │   ├── token_manager.py               # OAuth2 token refresh & authenticated requests
    │   ├── cache_service.py               # Catalyst Cache client (get/put/delete + keying)
    │   ├── translation.py                 # Kannada ↔ English translation via LLM
    │   └── example_usage.py              # cache service usage examples (dev reference)
    │
    ├── jobs/                              # scheduled background jobs
    │   └── forecast_cron.py               # APScheduler job: refreshes Prophet forecasts
    │
    ├── data/                              # static reference data
    │   └── district_socioeconomic.json    # socioeconomic indicators per Karnataka district
    │
    └── tests/                             # test suites
        ├── db/                            # ZCQL database connection & query tests
        └── llm_serving/                   # LLM API integration tests
```