# PRISM Backend Documentation

## Overview
PRISM backend is a FastAPI application that provides APIs for the crime analytics dashboard. It uses Catalyst SDK for database operations and includes scheduled tasks for data synchronization.

---

## Database Tables

### CaseMaster
Main table storing FIR (First Information Report) records.
- **CaseMasterID**: Primary key
- **PoliceStationID**: Foreign key to Unit table
- **CaseStatusID**: Foreign key to CaseStatusMaster table
- **CrimeMinorHeadID**: Foreign key to CrimeSubHead table
- **IncidentFromDate**: Date/time of incident
- Other case details

### Unit
Police station/unit information.
- **ROWID**: Primary key
- **DistrictID**: Foreign key to District table
- Unit details

### District
District information for Karnataka state.
- **ROWID**: Primary key
- **DistrictName**: Name of district

### CrimeSubHead
Crime categorization information.
- **ROWID**: Primary key
- **CrimeHeadName**: Name of crime type

### CaseStatusMaster
Case status information.
- **ROWID**: Primary key
- **CaseStatusName**: Status name (e.g., "Under Investigation")

### dashboard_stats
Pre-computed dashboard statistics for performance.
- **total_firs**: Total number of FIRs
- **active_cases**: Number of active cases
- **high_risk_offender_count**: Count of high-risk offenders
- **active_alert_count**: Count of unacknowledged alerts
- **computed_at**: Timestamp when stats were computed
- **trend_sparklines_json**: JSON string containing trend data

### crime_alerts
Alert notifications for crime spikes.
- **ROWID**: Primary key
- **alert_id**: Alert identifier
- **created_at**: Alert creation timestamp
- **district_id**: Foreign key to District (can be NULL)
- **crime_sub_head_id**: Foreign key to CrimeSubHead (can be NULL)
- **spike_ratio**: Ratio indicating severity of spike
- **severity**: Alert severity ('HIGH' or 'MEDIUM')
- **alert_message**: Alert description
- **is_acknowledged**: Acknowledgment status ('0' = unacknowledged, '1' = acknowledged)

---

## API Endpoints

### Dashboard APIs (`/api/dashboard`)

#### GET `/api/dashboard/stats`
Get dashboard statistics.

**Authentication**: Requires role `investigator`, `analyst`, or `supervisor`

**Response**:
```json
{
  "total_firs": 12345,
  "active_cases": 567,
  "high_risk_offender_count": 89,
  "active_alert_count": 6,
  "computed_at": "2026-07-09T10:30:00"
}
```

**Logic**:
1. First tries to fetch from `dashboard_stats` table (most recent record)
2. Falls back to on-the-fly computation if table is empty
3. Fallback computes total FIRs and active cases from CaseMaster

---

#### GET `/api/dashboard/district-crimes`
Get crime statistics by district.

**Authentication**: Requires role `investigator`, `analyst`, or `supervisor`

**Query Parameters**:
- `timeframe`: Time period filter (`24h`, `7d`, `30d`) - default: `30d`

**Response**:
```json
[
  {
    "district_id": 123,
    "district_name": "Bengaluru North",
    "total_firs": 150,
    "active_cases": 0,
    "high_risk_count": 0,
    "dominant_crime_type": "Robbery",
    "lat": 13.0,
    "lng": 77.5
  }
]
```

**Logic**:
1. Filters CaseMaster records by timeframe (IncidentFromDate >= since_date)
2. Joins with Unit, District, and CrimeSubHead tables
3. Groups by district and crime type
4. Computes total FIRs per district
5. Determines dominant crime type per district
6. Returns sorted by total_firs descending

---

#### GET `/api/dashboard/alerts`
Get active (unacknowledged) crime alerts.

**Authentication**: Requires role `investigator`, `analyst`, or `supervisor`

**Query Parameters**:
- `limit`: Maximum number of alerts to return - default: `10`

