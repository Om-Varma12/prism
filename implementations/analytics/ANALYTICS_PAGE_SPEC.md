# PRISM — Analytics & Patterns Page: Ground Truth Reference

> **Purpose of this document:** This is the anchor reference for the Analytics & Patterns
> page. If an AI agent working on this page becomes uncertain, starts inventing
> features, or drifts from scope, it should stop and re-read this document before
> continuing. Nothing described here should be reinterpreted, expanded, or
> "improved" without the scope changing explicitly first.

---

## 1. What This Page Is

The Analytics & Patterns page is PRISM's statistical intelligence layer. Where the
Network Explorer answers "who is connected to whom," this page answers
**"what is happening, where, and how is it changing over time."**

It directly implements two requirements from the hackathon problem statement:
- **Crime Pattern & Trend Analytics** (temporal, geographic, MO-based trends;
  hotspot and emerging cluster identification; seasonal/event-based analysis)
- **Sociological & AI-Driven Predictive Dashboards** (socio-economic correlation,
  predictive risk scoring, anomaly detection)

This page is **read-only and analytical**. It does not create, edit, or investigate
individual cases — that is the job of Intelligence Chat and Network Explorer. This
page exists to show **aggregate patterns across the entire crime dataset**, not
individual case details.

---

## 2. What This Page Is NOT

To prevent scope drift, explicitly excluded from this page:

- **Not a case management tool.** No editing FIRs, no case status changes.
- **Not a chat interface.** No natural language query box lives here — that's
  the Intelligence Chat page.
- **Not a duplicate of Network Explorer.** This page shows aggregate statistics
  (counts, trends, clusters). Network Explorer shows individual relationships
  (who is connected to whom). If a feature request involves rendering a graph
  of people/nodes/edges, it belongs on Network Explorer, not here.
- **Not a place to invent new database fields.** Every number on this page must
  trace back to a column that actually exists in `DATABASE_SCHEMA.md`, or to
  one of the five approved derived tables (`dashboard_stats`, `crime_alerts`,
  `risk_scores`, `conversations`, `audit_logs`). If a desired metric requires
  a field that doesn't exist (e.g., financial transaction data, phone records),
  do not fabricate it — flag the limitation instead.
- **Not a second risk-scoring system.** Risk scores are computed once, nightly,
  by the Cron job, and stored in `risk_scores`. This page reads that table.
  It never recalculates risk scores independently. If Network Explorer and
  this page ever show different risk scores for the same person, that is a bug.

---

## 3. The Three Tabs — Exact Scope

### Tab 1: Hotspot Map

**What it answers:** "Where is crime concentrating, and is that concentration
changing?"

**Shows:**
- A Karnataka district-level map with crime incidents clustered spatially
  (DBSCAN), rendered as sized/colored circles — cluster size communicates
  incident density, not individual pins for every FIR.
- A time-range slider (Jan 2023 → present) that re-filters the clustering
  to the selected window.
- An "Emerging Clusters" panel listing crime types/districts where the
  recent rate is significantly above historical baseline (spike_ratio > 2.0).
- A "Cluster Details" panel, populated on selecting a cluster, showing:
  incident count, dominant crime type, date range, and time-of-day
  distribution for that cluster only.

**Data source:** `CaseMaster.latitude`, `CaseMaster.longitude`,
`CaseMaster.IncidentFromDate`, joined to `CrimeSubHead` for crime type,
joined to `Unit` → `District` for geography. Emerging clusters read from
the `crime_alerts` table (already populated by the nightly Cron job — do
not recompute spike detection here).

**Explicitly out of scope for this tab:** point-level FIR markers, per-FIR
investigation detail, real-time streaming updates (this recalculates on
filter change, not continuously).

---

### Tab 2: Trend Analysis

**What it answers:** "How are crime patterns changing over time, and what
does the near future look like?"

**Shows:**
- Time-series charts (line/bar) of crime counts, groupable by crime
  category and district, at monthly or weekly granularity.
- Seasonal/event-based comparison — crime rate in a ±7-day window around
  known Karnataka festivals/events versus the yearly baseline for that
  same window.
- A forecast overlay (Prophet-generated) projecting the next 30 days,
  visually distinct from historical data (dashed line, different color/
  opacity — never rendered in a way that could be mistaken for actual
  recorded data).
- A secondary sociological panel: district-level crime rate overlaid
  against static, pre-loaded socioeconomic indicators (literacy rate,
  urbanization percentage) sourced from public Census data — this is
  intentionally static reference data, not derived from FIR records.

