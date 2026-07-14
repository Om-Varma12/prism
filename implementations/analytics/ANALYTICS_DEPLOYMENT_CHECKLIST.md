# Analytics & Patterns Page - Deployment Checklist

Use this checklist when deploying the Analytics & Patterns page to production.

## Pre-Deployment Checklist

### Dependencies
- [ ] Install Prophet: `pip install prophet`
- [ ] Install scikit-learn: `pip install scikit-learn`
- [ ] Install pandas: `pip install pandas`
- [ ] Verify Prophet installation: `python -c "from prophet import Prophet; print('OK')"`
- [ ] Verify DBSCAN installation: `python -c "from sklearn.cluster import DBSCAN; print('OK')"`

### Database Setup
- [ ] Verify `crime_forecasts` table exists in Catalyst Datastore
- [ ] Verify table has correct columns: ROWID, crime_category, forecast_date, predicted_value, lower_bound, upper_bound, generated_at, forecast_days
- [ ] Verify `risk_scores` table is populated with offender data
- [ ] Verify `crime_alerts` table is populated with alert data
- [ ] Verify `district_socioeconomic.json` exists in `backend/data/` directory

### Backend Configuration
- [ ] Analytics router registered in `main.py`: `app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])`
- [ ] Analytics schemas exist in `schemas/analytics.py`
- [ ] Analytics modules exist: `analytics/hotspot.py`, `analytics/trends.py`, `analytics/forecasting.py`
- [ ] Cron job script exists: `jobs/forecast_cron.py`
- [ ] Jobs package initialized: `jobs/__init__.py`

### Frontend Configuration
- [ ] Analytics page registered in `App.tsx`: `AnalyticsPage` component for Screen.ANALYTICS
- [ ] Analytics types exist: `types/analytics.ts`
- [ ] Analytics service exists: `services/analytics.service.ts`
- [ ] Analytics page components exist: `pages/Analytics/index.tsx`, `HotspotMap.tsx`, `TrendAnalysis.tsx`, `OffenderRiskBoard.tsx`

## Deployment Steps

### 1. Backend Deployment
- [ ] Deploy backend code to Catalyst
- [ ] Install Python dependencies (Prophet, scikit-learn, pandas)
- [ ] Verify backend starts without errors
- [ ] Test analytics endpoints:
  - [ ] GET `/api/analytics/hotspots`
  - [ ] GET `/api/analytics/emerging-clusters`
  - [ ] GET `/api/analytics/trends`
  - [ ] GET `/api/analytics/festival-calendar`
  - [ ] GET `/api/analytics/offender-risk`
  - [ ] GET `/api/analytics/socioeconomic` (test with Analyst/Supervisor role)

### 2. Cron Job Setup
- [ ] Schedule forecast generation Cron job for daily execution at 2 AM
- [ ] Test manual execution: `python jobs/forecast_cron.py`
- [ ] Verify `crime_forecasts` table is populated after execution
- [ ] Check Cron job logs for errors
- [ ] Verify forecast data appears in `/api/analytics/trends` response

### 3. Frontend Deployment
- [ ] Deploy frontend code to Catalyst
- [ ] Verify Analytics page renders without errors
- [ ] Test tab navigation (Hotspot Map, Trend Analysis, Offender Risk Board)
- [ ] Test API calls from frontend to backend
- [ ] Verify role-based access control (test with different user roles)

### 4. Cache Verification
- [ ] Verify Catalyst Cache is configured
- [ ] Test cache behavior for hotspots (5-minute TTL)
- [ ] Test cache behavior for emerging clusters (5-minute TTL)
- [ ] Test cache behavior for trends (1-hour TTL)
- [ ] Test cache behavior for offender risk (10-minute TTL)
- [ ] Test cache behavior for socioeconomic (1-hour TTL)

### 5. Role-Based Access Control
- [ ] Test `/api/analytics/socioeconomic` with Analyst role (should succeed)
- [ ] Test `/api/analytics/socioeconomic` with Supervisor role (should succeed)
- [ ] Test `/api/analytics/socioeconomic` with Investigator role (should return 403)
- [ ] Verify server-side enforcement (not just UI hiding)

## Post-Deployment Verification

### Functionality Tests
- [ ] Hotspot Map: Verify clusters display correctly on map
- [ ] Hotspot Map: Test date range slider functionality
- [ ] Hotspot Map: Verify emerging clusters panel updates
- [ ] Trend Analysis: Verify historical data displays
- [ ] Trend Analysis: Verify forecast data displays with confidence intervals
- [ ] Trend Analysis: Test granularity toggle (month/week)
- [ ] Trend Analysis: Test crime type and district filters
- [ ] Trend Analysis: Verify seasonal comparison panel displays
- [ ] Offender Risk Board: Verify offender cards display
- [ ] Offender Risk Board: Test risk score color coding
- [ ] Offender Risk Board: Test absconding status badge
- [ ] Offender Risk Board: Test pagination controls
- [ ] Offender Risk Board: Test filters (district, min_risk_score, is_absconding)
- [ ] Offender Risk Board: Test search by name
- [ ] Offender Risk Board: Test sort by risk_score and fir_count

### Performance Tests
- [ ] Verify hotspots endpoint responds within 5 seconds
- [ ] Verify trends endpoint responds within 5 seconds
- [ ] Verify offender risk endpoint responds within 5 seconds
- [ ] Verify cache reduces response time on subsequent requests
- [ ] Verify pagination prevents large result sets from slowing down

### Data Integrity Tests
- [ ] Verify risk scores match between Analytics page and Network Explorer
- [ ] Verify forecast data is visually distinct from historical data
- [ ] Verify no invented data appears in charts or tables
- [ ] Verify all numbers are traceable to database queries or Cron job output

### Monitoring Setup
- [ ] Set up monitoring for forecast Cron job execution
- [ ] Set up alerts for Cron job failures
- [ ] Set up monitoring for cache hit rates
- [ ] Set up monitoring for API response times
- [ ] Set up monitoring for error rates

## Rollback Plan

If deployment fails:
1. Revert backend code to previous version
2. Remove Cron job schedule
3. Revert frontend code to previous version
4. Clear Catalyst Cache
5. Verify system is stable before attempting redeployment

## Known Limitations

- Prophet requires minimum 2 data points for forecasting
- DBSCAN clustering may fail with insufficient data points
- Map visualization requires Leaflet installation (placeholder currently in place)
- Chart visualization requires Recharts installation (placeholder currently in place)
- Socioeconomic data is static and requires manual updates if demographics change

## Support Documentation

- Setup Guide: `backend/ANALYTICS_SETUP.md`
- API Documentation: `backend/BACKEND_DOCUMENTATION.md` (Analytics APIs section)
- Specification: `implementations/analytics/ANALYTICS_PAGE_SPEC.md`
- Database Schema: `backend/db/db-table-schema.md` (Section 9.6 for crime_forecasts)