**Response**:
```json
[
  {
    "alert_id": 1,
    "title": "Robbery Spike — Bengaluru North",
    "level": "CRITICAL",
    "details": "+150% above 90-day average",
    "district_name": "Bengaluru North",
    "crime_type": "Robbery",
    "spike_ratio": 2.5,
    "created_at": "2026-07-09T09:00:00",
    "time_ago": "1 hour ago"
  }
]
```

**Logic**:
1. Queries crime_alerts table for unacknowledged alerts (is_acknowledged = '0' or 0 or NULL)
2. LEFT JOINs with District and CrimeSubHead tables
3. Uses COALESCE to handle missing foreign keys (district_id, crime_sub_head_id)
4. Orders by severity (HIGH first) then created_at DESC
5. Converts severity to level ('HIGH' -> 'CRITICAL', 'MEDIUM' -> 'WARNING')
6. Computes time_ago string from created_at

---

#### GET `/api/dashboard/trends`
Get crime trend data with sparklines.

**Authentication**: Requires role `investigator`, `analyst`, or `supervisor`

**Response**:
```json
[
  {
    "crime_category": "Violent Crime",
    "weekly_counts": [10, 15, 12, 18, 20, 25, 22],
    "bar_heights": [40, 60, 48, 72, 80, 100, 88],
    "change_pct": 120.0,
    "trend": "up",
    "total_current": 122,
    "total_prior": 55
  }
]
```

**Logic**:
1. First tries to fetch pre-computed trend_sparklines_json from dashboard_stats
2. Falls back to on-the-fly computation if not available
3. Computes crime counts by category for current 30-day period
4. Calculates change percentage and trend direction
5. Normalizes weekly counts for bar chart heights
6. Returns trend data for categories: Violent Crime, Property Crime, Cyber Crime

---

### Analytics APIs (`/api/analytics`)

#### GET `/api/analytics/hotspots`
Get spatial crime hotspots using DBSCAN clustering.

**Authentication**: Requires role `investigator`, `analyst`, or `supervisor`

**Query Parameters**:
- `date_from`: Start date filter (YYYY-MM-DD format)
- `date_to`: End date filter (YYYY-MM-DD format)
- `district`: District name filter

**Response**:
```json
{
  "clusters": [
    {
      "cluster_id": 1,
      "centroid_lat": 13.0,
      "centroid_lng": 77.5,
      "point_count": 25,
      "radius_km": 2.5,
      "dominant_crime_type": "Robbery",
      "district": "Bengaluru North"
    }
  ],
  "total_incidents": 150,
  "filters": {
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "district": "Bengaluru North"
  },
  "generated_at": "2026-07-14T10:30:00"
}
```

**Logic**:
1. Queries CaseMaster with latitude/longitude for geospatial clustering
2. Applies DBSCAN clustering algorithm to identify hotspots
3. Computes cluster centroids, radius, and dominant crime type
4. Results cached for 5 minutes

---

#### GET `/api/analytics/emerging-clusters`
Get emerging crime clusters from crime_alerts table.

**Authentication**: Requires role `investigator`, `analyst`, or `supervisor`

**Response**:
```json
{
  "alerts": [
    {
      "alert_id": 1,
      "crime_type": "Robbery",
      "district": "Bengaluru North",
      "spike_ratio": 2.5,
      "baseline_count": 10,
      "current_count": 25,
      "detected_at": "2026-07-14T09:00:00",
      "acknowledged": false,
      "severity": "HIGH"
    }
  ],
  "total_alerts": 5,
  "generated_at": "2026-07-14T10:30:00"
}
```

**Logic**:
1. Queries crime_alerts table for recent alerts
2. Filters by spike_ratio > 2.0 for significant spikes
3. Returns sorted by severity and detection date
4. Results cached for 5 minutes

---

#### GET `/api/analytics/trends`
Get crime trend analysis with forecast data.

**Authentication**: Requires role `investigator`, `analyst`, or `supervisor`

**Query Parameters**:
- `granularity`: Time granularity (`month` or `week`) - default: `month`
- `crime_type`: Filter by crime type (optional)
- `district`: Filter by district (optional)

