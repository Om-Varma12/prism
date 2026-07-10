# PRISM — Chat Interface Implementation Steps

This document outlines the step-by-step implementation plan for the PRISM Intelligent Chat interface, including the technical tasks for each step and corresponding Git commit messages.

**Total Steps: 12**
**Estimated Effort: Backend-heavy (Steps 1–8), Frontend integration (Steps 9–12)**

---

### Step 1: Catalyst Quick ML LLM Service Client

**Implementation:**
- Create `backend/services/__init__.py`
- Create `backend/services/llm_client.py`
- Implement a `CatalystLLMClient` class wrapping the Catalyst Quick ML API:
  - `__init__()` — initializes Catalyst Quick ML endpoint
  - `chat_completion(system_prompt, user_prompt, json_mode=False) → str` — sends a chat completion request to Catalyst API, returns the response text
  - `chat_completion_json(system_prompt, user_prompt) → dict` — same but forces JSON output and parses the response
  - Includes retry logic (1 retry on rate limit) and timeout handling
- Install `requests` Python package (add to `requirements.txt`)

**Files Created:**
- `backend/services/__init__.py`
- `backend/services/llm_client.py`

**Commit Message:**
`feat(backend): implement Catalyst Quick ML LLM client service for agent pipeline`

---

### Step 2: Database Schema Context for SQL Agent

**Implementation:**
- Create `backend/agents/__init__.py`
- Create `backend/agents/text_to_sql/__init__.py`
- Create `backend/agents/text_to_sql/schema_context.py`
- Build the `SCHEMA_CONTEXT` string constant that contains:
  - All table definitions (columns, types, PKs, FKs) — condensed from `db-table-schema.md`
  - Join path rules (always start from CaseMaster, geography via Unit → District)
  - ZCQL-specific limitations (no CASE WHEN, no subqueries, no NOW(), use ROWID instead of PK names)
  - The 10 example query patterns from the schema doc
  - Column name mapping for common user terms (e.g., "district" → `District.DistrictName`, "crime type" → `CrimeSubHead.CrimeHeadName`, "status" → `CaseStatusMaster.CaseStatusName`)

**Files Created:**
- `backend/agents/__init__.py`
- `backend/agents/text_to_sql/__init__.py`
- `backend/agents/text_to_sql/schema_context.py`

**Commit Message:**
`feat(backend): create database schema context for text-to-sql agent prompts`

---

### Step 3: Text-to-SQL Agent Prompts and Validator

**Implementation:**
- Create `backend/agents/text_to_sql/prompts.py` with:
  - `SQL_SYSTEM_PROMPT` — instructs the LLM to act as a ZCQL expert for the KSP database, references the schema context, and mandates JSON output with `zcql_query`, `intent`, and `entities` fields
  - `SQL_USER_PROMPT_TEMPLATE` — template that injects the user's query and optional conversation context
- Create `backend/agents/text_to_sql/validator.py` with:
  - `validate_query(sql: str) → tuple[bool, str]` — checks:
    - Starts with `SELECT` (case-insensitive, after stripping)
    - Does not contain `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`
    - Contains `LIMIT` clause (inject `LIMIT 50` if missing and not an aggregation query)
    - References only known table names from our schema
  - `sanitize_query(sql: str) → str` — strips trailing semicolons, normalizes whitespace

**Files Created:**
- `backend/agents/text_to_sql/prompts.py`
- `backend/agents/text_to_sql/validator.py`

**Commit Message:**
`feat(backend): add text-to-sql prompts and sql validation safeguards`

---

### Step 4: Text-to-SQL Agent Implementation

**Implementation:**
- Create `backend/agents/text_to_sql/agent.py`
- Implement `TextToSQLAgent` class:
  - `__init__(llm_client: CatalystLLMClient)` — stores the LLM client and loads schema context
  - `generate_query(user_query: str, conversation_history: list[dict] = None) → dict` — main method:
    1. Builds system prompt with schema context
    2. Builds user prompt from template
    3. Calls `llm_client.chat_completion_json()`
    4. Parses the JSON response to extract `zcql_query`, `intent`, `entities`
    5. Runs `validate_query()` on the extracted SQL
    6. If validation fails, retries once with the error message appended to the prompt
    7. Returns `{ "zcql_query": str, "intent": str, "entities": dict, "is_valid": bool, "error": str | None }`

**Files Created:**
- `backend/agents/text_to_sql/agent.py`

**Commit Message:**
`feat(backend): implement text-to-sql agent with query generation and validation`

---

### Step 5: Response Structurer Agent

