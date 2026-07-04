# PRISM — Dashboard Page: Complete Data & API Specification

> This document maps every UI component in `CommandDashboardScreen.tsx` to its
> real data source, the FastAPI endpoint that serves it, the exact DB query behind
> it, and where each file lives in the folder structure.
> Use this as the single reference when wiring the dashboard to the backend.

---

## Component Map (top → bottom, left → right)

```
CommandDashboardScreen
│
├── Header
│   ├── Live Clock                     → client-side only (no API)
│   └── SYSTEM ONLINE badge            → client-side only
│
├── KPI Strip (4 cards)
│   ├── TOTAL FIRs                     → GET /api/dashboard/stats
│   ├── ACTIVE CASES                   → GET /api/dashboard/stats
│   ├── HIGH-RISK OFFENDERS            → GET /api/dashboard/stats
│   └── ACTIVE ALERTS                  → GET /api/dashboard/stats
│
├── Main Row (65/35)
│   ├── Crime Density Map (left)       → GET /api/dashboard/district-crimes
│   └── Active Alerts Feed (right)     → GET /api/dashboard/alerts
│
└── Bottom Row
    └── 30-Day Crime Trend Sparklines  → GET /api/dashboard/trends
```

---

## 1. Header

**Component location:** `frontend/src/pages/Dashboard/index.tsx` (inline, no sub-component)

**Data needed:** None from backend.
- Clock: already implemented in existing code — fix the hardcoded `OCT 24, 2023` to use real date
- SYSTEM ONLINE badge: static, always shown when page loads

**Fix in existing code:**
```tsx
// CURRENT (broken — always shows OCT 24 2023)
setCurrentTime(`OCT 24, 2023 // ${timeStr} IST`);

// CORRECT
const now = new Date();
const formatted = now.toLocaleDateString('en-IN', {
  month: 'short', day: '2-digit', year: 'numeric'
}).toUpperCase();
setCurrentTime(`${formatted} // ${timeStr} IST`);
```

---

## 2. KPI Strip — 4 Cards

### What each card shows

| Card | Field | Color | When to highlight |
|---|---|---|---|
| TOTAL FIRs | `total_firs` INT | Default white | Never |
| ACTIVE CASES | `active_cases` INT | Default white | Never |
| HIGH-RISK OFFENDERS | `high_risk_offender_count` INT | `text-tertiary` (orange) | Always |
| ACTIVE ALERTS | `active_alert_count` INT | `text-error` (red) | Always |

---

### Backend — FastAPI Router

**File:** `backend/routers/dashboard.py`

```python
from fastapi import APIRouter, Depends
from core.database import get_db
from core.security import require_role
from schemas.dashboard import DashboardStatsResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    db=Depends(get_db),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    """
    Returns precomputed KPI stats from the dashboard_stats table.
    Nightly Cron writes one fresh row. This endpoint reads the latest row only.
    Fast — single row lookup, no heavy aggregation at request time.
    """
    pass
```

**File:** `backend/schemas/dashboard.py`

```python
from pydantic import BaseModel
from datetime import datetime

class DashboardStatsResponse(BaseModel):
    total_firs: int
    active_cases: int
    high_risk_offender_count: int
    active_alert_count: int
    computed_at: datetime
```

**File:** `backend/analytics/` — this logic runs inside the nightly Cron job,
NOT inside the endpoint. The endpoint just reads `dashboard_stats` table.

The Cron job (`backend/jobs/nightly_aggregation.py`) runs these queries and
writes results to `dashboard_stats`:

```sql
-- total_firs
SELECT COUNT(*) FROM CaseMaster;

-- active_cases
SELECT COUNT(*) FROM CaseMaster cm
JOIN CaseStatusMaster csm ON cm.CaseStatusID = csm.CaseStatusID
WHERE csm.CaseStatusName = 'Under Investigation';

-- high_risk_offender_count
SELECT COUNT(*) FROM risk_scores
WHERE risk_score >= 70;

-- active_alert_count
SELECT COUNT(*) FROM crime_alerts
WHERE is_acknowledged = False;
```

---

### Frontend — Service + Hook

**File:** `frontend/src/services/dashboard.service.ts`

```typescript
import { apiClient } from '../lib/api-client';

