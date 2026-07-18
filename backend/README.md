# PRISM Backend

The backend of PRISM is a FastAPI service designed to run on Zoho Catalyst AppSail. It handles incoming requests from the React frontend client, routes AI database queries using a pipeline of LLM-powered agents, runs analytical calculations (geospatial hotspotting and forecasting), and hosts internal cron jobs to process alerts.

---

## 🛠️ Key Components & Technologies

*   **FastAPI & Uvicorn**: Async, high-performance web framework for APIs.
*   **Zoho Catalyst SDK (`zcatalyst_sdk`)**: Interface for reading/writing tables, purging cache, and sending messages.
*   **Catalyst QuickML**: Serves as the primary LLM inference engine (`crm-di-glm47b_30b_it`).
*   **APScheduler**: Embedded asynchronous cron runner scheduling real-time task synchronisations.
*   **Data Analysis Tools**: `scikit-learn` (DBSCAN for location clustering), `prophet` (time-series forecasting).

---

## 🤖 Multi-Agent AI System

The conversational chat system is implemented as a pipeline of cooperating agents located in `agents/`:

```
backend/agents/
├── router/             # Classifies input intent (general chat, database query, or translation)
├── text_to_sql/        # Translates English queries to Zoho Catalyst ZCQL queries
├── response_structurer/# Aggregates SQL outputs and structures the natural response + tables
├── general_chat/       # Converses on application support, instructions, and non-DB context
└── title_generator/    # Spawns background session titles for new chat queries
```

### Text-To-SQL Pipeline Flow
```
User Query ──> [QueryRouter] ──> is_kannada? ──> [TranslationService] ──> English Query
                                                                                │
                                                                                ▼
[ResponseStructurer] <── [Datastore Execution] <── [Validator] <── [TextToSQLAgent]
         │
         ▼
Cleaned Response + Table JSON
```

*   **ZCQL Validator (`validator.py`)**: Sanitizes and validates ZCQL queries prior to database execution. It automatically appends default `LIMIT` constraints (capped at ZCQL's maximum limit of 300) and halts non-SELECT statements.
*   **Count Handling Restriction**: Under the `CRITICAL COUNT / QUANTITY RULE` in `text_to_sql/prompts.py`, questions asking for the count of a specific entity (e.g. *"how many theft cases in Mysuru"*) are directed to perform a row-level SELECT. This allows the frontend to render the returned records in a table while the `ResponseStructurer` describes the calculated totals in normal text.

---

## 🗄️ Database Schema & APIs

All tables are defined in the ZCQL schema document located at [schema.md](file:///d:/STUDY/PROJECTS/prism/backend/db/schema.md). The backend exposes the following primary endpoints:

*   **`/api/chat`**
    *   `POST /query`: Submits a prompt, routes it to the correct agent, executes the generated SQL, and structures the response.
    *   `GET /history`: Retrieves all conversation session titles for the sidebar.
    *   `GET /messages`: Fetches previous chat messages to load a session in the client.
    *   `POST /new-session`: Initiates a new conversation ID.
    *   `DELETE /session/{id}`: Deletes a conversation session and all its messages.
*   **`/api/dashboard`**
    *   `GET /stats`: High-level aggregated KPIs.
    *   `GET /trends`: Fetches overall crime trend lines.
    *   `GET /district-crimes`: Retrieves the district crime counts over a specified timeframe.
*   **`/api/analytics`**
    *   `GET /hotspots`: Coordinates of crime clusters grouped by density (DBSCAN).
    *   `GET /trends`: Granular crime trends and temporal forecasts (Meta Prophet).
    *   `GET /risk-board`: Recidivism rankings based on crime frequency, status, and severity.
*   **`/api/network`**
    *   `GET /graph`: NetworkX adjacency matrix of criminals, cases, and accomplices.

---

## ⚙️ Local Installation & Development

### 1. Requirements
Ensure you have Python 3.10 installed on your system.

### 2. Dependency Setup
Navigate to the `backend` folder and run:
```bash
# Initialize venv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies using project spec
pip install --upgrade pip
pip install -r pyproject.toml
```
*(Alternatively, you can use `uv` for a fast installation: `uv pip install -r pyproject.toml`)*

### 3. Environment Variables (`.env`)
Create a `.env` file in the `backend` directory. Local development requires Zoho OAuth credentials to query the Catalyst QuickML LLM APIs:

```properties
# Zoho Client credentials registered at accounts.zoho.in
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token

# Target organization ID containing the QuickML project
CATALYST_ORG_ID=60074849663

# Fast API environment parameters
ENABLE_FASTAPI_CORS=true
```

To acquire a refresh token:
1. Register a client in the [Zoho Developer Console](https://api-console.zoho.in/) as a **Web Based** application.
2. Set the redirect URL to a dummy page or `http://localhost`.
3. Use the self-client page or authorize endpoint with scopes: `QuickML.chat.CREATE`, `QuickML.chat.READ`, or equivalent project parameters to get a code, then exchange the code for a refresh token.

### 4. Running the Dev Server
Start the app:
```bash
uvicorn main:app --host 127.0.0.1 --port 3001 --reload
```

---

## 🧪 Running Tests
Integration tests for database drivers and LLM serving are located in `tests/`:

```bash
# Test ZCQL datastore operations
python -m pytest tests/db/

# Test LLM serving connection
python -m pytest tests/llm_serving/
```
