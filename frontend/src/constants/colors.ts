/**
 * Centralized UI Color Palette & Design Tokens for PRISM
 * Single Source of Truth for all color variables.
 */

// Import from CommonJS module for unified single source of truth across Node & TS
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { COLORS: colorsRaw } = require('./colors.js');

export interface PrismColors {
  background: {
    dark: string;
    obsidian: string;
    page: string;
    darkAlt: string;
    canvas: string;
  };
  surface: {
    panel: string;
    panelRaised: string;
    container: string;
    containerLow: string;
    containerHigh: string;
    containerHighest: string;
    card: string;
    hover: string;
  };
  primary: {
    main: string;
    hover: string;
    fixed: string;
    light: string;
    lightText: string;
    blue: string;
    blueMuted: string;
    container: string;
  };
  accent: {
    cyan: string;
    teal: string;
    tealMuted: string;
    tealBright: string;
    lime: string;
    violet: string;
  };
  status: {
    error: string;
    errorSoft: string;
    errorLight: string;
    errorMuted: string;
    errorContainer: string;
    errorBgSoft: string;
    errorText: string;
    coral: string;
    pink: string;
    warning: string;
    amber: string;
    gold: string;
    goldMuted: string;
    yellowLight: string;
    yellowText: string;
    orange: string;
    success: string;
    greenMuted: string;
    greenMint: string;
    greenBorder: string;
  };
  text: {
    primary: string;
    heading: string;
    white: string;
    secondary: string;
    muted: string;
    slate: string;
    dim: string;
    dark: string;
    ghost: string;
  };
  border: {
    default: string;
    variant: string;
    tactical: string;
    line: string;
    scrollbarThumb: string;
    light: string;
  };
  graph: {
    nodeAccused: string;
    nodeAccusedBorder: string;
    nodeCrime: string;
    nodeCrimeBorder: string;
    nodeLocation: string;
    nodeLocationBorder: string;
    linkDefault: string;
    linkDark: string;
    clusters: Record<number, string>;
  };
}

export const COLORS: PrismColors = colorsRaw;
export default COLORS;