export interface DashboardStats {
  total_firs: number;
  active_cases: number;
  high_risk_offender_count: number;
  active_alert_count: number;
  computed_at: string;
}

export const dashboardService = {
  getStats: async (): Promise<DashboardStats> => {
    const res = await apiClient.get('/api/dashboard/stats');
    return res.data;
  },
};
```

**File:** `frontend/src/hooks/useDashboardStats.ts`

```typescript
import { useState, useEffect } from 'react';
import { dashboardService, DashboardStats } from '../services/dashboard.service';

export function useDashboardStats() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    dashboardService.getStats()
      .then(setStats)
      .catch(() => setError('Failed to load stats'))
      .finally(() => setLoading(false));
  }, []);

  return { stats, loading, error };
}
```

**Usage in `CommandDashboardScreen.tsx`:**
```tsx
const { stats, loading } = useDashboardStats();

// Replace kpis.totalFirs with:
{loading ? '...' : stats?.total_firs.toLocaleString('en-IN')}
```

---

## 3. Crime Density Map — Left Panel

### What it shows

Every district dot on the map needs a real crime count to:
- Set dot color intensity (higher count = brighter/larger dot)
- Populate the KPI strip when user clicks a district dot
- Drive the timeframe toggle (24h / 7d / 30d)

**Currently hardcoded:** 3 fixed districts with static numbers.
**Target:** Real district-wise FIR counts from DB, filtered by selected timeframe.

---

### Backend — FastAPI Endpoint

**File:** `backend/routers/dashboard.py` (add to existing router)

```python
from schemas.dashboard import DistrictCrimeResponse
from datetime import datetime, timedelta

@router.get("/district-crimes", response_model=list[DistrictCrimeResponse])
async def get_district_crimes(
    timeframe: str = "30d",   # query param: "24h" | "7d" | "30d"
    db=Depends(get_db),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    """
    Returns per-district FIR counts and active case counts
    for the selected timeframe. Used to color the map dots
    and populate KPI cards when a district is clicked.
    """
    pass
```

**File:** `backend/schemas/dashboard.py` (add to existing)

```python
class DistrictCrimeResponse(BaseModel):
    district_id: int
    district_name: str
    total_firs: int
    active_cases: int
    high_risk_count: int
    dominant_crime_type: str    # most frequent CrimeSubHead name
    lat: float                  # district centroid latitude (hardcoded per district)
    lng: float                  # district centroid longitude
```

**DB Query (runs inside the endpoint — small enough, no caching needed):**

```sql
-- Parameterized by timeframe: replace :since with computed date
SELECT
    d.DistrictID       AS district_id,
    d.DistrictName     AS district_name,
    COUNT(cm.CaseMasterID) AS total_firs,
    SUM(CASE WHEN csm.CaseStatusName = 'Under Investigation' THEN 1 ELSE 0 END) AS active_cases,
    MODE() WITHIN GROUP (ORDER BY cs.CrimeHeadName) AS dominant_crime_type
FROM CaseMaster cm
JOIN Unit u       ON cm.PoliceStationID = u.UnitID
JOIN District d   ON u.DistrictID = d.DistrictID
JOIN CrimeSubHead cs  ON cm.CrimeMinorHeadID = cs.CrimeSubHeadID
JOIN CaseStatusMaster csm ON cm.CaseStatusID = csm.CaseStatusID
WHERE cm.IncidentFromDate >= :since
GROUP BY d.DistrictID, d.DistrictName
ORDER BY total_firs DESC;
```

`:since` computed in Python:
```python
timeframe_map = {"24h": 1, "7d": 7, "30d": 30}
days = timeframe_map.get(timeframe, 30)
since = datetime.utcnow() - timedelta(days=days)
```

**District centroid coordinates (static dict in backend, not in DB):**

```python
# backend/analytics/hotspot.py or inline in router
DISTRICT_CENTROIDS = {
    "Bengaluru Urban":  {"lat": 12.9716, "lng": 77.5946},
    "Mysuru":           {"lat": 12.2958, "lng": 76.6394},
    "Dakshina Kannada": {"lat": 12.8703, "lng": 74.8428},
    "Belagavi":         {"lat": 15.8497, "lng": 74.4977},
    "Ballari":          {"lat": 15.1394, "lng": 76.9214},
    "Kalaburagi":       {"lat": 17.3297, "lng": 76.8343},
    "Hubballi-Dharwad": {"lat": 15.3647, "lng": 75.1240},
    "Shivamogga":       {"lat": 13.9299, "lng": 75.5681},
    "Tumakuru":         {"lat": 13.3379, "lng": 77.1173},
    "Hassan":           {"lat": 13.0033, "lng": 76.1004},
}
```

---

### Frontend — Service + Hook

**File:** `frontend/src/services/dashboard.service.ts` (add to existing)

```typescript
export interface DistrictCrimeData {
  district_id: number;
  district_name: string;
  total_firs: number;
  active_cases: number;
  high_risk_count: number;
  dominant_crime_type: string;
  lat: number;
  lng: number;
}

// Add to dashboardService object:
getDistrictCrimes: async (timeframe: '24h' | '7d' | '30d'): Promise<DistrictCrimeData[]> => {
  const res = await apiClient.get('/api/dashboard/district-crimes', {
    params: { timeframe }
  });
  return res.data;
},
```

**File:** `frontend/src/hooks/useDashboardStats.ts` — add alongside existing hook:

```typescript
export function useDistrictCrimes(timeframe: '24h' | '7d' | '30d') {
  const [data, setData] = useState<DistrictCrimeData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    dashboardService.getDistrictCrimes(timeframe)
      .then(setData)
      .finally(() => setLoading(false));
  }, [timeframe]);   // re-fetches when timeframe toggle changes

  return { data, loading };
}
```

**Usage in map component:**
```tsx
const { data: districts, loading: mapLoading } = useDistrictCrimes(activeTimeframe);