**Response**:
```json
{
  "data": [
    {
      "date": "2024-01-01",
      "count": 150,
      "is_forecast": false,
      "lower_bound": null,
      "upper_bound": null
    },
    {
      "date": "2024-08-15",
      "count": 180,
      "is_forecast": true,
      "lower_bound": 160,
      "upper_bound": 200
    }
  ],
  "filters": {
    "granularity": "month",
    "crime_type": "Robbery",
    "district": "Bengaluru North"
  },
  "total_count": 20,
  "generated_at": "2026-07-14T10:30:00"
}
```

**Logic**:
1. Aggregates crime counts by month or week from CaseMaster
2. Merges historical data with Prophet forecast data from crime_forecasts table
3. Marks forecast points with is_forecast flag
4. Includes confidence intervals (lower_bound, upper_bound) for forecasts
5. Results cached for 1 hour

---

#### GET `/api/analytics/festival-calendar`
Get seasonal crime comparisons around Karnataka festivals.

**Authentication**: Requires role `investigator`, `analyst`, or `supervisor`

**Response**:
```json
{
  "comparisons": [
    {
      "event_name": "Dasara",
      "event_date": "2024-10-12",
      "window_start": "2024-10-05",
      "window_end": "2024-10-19",
      "event_window_count": 45,
      "baseline_window_count": 20,
      "percentage_change": 125.0
    }
  ],
  "generated_at": "2026-07-14T10:30:00"
}
```

**Logic**:
1. Uses static Karnataka festival calendar
2. Computes crime counts in ±7-day window around each festival
3. Compares to baseline (same window in other months)
4. Results cached for 1 hour

---

#### GET `/api/analytics/offender-risk`
Get offender risk scores from risk_scores table.

**Authentication**: Requires role `investigator`, `analyst`, or `supervisor`

**Query Parameters**:
- `district`: Filter by district (optional)
- `min_risk_score`: Minimum risk score filter (0-100)
- `is_absconding`: Filter by absconding status (true/false)
- `page`: Page number - default: 1
- `page_size`: Items per page - default: 20

**Response**:
```json
{
  "offenders": [
    {
      "accused_id": 123,
      "accused_name": "John Doe",
      "risk_score": 85,
      "mo_tag": "Vehicle Theft Specialist",
      "district_ids": ["Bengaluru North", "Mysuru"],
      "is_absconding": true,
      "fir_count": 15
    }
  ],
  "total_count": 150,
  "page": 1,
  "page_size": 20,
  "filters": {
    "district": "Bengaluru North",
    "min_risk_score": 70,
    "is_absconding": true
  },
  "generated_at": "2026-07-14T10:30:00"
}
```

**Logic**:
1. Queries risk_scores derived table
2. Applies filters for district, min_risk_score, is_absconding
3. Sorts by risk_score descending
4. Implements pagination
5. Results cached for 10 minutes

---

#### GET `/api/analytics/socioeconomic`
Get district-level socioeconomic indicators.

**Authentication**: Requires role `analyst` or `supervisor` (role-gated)

**Response**:
```json
{
  "districts": [
    {
      "district": "Bengaluru Urban",
      "literacy_rate": 87.67,
      "urbanization_percentage": 90.56,
      "population": 9621551
    }
  ],
  "generated_at": "2026-07-14T10:30:00"
}
```

**Logic**:
1. Returns static Karnataka district socioeconomic data from JSON file
2. Includes literacy rate, urbanization percentage, and population
3. Server-side role enforcement (Analyst/Supervisor only)
4. Results cached for 1 hour

---

### Database Test/Debug APIs (`/db/test`)

#### GET `/db/test/schema`
Get schema of all database tables.

**Response**:
```json
{
  "status": "success",
  "schema": {
    "CaseMaster": [
      {
        "column_name": "CaseMasterID",
        "data_type": "bigint",
        "is_mandatory": true,
        "is_unique": true
      }
    ],
    "District": [...],
    ...
  }
}
```

