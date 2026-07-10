# PRISM — Intelligent Chat Interface: Full Implementation Plan

> **Scope:** Build a complete end-to-end Intelligent Chat system where the user types natural
> language questions, the backend understands the query, generates a safe ZCQL query, executes
> it against the Zoho Catalyst DataStore, structures the results with an LLM, and sends a
> rich response (text + table + SQL transparency) to the frontend.

---

## 0. Current State Assessment

The chat UI (`ChatScreen.tsx`) already has a **complete, polished 3-column layout** — but it is 100% mock data driven with zero backend integration:

| Component | Current State | Target |
|---|---|---|
| **Chat Messages** | Loaded from `INITIAL_CHAT_MESSAGES` in `mockData.ts` | Real AI responses from `POST /api/chat/query` |
| **Send Message** | Looks up `CHAT_RESPONSES` dict by exact lowercase match, falls back to generic text | Sends query to backend multi-agent pipeline → gets real DB results |
| **Conversation History** | Static `CONVERSATION_HISTORY` array, clicking loads hardcoded messages | Persisted in `conversations` table, loaded from `GET /api/chat/history` |
| **Data Tables** | Hardcoded `tableData` arrays with fake FIR numbers | Real FIR records from ZCQL queries against `CaseMaster` |
| **SQL Transparency** | Hardcoded SQL strings in mock responses | Real generated ZCQL shown in collapsible drawer |
| **Data Sources** | Static placeholder text | Real table names and record counts from query execution |
| **Right Sidebar** | Hardcoded entities (Suresh Hegde, Yelahanka PS) and 3 static follow-ups | Dynamically extracted entities and AI-generated follow-ups |
| **Typing Indicator** | Shows for 1.5s `setTimeout` | Shows while actual backend request is in-flight |

**Backend state:** No `agents/`, `services/`, or `routers/chat.py` exist. The `conversations` table schema is defined in `db-table-schema.md` but may not be created in the Catalyst DataStore yet. The core database dependency (`get_zcql`) already works.

---

## 1. Architecture Overview

### 1.1 The Multi-Agent Pipeline

