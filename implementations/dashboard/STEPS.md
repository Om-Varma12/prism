# PRISM — Dashboard Implementation Steps

This document outlines the step-by-step implementation plan for the PRISM Dashboard, including the technical tasks to be completed in each step and the corresponding Git commit messages.

---

### Step 1: Backend Core Infrastructure

**Implementation:**
- Create `backend/core/__init__.py`
- Create `backend/core/database.py` and extract the `get_datastore()` dependency to connect to Zoho Catalyst DataStore.
- Create `backend/core/security.py` and implement the `require_role()` dependency (initially as a permissive stub for fast development).
- Update `backend/main.py` to register the upcoming dashboard router.

**Commit Message:**
`feat(backend): implement core database and security dependencies for dashboard`

---

### Step 2: Backend Dashboard Schemas

**Implementation:**
- Create `backend/schemas/__init__.py`
- Create `backend/schemas/dashboard.py` with the 4 required Pydantic response models:
  - `DashboardStatsResponse`
  - `DistrictCrimeResponse`
  - `AlertResponse`
  - `TrendResponse` (and `SparklineWeek`)

**Commit Message:**
`feat(backend): define pydantic schemas for dashboard API responses`

---

### Step 3: Backend Dashboard Router (Stub Data)

**Implementation:**
- Create `backend/routers/__init__.py`
- Create `backend/routers/dashboard.py`
- Implement 4 GET endpoints (`/stats`, `/district-crimes`, `/alerts`, `/trends`) that return hardcoded mock data matching the current frontend UI. This unblocks frontend development while real DB queries are written.

**Commit Message:**
`feat(backend): create dashboard API endpoints with stub data to unblock frontend`

---

### Step 4: Frontend API Client Setup

**Implementation:**
- Install `axios` in the `frontend` directory.
- Update `frontend/package.json` to include `"proxy": "http://localhost:8000"`.
- Create `frontend/src/lib/api-client.ts` and configure the axios instance with interceptors and Catalyst session cookie support.

**Commit Message:**
`feat(frontend): setup axios api client and local development proxy`

---

### Step 5: Frontend Dashboard Service

**Implementation:**
- Create `frontend/src/services/dashboard.service.ts`
- Define TypeScript interfaces matching the backend schemas (`DashboardStats`, `DistrictCrimeData`, `AlertItem`, `TrendData`).
- Implement the 4 service functions (`getStats`, `getDistrictCrimes`, `getAlerts`, `getTrends`) to call the FastAPI backend using `apiClient`.

**Commit Message:**
`feat(frontend): create dashboard service for API communication`

---

### Step 6: Frontend Custom Hooks

**Implementation:**
- Create `frontend/src/hooks/useDashboardStats.ts`
- Implement 4 custom React hooks:
  - `useDashboardStats` (fetches once)
  - `useDistrictCrimes` (re-fetches on timeframe change)
  - `useAlerts` (fetches on mount, polls every 60s)
  - `useTrends` (fetches once)
- Add proper loading and error state management to each hook.

**Commit Message:**
`feat(frontend): implement react hooks for dashboard data fetching and polling`

---

### Step 7: Frontend UI Wiring - Phase 1 (Clock & KPIs)

**Implementation:**
- Modify `frontend/src/components/CommandDashboardScreen.tsx`
- Replace the hardcoded `"OCT 24, 2023"` string with a real dynamic date generator.
- Integrate `useDashboardStats` and replace the 4 hardcoded KPI values with data from the API. Add `animate-pulse` shimmer loaders for the loading state.

**Commit Message:**
`feat(frontend): wire dynamic clock and kpi strip to dashboard API`

---

### Step 8: Frontend UI Wiring - Phase 2 (Map & Alerts)

**Implementation:**
- Modify `frontend/src/components/CommandDashboardScreen.tsx`
- Integrate `useDistrictCrimes` and replace the 3 static map pins with a `.map()` rendering dynamic pins based on API data and latitude/longitude projection.
- Integrate `useAlerts` and replace the static mock alerts with real alerts from the API. Implement skeleton loaders for the alerts feed.

**Commit Message:**
`feat(frontend): wire crime density map and active alerts feed to real data`

---

### Step 9: Frontend UI Wiring - Phase 3 (Sparklines & Cleanup)

**Implementation:**
- Modify `frontend/src/components/CommandDashboardScreen.tsx`
- Integrate `useTrends` and replace the hardcoded sparkline arrays with real data, dynamically calculating bar heights and trend indicators.
- Update `frontend/src/types.ts` if needed (e.g., adding the `'WARNING'` level to `Alert`).
- Remove unused mock data imports and the `getKpis()` function.

**Commit Message:**
`feat(frontend): wire trend sparklines and remove legacy mock data from dashboard`

---

### Step 10: Backend Analytics Utilities

**Implementation:**
- Create `backend/analytics/__init__.py`
- Create `backend/analytics/trends.py`
- Add utility variables and functions: `DISTRICT_CENTROIDS`, `TREND_CATEGORIES`, `normalize()`, `compute_trend()`, and `format_time_ago()`.

**Commit Message:**
`feat(backend): add analytics utility functions for dashboard computations`

---

### Step 11: Backend Router (Real DB Queries)

**Implementation:**
- Modify `backend/routers/dashboard.py`
- Replace the stub data in `/stats` with a query to the `dashboard_stats` table.
- Replace the stub data in `/alerts` with a query to the `crime_alerts` table.
- Replace the stub data in `/district-crimes` and `/trends` with real ZCQL queries against `CaseMaster` (or `dashboard_stats` if precomputed), incorporating the analytics utilities.

**Commit Message:**
`feat(backend): replace stub endpoints with real ZCQL database queries`

---

### Step 12: Final Verification & Seed Data Test

**Implementation:**
- Verify the existence of the required Catalyst DataStore tables (`dashboard_stats`, `crime_alerts`, `risk_scores`). Create and seed them if necessary.
- Run an end-to-end test with the complete system to ensure all loading states, data visualizations, and map projections work correctly.

**Commit Message:**
`chore: final verification and end-to-end testing of dashboard module`