**Usage**: Debug endpoint to inspect table structures

---

#### GET `/db/test/update-alerts-acknowledgment`
Update 5 most recent alerts to unacknowledged status.

**Response**:
```json
{
  "status": "success",
  "message": "Updated 5 alerts to is_acknowledged = false",
  "updated_count": 5
}
```

**Logic**:
1. Fetches 5 most recent alerts ordered by created_at DESC
2. Updates is_acknowledged to 0 for alerts that are currently 1 or NULL
3. Skips alerts already at 0

---

#### GET `/db/test/update-dashboard-stats`
Update dashboard_stats.active_alert_count based on unacknowledged alerts.

**Response**:
```json
{
  "status": "success",
  "message": "Synced dashboard_stats.active_alert_count from 0 to 5",
  "old_count": 0,
  "new_count": 5
}
```

**Logic**:
1. Counts unacknowledged alerts from crime_alerts table
2. Updates dashboard_stats.active_alert_count with the count
3. Handles string/int data types for is_acknowledged

---

#### GET `/db/test/auto-sync-alerts`
Manual trigger for alert count synchronization (same as scheduled task).

**Response**:
```json
{
  "status": "success",
  "message": "Synced dashboard_stats.active_alert_count from 0 to 5",
  "old_count": 0,
  "new_count": 5
}
```

**Logic**: Same as update-dashboard-stats, but uses reusable sync_alert_count function

---

### Data Insertion/Truncation APIs (`/db/test`)

#### GET `/db/test/insert-data`
Insert seed data into tables (Units, Employees, CaseMaster, etc.)

#### GET `/db/test/truncate-data`
Truncate all tables (delete all data)

#### GET `/db/test/insert-derived-data`
Insert derived/computed data

#### GET `/db/test/truncate-derived-data`
Truncate derived data tables

#### GET `/db/test/insert-recent-cases`
Insert recent case data for testing

---

## Scheduled Tasks

### Alert Count Synchronization
**Scheduler**: APScheduler (AsyncIOScheduler)
**Interval**: Every 5 minutes
**Function**: `scheduled_sync_alerts()`

**Logic**:
1. Initializes Catalyst SDK without request context
2. Calls `sync_alert_count(zcql, datastore)` function
3. Counts unacknowledged alerts from crime_alerts
4. Updates dashboard_stats.active_alert_count
5. Logs success/failure

**Lifecycle**:
- Starts on application startup
- Stops on application shutdown
- Replaces existing job if already running

---

## Authentication & Authorization

### Role-Based Access Control
Uses `require_role()` dependency to enforce role-based access.

**Allowed Roles**:
- `investigator`
- `analyst`
- `supervisor`

**Implementation**:
- Decorator on protected endpoints
- Checks user role from request context
- Returns 403 Forbidden if unauthorized

---

## CORS Configuration

**Allowed Origins**: `*` (all origins)
**Allowed Methods**: `*` (all methods)
**Allowed Headers**: `*` (all headers)
**Allow Credentials**: `true`

---

## Data Type Notes

### is_acknowledged Field
- Stored as both string ('0', '1') and integer (0, 1) in database
- Queries must handle both formats: `is_acknowledged = '0' OR is_acknowledged = 0 OR is_acknowledged IS NULL`
- String format appears to be the actual storage format

### ZCQL Result Structure
- ZCQL returns nested results under table name key
- Example: `result[0].get('crime_alerts', result[0])`
- Must handle both nested and flat result structures

### Date/Time Handling
- Stored as strings in format: `YYYY-MM-DD HH:MM:SS`
- Converted to datetime objects in Python
- Timezone-aware dates are converted to naive for comparison

---

## Error Handling

### Dashboard APIs
- Try-catch blocks around database queries
- Fallback to on-the-fly computation if pre-computed data unavailable
- Returns empty arrays or zero values on error
- Errors logged but not exposed to client

### Test/Debug APIs
- Try-catch blocks around all operations
- Returns error messages in response body
- Errors printed to console for debugging