```
┌──────────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                     │
│  ChatInput → POST /api/chat/query { query, session_id }             │
│                                                                      │
│  ← Response: { text, table_data[], sql_query, sources, followups[] }│
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    BACKEND: Chat Router                               │
│  POST /api/chat/query                                                │
│  GET  /api/chat/history                                              │
│  POST /api/chat/new                                                  │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│              AGENT 1: Query Understanding + SQL Generation           │
│                                                                      │
│  Input:  Natural language query + DB schema context                  │
│  Steps:  1. Classify intent (data query / analytical / general)     │
│          2. Extract entities (district, crime type, status, dates)   │
│          3. Generate ZCQL query using schema context                 │
│          4. Validate query (SELECT-only, has LIMIT, safe joins)      │
│  Output: { zcql_query, intent, entities_extracted }                  │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│              QUERY EXECUTION (Direct ZCQL)                           │
│                                                                      │
│  Input:  Validated ZCQL query                                        │
│  Steps:  Execute via zcql.execute_query()                           │
│          Record: tables_accessed, record_count, execution_time       │
│  Output: { raw_rows[], metadata }                                    │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│              AGENT 2: Response Structurer                            │
│                                                                      │
│  Input:  Original query + raw DB rows + metadata                    │
│  Steps:  1. Summarize results in natural language                   │
│          2. Format table data for frontend display                   │
│          3. Extract mentioned entities (persons, locations)          │
│          4. Generate follow-up suggestions                          │
│  Output: { response_text, table_data, entities, follow_ups }        │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Decisions

| Concern | Tool | Rationale |
|---|---|---|
| **LLM Provider** | Groq API (Llama 3 / Mixtral) | Free tier, fast inference, already planned in `project-structure.md` |
| **SQL Generation** | LLM with schema context injection | The full DB schema + query patterns are injected as system prompt context |
| **SQL Validation** | Python regex + AST checks | Whitelist `SELECT` only, enforce `LIMIT`, block dangerous keywords |
| **DB Execution** | `zcql.execute_query()` | Already proven in `dashboard.py` — same Zoho Catalyst pattern |
| **Response Structuring** | LLM (second call) | Takes raw data + original question → produces natural language summary |
| **Frontend State** | React `useState` (local) | No global store needed — ChatScreen is self-contained |
| **API Communication** | Existing `apiClient` (axios) | Already configured with `baseURL: localhost:3001`, `withCredentials` |
| **Conversation Persistence** | `conversations` table in Catalyst DataStore | Schema already defined in `db-table-schema.md` |

---

## 2. Detailed Data Flow (Worked Example)

**User types:** `"Show me recent robbery FIRs in Bengaluru with active status"`

### Step A — Frontend sends request
```json
POST /api/chat/query
{
  "query": "Show me recent robbery FIRs in Bengaluru with active status",
  "session_id": "sess-abc-123"
}
```

### Step B — Agent 1: Query Understanding + SQL Generation

The LLM receives the full database schema as system context, plus the user query. It produces:

```json
{
  "intent": "data_query",
  "entities": {
    "crime_type": "Robbery",
    "district": "Bengaluru Urban",
    "status": "Under Investigation",
    "time_filter": "recent (30 days)"
  },
  "zcql_query": "SELECT CaseMaster.ROWID, CaseMaster.CrimeNo, CaseMaster.IncidentFromDate, CrimeSubHead.CrimeHeadName, CaseStatusMaster.CaseStatusName, District.DistrictName FROM CaseMaster INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID INNER JOIN District ON Unit.DistrictID = District.ROWID INNER JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID INNER JOIN CaseStatusMaster ON CaseMaster.CaseStatusID = CaseStatusMaster.ROWID WHERE CrimeSubHead.CrimeHeadName = 'Robbery' AND District.DistrictName = 'Bengaluru Urban' AND CaseStatusMaster.CaseStatusName = 'Under Investigation' ORDER BY CaseMaster.IncidentFromDate DESC LIMIT 20"
}
```

### Step C — SQL Validation

Python validator checks:
- ✅ Starts with `SELECT`
- ✅ No `INSERT/UPDATE/DELETE/DROP/ALTER`
- ✅ Has `LIMIT` clause
- ✅ Joins follow Rule 1 (start from CaseMaster) and Rule 2 (geography via Unit → District)

### Step D — Query Execution

```python
results = zcql.execute_query(validated_query)
# Returns list of row dicts from Catalyst DataStore
# Also records: tables_accessed = ["CaseMaster", "Unit", "District", "CrimeSubHead", "CaseStatusMaster"]
#               records_scanned = len(results)
```

### Step E — Agent 2: Response Structurer

LLM receives:
- Original query: "Show me recent robbery FIRs in Bengaluru..."
- Raw results: `[{CrimeNo: "104430006202600001", IncidentFromDate: "2026-06-28", ...}, ...]`
- Metadata: 4 rows returned, 5 tables joined

LLM produces:
```json
{
  "response_text": "I found 4 active robbery cases in Bengaluru Urban from the last 30 days. The incidents are concentrated around Yelahanka and Whitefield police station jurisdictions.",
  "table_data": [
    {"firNo": "BN-2026-00847", "crimeType": "Robbery", "district": "Bengaluru Urban", "status": "Under Investigation"},
    ...
  ],
  "entities": [
    {"name": "Bengaluru Urban", "type": "location", "detail": "District"},
    {"name": "Yelahanka PS", "type": "location", "detail": "Police Station"}
  ],
  "follow_ups": [
    "Show accused persons in these robbery cases",
    "Compare robbery trends with last quarter",
    "Find similar cases in surrounding districts"
  ]
}
```

### Step F — Frontend renders response

The response is rendered as:
- AI text bubble with the summary
- Data table with FIR rows
- Collapsible "View SQL Query" showing the generated ZCQL
- Collapsible "Data Sources (N records scanned)" showing table names
- Right sidebar updates with extracted entities and follow-up buttons

---

## 3. ZCQL Compatibility Notes

> **CRITICAL:** The database is Zoho Catalyst DataStore, NOT PostgreSQL. ZCQL has specific quirks:

| Feature | Standard SQL | ZCQL Equivalent |
|---|---|---|
| Primary key reference | `table.ColumnID` | `table.ROWID` (every table has an auto-generated ROWID) |
| Date functions | `NOW()`, `DATE_TRUNC()` | Not supported — compute dates in Python, pass as string literals |
| LIKE | `LIKE '%term%'` | Supported ✅ |
| JOIN | `INNER JOIN`, `LEFT JOIN` | Supported ✅ |
| GROUP BY | Standard | Supported ✅ |
| ORDER BY | Standard | Supported ✅ |
| LIMIT | `LIMIT N` | Supported ✅ |
| CASE WHEN | Standard | **NOT supported** — do this in Python post-processing |
| Subqueries | Standard | **NOT supported** — must split into multiple queries |
| COUNT/SUM/AVG | Standard | Supported ✅ |
| COALESCE | Standard | Supported ✅ |

The system prompt for Agent 1 must explicitly document these ZCQL limitations so the LLM does not generate unsupported SQL constructs.

---

## 4. Proposed Changes — File-by-File

### Backend Files

---

#### [NEW] `backend/services/groq_client.py`
Wrapper around the Groq API for LLM calls. Handles:
- API key from environment variable
- Model selection (llama-3.3-70b-versatile or similar)
- Chat completion calls with system + user messages
- JSON response parsing with error handling
- Retry logic for rate limits

---

#### [NEW] `backend/agents/__init__.py`
Empty init file for the agents package.

---

#### [NEW] `backend/agents/text_to_sql/schema_context.py`
Contains the full database schema as a formatted string constant that gets injected into the LLM system prompt. Includes:
- All table names with their columns and types
- All foreign key relationships
- The join path rules (Rule 1–12 from `db-table-schema.md`)
- ZCQL-specific syntax notes and limitations
- Example query patterns for common question types

---

#### [NEW] `backend/agents/text_to_sql/prompts.py`
System and user prompt templates for Agent 1:
- `SYSTEM_PROMPT`: "You are a SQL expert for the Karnataka Police FIR database. Given a natural language question, generate a ZCQL query..."
- `USER_PROMPT_TEMPLATE`: Formats the user's query with any conversation context

---

#### [NEW] `backend/agents/text_to_sql/validator.py`
SQL safety validation module:
- `validate_query(sql: str) → tuple[bool, str]`
- Checks: SELECT-only, has LIMIT, no dangerous keywords, valid table names
- Returns `(is_valid, error_message)`

---

#### [NEW] `backend/agents/text_to_sql/agent.py`
The Text-to-SQL Agent class:
- `__init__(groq_client, schema_context)` — initializes with LLM client and schema
- `generate_query(user_query: str, conversation_context: list) → dict` — calls LLM, parses response, validates SQL
- Returns: `{ zcql_query, intent, entities, error }`

---

#### [NEW] `backend/agents/response_structurer/prompts.py`
System and user prompt templates for Agent 2:
- `SYSTEM_PROMPT`: "You are an intelligence analyst assistant. Given raw database results and the original question, create a structured response..."
- `USER_PROMPT_TEMPLATE`: Formats the original query + raw data rows + metadata

---

#### [NEW] `backend/agents/response_structurer/agent.py`
The Response Structurer Agent class:
- `__init__(groq_client)` — initializes with LLM client
- `structure_response(query, raw_results, metadata) → dict` — calls LLM to produce summary, table data, entities, follow-ups
- Returns: `{ response_text, table_data, entities, follow_ups }`
- Handles edge cases: no results, single result, error results

---

#### [NEW] `backend/schemas/chat.py`
Pydantic request/response models:

```python
class ChatQueryRequest(BaseModel):
    query: str
    session_id: str

