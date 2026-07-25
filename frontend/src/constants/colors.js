/**
 * PRISM Design System
 * Premium Enterprise Dashboard Theme
 *
 * Style:
 * - Obsidian Background
 * - Graphite Surfaces
 * - Copper Brand Accent
 * - Gold Secondary Accent
 */

const COLORS = {
  // ─────────────────────────────────────────────
  // Backgrounds
  // ─────────────────────────────────────────────
  background: {
    dark: "#09090B",
    obsidian: "#fff",
    page: "#000",
    darkAlt: "#000",
    canvas: "#070708",
  },

  // ─────────────────────────────────────────────
  // Surfaces
  // ─────────────────────────────────────────────
  surface: {
    panel: "#111214",
    panelRaised: "#181A1E",

    container: "#1B1D21",
    containerLow: "#15171A",
    containerHigh: "#23262B",
    containerHighest: "#2B2F35",

    card: "#1B1D21",
    hover: "#23262B",

    sidebar: "#111214",
  },

  // ─────────────────────────────────────────────
  // Brand
  // ─────────────────────────────────────────────
  primary: {
    main: "#C8743A",
    hover: "#DA8B54",

    fixed: "#C8743A",

    light: "#F5D2BC",
    lightText: "#FFF4ED",

    copper: "#C8743A",
    copperDark: "#9F592B",

    container: "#3A2417",
  },

  // ─────────────────────────────────────────────
  // Accent
  // ─────────────────────────────────────────────
  accent: {
    gold: "#D8B36A",
    bronze: "#B98746",

    olive: "#7C8B53",
    forest: "#537A5A",

    plum: "#695C88",
    terracotta: "#B25B45",
  },

  // ─────────────────────────────────────────────
  // Status
  // ─────────────────────────────────────────────
  status: {
    success: "#38B46A",
    greenMint: "#7ED8A4",
    greenMuted: "#1F4D35",

    warning: "#D99A2B",
    amber: "#E4B64D",
    yellowLight: "#F6E3B4",

    error: "#D94F4F",
    errorSoft: "#E06A6A",
    errorLight: "#F2A0A0",
    errorMuted: "#512121",

    coral: "#CC5F4A",
    pink: "#C56A78",
  },

  // ─────────────────────────────────────────────
  // Typography
  // ─────────────────────────────────────────────
  text: {
    heading: "#FFFFFF",

    primary: "#ECECEC",
    secondary: "#B5B7BC",

    muted: "#90949B",
    slate: "#757982",

    dim: "#5F636B",
    dark: "#474B52",

    ghost: "#34373D",

    white: "#FFFFFF",

    onAccent: "#09090B",
  },

  // ─────────────────────────────────────────────
  // Borders
  // ─────────────────────────────────────────────
  border: {
    default: "#2A2D33",
    variant: "#22252A",

    tactical: "#C8743A",

    line: "#2A2D33",

    scrollbarThumb: "#454A52",

    light: "rgba(255,255,255,0.08)",
  },

  // ─────────────────────────────────────────────
  // Graph Colors
  // ─────────────────────────────────────────────
  graph: {
    nodeAccused: "#D94F4F",
    nodeAccusedBorder: "#7A2626",

    nodeCrime: "#C8743A",
    nodeCrimeBorder: "#8F4E27",

    nodeLocation: "#D8B36A",
    nodeLocationBorder: "#8E7645",

    linkDefault: "#8D939A",
    linkDark: "#555A63",

    clusters: {
      0: "#C8743A",
      1: "#D8B36A",
      2: "#38B46A",
      3: "#7C8B53",
      4: "#B25B45",
      5: "#695C88",
      6: "#8B8B8B",
      7: "#537A5A",
    },
  },
};

module.exports = { COLORS };