// When user clicks a district dot:
const handleDistrictClick = (district: DistrictCrimeData) => {
  setActiveDistrict(district.district_name);
  setActiveKpis({
    totalFirs: district.total_firs,
    activeCases: district.active_cases,
    highRisk: district.high_risk_count,
  });
};

// Dot color intensity based on real count:
const getIntensity = (count: number, max: number) => {
  const ratio = count / max;
  if (ratio > 0.7) return 'bg-red-500 border-red-500';
  if (ratio > 0.4) return 'bg-orange-500 border-orange-500';
  return 'bg-yellow-500 border-yellow-500';
};
```

**File:** `frontend/src/components/maps/KarnatakaMap.tsx`
```
This component receives `districts: DistrictCrimeData[]` as props.
Renders each district as a positioned dot based on lat/lng projected
onto the SVG viewBox coordinate space.
```

---

## 4. Active Alerts Feed — Right Panel

### What it shows

Each alert card shows:
- Title (crime type + district)
- Level badge: CRITICAL / WARNING
- Details line: spike ratio as percentage
- Timestamp relative to now ("2h ago")
- Source: district name + police station

**Currently:** Pulled from `INITIAL_ALERTS` in `mockData.ts` — static array.
**Target:** Real rows from `crime_alerts` table, unacknowledged only.

---

### Backend — FastAPI Endpoint

**File:** `backend/routers/dashboard.py` (add to existing router)

```python
from schemas.dashboard import AlertResponse