class ChatTableRow(BaseModel):
    firNo: str
    crimeType: str
    district: str
    status: str

class ChatEntity(BaseModel):
    name: str
    type: str        # "person" | "location" | "crime_type"
    detail: str

class ChatQueryResponse(BaseModel):
    message_id: str
    response_text: str
    table_data: list[ChatTableRow]
    sql_query: str
    scanned_records: int
    sources: list[str]
    entities: list[ChatEntity]
    follow_ups: list[str]
    timestamp: str

class ConversationItem(BaseModel):
    session_id: str
    title: str
    created_at: str
    category: str    # "Today" | "Previous 7 Days" | "Older"

class ChatHistoryResponse(BaseModel):
    conversations: list[ConversationItem]
```

---

#### [NEW] `backend/routers/chat.py`
FastAPI router with 3 endpoints:

```
POST /api/chat/query     — Main endpoint: receives query, runs pipeline, returns response
GET  /api/chat/history   — Returns conversation history for current user
POST /api/chat/new       — Creates a new conversation session, returns session_id
```

The `/query` endpoint orchestrates:
1. Call Agent 1 (Text-to-SQL) → get ZCQL
2. Validate the ZCQL
3. Execute via `zcql.execute_query()`
4. Call Agent 2 (Response Structurer) → get formatted response
5. Save to `conversations` table
6. Return `ChatQueryResponse`

---

#### [MODIFY] `backend/main.py`
- Import and register the new chat router
- Add Groq API key to environment (or load from `.env`)

---

### Frontend Files

---

#### [NEW] `frontend/src/services/chat.service.ts`
API service following the `dashboard.service.ts` pattern:

```typescript
export const chatService = {
  sendQuery: async (query: string, sessionId: string): Promise<ChatQueryResponse> => { ... },
  getHistory: async (): Promise<ConversationItem[]> => { ... },
  newConversation: async (): Promise<{ session_id: string }> => { ... },
};
```

---

#### [NEW] `frontend/src/hooks/useChat.ts`
Custom React hook managing chat state:
- `messages` state with add/reset
- `sendMessage(text)` — calls `chatService.sendQuery()`, manages typing indicator
- `loadHistory()` — fetches conversation list
- `startNewConversation()` — calls `chatService.newConversation()`
- Exposes: `{ messages, isTyping, history, sendMessage, loadHistory, startNewConversation, activeSessionId }`

---

#### [NEW] `frontend/src/types/chat.ts` (or extend existing `types.ts`)
Add new interfaces to match backend response:

```typescript
export interface ChatEntity {
  name: string;
  type: 'person' | 'location' | 'crime_type';
  detail: string;
}

