# PRISM Frontend Client

The frontend of PRISM is a Single Page Application (SPA) built using React, TypeScript, and Tailwind CSS. It communicates with the FastAPI backend deployed on Catalyst AppSail and provides an interactive command center for crime intelligence mapping, predictive analytics, network graph navigation, and natural language database querying.

---

## 🛠️ Key Components & Technologies

*   **UI Framework**: React with TypeScript.
*   **Styling**: Tailwind CSS for styling layout, tokens, animations, and custom panels.
*   **Data Fetching & Caching**: `@tanstack/react-query` (React Query) for state sync, history polling, and automatic invalidation.
*   **Geospatial Maps**: Leaflet (`react-leaflet`) for rendering coordinates, markers, heatmaps, and region boundaries.
*   **Data Visualizations**: Recharts for crime timelines, temporal forecasting boundaries, and KPI indicators.
*   **Interactive Visualizations**: D3.js for force-directed criminal associate network graphs.

---

## 🧭 Page States & Address Bar Routing Sync

PRISM implements a custom page navigation and state synchronization mechanism in `App.tsx` and `hooks/useChat.ts` that links page state and chat sessions directly to the browser URL:

```
Address Bar URL: /app?page=chat&session_id=9ed95fe3-9451-4f4c-b5de-6061d200be4b
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
[App.tsx] Syncs Page State             [useChat.ts] Syncs Chat Session
- page=dashboard                       - restructures history on load
- page=chat                            - popstate handles back/forward buttons
- page=analytics                       - invalidates query caches dynamically
- page=network
```

### Back/Forward Browser Buttons
The app registers global `popstate` event listeners. When an analyst clicks the browser's Back/Forward buttons, the app automatically reflects page adjustments and restores previously opened chat session states without reloading the application.

---

## 📁 Key Screens

The main screen views are flat components stored under `src/components/`:

*   **`CommandDashboardScreen.tsx`**: Features the main KPI metrics, real-time alert feed (with acknowledgment actions), overall crime category trends, and an interactive SVG district map of Karnataka.
*   **`ChatScreen.tsx`**: Features the multi-agent conversational interface. It includes an input box with voice capability (Web Speech API), a message thread (handling markdown, markdown alerts, and suggested actions), an **SQL transparency drawer** showing generated ZCQL, and a **dynamic results table** that builds table columns on the fly from whatever data keys are returned.
*   **`AnalyticsScreen.tsx`**: Features tab routers for:
    *   *Geospatial Hotspots*: Leaflet map detailing DBSCAN density crime clusters.
    *   *Trend Analysis*: Historical charts overlaid with temporal forecasting data (Prophet).
    *   *Offender Risk Board*: Rank listings of high-risk recidivists.
*   **`NetworkExplorerScreen.tsx`**: Features the force-directed D3 network graph rendering linkages between cases, accomplices, and gangs. Clicking a node opens a slide-in profiling drawer detailing key metrics (centrality and crime involvement).
*   **`LoginScreen.tsx`**: High-fidelity authorization page displaying an atmospheric, themed landing layout.

---

## ⚙️ Local Installation & Development

### 1. Requirements
Ensure you have Node.js v18+ and npm installed.

### 2. Dependency Setup
Navigate to the `frontend` folder and install packages:
```bash
npm install
```

### 3. Environment Variables Configuration
Create a `.env` file in the `frontend` folder:
```bash
cp .env.example .env
```
> 🔑 **Required**: Open `frontend/.env` and configure `REACT_APP_CLERK_PUBLISHABLE_KEY` with your Clerk API key. Without this key, the application will fail to run with a publishable key missing error.

### 4. Running the Application
For local development, it is highly recommended to run the unified dev server from the **root directory** of the repository:
```bash
# Return to root directory
cd ..
# Start unified server
catalyst serve
```
This runs the frontend and backend together, setting up routing proxies automatically.

If you wish to run only the frontend standalone (without backend mock API gateway routing):
```bash
npm start
```
This serves the client at `http://localhost:3000`.

### 5. Production Build
To compile the production-ready build:
```bash
npm run build
```
The output will be placed in the `build/` directory, ready to be deployed to Catalyst Web Client Hosting.