@router.get("/alerts", response_model=list[AlertResponse])
async def get_active_alerts(
    limit: int = 10,
    db=Depends(get_db),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    """
    Returns unacknowledged alerts ordered by severity then recency.
    CRITICAL (spike_ratio >= 3.0) first, then MEDIUM, then by created_at DESC.
    Limit default 10 — dashboard only shows top alerts, not all history.
    """
    pass
```

**File:** `backend/schemas/dashboard.py` (add)

```python
class AlertResponse(BaseModel):
    alert_id: int
    title: str              # "{crime_type} Spike — {district_name}"
    level: str              # "CRITICAL" | "WARNING"
    details: str            # "+340% above 90-day average"
    district_name: str
    crime_type: str
    spike_ratio: float
    created_at: datetime
    time_ago: str           # "2h ago" — computed in backend
```

**DB Query:**

```sql
SELECT
    ca.alert_id,
    ca.spike_ratio,
    ca.severity,
    ca.alert_message,
    ca.created_at,
    d.DistrictName   AS district_name,
    cs.CrimeHeadName AS crime_type
FROM crime_alerts ca
JOIN District d      ON ca.district_id = d.DistrictID
JOIN CrimeSubHead cs ON ca.crime_sub_head_id = cs.CrimeSubHeadID
WHERE ca.is_acknowledged = False
ORDER BY
    CASE ca.severity WHEN 'HIGH' THEN 0 ELSE 1 END,
    ca.created_at DESC
LIMIT :limit;
```

**Response assembly in Python:**
```python
def format_time_ago(created_at: datetime) -> str:
    diff = datetime.utcnow() - created_at
    hours = int(diff.total_seconds() / 3600)
    if hours < 1:
        return f"{int(diff.total_seconds() / 60)}m ago"
    if hours < 24:
        return f"{hours}h ago"
    return f"{diff.days}d ago"

# Map severity → UI level
level = "CRITICAL" if row.severity == "HIGH" else "WARNING"

# Build title
title = f"{row.crime_type} Spike — {row.district_name}"

# Build details
details = f"+{int((row.spike_ratio - 1) * 100)}% above 90-day average"
```

---

### Frontend — Service + Hook

**File:** `frontend/src/services/dashboard.service.ts` (add)

```typescript
export interface AlertItem {
  alert_id: number;
  title: string;
  level: 'CRITICAL' | 'WARNING';
  details: string;
  district_name: string;
  crime_type: string;
  spike_ratio: number;
  created_at: string;
  time_ago: string;
}

// Add to dashboardService:
getAlerts: async (limit = 10): Promise<AlertItem[]> => {
  const res = await apiClient.get('/api/dashboard/alerts', {
    params: { limit }
  });
  return res.data;
},
```

**File:** `frontend/src/hooks/useDashboardStats.ts` (add)

```typescript
export function useAlerts() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardService.getAlerts()
      .then(setAlerts)
      .finally(() => setLoading(false));

    // Poll every 60 seconds — alerts change when Cron runs
    const interval = setInterval(() => {
      dashboardService.getAlerts().then(setAlerts);
    }, 60_000);

    return () => clearInterval(interval);
  }, []);

  return { alerts, loading };
}
```

**File:** `frontend/src/components/data-display/AlertItem.tsx`

```typescript
// Props the component expects:
interface AlertItemProps {
  alert: AlertItem;
}

// Map level to color class:
const isCritical = alert.level === 'CRITICAL';
const accentColor = isCritical ? 'bg-error' : 'bg-tertiary';
const textColor   = isCritical ? 'text-error' : 'text-tertiary';

// Source line replaces hardcoded "alert.source":
<span className="font-label-mono text-[11px]">
  {alert.time_ago} // {alert.district_name}
</span>
```

**Usage in `CommandDashboardScreen.tsx`:**
```tsx
// Remove: import { INITIAL_ALERTS } from '../data/mockData';
// Remove: const [alerts, setAlerts] = useState<Alert[]>(INITIAL_ALERTS);

const { alerts, loading: alertsLoading } = useAlerts();

// Badge count now real:
<span>{alerts.length}</span>

// Map over real data — same JSX structure, different props source
```

---

## 5. 30-Day Crime Trend Sparklines — Bottom Row

### What it shows

5 crime categories, each showing:
- 7 bars representing last 7 weeks of that crime type
- Change % vs previous period (current 30d vs prior 30d)
- Trend direction icon (up / down / flat)

**Currently:** Fully hardcoded arrays.
**Target:** Real weekly counts per crime category from DB.

---

### Backend — FastAPI Endpoint

**File:** `backend/routers/dashboard.py` (add)

```python
from schemas.dashboard import TrendResponse

@router.get("/trends", response_model=list[TrendResponse])
async def get_crime_trends(
    db=Depends(get_db),
    user=Depends(require_role(["investigator", "analyst", "supervisor"]))
):
    """
    Returns last 7 weeks of weekly FIR counts for 5 major crime categories.
    Also computes % change vs prior 30-day window.
    Results are precomputed by nightly Cron and stored in dashboard_stats
    as trend_sparklines_json — this endpoint reads and parses that JSON.
    """
    pass
```

**File:** `backend/schemas/dashboard.py` (add)

```python
class SparklineWeek(BaseModel):
    week_label: str     # "W1", "W2" ... "W7"
    count: int