**Implementation:**
- Create `backend/agents/response_structurer/__init__.py`
- Create `backend/agents/response_structurer/prompts.py` with:
  - `RESPONSE_SYSTEM_PROMPT` — instructs the LLM to act as an intelligence analyst assistant that takes raw DB results and produces a structured response
  - `RESPONSE_USER_PROMPT_TEMPLATE` — template that injects: original query, raw results (JSON), record count, table names accessed
  - Output format mandated: `{ response_text, table_data: [{firNo, crimeType, district, status}], entities: [{name, type, detail}], follow_ups: [str] }`
- Create `backend/agents/response_structurer/agent.py` with:
  - `ResponseStructurer` class:
    - `__init__(llm_client: CatalystLLMClient)`
    - `structure_response(query: str, raw_results: list[dict], metadata: dict) → dict` — calls LLM, parses JSON response
    - Handles edge cases: empty results → "No matching records found" + broadening suggestions
    - Handles LLM parse failure → falls back to raw data display with generic summary

**Files Created:**
- `backend/agents/response_structurer/__init__.py`
- `backend/agents/response_structurer/prompts.py`
- `backend/agents/response_structurer/agent.py`

**Commit Message:**
`feat(backend): implement response structurer agent for natural language summaries`

---

### Step 6: Chat Pydantic Schemas

**Implementation:**
- Create `backend/schemas/chat.py` with the following Pydantic models:
  - `ChatQueryRequest` — `{ query: str, session_id: str }`
  - `ChatTableRow` — `{ firNo: str, crimeType: str, district: str, status: str }`
  - `ChatEntity` — `{ name: str, type: str, detail: str }`
  - `ChatQueryResponse` — `{ message_id: str, response_text: str, table_data: list[ChatTableRow], sql_query: str, scanned_records: int, sources: list[str], entities: list[ChatEntity], follow_ups: list[str], timestamp: str }`
  - `ConversationItem` — `{ session_id: str, title: str, created_at: str, category: str }`
  - `ChatHistoryResponse` — `{ conversations: list[ConversationItem] }`

**Files Created:**
- `backend/schemas/chat.py`

**Commit Message:**
`feat(backend): define pydantic schemas for chat API request and response models`

---

### Step 7: Chat Router (Full Pipeline)

