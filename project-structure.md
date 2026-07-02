```
prism/
│
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml                 # local dev: backend + postgres together
│
├── frontend/                          # Vite + React + TypeScript
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── package.json
│   ├── .env.local
│   │
│   └── src/
│       ├── main.tsx                   # app entry point
│       ├── App.tsx                    # router setup
│       ├── vite-env.d.ts
│       │
│       ├── assets/                    # static assets
│       │   ├── karnataka-map.svg      # the district map SVG
│       │   └── logo.svg
│       │
│       ├── styles/
│       │   ├── globals.css            # css variables, base reset
│       │   └── tokens.css             # design tokens (colors, spacing, type)
│       │
│       ├── types/                     # all TypeScript interfaces/types
│       │   ├── auth.ts
│       │   ├── case.ts                # CaseMaster, Accused, Victim etc
│       │   ├── analytics.ts           # hotspot, trend, forecast types
│       │   ├── network.ts             # graph nodes, edges, clusters
│       │   ├── chat.ts                # message, conversation, query result
│       │   └── index.ts               # barrel export
│       │
│       ├── constants/
│       │   ├── roles.ts               # role definitions and permissions
│       │   ├── routes.ts              # all route path constants
│       │   └── api.ts                 # API base URL, endpoint paths
│       │
│       ├── lib/                       # pure utility functions, no React
│       │   ├── api-client.ts          # axios instance + interceptors
│       │   ├── auth.ts                # token read/write/decode helpers
│       │   ├── formatters.ts          # date, number, case-number formatters
│       │   ├── risk-color.ts          # risk score → color mapping
│       │   └── voice.ts              # Web Speech API wrapper
│       │
│       ├── hooks/                     # custom React hooks
│       │   ├── useAuth.ts
│       │   ├── useChat.ts
│       │   ├── useDashboardStats.ts
│       │   ├── useNetworkGraph.ts
│       │   ├── useHotspots.ts
│       │   ├── useOffenderProfile.ts
│       │   └── useVoiceInput.ts
│       │
│       ├── store/                     # Zustand global state
│       │   ├── auth.store.ts          # user, role, token
│       │   ├── chat.store.ts          # active conversation, messages
│       │   ├── network.store.ts       # selected node, active filters
│       │   └── alerts.store.ts        # active alert feed
│       │
│       ├── services/                  # API call functions (not hooks)
│       │   ├── auth.service.ts
│       │   ├── chat.service.ts
│       │   ├── cases.service.ts
│       │   ├── network.service.ts
│       │   ├── analytics.service.ts
│       │   └── offenders.service.ts
│       │
│       ├── components/                # shared, reusable UI components
│       │   ├── ui/                    # atomic primitives
│       │   │   ├── Button.tsx
│       │   │   ├── Input.tsx
│       │   │   ├── Badge.tsx          # status/severity tags
│       │   │   ├── Card.tsx
│       │   │   ├── Spinner.tsx
│       │   │   ├── Tooltip.tsx
│       │   │   ├── Divider.tsx
│       │   │   ├── Modal.tsx
│       │   │   └── index.ts
│       │   │
│       │   ├── layout/
│       │   │   ├── Sidebar.tsx        # persistent left nav
│       │   │   ├── SidebarItem.tsx
│       │   │   ├── PageShell.tsx      # wraps every page: sidebar + content area
│       │   │   └── StatusBar.tsx      # bottom bar: role, district, time
│       │   │
│       │   ├── data-display/
│       │   │   ├── KpiCard.tsx        # the big number + label cards
│       │   │   ├── AlertItem.tsx      # single alert in the feed
│       │   │   ├── AlertFeed.tsx
│       │   │   ├── Sparkline.tsx      # single recharts sparkline
│       │   │   ├── DataTable.tsx      # reusable sortable table
│       │   │   ├── RiskBar.tsx        # horizontal risk score bar
│       │   │   ├── Timeline.tsx       # case investigation timeline
│       │   │   └── EntityCard.tsx     # accused/victim/location mini card
│       │   │
│       │   ├── maps/
│       │   │   ├── KarnatakaMap.tsx   # SVG district map (dashboard)
│       │   │   ├── HotspotMap.tsx     # Mapbox heatmap (analytics)
│       │   │   └── MapLegend.tsx
│       │   │
│       │   ├── charts/
│       │   │   ├── CrimeTrendChart.tsx
│       │   │   ├── DemographicChart.tsx
│       │   │   ├── ForecastChart.tsx
│       │   │   └── HourlyDistribution.tsx
│       │   │
│       │   ├── network/
│       │   │   ├── NetworkGraph.tsx   # D3 force-directed graph
│       │   │   ├── NodeDetailPanel.tsx
│       │   │   ├── FilterPanel.tsx
│       │   │   └── ClusterLabel.tsx
│       │   │
│       │   └── chat/
│       │       ├── ChatMessage.tsx    # single message bubble/block
│       │       ├── ChatThread.tsx     # full message list
│       │       ├── ChatInput.tsx      # input bar + mic button
│       │       ├── SqlDrawer.tsx      # collapsible SQL transparency panel
│       │       ├── SourcesDrawer.tsx  # collapsible data sources panel
│       │       ├── ConversationList.tsx
│       │       └── SuggestedQueries.tsx
│       │
│       └── pages/                     # one folder per route
│           ├── Login/
│           │   ├── index.tsx
│           │   └── LoginMap.tsx       # the atmospheric left-side map
│           │
│           ├── Dashboard/
│           │   └── index.tsx
│           │
│           ├── Chat/
│           │   └── index.tsx
│           │
│           ├── NetworkExplorer/
│           │   └── index.tsx
│           │
│           ├── Analytics/
│           │   ├── index.tsx
│           │   ├── HotspotTab.tsx
│           │   ├── TrendTab.tsx
│           │   └── RiskBoardTab.tsx
│           │
│           └── NotFound/
│               └── index.tsx
│
│
└── backend/                           # Python — FastAPI
    │
    ├── Dockerfile                     # for Catalyst AppSail deployment
    ├── requirements.txt
    ├── .env.example
    ├── main.py                        # FastAPI app entry point
    │
    ├── core/                          # app-wide configuration
    │   ├── config.py                  # pydantic settings, env vars
    │   ├── database.py                # DB connection, session factory
    │   ├── security.py                # JWT decode, role extraction
    │   ├── logger.py                  # structured logging setup
    │   └── exceptions.py             # custom HTTP exception classes
    │
    ├── middleware/
    │   ├── audit_log.py               # logs every request to audit_logs table
    │   ├── role_guard.py              # role-based access enforcement
    │   └── cors.py
    │
    ├── models/                        # SQLAlchemy ORM models (mirror given schema)
    │   ├── case.py                    # CaseMaster
    │   ├── accused.py                 # Accused
    │   ├── victim.py                  # Victim
    │   ├── complainant.py             # ComplainantDetails
    │   ├── arrest.py                  # ArrestSurrender
    │   ├── chargesheet.py             # ChargesheetDetails
    │   ├── act.py                     # Act, Section, ActSectionAssociation
    │   ├── lookup.py                  # CrimeHead, CrimeSubHead, GravityOffence etc
    │   ├── geography.py               # State, District, Unit, UnitType
    │   ├── employee.py                # Employee, Rank, Designation
    │   ├── derived.py                 # our added tables: risk_scores,
    │   │                              #   crime_alerts, dashboard_stats,
    │   │                              #   audit_logs, conversations
    │   └── __init__.py
    │
    ├── schemas/                       # Pydantic request/response schemas
    │   ├── chat.py                    # ChatRequest, ChatResponse, MessageSchema
    │   ├── network.py                 # GraphResponse, NodeSchema, EdgeSchema
    │   ├── analytics.py               # HotspotResponse, TrendResponse
    │   ├── offender.py                # OffenderProfile, RiskScore
    │   ├── dashboard.py               # DashboardStats, AlertSchema
    │   └── auth.py                    # TokenPayload, UserContext
    │
    ├── routers/                       # FastAPI routers, one per domain
    │   ├── auth.py                    # POST /auth/verify (Catalyst Auth callback)
    │   ├── chat.py                    # POST /chat/query, GET /chat/history
    │   ├── network.py                 # GET /network/graph, GET /network/profile/{id}
    │   ├── analytics.py               # GET /analytics/hotspots, /trends, /risk-board
    │   ├── dashboard.py               # GET /dashboard/stats, /alerts
    │   ├── cases.py                   # GET /cases/{id}, /cases/similar
    │   └── offenders.py               # GET /offenders/{id}, /offenders/search
    │
    ├── agents/                        # the multi-agent intelligence system
    │   ├── orchestrator.py            # routes queries to correct agent
    │   ├── base_agent.py              # abstract base class for all agents
    │   │
    │   ├── text_to_sql/
    │   │   ├── agent.py               # Text-to-SQL agent (Groq LLM)
    │   │   ├── schema_context.py      # schema string injected into prompt
    │   │   ├── validator.py           # validates generated SQL before execution
    │   │   └── prompts.py             # system + user prompt templates
    │   │
    │   ├── rag/
    │   │   ├── agent.py               # RAG agent for investigative queries
    │   │   ├── embedder.py            # sentence-transformers embedding logic
    │   │   ├── vector_store.py        # ChromaDB client wrapper
    │   │   ├── retriever.py           # query → retrieve → rerank
    │   │   └── prompts.py
    │   │
    │   ├── network_agent/
    │   │   ├── agent.py               # graph query + analysis agent
    │   │   ├── graph_builder.py       # NetworkX graph construction from DB
    │   │   ├── community_detection.py # Louvain clustering
    │   │   ├── centrality.py          # betweenness, degree centrality
    │   │   └── entity_resolver.py     # fuzzy name matching (rapidfuzz)
    │   │
    │   └── summarizer/
    │       ├── agent.py               # case summary + lead recommendation agent
    │       └── prompts.py
    │
    ├── analytics/                     # standalone analytics modules (not agents)
    │   ├── hotspot.py                 # DBSCAN geospatial clustering
    │   ├── trends.py                  # temporal aggregation queries
    │   ├── forecasting.py             # Prophet time-series forecasting
    │   ├── risk_scoring.py            # weighted offender risk formula
    │   ├── mo_extractor.py            # LLM-based MO extraction from BriefFacts
    │   ├── sociological.py            # demographic correlation queries
    │   └── alert_engine.py            # spike detection + alert generation
    │
    ├── services/                      # infrastructure/external service wrappers
    │   ├── groq_client.py             # Groq API wrapper
    │   ├── cache.py                   # Catalyst Cache client wrapper
    │   ├── storage.py                 # Catalyst Stratus (object storage) wrapper
    │   └── translation.py             # IndicTrans2 wrapper (Kannada ↔ English)
    │
    ├── jobs/                          # scheduled jobs (run by Catalyst Cron)
    │   ├── nightly_aggregation.py     # precompute dashboard stats
    │   ├── risk_score_refresh.py      # recompute all risk scores
    │   ├── forecast_refresh.py        # refresh Prophet forecasts
    │   └── alert_detection.py         # run alert_engine, fire Catalyst Signals
    │
    └── data/                          # synthetic data generation (not deployed)
        ├── generator/
        │   ├── main.py                # entry point — generates everything
        │   ├── config.py              # scale config (n_firs, n_districts etc)
        │   ├── geography.py           # Karnataka districts, police stations
        │   ├── criminal_ecosystem.py  # gang definitions, MO patterns
        │   ├── fir_generator.py       # generates CaseMaster rows
        │   ├── accused_generator.py   # generates Accused rows with planted clusters
        │   ├── victim_generator.py
        │   ├── briefacts_generator.py # LLM-generated realistic FIR text
        │   └── seed_lookups.py        # populates all lookup tables
        │
        └── output/                    # generated SQL/CSV files (gitignored)
            ├── lookups.sql
            ├── cases.sql
            ├── accused.sql
            └── ...
```