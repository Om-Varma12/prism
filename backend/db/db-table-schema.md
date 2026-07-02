# Drishti — Database Schema Reference
### Karnataka Police FIR System | AI Agent Reference Document

> **Purpose:** This document is the authoritative reference for all AI agents, query generators, and developers working with the Drishti crime intelligence database. Every table, every column, every foreign key relationship, and every query pattern is documented here. Read this before writing any SQL.

---

## Table of Contents

1. [Database Overview](#1-database-overview)
2. [Schema Architecture](#2-schema-architecture)
3. [Core Tables](#3-core-tables)
4. [Person Tables](#4-person-tables)
5. [Legal Classification Tables](#5-legal-classification-tables)
6. [Geography & Organisational Tables](#6-geography--organisational-tables)
7. [Employee Tables](#7-employee-tables)
8. [Lookup / Reference Tables](#8-lookup--reference-tables)
9. [Derived Tables (Drishti-Added)](#9-derived-tables-drishti-added)
10. [Full Relationship Matrix](#10-full-relationship-matrix)
11. [Entity Relationship Summary](#11-entity-relationship-summary)
12. [Query Patterns & Examples](#12-query-patterns--examples)
13. [Critical Rules for Query Generation](#13-critical-rules-for-query-generation)

---

## 1. Database Overview

The Karnataka State Police (KSP) FIR database captures every First Information Report (FIR) registered at any police station across Karnataka. It records the incident, the people involved (accused, victims, complainants), the legal acts and sections invoked, the investigation status, and the geographic and organisational context.

**Scale context for query planning:**
- ~30 districts across Karnataka
- ~150–200 police stations (Units)
- Thousands of FIRs per year
- Multiple accused, victims, and complainants per FIR

**The central table is `CaseMaster`.** Every other table connects to it either directly or transitively. When in doubt about a join path, start from `CaseMaster`.

---

## 2. Schema Architecture

```
                        ┌─────────────────┐
                        │   CaseMaster    │  ← Central table. Every FIR is one row here.
                        │  (CaseMasterID) │
                        └────────┬────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
   ┌─────────────┐      ┌──────────────────┐   ┌─────────────────────┐
   │   Accused   │      │     Victim       │   │ ComplainantDetails  │
   │(per FIR)    │      │   (per FIR)      │   │   (per FIR)         │
   └──────┬──────┘      └──────────────────┘   └─────────────────────┘
          │
          ▼
   ┌──────────────────┐
   │ ArrestSurrender  │  ← Links back to CaseMaster AND Accused
   └──────────────────┘

          │  (also from CaseMaster)
          ▼
   ┌─────────────────────┐     ┌──────────────────┐
   │ ActSectionAssoc.    │────▶│  Act + Section   │
   └─────────────────────┘     └──────────────────┘

          │  (also from CaseMaster)
          ▼
   ┌──────────────────┐
   │ChargesheetDetails│
   └──────────────────┘

LOOKUP TABLES (referenced by CaseMaster FKs):
CaseCategory │ GravityOffence │ CrimeHead │ CrimeSubHead │ CaseStatusMaster │ Court

GEOGRAPHY (referenced throughout):
State ◀── District ◀── Unit (Police Station)

EMPLOYEES:
Employee ──▶ Unit, District, Rank, Designation
```

---

## 3. Core Tables

---

### 3.1 `CaseMaster`

**The root table. Every FIR/case is one row here.**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `CaseMasterID` | INT | **PK** | Unique identifier for each FIR/case. Use this to join to all child tables. |
| `CrimeNo` | VARCHAR | — | Structured crime number. Format: `[1-digit Category Code][4-digit District ID][4-digit Station ID][4-digit Year][5-digit Serial]`. Example: `104430006202600001` = FIR (1), District 4430, Station 006, Year 2026, Serial 00001 |
| `CaseNo` | VARCHAR | — | Shorter case number. Format: `YYYY` + 5-digit serial = last 9 digits of `CrimeNo`. Example: `202600001` |
| `CrimeRegisteredDate` | DATE | — | Date the FIR was officially registered at the police station |
| `PolicePersonID` | INT | FK → `Employee.EmployeeID` | The officer who registered/filed the FIR |
| `PoliceStationID` | INT | FK → `Unit.UnitID` | The police station where the FIR was registered |
| `CaseCategoryID` | INT | FK → `CaseCategory.CaseCategoryID` | Category: FIR, UDR, Zero FIR, PAR, etc. |
| `GravityOffenceID` | INT | FK → `GravityOffence.GravityOffenceID` | Gravity level: Heinous, Serious, Non-Heinous |
| `CrimeMajorHeadID` | INT | FK → `CrimeHead.CrimeHeadID` | Major crime classification (e.g., Crimes Against Body) |
| `CrimeMinorHeadID` | INT | FK → `CrimeSubHead.CrimeSubHeadID` | Specific crime type (e.g., Murder, Robbery, Theft) |
| `CaseStatusID` | INT | FK → `CaseStatusMaster.CaseStatusID` | Current status: Under Investigation, Charge Sheeted, Closed, etc. |
| `CourtID` | INT | FK → `Court.CourtID` | Court where the case is being heard (if applicable) |
| `IncidentFromDate` | DATETIME | — | Start date and time of the incident (when it happened, not when reported) |
| `IncidentToDate` | DATETIME | — | End date and time of the incident |
| `InfoReceivedPSDate` | DATETIME | — | When the police station received information about the incident |
| `latitude` | DECIMAL | — | GPS latitude of the incident location. Use for geospatial clustering and hotspot analysis. |
| `longitude` | DECIMAL | — | GPS longitude of the incident location. |
| `BriefFacts` | NVARCHAR(MAX) | — | Full narrative summary of the case written by the registering officer. Primary source for RAG, MO extraction, and case similarity analysis. Can be very long. |

**Key notes for query agents:**
- `IncidentFromDate` ≠ `CrimeRegisteredDate`. The incident may have happened days before the FIR was filed. Use `IncidentFromDate` for "when did the crime happen" queries and `CrimeRegisteredDate` for "when was it reported" queries.
- `latitude` and `longitude` can be NULL for older records or where GPS was unavailable. Always filter with `WHERE latitude IS NOT NULL` before geospatial operations.
- `BriefFacts` is the richest text field in the entire schema. It is the only field containing narrative context. Pass it to the LLM for MO extraction, summarisation, and case similarity.
- `CrimeMinorHeadID` is the most specific crime type. Use this for granular crime-type filtering. `CrimeMajorHeadID` is broader grouping.

---

### 3.2 `ChargesheetDetails`

**One chargesheet per case. Records the final legal outcome of investigation.**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `CSID` | INT | **PK** | Unique identifier for the chargesheet record |
| `CaseMasterID` | INT | FK → `CaseMaster.CaseMasterID` | The FIR this chargesheet belongs to |
| `csdate` | DATETIME | — | Date the chargesheet was filed in court |
| `cstype` | CHAR | — | Final report type: `A` = Chargesheet (convicted), `B` = False Case, `C` = Undetected (unsolved) |
| `PolicePersonID` | INT | FK → `Employee.EmployeeID` | Officer who filed the chargesheet |

**Key notes:**
- Not all cases have a chargesheet. Only cases that reach a conclusion have a row here. Use `LEFT JOIN` when including this table.
- `cstype = 'A'` means the case was successfully chargesheeted (prosecution proceeded).
- `cstype = 'C'` means the crime went undetected / unsolved. This is important for investigative outcome analysis.
- `cstype = 'B'` means the FIR was found to be false.

---

### 3.3 `ActSectionAssociation`

**Maps which legal acts and sections are invoked for each case. One case can invoke multiple act-section combinations.**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `CaseMasterID` | INT | FK → `CaseMaster.CaseMasterID` | The FIR this act-section applies to |
| `ActID` | INT | FK → `Act.ActCode` | The legal act (e.g., IPC, NDPS Act, IT Act) |
| `SectionID` | INT | FK → `Section.SectionCode` | The specific section of the act (e.g., 302, 307, 420) |
| `ActOrderID` | INT | — | Display/print ordering of acts within the case |
| `SectionOrderID` | INT | — | Display/print ordering of sections under each act |

**Key notes:**
- This is a junction/bridge table with no single PK — the composite of `(CaseMasterID, ActID, SectionID)` is effectively unique.
- This table is the most reliable proxy for **Modus Operandi** in structured form. Cases with the same section pattern (e.g., IPC 379 + IPC 411) tend to share a similar MO.
- For MO clustering, group cases by their `ActID + SectionID` set, not individual sections.
- Always join to `Act` and `Section` tables to get human-readable descriptions.

---

## 4. Person Tables

---

### 4.1 `Accused`

**Every person accused in an FIR. One FIR can have multiple accused (A1, A2, A3…).**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `AccusedMasterID` | INT | **PK** | Unique identifier for this accused record |
| `CaseMasterID` | INT | FK → `CaseMaster.CaseMasterID` | The FIR this accused is linked to |
| `AccusedName` | VARCHAR | — | Full name of the accused as recorded in the FIR |
| `AgeYear` | INT | — | Age of the accused at time of FIR |
| `GenderID` | INT | — | Gender: `M` = Male, `F` = Female, `T` = Transgender |
| `PersonID` | VARCHAR | — | Accused sort label within this FIR: A1, A2, A3… Primary accused is A1. |

**Critical notes for agents:**
- **There is no cross-case persistent identity.** The same real person appearing in 5 FIRs will have 5 separate rows in `Accused`, each with their own `AccusedMasterID`. There is no `PersonMasterID` or national ID linking them.
- **Repeat offender detection requires fuzzy matching:** Use `AccusedName` + `AgeYear` + `GenderID` to group records that likely represent the same person. A name similarity score > 85% (token sort ratio) AND age difference ≤ 2 years AND same gender is a strong match signal.
- `PersonID = 'A1'` is the primary / principal accused. When counting "accused per case", group by `CaseMasterID`.
- `AgeYear` can be NULL in some records. Handle gracefully in queries.

---

### 4.2 `Victim`

**Every victim in an FIR. One FIR can have multiple victims.**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `VictimMasterID` | INT | **PK** | Unique identifier for this victim record |
| `CaseMasterID` | INT | FK → `CaseMaster.CaseMasterID` | The FIR this victim belongs to |
| `VictimName` | VARCHAR | — | Full name of the victim |
| `AgeYear` | INT | — | Age of the victim in years |
| `GenderID` | INT | — | Gender: `M`, `F`, `T` |
| `VictimPolice` | VARCHAR | — | `1` if the victim is a police officer, `0` otherwise |

**Key notes:**
- For demographic analysis of victims (age groups, gender distribution by crime type), always join `Victim` → `CaseMaster` → `CrimeSubHead`.
- `VictimPolice = '1'` is a special flag — crimes against police officers are a distinct analytical category.

---

### 4.3 `ComplainantDetails`

**The person who filed the complaint. Not necessarily the victim. One FIR can have multiple complainants.**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `ComplainantID` | INT | **PK** | Unique identifier for this complainant record |
| `CaseMasterID` | INT | FK → `CaseMaster.CaseMasterID` | The FIR this complainant filed |
| `ComplainantName` | VARCHAR | — | Full name of the complainant |
| `AgeYear` | INT | — | Age of the complainant |
| `OccupationID` | INT | FK → `OccupationMaster.OccupationID` | Occupation of the complainant |
| `ReligionID` | INT | FK → `ReligionMaster.ReligionID` | Religion of the complainant |
| `CasteID` | INT | FK → `CasteMaster.caste_master_id` | Caste of the complainant |
| `GenderID` | INT | — | Gender of the complainant |

**Key notes:**
- `ComplainantDetails` is the primary source of **socio-demographic data** for sociological crime analysis. It contains occupation, religion, and caste — the richest demographic fields in the schema.
- These fields are sensitive. Access should be restricted to Analyst and above roles.
- The complainant and the victim are often different people (e.g., a family member files a complaint for a murder victim).
- For socioeconomic analysis, join `ComplainantDetails` → `OccupationMaster` → `CaseMaster` → `CrimeSubHead`.

---

### 4.4 `ArrestSurrender`

**Records each arrest or voluntary surrender event linked to a case and accused.**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `ArrestSurrenderID` | INT | **PK** | Unique identifier for this arrest/surrender event |
| `CaseMasterID` | INT | FK → `CaseMaster.CaseMasterID` | The FIR this arrest is linked to |
| `ArrestSurrenderTypeID` | INT | — | Type: arrest or voluntary surrender (lookup value) |
| `ArrestSurrenderDate` | DATE | — | Date of the arrest or surrender |
| `ArrestSurrenderStateId` | INT | FK → `State.StateID` | State where arrest/surrender occurred |
| `ArrestSurrenderDistrictId` | INT | FK → `District.DistrictID` | District where arrest/surrender occurred |
| `PoliceStationID` | INT | FK → `Unit.UnitID` | Police station handling the arrest |
| `IOID` | INT | FK → `Employee.EmployeeID` | Investigating Officer who made the arrest |
| `CourtID` | INT | FK → `Court.CourtID` | Court before which the accused was produced |
| `AccusedMasterID` | INT | FK → `Accused.AccusedMasterID` | The accused person arrested |
| `IsAccused` | BIT | — | `1` = this person is the primary accused in the case |
| `IsComplainantAccused` | BIT | — | `1` = the complainant is also the accused (rare edge case) |

**Key notes:**
- An accused person with NO matching row in `ArrestSurrender` for their `AccusedMasterID` is **still at large / absconding**. This is a key signal for offender risk scoring.
- The arrest district (`ArrestSurrenderDistrictId`) may differ from the FIR district (`Unit.DistrictID` via `CaseMaster.PoliceStationID`). This reveals cross-district criminal movement.
- `IOID` (Investigating Officer ID) lets you track which officers are making the most arrests — useful for workload and performance analytics.

---

## 5. Legal Classification Tables

---

### 5.1 `Act`

**The legal acts under which charges are framed (e.g., Indian Penal Code, NDPS Act).**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `ActCode` | VARCHAR | **PK** | Unique code for the act (e.g., `IPC`, `NDPS`, `IT`) |
| `ActDescription` | VARCHAR | — | Full official name of the act |
| `ShortName` | VARCHAR | — | Common abbreviated name |
| `Active` | BIT | — | `1` = currently active and usable |

---

### 5.2 `Section`

**Individual sections within a legal act (e.g., IPC Section 302 = Murder).**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `ActCode` | VARCHAR | FK → `Act.ActCode` | Parent act this section belongs to |
| `SectionCode` | VARCHAR | — | Section number (e.g., `302`, `307`, `379`, `420`) |
| `SectionDescription` | VARCHAR | — | Full description of what this section covers |
| `Active` | BIT | — | `1` = currently active |

**Key notes:**
- The composite `(ActCode, SectionCode)` is the effective identifier for a specific legal charge.
- Common section patterns are a reliable MO proxy. Example: IPC 379 (theft) + IPC 411 (receiving stolen property) together suggest organised property crime.

---

### 5.3 `CrimeHead`

**Major crime head / group classification.**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `CrimeHeadID` | INT | **PK** | Unique identifier |
| `CrimeGroupName` | VARCHAR | — | Name of the major crime group (e.g., "Crimes Against Body", "Crimes Against Property", "Cyber Crimes") |
| `Active` | BIT | — | `1` = active |

---

### 5.4 `CrimeSubHead`

**Specific crime type within a major head (the most granular crime classification).**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `CrimeSubHeadID` | INT | **PK** | Unique identifier |
| `CrimeHeadID` | INT | FK → `CrimeHead.CrimeHeadID` | Parent major crime head |
| `CrimeHeadName` | VARCHAR | — | Name of this specific crime (e.g., "Murder", "Robbery", "Chain Snatching", "Vehicle Theft") |
| `SeqID` | INT | — | Display sort order |

**Key notes:**
- `CrimeSubHead` is referenced by `CaseMaster.CrimeMinorHeadID`. This is the most specific crime type available and should be used for granular crime-type queries.
- For broad crime category queries, join to `CrimeHead` via `CrimeSubHead.CrimeHeadID`.

---

### 5.5 `CrimeHeadActSection`

**Maps crime heads to their associated acts and sections. A reference/classification table.**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `CrimeHeadID` | INT | FK → `CrimeHead.CrimeHeadID` | Crime head this mapping belongs to |
| `ActCode` | VARCHAR | FK → `Act.ActCode` | The legal act |
| `SectionCode` | VARCHAR | — | The section within the act |

**Key notes:**
- This is a reference table for understanding which legal sections correspond to which crime types. Use it for cross-referencing, not for per-case queries (use `ActSectionAssociation` for per-case data).

---

## 6. Geography & Organisational Tables

---

### 6.1 `State`

| Column Name | Type | Key | Description |
|---|---|---|---|
| `StateID` | INT | **PK** | Unique identifier |
| `StateName` | VARCHAR | — | State name (e.g., "Karnataka") |
| `NationalityID` | INT | — | Nationality reference |
| `Active` | BIT | — | `1` = active |

---

### 6.2 `District`

| Column Name | Type | Key | Description |
|---|---|---|---|
| `DistrictID` | INT | **PK** | Unique identifier. Referenced throughout the schema. |
| `DistrictName` | VARCHAR | — | Name of the district (e.g., "Bengaluru Urban", "Mysuru", "Dakshina Kannada") |
| `StateID` | INT | FK → `State.StateID` | State this district belongs to |
| `Active` | BIT | — | `1` = active |

---

### 6.3 `Unit`

**A police station or administrative unit. This is what `CaseMaster.PoliceStationID` points to.**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `UnitID` | INT | **PK** | Unique identifier for the unit/police station |
| `UnitName` | VARCHAR | — | Name of the police station or unit |
| `TypeID` | INT | FK → `UnitType.UnitTypeID` | Type of unit (Police Station, Circle Office, District HQ, etc.) |
| `ParentUnit` | INT | — | Self-reference to `UnitID` — parent unit in the hierarchy |
| `NationalityID` | INT | — | Nationality reference |
| `StateID` | INT | FK → `State.StateID` | State the unit belongs to |
| `DistrictID` | INT | FK → `District.DistrictID` | District the unit belongs to |
| `Active` | BIT | — | `1` = active |

**Key notes:**
- `Unit` is the police station. To find all FIRs in a district: `CaseMaster JOIN Unit ON CaseMaster.PoliceStationID = Unit.UnitID WHERE Unit.DistrictID = ?`
- `ParentUnit` enables hierarchical queries — a Circle Office oversees multiple Police Stations, a District HQ oversees Circle Offices.
- Most analytical queries will filter by `Unit.DistrictID` to scope to a specific district.

---

### 6.4 `UnitType`

| Column Name | Type | Key | Description |
|---|---|---|---|
| `UnitTypeID` | INT | **PK** | Unique identifier |
| `UnitTypeName` | VARCHAR | — | Type name (e.g., "Police Station", "Circle Office", "District Armed Reserve") |
| `CityDistState` | VARCHAR | — | Operational level: `City`, `District`, or `State` |
| `Hierarchy` | INT | — | Hierarchy level number — lower number = higher authority |
| `Active` | BIT | — | `1` = active |

---

### 6.5 `Court`

| Column Name | Type | Key | Description |
|---|---|---|---|
| `CourtID` | INT | **PK** | Unique identifier |
| `CourtName` | VARCHAR | — | Full name of the court |
| `DistrictID` | INT | FK → `District.DistrictID` | District where the court is located |
| `StateID` | INT | FK → `State.StateID` | State where the court is located |
| `Active` | BIT | — | `1` = active |

---

## 7. Employee Tables

---

### 7.1 `Employee`

**All police department employees — from constables to IPS officers.**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `EmployeeID` | INT | **PK** | Unique identifier. Referenced by `CaseMaster.PolicePersonID` and `ArrestSurrender.IOID` |
| `DistrictID` | INT | FK → `District.DistrictID` | District where currently posted |
| `UnitID` | INT | FK → `Unit.UnitID` | Unit/police station assigned to |
| `RankID` | INT | FK → `Rank.RankID` | Current rank |
| `DesignationID` | INT | FK → `Designation.DesignationID` | Current designation |
| `KGID` | VARCHAR | — | Karnataka Government ID — unique employee number in government records |
| `FirstName` | VARCHAR | — | First name of the employee |
| `EmployeeDOB` | DATE | — | Date of birth |
| `GenderID` | INT | — | Gender |
| `BloodGroupID` | INT | — | Blood group |
| `PhysicallyChallenged` | BIT | — | `1` = physically challenged |
| `AppointmentDate` | DATE | — | Date of appointment to government service |

---

### 7.2 `Rank`

| Column Name | Type | Key | Description |
|---|---|---|---|
| `RankID` | INT | **PK** | Unique identifier |
| `RankName` | VARCHAR | — | Rank name (e.g., "Constable", "Head Constable", "ASI", "SI", "Inspector", "DSP", "SP", "IGP", "DGP") |
| `Hierarchy` | INT | — | Rank hierarchy — **lower number = higher rank** |
| `Active` | BIT | — | `1` = active |

---

### 7.3 `Designation`

| Column Name | Type | Key | Description |
|---|---|---|---|
| `DesignationID` | INT | **PK** | Unique identifier |
| `DesignationName` | VARCHAR | — | Designation name (e.g., "Investigating Officer", "SHO", "Station Writer") |
| `Active` | BIT | — | `1` = active |
| `SortOrder` | INT | — | Display sort order |

---

## 8. Lookup / Reference Tables

These are small, stable tables that store enumerated values referenced by FK columns in larger tables.

---

### 8.1 `CaseCategory`

Referenced by `CaseMaster.CaseCategoryID`

| Column Name | Type | Key | Description |
|---|---|---|---|
| `CaseCategoryID` | INT | **PK** | Unique identifier |
| `LookupValue` | VARCHAR | — | Category name: `FIR`, `UDR` (Unnatural Death Report), `PAR` (Preliminary Arrest Report), `Zero FIR` |

**CrimeNo first digit encodes this:** `1` = FIR, `3` = UDR, `4` = PAR, `8` = Zero FIR.

---

### 8.2 `GravityOffence`

Referenced by `CaseMaster.GravityOffenceID`

| Column Name | Type | Key | Description |
|---|---|---|---|
| `GravityOffenceID` | INT | **PK** | Unique identifier |
| `LookupValue` | VARCHAR | — | Gravity description: `Heinous`, `Serious`, `Non-Heinous` |

**Used in risk scoring:** Heinous = highest weight, Non-Heinous = lowest weight.

---

### 8.3 `CaseStatusMaster`

Referenced by `CaseMaster.CaseStatusID`

| Column Name | Type | Key | Description |
|---|---|---|---|
| `CaseStatusID` | INT | **PK** | Unique identifier |
| `CaseStatusName` | VARCHAR | — | Status name: `Under Investigation`, `Charge Sheeted`, `Closed`, `Referred to Court`, `Stayed` |

---

### 8.4 `OccupationMaster`

Referenced by `ComplainantDetails.OccupationID`

| Column Name | Type | Key | Description |
|---|---|---|---|
| `OccupationID` | INT | **PK** | Unique identifier |
| `OccupationName` | VARCHAR | — | Occupation name (e.g., "Farmer", "Government Employee", "Business", "Student", "Daily Wage Worker") |

---

### 8.5 `ReligionMaster`

Referenced by `ComplainantDetails.ReligionID`

| Column Name | Type | Key | Description |
|---|---|---|---|
| `ReligionID` | INT | **PK** | Unique identifier |
| `ReligionName` | VARCHAR | — | Religion name (e.g., "Hindu", "Muslim", "Christian", "Jain", "Buddhist") |

---

### 8.6 `CasteMaster`

Referenced by `ComplainantDetails.CasteID`

| Column Name | Type | Key | Description |
|---|---|---|---|
| `caste_master_id` | INT | **PK** | Unique identifier. Note: lowercase column name — use exactly as written. |
| `caste_master_name` | VARCHAR | — | Caste name |

---

## 9. Derived Tables (Drishti-Added)

These tables do not exist in the original KSP schema. They are added by the Drishti platform to support analytics, alerting, and intelligence features. They are stored in the same database alongside the source tables.

---

### 9.1 `dashboard_stats`

Precomputed aggregates refreshed nightly by Cron. Eliminates expensive COUNT queries on every dashboard load.

| Column Name | Type | Description |
|---|---|---|
| `stat_id` | INT PK | Row identifier |
| `computed_at` | DATETIME | When this row was computed |
| `total_firs` | INT | Total FIR count across all stations |
| `active_cases` | INT | Cases with status = Under Investigation |
| `high_risk_offender_count` | INT | Offenders with risk_score ≥ 70 |
| `active_alert_count` | INT | Unacknowledged alerts in crime_alerts |
| `district_crime_json` | JSON | District-wise FIR counts for the map |
| `trend_sparklines_json` | JSON | Last-30-day daily counts per crime category |

---

### 9.2 `crime_alerts`

Populated by the alert detection Cron job and Catalyst Signals. Feeds the Dashboard alert feed.

| Column Name | Type | Description |
|---|---|---|
| `alert_id` | INT PK | Unique identifier |
| `created_at` | DATETIME | When this alert was generated |
| `district_id` | INT FK → `District.DistrictID` | District the alert relates to |
| `crime_sub_head_id` | INT FK → `CrimeSubHead.CrimeSubHeadID` | Crime type spiking |
| `spike_ratio` | DECIMAL | Recent rate ÷ historical baseline (e.g., 3.4 = 340% above average) |
| `severity` | VARCHAR | `HIGH` (ratio > 3.0) or `MEDIUM` (ratio 2.0–3.0) |
| `alert_message` | VARCHAR | Human-readable message: "Robbery up 340% in Bengaluru North" |
| `is_acknowledged` | BIT | `0` = active alert, `1` = acknowledged by a supervisor |

---

### 9.3 `risk_scores`

Precomputed offender risk scores. Refreshed nightly. Feeds the Offender Risk Board.

| Column Name | Type | Description |
|---|---|---|
| `risk_score_id` | INT PK | Unique identifier |
| `accused_name` | VARCHAR | Canonical name (from the most recent FIR record) |
| `accused_age` | INT | Age from most recent record |
| `gender_id` | INT | Gender |
| `fir_count` | INT | Number of FIRs this person appears in |
| `district_ids` | JSON | Array of district IDs where active |
| `crime_types` | JSON | Array of `CrimeSubHeadID` values across all FIRs |
| `is_absconding` | BIT | `1` if latest FIR has no ArrestSurrender record |
| `gravity_avg` | DECIMAL | Average gravity score across all cases |
| `risk_score` | DECIMAL | Final weighted score (0–100) |
| `mo_tag` | VARCHAR | LLM-extracted modus operandi summary |
| `computed_at` | DATETIME | Last computed timestamp |

---

### 9.4 `conversations`

Stores chat history per user for the Intelligence Chat feature.

| Column Name | Type | Description |
|---|---|---|
| `conversation_id` | INT PK | Unique identifier |
| `user_id` | VARCHAR | Catalyst Auth user identifier |
| `session_id` | VARCHAR | Groups messages into one conversation thread |
| `role` | VARCHAR | `user` or `assistant` |
| `content` | TEXT | Message text |
| `sql_generated` | TEXT | SQL query generated (if any) for this turn — for audit |
| `created_at` | DATETIME | Timestamp |

---

### 9.5 `audit_logs`

Every API request logged here for governance and traceability.

| Column Name | Type | Description |
|---|---|---|
| `log_id` | INT PK | Unique identifier |
| `user_id` | VARCHAR | Catalyst Auth user who made the request |
| `user_role` | VARCHAR | Role at time of request |
| `endpoint` | VARCHAR | API endpoint accessed |
| `query_text` | TEXT | The natural language query (for chat endpoints) |
| `tables_accessed` | VARCHAR | Comma-separated list of tables touched |
| `ip_address` | VARCHAR | Client IP |
| `created_at` | DATETIME | Timestamp |

---

## 10. Full Relationship Matrix

| Parent Table | Parent Column | Relationship | Child Table | Child Column | Notes |
|---|---|---|---|---|---|
| `CaseMaster` | `CaseMasterID` | One → Many | `Victim` | `CaseMasterID` | One FIR, multiple victims |
| `CaseMaster` | `CaseMasterID` | One → Many | `Accused` | `CaseMasterID` | One FIR, multiple accused |
| `CaseMaster` | `CaseMasterID` | One → Many | `ArrestSurrender` | `CaseMasterID` | One FIR, multiple arrests |
| `CaseMaster` | `CaseMasterID` | One → Many | `ComplainantDetails` | `CaseMasterID` | One FIR, multiple complainants |
| `CaseMaster` | `CaseMasterID` | One → Many | `ActSectionAssociation` | `CaseMasterID` | One FIR, multiple act-sections |
| `CaseMaster` | `CaseMasterID` | One → One | `ChargesheetDetails` | `CaseMasterID` | One FIR, at most one chargesheet |
| `CaseMaster` | `CaseCategoryID` | Many → One | `CaseCategory` | `CaseCategoryID` | |
| `CaseMaster` | `GravityOffenceID` | Many → One | `GravityOffence` | `GravityOffenceID` | |
| `CaseMaster` | `CrimeMajorHeadID` | Many → One | `CrimeHead` | `CrimeHeadID` | |
| `CaseMaster` | `CrimeMinorHeadID` | Many → One | `CrimeSubHead` | `CrimeSubHeadID` | |
| `CaseMaster` | `CaseStatusID` | Many → One | `CaseStatusMaster` | `CaseStatusID` | |
| `CaseMaster` | `CourtID` | Many → One | `Court` | `CourtID` | |
| `CaseMaster` | `PolicePersonID` | Many → One | `Employee` | `EmployeeID` | Registering officer |
| `CaseMaster` | `PoliceStationID` | Many → One | `Unit` | `UnitID` | Filing police station |
| `Accused` | `AccusedMasterID` | One → Many | `ArrestSurrender` | `AccusedMasterID` | One accused, multiple arrest events |
| `ArrestSurrender` | `ArrestSurrenderStateId` | Many → One | `State` | `StateID` | |
| `ArrestSurrender` | `ArrestSurrenderDistrictId` | Many → One | `District` | `DistrictID` | |
| `ArrestSurrender` | `PoliceStationID` | Many → One | `Unit` | `UnitID` | |
| `ArrestSurrender` | `IOID` | Many → One | `Employee` | `EmployeeID` | Investigating Officer |
| `ArrestSurrender` | `CourtID` | Many → One | `Court` | `CourtID` | |
| `ComplainantDetails` | `OccupationID` | Many → One | `OccupationMaster` | `OccupationID` | |
| `ComplainantDetails` | `ReligionID` | Many → One | `ReligionMaster` | `ReligionID` | |
| `ComplainantDetails` | `CasteID` | Many → One | `CasteMaster` | `caste_master_id` | Note lowercase PK column name |
| `ActSectionAssociation` | `ActID` | Many → One | `Act` | `ActCode` | |
| `ActSectionAssociation` | `SectionID` | Many → One | `Section` | `SectionCode` | |
| `CrimeSubHead` | `CrimeHeadID` | Many → One | `CrimeHead` | `CrimeHeadID` | |
| `CrimeHead` | `CrimeHeadID` | One → Many | `CrimeHeadActSection` | `CrimeHeadID` | |
| `Act` | `ActCode` | One → Many | `CrimeHeadActSection` | `ActCode` | |
| `Act` | `ActCode` | One → Many | `Section` | `ActCode` | |
| `Court` | `DistrictID` | Many → One | `District` | `DistrictID` | |
| `District` | `StateID` | Many → One | `State` | `StateID` | |
| `Unit` | `TypeID` | Many → One | `UnitType` | `UnitTypeID` | |
| `Unit` | `StateID` | Many → One | `State` | `StateID` | |
| `Unit` | `DistrictID` | Many → One | `District` | `DistrictID` | |
| `Employee` | `DistrictID` | Many → One | `District` | `DistrictID` | |
| `Employee` | `UnitID` | Many → One | `Unit` | `UnitID` | |
| `Employee` | `RankID` | Many → One | `Rank` | `RankID` | |
| `Employee` | `DesignationID` | Many → One | `Designation` | `DesignationID` | |

---

## 11. Entity Relationship Summary

```
State (1) ──────────────────── (many) District
District (1) ───────────────── (many) Unit (Police Station)
District (1) ───────────────── (many) Court
District (1) ───────────────── (many) Employee

Unit (1) ───────────────────── (many) CaseMaster         [via PoliceStationID]
Unit (1) ───────────────────── (many) Employee            [via UnitID]
UnitType (1) ───────────────── (many) Unit                [via TypeID]

CaseMaster (1) ─────────────── (many) Accused
CaseMaster (1) ─────────────── (many) Victim
CaseMaster (1) ─────────────── (many) ComplainantDetails
CaseMaster (1) ─────────────── (many) ActSectionAssociation
CaseMaster (1) ─────────────── (many) ArrestSurrender
CaseMaster (1) ─────────────── (1)    ChargesheetDetails  [LEFT JOIN — not all cases]

Accused (1) ────────────────── (many) ArrestSurrender     [via AccusedMasterID]

ActSectionAssociation (many) ── (1)   Act
ActSectionAssociation (many) ── (1)   Section
Act (1) ────────────────────── (many) Section
Act (1) ────────────────────── (many) CrimeHeadActSection
CrimeHead (1) ──────────────── (many) CrimeSubHead
CrimeHead (1) ──────────────── (many) CrimeHeadActSection

Employee (1) ───────────────── (many) CaseMaster          [via PolicePersonID — registering]
Employee (1) ───────────────── (many) ArrestSurrender      [via IOID — investigating]
Employee (1) ───────────────── (many) ChargesheetDetails   [via PolicePersonID]

Rank (1) ───────────────────── (many) Employee
Designation (1) ────────────── (many) Employee
CaseCategory (1) ───────────── (many) CaseMaster
GravityOffence (1) ─────────── (many) CaseMaster
CrimeSubHead (1) ───────────── (many) CaseMaster           [via CrimeMinorHeadID]
CrimeHead (1) ──────────────── (many) CaseMaster           [via CrimeMajorHeadID]
CaseStatusMaster (1) ───────── (many) CaseMaster
Court (1) ──────────────────── (many) CaseMaster
Court (1) ──────────────────── (many) ArrestSurrender

ComplainantDetails (many) ───── (1)   OccupationMaster
ComplainantDetails (many) ───── (1)   ReligionMaster
ComplainantDetails (many) ───── (1)   CasteMaster
```

---

## 12. Query Patterns & Examples

### Pattern 1: FIRs in a specific district
```sql
SELECT cm.CaseMasterID, cm.CrimeNo, cm.IncidentFromDate, 
       cs.CrimeHeadName AS crime_type,
       csm.CaseStatusName AS status
FROM CaseMaster cm
JOIN Unit u ON cm.PoliceStationID = u.UnitID
JOIN District d ON u.DistrictID = d.DistrictID
JOIN CrimeSubHead cs ON cm.CrimeMinorHeadID = cs.CrimeSubHeadID
JOIN CaseStatusMaster csm ON cm.CaseStatusID = csm.CaseStatusID
WHERE d.DistrictName = 'Bengaluru Urban'
  AND cm.IncidentFromDate >= '2024-01-01'
ORDER BY cm.IncidentFromDate DESC;
```

---

### Pattern 2: All accused in a case
```sql
SELECT a.AccusedMasterID, a.AccusedName, a.AgeYear, a.GenderID, 
       a.PersonID,
       CASE WHEN ar.ArrestSurrenderID IS NOT NULL 
            THEN 'Arrested' ELSE 'Absconding' END AS arrest_status
FROM Accused a
LEFT JOIN ArrestSurrender ar ON a.AccusedMasterID = ar.AccusedMasterID
WHERE a.CaseMasterID = 1001
ORDER BY a.PersonID;
```

---

### Pattern 3: Repeat offender detection (fuzzy match proxy — exact name + age)
```sql
-- Find all cases for a specific accused by name and approximate age
SELECT a.AccusedName, a.AgeYear, a.CaseMasterID,
       cm.IncidentFromDate, cs.CrimeHeadName,
       d.DistrictName
FROM Accused a
JOIN CaseMaster cm ON a.CaseMasterID = cm.CaseMasterID
JOIN CrimeSubHead cs ON cm.CrimeMinorHeadID = cs.CrimeSubHeadID
JOIN Unit u ON cm.PoliceStationID = u.UnitID
JOIN District d ON u.DistrictID = d.DistrictID
WHERE a.AccusedName LIKE '%Rauf%'
  AND a.AgeYear BETWEEN 28 AND 32
ORDER BY cm.IncidentFromDate;
```

---

### Pattern 4: Co-accused network (same FIR)
```sql
-- Find all accused who appeared in the same FIR as a given accused
SELECT a2.AccusedName, a2.AgeYear, a2.GenderID,
       a1.CaseMasterID,
       cm.IncidentFromDate,
       cs.CrimeHeadName
FROM Accused a1
JOIN Accused a2 ON a1.CaseMasterID = a2.CaseMasterID
              AND a1.AccusedMasterID != a2.AccusedMasterID
JOIN CaseMaster cm ON a1.CaseMasterID = cm.CaseMasterID
JOIN CrimeSubHead cs ON cm.CrimeMinorHeadID = cs.CrimeSubHeadID
WHERE a1.AccusedName LIKE '%Rauf%'
ORDER BY cm.IncidentFromDate;
```

---

### Pattern 5: Crime hotspot data (for DBSCAN input)
```sql
SELECT cm.CaseMasterID, cm.latitude, cm.longitude,
       cm.IncidentFromDate,
       cs.CrimeHeadName AS crime_type,
       d.DistrictName
FROM CaseMaster cm
JOIN CrimeSubHead cs ON cm.CrimeMinorHeadID = cs.CrimeSubHeadID
JOIN Unit u ON cm.PoliceStationID = u.UnitID
JOIN District d ON u.DistrictID = d.DistrictID
WHERE cm.latitude IS NOT NULL
  AND cm.longitude IS NOT NULL
  AND cm.IncidentFromDate >= '2024-01-01'
ORDER BY cm.IncidentFromDate;
```

---

### Pattern 6: Crime trend over time (monthly)
```sql
SELECT DATE_TRUNC('month', cm.IncidentFromDate) AS month,
       cs.CrimeHeadName AS crime_type,
       COUNT(*) AS incident_count
FROM CaseMaster cm
JOIN CrimeSubHead cs ON cm.CrimeMinorHeadID = cs.CrimeSubHeadID
JOIN Unit u ON cm.PoliceStationID = u.UnitID
WHERE u.DistrictID = 5
  AND cm.IncidentFromDate >= '2022-01-01'
GROUP BY month, cs.CrimeHeadName
ORDER BY month, cs.CrimeHeadName;
```

---

### Pattern 7: Victim demographics by crime type
```sql
SELECT cs.CrimeHeadName AS crime_type,
       v.GenderID,
       CASE 
         WHEN v.AgeYear < 18 THEN 'Minor'
         WHEN v.AgeYear BETWEEN 18 AND 35 THEN '18-35'
         WHEN v.AgeYear BETWEEN 36 AND 60 THEN '36-60'
         ELSE '60+' 
       END AS age_group,
       COUNT(*) AS victim_count
FROM Victim v
JOIN CaseMaster cm ON v.CaseMasterID = cm.CaseMasterID
JOIN CrimeSubHead cs ON cm.CrimeMinorHeadID = cs.CrimeSubHeadID
GROUP BY cs.CrimeHeadName, v.GenderID, age_group
ORDER BY victim_count DESC;
```

---

### Pattern 8: Case outcome analysis by crime type
```sql
SELECT cs.CrimeHeadName AS crime_type,
       cd.cstype,
       CASE cd.cstype 
         WHEN 'A' THEN 'Chargesheeted'
         WHEN 'B' THEN 'False Case'
         WHEN 'C' THEN 'Undetected'
       END AS outcome,
       COUNT(*) AS case_count
FROM ChargesheetDetails cd
JOIN CaseMaster cm ON cd.CaseMasterID = cm.CaseMasterID
JOIN CrimeSubHead cs ON cm.CrimeMinorHeadID = cs.CrimeSubHeadID
GROUP BY cs.CrimeHeadName, cd.cstype
ORDER BY cs.CrimeHeadName, cd.cstype;
```

---

### Pattern 9: Offender risk scoring inputs
```sql
SELECT 
    a.AccusedName,
    a.AgeYear,
    a.GenderID,
    COUNT(DISTINCT a.CaseMasterID) AS fir_count,
    AVG(CASE go.LookupValue 
          WHEN 'Heinous' THEN 10 
          WHEN 'Serious' THEN 7 
          ELSE 3 END) AS avg_gravity_score,
    COUNT(ar.ArrestSurrenderID) AS arrest_count,
    MAX(cm.IncidentFromDate) AS last_seen_date
FROM Accused a
JOIN CaseMaster cm ON a.CaseMasterID = cm.CaseMasterID
JOIN GravityOffence go ON cm.GravityOffenceID = go.GravityOffenceID
LEFT JOIN ArrestSurrender ar ON a.AccusedMasterID = ar.AccusedMasterID
GROUP BY a.AccusedName, a.AgeYear, a.GenderID
HAVING COUNT(DISTINCT a.CaseMasterID) >= 2  -- only repeat offenders
ORDER BY fir_count DESC, avg_gravity_score DESC;
```

---

### Pattern 10: Full case detail (single FIR)
```sql
SELECT 
    cm.CaseMasterID, cm.CrimeNo, cm.CrimeRegisteredDate,
    cm.IncidentFromDate, cm.IncidentToDate,
    cm.latitude, cm.longitude,
    cm.BriefFacts,
    cat.LookupValue AS case_category,
    go.LookupValue AS gravity,
    ch.CrimeGroupName AS major_crime_head,
    cs.CrimeHeadName AS minor_crime_head,
    status.CaseStatusName AS case_status,
    u.UnitName AS police_station,
    d.DistrictName AS district,
    e.FirstName AS registering_officer
FROM CaseMaster cm
JOIN CaseCategory cat ON cm.CaseCategoryID = cat.CaseCategoryID
JOIN GravityOffence go ON cm.GravityOffenceID = go.GravityOffenceID
JOIN CrimeHead ch ON cm.CrimeMajorHeadID = ch.CrimeHeadID
JOIN CrimeSubHead cs ON cm.CrimeMinorHeadID = cs.CrimeSubHeadID
JOIN CaseStatusMaster status ON cm.CaseStatusID = status.CaseStatusID
JOIN Unit u ON cm.PoliceStationID = u.UnitID
JOIN District d ON u.DistrictID = d.DistrictID
JOIN Employee e ON cm.PolicePersonID = e.EmployeeID
WHERE cm.CaseMasterID = 1001;
```

---

## 13. Critical Rules for Query Generation

**Read these before generating any SQL against this schema.**

---

**Rule 1: Always start joins from CaseMaster**
`CaseMaster` is the hub. To get from `Accused` to `District`, the path is:
`Accused → CaseMaster → Unit → District`
Never try to shortcut this.

---

**Rule 2: Geography path is always Unit → District → State**
To filter FIRs by district:
```sql
JOIN Unit u ON cm.PoliceStationID = u.UnitID
JOIN District d ON u.DistrictID = d.DistrictID
WHERE d.DistrictName = 'Mysuru'
```
There is no direct `DistrictID` on `CaseMaster`. Always go through `Unit`.

---

**Rule 3: Use LEFT JOIN for ChargesheetDetails**
Not every case has a chargesheet. `INNER JOIN` on `ChargesheetDetails` will silently drop all unresolved/open cases from your results. Always use `LEFT JOIN`.

```sql
-- WRONG — drops all open cases
JOIN ChargesheetDetails cd ON cm.CaseMasterID = cd.CaseMasterID

-- CORRECT
LEFT JOIN ChargesheetDetails cd ON cm.CaseMasterID = cd.CaseMasterID
```

---

**Rule 4: Use LEFT JOIN for ArrestSurrender when checking absconding status**
An accused with no ArrestSurrender record is absconding. You need `LEFT JOIN` to detect this.
```sql
LEFT JOIN ArrestSurrender ar ON a.AccusedMasterID = ar.AccusedMasterID
-- Then: WHERE ar.ArrestSurrenderID IS NULL means absconding
```

---

**Rule 5: IncidentFromDate ≠ CrimeRegisteredDate**
- `IncidentFromDate` = when the crime happened
- `CrimeRegisteredDate` = when the FIR was filed (can be days later)
- For "crimes that happened last month" → use `IncidentFromDate`
- For "FIRs registered last month" → use `CrimeRegisteredDate`

---

**Rule 6: CrimeMinorHeadID is the specific crime type**
`CaseMaster.CrimeMinorHeadID` → `CrimeSubHead.CrimeSubHeadID` is the most granular crime classification. For broad category queries, join further to `CrimeHead` via `CrimeSubHead.CrimeHeadID`. Most crime-type queries should filter on `CrimeSubHead`.

---

**Rule 7: Accused has no cross-case identity**
The `Accused` table has one row per accused per FIR. The same physical person in 3 FIRs = 3 rows with different `AccusedMasterID` values. Cross-case identity requires application-level fuzzy matching, not a DB join. Never assume two accused rows represent different people just because `AccusedMasterID` is different.

---

**Rule 8: latitude/longitude can be NULL — always filter**
```sql
WHERE cm.latitude IS NOT NULL AND cm.longitude IS NOT NULL
```
Any geospatial query must include this filter or risk passing NULLs to clustering algorithms.

---

**Rule 9: CasteMaster uses lowercase column name**
The PK is `caste_master_id` (all lowercase), not `CasteMasterID`. The FK in `ComplainantDetails` is `CasteID`. This is an inconsistency in the original schema.
```sql
JOIN CasteMaster cm2 ON cd.CasteID = cm2.caste_master_id  -- correct
```

---

**Rule 10: SELECT only, never mutate**
The Text-to-SQL agent must generate `SELECT` statements only. Never `INSERT`, `UPDATE`, `DELETE`, or `DROP`. Validate all generated SQL with a whitelist check before execution. If generated SQL contains any non-SELECT keyword at the statement level, reject it.

---

**Rule 11: Always include LIMIT on unbounded queries**
Raw queries without filters can return thousands of rows. Default to `LIMIT 100` unless the query is an aggregation. For analytical queries (GROUP BY, COUNT, etc.), no limit is needed since the result set is already aggregated.

---

**Rule 12: Sensitive fields — role-gated**
The following fields must only appear in query results for users with `Analyst` or higher role:
- `ComplainantDetails.ReligionID` / `ReligionMaster.ReligionName`
- `ComplainantDetails.CasteID` / `CasteMaster.caste_master_name`

The Text-to-SQL agent must check the user's role before including these columns in generated SQL.

---

*Document version: 1.0 | Maintained by PRISM TEAM | Last updated: 2 July 2026*