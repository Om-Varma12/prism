# PRISM: Police Record Information & Security Management

> AI-powered crime intelligence & analytics platform for the Karnataka State Police Department

*"A crime is not an isolated event. It's a node in a network of people, places, behaviors, and time."*

PRISM turns static FIR records into conversational, network-aware, predictive intelligence — enabling officers and analysts to ask questions in plain language (English or Kannada), see criminal associations as a live graph, and act on forecasted hotspots before incidents escalate.

---

## 🏆 Hackathon Context

Built for **Zoho Catalyst Hackathon — Problem Statement 1 (PS1)**: Design an AI-powered analytics platform for the Karnataka State Police FIR database to enable data-driven law enforcement decisions.

The KSP-provided ER schema is treated as the source of truth. All ZCQL queries follow the join rules and constraints documented in [`backend/db/schema.md`](backend/db/schema.md).

---

## ✨ Feature Pillars

| # | Pillar |
|---|---|
| 1 | **Conversational Crime Intelligence** — NL chat (English + Kannada + Manglish voice), Text-to-SQL agent, dynamic table rendering, PDF export |
| 2 | **Criminal Network Analysis** — D3.js force graph, co-accused linking, community detection (Louvain), centrality ranking |
| 3 | **Pattern & Trend Analytics** — DBSCAN geospatial hotspots, seasonal trend lines, Prophet time-series forecasting |
| 4 | **Offender Profiling & Risk Scoring** — Multi-factor recidivism risk score, nightly precompute, absconding flags |
| 5 | **Explainable, Role-Gated Intelligence** — SQL transparency drawer, role-aware query restrictions, audit logging |

---

## 🛠️ Architecture & Tech Stack

![PRISM Architecture Diagram](resources/arch-dia.png)

### Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19 + TypeScript, Create React App, Tailwind CSS, D3.js, Recharts, Leaflet |
| **Backend** | FastAPI (Python 3.13), multi-agent pipeline (Router → Text-to-SQL → Structurer) |
| **LLM** | Zoho Catalyst QuickML (hosted LLM serving — `crm-di-glm47b_30b_it`) |
| **Database** | Zoho Catalyst Data Store (ZCQL), schema per KSP-provided ER diagram |
| **Analytics** | NetworkX + Louvain (graph/community), scikit-learn DBSCAN (hotspots), Prophet (forecasting) |
| **Auth** | Clerk (custom branded login screen, session management) |
| **Infra** | Zoho Catalyst — AppSail, API Gateway, Cron, Cache, Stratus, Domain Mappings |

**AppSail is the brain. Data Store is the memory. Cron + Signals is the nervous system. Cache + Gateway keep it fast and secure.**

```
React SPA → Catalyst API Gateway → AppSail (FastAPI multi-agent backend) → Catalyst Data Store
```

### Infrastructure Layer (Zoho Catalyst)
*   **AppSail**: OCI/Docker container hosting the FastAPI server.
*   **API Gateway**: Secure traffic routing, CORS enforcement, and request throttling.
*   **Data Store**: Cloud relational database powering transactional crime tables.
*   **Cache**: Redis-backed segment for fast storage of session histories, KPI stats, and query results.
*   **Cron**: Runs daily jobs to recompute forecasts, risk metrics, and detect spikes.

---

## 📁 Repository Structure

```
prism/
│
├── frontend/                   # React + TypeScript SPA (Create React App)
│   ├── public/                 # Static assets & index.html
│   └── src/
│       ├── components/         # Page-level screen components & shared UI
│       ├── constants/          # API URLs, config constants
│       ├── data/               # Static reference data (districts, crime types, etc.)
│       ├── hooks/              # Custom React hooks (useChat, useNetwork, etc.)
│       ├── lib/                # Utility / helper functions
│       ├── pages/              # Top-level page wrappers
│       ├── services/           # Axios API service modules
│       └── types/              # Shared TypeScript type definitions
│
├── backend/                    # FastAPI Python backend (Catalyst AppSail)
│   ├── agents/                 # Multi-agent AI pipeline
│   │   ├── general_chat/       # General conversational agent
│   │   ├── network_agent/      # Criminal network graph builder
│   │   ├── response_structurer/# Formats SQL results into natural language + tables
│   │   ├── router/             # Intent classifier (DB query / general / Kannada)
│   │   ├── text_to_sql/        # Translates English queries → ZCQL
│   │   └── title_generator/    # Background session title generation
│   ├── analytics/              # DBSCAN hotspot, Prophet forecasting, risk scoring
│   ├── core/                   # database.py — SDK dependency helpers (get_zcql, get_datastore)
│   ├── data/                   # Static reference data used by backend
│   ├── db/                     # schema.md — full table reference & ZCQL constraints
│   ├── jobs/                   # APScheduler cron job definitions
│   ├── routers/                # FastAPI route handlers
│   │   ├── analytics.py        # Hotspots, trends, risk board, forecasting
│   │   ├── chat.py             # Conversational AI pipeline endpoint
│   │   ├── dashboard.py        # KPI stats, alerts, district crime counts
│   │   └── network.py          # Criminal network graph API
│   ├── schemas/                # Pydantic request/response models
│   ├── services/               # Shared service utilities (LLM calls, translation)
│   └── tests/
│       ├── db/                 # Data seeding & truncation endpoints
│       └── llm_serving/        # LLM connectivity tests
│
├── catalyst.json               # Catalyst project configuration (AppSail + client)
├── services-used.md            # All Zoho Catalyst services provisioned
└── project-structure.md        # Extended project directory reference
```