class TrendResponse(BaseModel):
    crime_category: str         # "Robbery", "Theft", "Assault", "Vehicle Crime", "Burglary"
    crime_sub_head_ids: list[int]   # which CrimeSubHeadIDs map to this category
    weekly_counts: list[int]    # 7 values, oldest → newest (for bar heights)
    bar_heights: list[int]      # normalized 0-100 for rendering (max week = 100)
    change_pct: float           # e.g. +12.5 or -3.2
    trend: str                  # "up" | "down" | "flat"
    total_current: int          # sum of last 30 days
    total_prior: int            # sum of prior 30 days
```

**DB Query (runs in Cron job, cached in `trend_sparklines_json`):**

```sql
-- Weekly counts per crime category — last 7 weeks
-- Run once per category (5 queries total, or one with GROUP BY)

SELECT
    DATE_TRUNC('week', cm.IncidentFromDate) AS week_start,
    COUNT(*) AS incident_count
FROM CaseMaster cm
JOIN CrimeSubHead cs ON cm.CrimeMinorHeadID = cs.CrimeSubHeadID
WHERE
    cs.CrimeHeadName IN ('Robbery', 'Chain Snatching')  -- maps to "Robbery" category
    AND cm.IncidentFromDate >= NOW() - INTERVAL '7 weeks'
GROUP BY week_start
ORDER BY week_start ASC;

-- Change % query
SELECT
    SUM(CASE WHEN cm.IncidentFromDate >= NOW() - INTERVAL '30 days' THEN 1 ELSE 0 END) AS current_30d,
    SUM(CASE WHEN cm.IncidentFromDate BETWEEN NOW() - INTERVAL '60 days'
                                          AND NOW() - INTERVAL '30 days' THEN 1 ELSE 0 END) AS prior_30d
FROM CaseMaster cm
JOIN CrimeSubHead cs ON cm.CrimeMinorHeadID = cs.CrimeSubHeadID
WHERE cs.CrimeHeadName IN ('Robbery', 'Chain Snatching');
```

**Crime category → CrimeSubHead mapping (static in backend):**

```python
# backend/analytics/trends.py
TREND_CATEGORIES = {
    "Robbery":      [201, 202],   # Robbery + Chain Snatching
    "Theft":        [203, 204],   # Vehicle Theft + Burglary
    "Assault":      [101, 102],   # Murder + Attempt to Murder
    "Vehicle Crime":[203],        # Vehicle Theft only
    "Cyber Crime":  [401],        # Online Fraud
}
```

**Normalization for bar heights:**
```python
def normalize(counts: list[int]) -> list[int]:
    max_val = max(counts) if max(counts) > 0 else 1
    return [int((c / max_val) * 100) for c in counts]
```

**Change % + trend direction:**
```python
def compute_trend(current: int, prior: int) -> tuple[float, str]:
    if prior == 0:
        return (0.0, "flat")
    change = ((current - prior) / prior) * 100
    trend = "up" if change > 2 else "down" if change < -2 else "flat"
    return (round(change, 1), trend)
```

---

### Frontend — Service + Hook

**File:** `frontend/src/services/dashboard.service.ts` (add)

```typescript
export interface TrendData {
  crime_category: string;
  weekly_counts: number[];
  bar_heights: number[];    // use these for rendering, not raw counts
  change_pct: number;
  trend: 'up' | 'down' | 'flat';
  total_current: number;
  total_prior: number;
}

// Add to dashboardService:
getTrends: async (): Promise<TrendData[]> => {
  const res = await apiClient.get('/api/dashboard/trends');
  return res.data;
},
```

**File:** `frontend/src/hooks/useDashboardStats.ts` (add)

```typescript
export function useTrends() {
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardService.getTrends()
      .then(setTrends)
      .finally(() => setLoading(false));
  }, []);

  return { trends, loading };
}
```

**Usage in `CommandDashboardScreen.tsx`:**
```tsx
const { trends, loading: trendsLoading } = useTrends();