---

## Frontend Integration

### API Base URL
- Backend runs on `http://localhost:3001`
- Frontend makes requests to `/api/dashboard/*` endpoints

### React Query Integration
- Frontend uses React Query (TanStack Query) for data fetching
- Alerts endpoint: 60-second refetch interval
- Other endpoints: Manual refetch or stale-time based

### Current Frontend State
- Alerts are currently hardcoded in frontend (6 sample alerts)
- Backend API calls for alerts are disabled
- Other endpoints (stats, district-crimes, trends) still use backend

---

## Development Notes

### Adding New Endpoints
1. Create router in `routers/` directory
2. Register router in `main.py` with `app.include_router()`
3. Add schemas in `schemas/` directory if needed
4. Use `get_zcql` and `get_datastore` dependencies for database access
5. Add role-based authorization with `require_role()`

### Database Queries
- Use ZCQL for SQL-like queries
- Handle nested result structures
- Use COALESCE for NULL handling
- Account for string/int data type variations

### Testing
- Use `/db/test/*` endpoints for data manipulation
- Use `/db/test/schema` to inspect table structures
- Manual sync endpoint available for testing scheduled logic

---

## Known Issues & Workarounds

### Alert Display Issue
- **Problem**: Alerts not displaying on frontend despite database having data
- **Cause**: is_acknowledged stored as string '0'/'1', queries expected integer 0/1
- **Fix**: Updated queries to handle both string and integer formats
- **Current Status**: Frontend uses hardcoded alerts (bypassing backend)

### Missing Foreign Keys
- **Problem**: crime_alerts.district_id and crime_sub_head_id are empty
- **Fix**: Used COALESCE to fallback to alert_message and 'Crime' string
- **Impact**: District names show alert_message instead of actual district names

---

## File Structure

```
backend/
├── main.py                          # FastAPI app and router registration
├── routers/
│   └── dashboard.py                 # Dashboard API endpoints
├── schemas/
│   └── dashboard.py                 # Pydantic response models
├── core/
│   ├── database.py                  # Database connection helpers
│   └── security.py                  # Authentication/authorization
├── analytics/
│   └── trends.py                    # Trend computation logic
└── tests/db/
    ├── data_insertion.py            # Seed data insertion
    ├── truncate.py                  # Data truncation
    ├── table_schema.py              # Schema inspection
    ├── insert_derived_data.py       # Derived data insertion
    ├── truncate_derived.py         # Derived data truncation
    ├── insert_recent_cases.py       # Recent case insertion
    ├── update_alerts_acknowledgment.py  # Alert acknowledgment updates
    ├── update_dashboard_stats.py    # Dashboard stats updates
    └── auto_sync_alerts.py          # Alert sync scheduled task
```

---

## Environment Setup

### Dependencies
- FastAPI
- zcatalyst-sdk (Catalyst SDK)
- APScheduler (for scheduled tasks)
- Pydantic (for schemas)

### Running the Backend
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 3001
```

### Catalyst SDK Initialization
- Requires Catalyst environment or request context
- For scheduled tasks: `zcatalyst_sdk.initialize()`
- For API endpoints: `zcatalyst_sdk.initialize(req=request)`

---

## API Quick Reference

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/dashboard/stats` | GET | Yes | Get dashboard KPIs |
| `/api/dashboard/district-crimes` | GET | Yes | Get district crime stats |
| `/api/dashboard/alerts` | GET | Yes | Get active alerts |
| `/api/dashboard/trends` | GET | Yes | Get crime trends |
| `/db/test/schema` | GET | No | Get table schemas |
| `/db/test/update-alerts-acknowledgment` | GET | No | Update alert status |
| `/db/test/update-dashboard-stats` | GET | No | Update dashboard stats |
| `/db/test/auto-sync-alerts` | GET | No | Manual alert sync |
| `/db/test/insert-data` | GET | No | Insert seed data |
| `/db/test/truncate-data` | GET | No | Truncate all data |