**Implementation:**
- Create `backend/routers/chat.py` with prefix `/api/chat`:
  
  **`POST /query`** — Main endpoint:
  1. Receive `ChatQueryRequest` body
  2. Instantiate `CatalystLLMClient`, `TextToSQLAgent`, `ResponseStructurer`
  3. Call `text_to_sql_agent.generate_query(request.query)`
  4. If valid SQL → execute via `zcql.execute_query(generated_sql)`
  5. Flatten ZCQL result rows (handle nested dict structure)
  6. Call `response_structurer.structure_response(query, flat_results, metadata)`
  7. Build `ChatQueryResponse` from Agent 2 output + SQL + metadata
  8. Optionally save to `conversations` table (try/except — skip if table doesn't exist)
  9. Return response
  
  **`GET /history`** — Conversation history:
  1. Query `conversations` table grouped by `session_id`
  2. Extract first user message as title
  3. Categorize by date (Today / Previous 7 Days / Older)
  4. Return `ChatHistoryResponse`
  
  **`POST /new`** — New conversation:
  1. Generate a new UUID `session_id`
  2. Return `{ session_id }`

- Update `backend/main.py` to register the chat router

**Files Created:**
- `backend/routers/chat.py`

**Files Modified:**
- `backend/main.py` — add `from routers.chat import router as chat_router` and `app.include_router()`

**Commit Message:**
`feat(backend): implement chat router with full agent pipeline orchestration`

---

### Step 8: Backend Testing and Environment Setup

**Implementation:**
- Add `requests` to `backend/requirements.txt`
- Catalyst SDK handles authentication automatically
- Manually test the pipeline:
  - Start backend: `uvicorn main:app --port 3001`
  - `curl -X POST http://localhost:3001/api/chat/query -H "Content-Type: application/json" -d '{"query": "Show me robbery cases in Bengaluru", "session_id": "test-1"}'`
  - Verify the response contains real data from the database
- Test edge cases:
  - Empty query → should return error message
  - Query about non-existent district → should return "no results found"
  - Very long query → should still work within LLM context limits

**Files Modified:**
- `backend/requirements.txt`

**Commit Message:**
`chore(backend): add requests dependency and test chat agent pipeline end-to-end`

---

### Step 9: Frontend TypeScript Types Update

**Implementation:**
- Update `frontend/src/types.ts` to add new interfaces:
  - `ChatEntity` — for entities extracted by the AI
  - `ChatQueryResponse` — full response from the backend (matching the Pydantic schema)
  - `ConversationItem` — for conversation history items
- Keep existing `ChatMessage`, `ChatTableRow` types unchanged (they're still used for local rendering state)

**Files Modified:**
- `frontend/src/types.ts`

**Commit Message:**
`feat(frontend): extend typescript types for chat API integration`

---

### Step 10: Frontend Chat Service

**Implementation:**
- Create `frontend/src/services/chat.service.ts` following the `dashboard.service.ts` pattern:
  - `sendQuery(query: string, sessionId: string): Promise<ChatQueryResponse>` — `POST /api/chat/query`
  - `getHistory(): Promise<ConversationItem[]>` — `GET /api/chat/history`
  - `newConversation(): Promise<{ session_id: string }>` — `POST /api/chat/new`
- All methods use the existing `apiClient` from `lib/api-client.ts`

**Files Created:**
- `frontend/src/services/chat.service.ts`

**Commit Message:**
`feat(frontend): create chat service for backend API communication`

---

### Step 11: Frontend Chat Hook

**Implementation:**
- Create `frontend/src/hooks/useChat.ts`:
  - Manages state: `messages: ChatMessage[]`, `isTyping: boolean`, `history: ConversationItem[]`, `activeSessionId: string`, `latestResponse: ChatQueryResponse | null`
  - `sendMessage(text: string)`:
    1. Add user message to `messages`
    2. Set `isTyping = true`
    3. Call `chatService.sendQuery(text, activeSessionId)`
    4. On success: convert `ChatQueryResponse` → `ChatMessage`, add to messages, store `latestResponse`
    5. On error: add error message to messages
    6. Set `isTyping = false`
  - `loadHistory()` — calls `chatService.getHistory()`, sets `history`
  - `startNewConversation()` — calls `chatService.newConversation()`, resets messages, sets new session ID
  - `selectConversation(sessionId)` — placeholder for loading specific conversation messages
  - Generates a session ID on mount via `chatService.newConversation()`

**Files Created:**
- `frontend/src/hooks/useChat.ts`

**Commit Message:**
`feat(frontend): implement useChat hook for chat state management and API calls`

---

### Step 12: Frontend ChatScreen Integration

**Implementation:**
- Modify `frontend/src/components/ChatScreen.tsx`:
  - Import and use `useChat` hook instead of local state + mock data
  - Remove all imports from `../data/mockData` (`INITIAL_CHAT_MESSAGES`, `CONVERSATION_HISTORY`, `CHAT_RESPONSES`)
  - **Left sidebar (Conversation History):**
    - Replace `CONVERSATION_HISTORY` with `history` from hook
    - `handleHistoryClick` → calls `selectConversation(sessionId)` from hook
    - "New Conversation" button → calls `startNewConversation()` from hook
  - **Center (Chat Messages):**
    - Replace `messages` state → use from hook
    - Replace `handleSendMessage` → use `sendMessage()` from hook
    - `isTyping` → use from hook (now tracks real API in-flight state)
    - Message rendering unchanged (same `ChatMessage` shape)
  - **Right sidebar (Context Panel):**
    - Replace hardcoded entities → use `latestResponse.entities` from hook
    - Replace hardcoded follow-ups → use `latestResponse.follow_ups` from hook
    - Follow-up buttons still call `sendMessage(text)` on click
  - **SQL/Sources drawers:**
    - `sqlQuery` now shows the real generated ZCQL from the backend
    - `scannedRecords` now shows real record count
    - Data Sources section shows `latestResponse.sources` (real table names)
  - Remove all `setTimeout` mock response logic

**Files Modified:**
- `frontend/src/components/ChatScreen.tsx`

**Commit Message:**
`feat(frontend): integrate ChatScreen with real backend API, remove all mock data`

---

## Summary

| Step | Layer | Description |
|------|-------|-------------|
| 1 | Backend | Catalyst Quick ML LLM client service |
| 2 | Backend | Database schema context for SQL agent |
| 3 | Backend | Text-to-SQL prompts and SQL validator |
| 4 | Backend | Text-to-SQL agent implementation |
| 5 | Backend | Response structurer agent |
| 6 | Backend | Chat Pydantic schemas |
| 7 | Backend | Chat router (full pipeline orchestration) |
| 8 | Backend | Testing and environment setup |
| 9 | Frontend | TypeScript types update |
| 10 | Frontend | Chat API service |
| 11 | Frontend | useChat hook |
| 12 | Frontend | ChatScreen integration (remove mocks) |