// Replace hardcoded array with real data:
{(trendsLoading ? [] : trends).map((trend, idx) => {
  const isUp   = trend.trend === 'up';
  const isDown = trend.trend === 'down';
  const changeStr = `${trend.change_pct > 0 ? '+' : ''}${trend.change_pct}%`;
  const colorClass = isUp ? 'text-error' : isDown ? 'text-primary' : 'text-on-surface-variant';
  const icon = isUp ? 'trending_up' : isDown ? 'trending_down' : 'trending_flat';

  return (
    <div key={idx} className="...">
      <span>{trend.crime_category}</span>
      <span className={colorClass}>
        <icon>{icon}</icon>
        {changeStr}
      </span>
      <div className="h-12 w-full flex items-end gap-1">
        {trend.bar_heights.map((height, bIdx) => (
          <div key={bIdx} style={{ height: `${height}%` }}
               className={isUp ? 'bg-tertiary' : 'bg-primary-container'} />
        ))}
      </div>
    </div>
  );
})}
```

---

## 6. Skeleton / Loading States

Every component should show a loading state while data fetches.
Add to `frontend/src/components/ui/`:

**File:** `frontend/src/components/ui/Spinner.tsx` — already in folder structure, use it.

Pattern for KPI cards while loading:
```tsx
{loading ? (
  <span className="font-display-lg text-display-lg text-on-surface-variant animate-pulse">
    ——
  </span>
) : (
  <span className="font-display-lg text-display-lg text-on-surface">
    {stats?.total_firs.toLocaleString('en-IN')}
  </span>
)}
```

Pattern for alerts while loading:
```tsx
{alertsLoading ? (
  Array.from({ length: 3 }).map((_, i) => (
    <div key={i} className="h-16 bg-surface animate-pulse rounded border border-tactical" />
  ))
) : (
  alerts.map(alert => <AlertItem key={alert.alert_id} alert={alert} />)
)}
```

---

## 7. Complete API Summary for Dashboard

| Endpoint | Method | Params | Auth | Served from |
|---|---|---|---|---|
| `/api/dashboard/stats` | GET | none | any role | `routers/dashboard.py` |
| `/api/dashboard/district-crimes` | GET | `timeframe: 24h\|7d\|30d` | any role | `routers/dashboard.py` |
| `/api/dashboard/alerts` | GET | `limit: int = 10` | any role | `routers/dashboard.py` |
| `/api/dashboard/trends` | GET | none | any role | `routers/dashboard.py` |

All 4 endpoints live in one router file. All are read-only GET. All require authentication via `require_role` middleware which validates the JWT from Catalyst Auth.

---

## 8. Files to Create / Modify — Checklist

### Backend (create or add to)
```
backend/
├── routers/dashboard.py          ← CREATE — 4 endpoints defined here
├── schemas/dashboard.py          ← CREATE — DashboardStatsResponse,
│                                             DistrictCrimeResponse,
│                                             AlertResponse, TrendResponse
├── analytics/trends.py           ← CREATE — TREND_CATEGORIES map,
│                                             normalize(), compute_trend()
└── jobs/nightly_aggregation.py   ← CREATE — runs the heavy queries,
                                              writes to dashboard_stats
```

### Frontend (create or modify)
```
frontend/src/
├── services/dashboard.service.ts    ← CREATE — 4 service functions
├── hooks/useDashboardStats.ts       ← CREATE — 4 hooks
├── components/
│   ├── data-display/AlertItem.tsx   ← CREATE — single alert card component
│   └── maps/KarnatakaMap.tsx        ← CREATE — map with real district dots
└── pages/Dashboard/index.tsx        ← MODIFY — wire all hooks, remove mockData import
```

### Delete
```
frontend/src/data/mockData.ts   ← DELETE INITIAL_ALERTS export (or full file
                                   once all pages are wired to real APIs)
```

---

## 9. Implementation Order (do this sequence)

```
1. backend/schemas/dashboard.py          → define all 4 response models first
2. backend/routers/dashboard.py          → stub all 4 endpoints, return hardcoded
                                           data initially to unblock frontend
3. frontend/src/services/dashboard.service.ts → 4 service functions
4. frontend/src/hooks/useDashboardStats.ts    → 4 hooks consuming services
5. frontend/src/pages/Dashboard/index.tsx     → wire hooks, remove mockData
6. backend/analytics/trends.py               → real trend computation logic
7. backend/jobs/nightly_aggregation.py       → real Cron job writing to dashboard_stats
8. backend/routers/dashboard.py              → replace stubs with real DB queries
9. Test end-to-end with seed data
10. Verify alert feed updates when crime_alerts table changes