> 📖 **Database schema pointer**: Before writing any backend query, read [`backend/db/schema.md`](backend/db/schema.md). It contains the full table reference, join rules, and ZCQL constraints derived from the KSP-provided ER diagram — the single most important reference file for backend work.

---

## ⚙️ Quick Start & Installation

### Prerequisites
*   [Node.js](https://nodejs.org/) v18+ & npm v9+
*   [Python](https://www.python.org/) v3.10+
*   **Zoho Catalyst CLI** — Required to run the unified dev server. Install it by following the [Installing Catalyst CLI Guide](https://docs.catalyst.zoho.com/en/getting-started/installing-catalyst-cli/).
*   A **Zoho Catalyst project** with Data Store tables provisioned (see schema.md)
*   A **Clerk application** (free tier) for authentication — get your publishable key from [dashboard.clerk.com](https://dashboard.clerk.com)

---

### Step-by-Step Setup

#### 1. Configure the Frontend Client
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Copy the environment variables template and configure your parameters:
   ```bash
   cp .env.example .env
   ```
   > 🔑 **Required**: Open `frontend/.env` and insert your Clerk publishable key (`REACT_APP_CLERK_PUBLISHABLE_KEY`) from the [Clerk Dashboard](https://dashboard.clerk.com).
3. Install frontend dependencies:
   ```bash
   npm install
   ```

#### 2. Configure the Backend Server
1. Navigate to the `backend` directory:
   ```bash
   cd ../backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment variables template and configure your parameters:
   ```bash
   cp .env.example .env
   ```
   > 🔑 **Required**: Open `backend/.env` and populate your Zoho Catalyst Client ID, Client Secret, and Refresh Token. Refer to [backend/README.md](backend/README.md#3-environment-variables-env) for details on how to generate these.

---

### 🏃 Running the Project Locally

Once both folders have their dependencies installed and `.env` files properly configured:

1. Return to the **root level** of the project:
   ```bash
   cd ..
   ```
2. Start the unified development server:
   ```bash
   catalyst serve
   ```
   This command starts the local Catalyst environment, automatically hosting:
   *   The **FastAPI backend** (AppSail)
   *   The **React frontend client** (served via the React plugin)

   Both services launch simultaneously and are automatically routed and connected together.
3. Access the web app in your browser (typically at `http://localhost:3000` or the port output by the CLI).

> 💡 *For more details on specific components, refer to [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md).*

---

### 🌱 Seeding Demo Data

After launching the server, use these endpoints to populate the database with sample data:

| Endpoint | Description |
|---|---|
| `GET /db/tests/insert-derived-data` | Seeds `dashboard_stats`, `crime_alerts`, `risk_scores`, `conversations`, `audit_logs` |
| `GET /db/tests/insert-new-data` | Inserts 20 rows per derived table with dates within the last 7 days |
| `GET /db/tests/insert-recent-cases` | Seeds recent `CaseMaster` records with fresh timestamps |
| `GET /db/tests/truncate-derived` | Clears all derived/analytics tables (use before re-seeding) |

---

## 📦 Deployment

Deploy to your active Zoho Catalyst environment:

1. Authenticate with Catalyst:
   ```bash
   catalyst login
   ```
2. Initialize or verify your project directory:
   ```bash
   catalyst project:use
   ```
3. Deploy both client and backend:
   ```bash
   catalyst deploy
   ```

All Catalyst services provisioned for this project are documented in [`services-used.md`](services-used.md).

---

## 🧠 Key Design Decisions

- **Entity resolution is application-layer**: The KSP schema has no cross-case offender identity field (`PersonID` is per-FIR). Accused name matching across cases uses `rapidfuzz` string similarity at query time — not a normalized table.
- **Risk scores are nightly precomputed**: Scores are written to the `risk_scores` table once per cron cycle and served statically. This avoids expensive per-request joins across `CaseMaster`, `Accused`, and `ArrestSurrender` for every page load.
- **QuickML is used only for LLM serving, not RAG**: The system uses a custom multi-agent pipeline (Router → Translation → Text-to-SQL → Validator → Structurer) rather than an off-the-shelf RAG framework. This gives full control over query generation, validation, and structured response formatting.

---

## ⚠️ Known Limitations

- **No cross-FIR offender identity**: The schema does not have a global offender ID. Network links are inferred from shared accused names and co-case appearances — fuzzy, not authoritative.
- **Kannada via translation, not native NLU**: The system translates Kannada/Manglish queries to English before processing. Native Kannada NLU or a Kannada-trained model is not integrated.
- **Financial crime linking not supported**: The schema lacks financial transaction tables. PMLA and money laundering cases appear in `CaseMaster` but cannot be linked to transaction data.
- **Forecasting requires sufficient historical data**: Meta's Prophet requires a meaningful time-series baseline. Thin data in a district may produce unreliable trend projections.

---

## 👥 Team

Built by **Elden Lords** for the Zoho Catalyst Hackathon.

---

## 📄 License & Acknowledgments

- **Database Schema**: Derived from the Karnataka State Police FIR schema provided as part of PS1.
- **LLM Serving**: Powered by Zoho Catalyst QuickML.
- Built on **Zoho Catalyst** — AppSail, Data Store, API Gateway, Cache, Cron, and Stratus.