export interface ChatQueryResponse {
  message_id: string;
  response_text: string;
  table_data: ChatTableRow[];
  sql_query: string;
  scanned_records: number;
  sources: string[];
  entities: ChatEntity[];
  follow_ups: string[];
  timestamp: string;
}

export interface ConversationItem {
  session_id: string;
  title: string;
  created_at: string;
  category: 'Today' | 'Previous 7 Days' | 'Older';
}
```

---

#### [MODIFY] `frontend/src/components/ChatScreen.tsx`
Replace all mock data usage with the `useChat` hook:
- Replace `INITIAL_CHAT_MESSAGES` → `messages` from hook
- Replace `handleSendMessage` setTimeout logic → `sendMessage()` from hook
- Replace `CONVERSATION_HISTORY` → `history` from hook
- Replace hardcoded entities/follow-ups → dynamic from latest AI response
- `isTyping` now tracks real API request in-flight state

---

## 5. Open Questions for Review

> [!IMPORTANT]
> **LLM Provider:** The plan uses Groq (free tier). Do you have a Groq API key, or would you prefer a different LLM provider (e.g., Google Gemini API, OpenAI, local Ollama)?

> [!IMPORTANT]
> **Conversation Persistence:** The `conversations` table is defined in the DB schema docs. Has it been created in the Catalyst DataStore console? If not, should we skip persistence for now and keep conversations in-memory (frontend-only)?

> [!WARNING]
> **ZCQL Limitations:** ZCQL does not support `CASE WHEN`, subqueries, or date functions like `NOW()`. The LLM prompt must be very explicit about these constraints. Complex queries may need to be split into multiple ZCQL calls with Python post-processing. This adds latency but is unavoidable with Catalyst DataStore.

---

## 6. Error Handling Strategy

| Failure Point | Handling |
|---|---|
| LLM API down / rate limited | Return a graceful error message: "Intelligence system temporarily unavailable. Please try again." |
| LLM generates invalid SQL | Validator catches it → retry once with error feedback to LLM → if still fails, return error to user |
| ZCQL execution fails | Catch exception → return: "Unable to retrieve data for this query. Try rephrasing." |
| No results found | Agent 2 generates: "No matching records found for your query." with suggestions to broaden search |
| LLM returns malformed JSON | Parse with fallback → extract text response even if structured fields fail |
| Conversation table doesn't exist | Gracefully skip persistence, log warning, still return response |

---

## 7. Verification Plan

### Automated Tests
- `npx tsc --noEmit` — TypeScript type checking across all new frontend files
- `npm run build` — Ensure frontend builds successfully
- Python import test: `python -c "from agents.text_to_sql.agent import TextToSQLAgent"` — Verify backend modules import correctly

### Manual End-to-End Tests
1. Send "Show me robbery cases in Bengaluru" → Verify real FIR data in response table
2. Send "How many FIRs were registered last month?" → Verify count aggregation works
3. Send "Who are the accused in case CrimeNo X?" → Verify person table joins work
4. Click "New Conversation" → Verify session resets
5. Expand SQL drawer → Verify real generated ZCQL is shown
6. Expand Data Sources → Verify table names and record count are real
7. Click a suggested follow-up → Verify it sends as a new query
8. Reload page → Verify conversation history loads from API (if persistence enabled)
