---
name: 'PRISM: Crime Intelligence & Analytics'
colors:
  surface: '#11131a'
  surface-dim: '#11131a'
  surface-bright: '#373941'
  surface-container-lowest: '#0c0e15'
  surface-container-low: '#191b23'
  surface-container: '#1d1f27'
  surface-container-high: '#282a31'
  surface-container-highest: '#33343c'
  on-surface: '#e1e2ec'
  on-surface-variant: '#c3c6d6'
  inverse-surface: '#e1e2ec'
  inverse-on-surface: '#2e3038'
  outline: '#8d909f'
  outline-variant: '#434654'
  surface-tint: '#b3c5ff'
  primary: '#b3c5ff'
  on-primary: '#002b75'
  primary-container: '#3b6fe8'
  on-primary-container: '#ffffff'
  inverse-primary: '#1656cf'
  secondary: '#c4c6d0'
  on-secondary: '#2d3038'
  secondary-container: '#44474f'
  on-secondary-container: '#b3b5be'
  tertiary: '#ffb68c'
  on-tertiary: '#532200'
  tertiary-container: '#bf5800'
  on-tertiary-container: '#ffffff'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b3c5ff'
  on-primary-fixed: '#001849'
  on-primary-fixed-variant: '#003fa4'
  secondary-fixed: '#e0e2ec'
  secondary-fixed-dim: '#c4c6d0'
  on-secondary-fixed: '#191c22'
  on-secondary-fixed-variant: '#44474f'
  tertiary-fixed: '#ffdbc9'
  tertiary-fixed-dim: '#ffb68c'
  on-tertiary-fixed: '#321200'
  on-tertiary-fixed-variant: '#763400'
  background: '#11131a'
  on-background: '#e1e2ec'
  surface-variant: '#33343c'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-mono:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
  data-mono-bold:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '700'
    lineHeight: 20px
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 32px
---

## Brand & Style
The design system is engineered for high-stakes law enforcement intelligence and situational awareness. It prioritizes rapid data ingestion, clarity, and institutional authority. The aesthetic is a refined version of **Modern Corporate/Technical Minimalism**—striking a balance between enterprise reliability and developer-centric precision.

The UI is intentionally flat and structured, avoiding decorative flourishes like gradients or blurs to ensure maximum performance and focus. It utilizes a strict "clinical" approach where every pixel serves a functional purpose, evoking a sense of calm under pressure for intelligence officers and analysts.

## Colors
This design system operates exclusively in a high-contrast dark mode to reduce eye strain during extended surveillance or data analysis sessions. 

- **Primary Accent:** Institutional Blue (#3B6FE8) is reserved for primary actions, active states, and critical brand identifiers.
- **Semantic Palette:** Red, Orange, and Green are used strictly for status indicators (Danger, Warning, Safe). These must never be used for decorative purposes.
- **Neutrals:** The palette uses a tiered grayscale to establish hierarchy:
  - **Base (#0A0C10):** The primary background canvas.
  - **Surface (#111318):** Secondary areas like sidebars or secondary panels.
  - **Elevated (#1A1D24):** Components that require distinct separation from the base.
  - **Border (#252830):** Structural definition for all UI elements.

## Typography
The typography strategy employs a dual-font approach to differentiate between administrative UI and technical intelligence.

- **Inter:** Used for all standard interface elements, navigation, and body text. Use Semi-Bold (600) or Bold (700) for headers to maintain high legibility against the dark background.
- **JetBrains Mono:** Used for technical data points, case IDs, coordinates, timestamps, and wordmarks. This monospaced font ensures that numerical data is perfectly aligned in tables and lists, facilitating quick scanning.

All text should prioritize legibility. Use `label-mono` for secondary metadata and `data-mono-bold` for critical reference numbers (e.g., FIR numbers, suspect IDs).

## Layout & Spacing
The layout follows a strict 4px grid system to ensure high information density without visual clutter. 

- **Grid:** A 12-column fluid grid is used for dashboard layouts, allowing for modular "widgets" to span 3, 4, 6, or 12 columns.
- **Information Density:** Use compact spacing (`sm` and `md`) for data-heavy views. Vertical rhythm is maintained through 24px increments.
- **Breakpoints:**
  - **Mobile (<768px):** Single column, 16px side margins.
  - **Tablet (768px - 1280px):** 6-column grid, persistent sidebar collapses to icons.
  - **Desktop (>1280px):** 12-column grid, 32px side margins.

## Elevation & Depth
Elevation is achieved through color-stepping and 1px borders rather than shadows. This creates a flat, "tactical" feel.

- **Flat Layering:** Use the `Border (#252830)` token to define all interactive and container boundaries. 
- **Z-Axis Hierarchy:**
  - **Level 0 (Background):** #0A0C10.
  - **Level 1 (Panels/Cards):** #111318 with 1px border.
  - **Level 2 (Popovers/Modals):** #1A1D24 with a slightly brighter 1px border (#3B6FE8 at 20% opacity).
- **Active State:** Instead of shadows, use the Primary Accent (#3B6FE8) as a 1px border or a subtle left-hand "indicator strip" to denote selection or focus.

## Shapes
Shapes in this design system are disciplined and professional. 

- **Radius:** A consistent 6px to 8px radius is applied to cards, buttons, and input fields. This is "Soft" enough to feel modern but "Sharp" enough to maintain a serious, institutional character.
- **Prohibited:** No pill-shaped buttons or fully circular elements (except for avatars/status pips). Every interactive surface should feel like a modular component within a larger machine.

## Components
- **Buttons:** Solid #3B6FE8 for primary actions. Ghost buttons with 1px #252830 borders for secondary actions. Text must be Inter Bold.
- **Input Fields:** Background #111318, 1px border #252830. On focus, the border changes to #3B6FE8. Use JetBrains Mono for inputs containing technical data.
- **Status Chips:** Rectangular with 4px radius. No background fill; use a 1px border and text in the semantic color (e.g., Red for Danger).
- **Data Tables:** High density. Use #111318 for headers and #0A0C10 for alternating rows. Borders should only be horizontal.
- **Analytics Cards:** Use `Elevated` background. Header of the card should be separated by a 1px #252830 line.
- **Navigation:** Persistent left-hand rail using icons with 14px Inter Medium labels. Active state indicated by a 2px vertical line in Primary Accent.