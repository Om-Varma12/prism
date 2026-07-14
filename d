# Implementation Plan

## Overview
Fix the "Map container is already initialized" error in the Analytics tab by properly managing the Leaflet MapContainer lifecycle during tab switching and conditional rendering.

## Problem Analysis
The error occurs in `frontend/src/pages/Analytics/HotspotMap.tsx` because:
1. The `MapContainer` component is conditionally rendered based on `hotspotsLoading` state
2. The `key="hotspot-map"` is static and doesn't change when the map is re-mounted
3. When switching tabs in `AnalyticsPage` (index.tsx), the `HotspotMap` component unmounts and remounts
4. Leaflet's internal state may not properly clean up when the map container DOM element persists, causing the "already initialized" error on re-initialization

## Types
No new types or type modifications are required for this fix.

## Files
- **Modified:** `frontend/src/pages/Analytics/HotspotMap.tsx` - Fix the MapContainer lifecycle management
- **Modified:** `frontend/src/pages/Analytics/index.tsx` - Add proper key management for tab content

## Functions
- **Modified:** `HotspotMap` component in `HotspotMap.tsx` - Add proper map cleanup and key management
- **Modified:** `AnalyticsPage` component in `index.tsx` - Ensure proper component unmounting

## Classes
No class modifications required.

## Dependencies
No new dependencies required. The fix uses existing react-leaflet APIs.

## Testing
- Test by switching between tabs in the Analytics page
- Test by refreshing the analytics page
- Test by changing filters that trigger data re-fetching

## Implementation Order
1. Modify `HotspotMap.tsx` to use `useRef` and proper cleanup for the map container
2. Add `whenCreated` and `whenRemoved` handlers to properly manage Leaflet map instance
3. Update the `key` prop to use a dynamic value that changes when needed
4. Ensure the map container has a stable DOM reference