**Data source:** `CaseMaster.IncidentFromDate`, `CrimeMinorHeadID`,
`CrimeMajorHeadID`, joined to `Unit` → `District`. Forecast values are
precomputed by a scheduled Cron job (Prophet must never run synchronously
inside a page request — it is too slow). Festival calendar and district
socioeconomic data are static JSON bundled with the backend, not derived
from any table.

**Explicitly out of scope for this tab:** individual case links, MO
pattern clustering (that lives conceptually closer to Network Explorer /
Intelligence Chat), financial trend data (no financial fields exist in
the schema).

---

### Tab 3: Offender Risk Board

**What it answers:** "Who are the highest-priority individuals for
investigative attention, ranked and filterable?"

**Shows:**
- A sortable, filterable table: offender name, risk score (0–100,
  color-coded by band), MO tag, last known district, absconding status,
  and total FIR count.
- Filters: district, minimum risk score, absconding status only.
- Sorting: by risk score or FIR count.
- Clicking a row opens the same accused profile used by Network Explorer
  — same identity (`canonical_id` / `accused_id`), not a separate lookup.

**Data source:** the `risk_scores` derived table exclusively. This table
is precomputed nightly and already consumed by Network Explorer's profile
panel. This tab performs filtering, sorting, and pagination on that table
— it does not touch `CaseMaster`, `Accused`, or any other source table
directly, and it does not run any scoring logic of its own.

**Explicitly out of scope for this tab:** editing risk scores, manually
overriding an offender's status, displaying full case history inline
(that belongs in the profile view, reached by clicking through).

---

## 4. Data Integrity Rules (Non-Negotiable)

1. **One risk score per person, one source of truth.** The `risk_scores`
   table is the only place risk scores are computed. Every page that
   displays a risk score reads from this table. If this page ever shows
   a different number than Network Explorer for the same person, that is
   a defect to fix immediately, not a design choice to justify.

2. **No invented data.** If a chart or metric would look more impressive
   with data the schema doesn't support (financial trails, phone records,
   migration statistics tied to individual cases), do not simulate or
   estimate it. Either omit the feature or clearly label it as
   unavailable/future-scope in the UI.

3. **Forecasts are always visually distinct from historical data.** A
   viewer glancing at the trend chart must be able to tell, without
   reading a legend, which portion is recorded fact and which is a
   projection.

4. **Sociological/demographic breakdowns respect role gating.** Any query
   touching `ComplainantDetails.ReligionID` or `ComplainantDetails.CasteID`
   must confirm the requesting user's role is Analyst or Supervisor before
   that data leaves the backend — this is enforced server-side, not by
   hiding a UI element client-side.

5. **Every number must be traceable.** For any value shown on this page,
   it should be possible to point to the exact query (or Cron job output)
   that produced it. If that traceability breaks, the number should not
   ship.

---

## 5. Reused Infrastructure (Do Not Duplicate)

This page is built to share infrastructure with the rest of PRISM, not
reinvent it:

| Need | Reuse This | Do NOT |
|---|---|---|
| Query the DB | `services/zcql_client.py` (`ZCQLClient`, paginated execution) | Write raw ZCQL string concatenation inline in route handlers |
| Emerging crime spikes | `crime_alerts` table, populated by the existing alert-detection Cron job | Re-implement spike-ratio detection logic in this page's backend |
| Offender risk scores | `risk_scores` table | Recompute a formula inside the Analytics router |
| Accused identity | The same `canonical_id` scheme used by Network Explorer's entity resolver | Create a second identity/ID system for offenders |
| Role checks | `core/security.py` `require_role()` dependency | Write ad hoc role-checking logic per endpoint |

---

## 6. Definition of Done

This page is complete when:

- All three tabs render exclusively from real queries against the schema
  described in `DATABASE_SCHEMA.md` and the five approved derived tables.
- Hotspot clustering, trend aggregation, and forecast generation each map
  to a documented backend module, not inline logic scattered across route
  handlers.
- The risk score and MO tag for any given offender are identical whether
  viewed here or in Network Explorer.
- No chart, table, or panel on this page displays a value that cannot be
  traced back to a specific query or Cron job output.
- Role-gated fields never appear in API responses to unauthorized roles,
  verified at the backend, not just hidden in the frontend.

---

*If any instruction elsewhere conflicts with this document, this document wins
for the Analytics & Patterns page. Escalate the conflict rather than guessing.*
