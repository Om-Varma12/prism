/**
 * District coordinate mapping for Karnataka map markers.
 * Keys are exact district names as stored in the database.
 * Values are SVG coordinates (cx, cy) from the map.svg viewBox.
 */

export const districtCoordinates: Record<string, { cx: number; cy: number }> = {
  // Districts from backend analytics/trends.py
  "Bengaluru Urban": { cx: 2.32, cy: 4.80 },
  "Mysuru": { cx: 2.065, cy: 5.4 },
  "Dakshina Kannada": { cx: 1.83, cy: 4.85 },
  "Belagavi": { cx: 1.77, cy: 2.26 },
  "Ballari": { cx: 2.3, cy: 3.05 }, // vijayanagara in SVG
  "Kalaburagi": { cx: 2.21, cy: 1.6 },
  "Hubballi-Dharwad": { cx: 1.1, cy: 2.78 }, // dharwad in SVG
  "Shivamogga": { cx: 1.05, cy: 3.98 }, // shimoga in SVG
  "Tumakuru": { cx: 2.5, cy: 4.6 }, // tumkur in SVG
  "Hassan": { cx: 1.8, cy: 4.93 },

  // Additional districts from SVG (for future compatibility)
  Bidar: { cx: 2.97, cy: 0.6 },
  Yadgir: { cx: 2.65, cy: 2.25 },
  Bijapur: { cx: 1.85, cy: 1.6 },
  Bagalkot: { cx: 1.55, cy: 2.1 },
  Gadag: { cx: 1.55, cy: 2.78 }, // gagad in SVG
  Koppal: { cx: 2.05, cy: 2.67 },
  "Uttara Kannada": { cx: 0.6, cy: 3.25 },
  Haveri: { cx: 1.3, cy: 3.35 },
  Udupi: { cx: 0.78, cy: 4.45 },
  Davanagere: { cx: 1.7, cy: 3.7 },
  Chikmagalur: { cx: 1.5, cy: 4.5 },
  Chitradurga: { cx: 2.2, cy: 3.95 },
  Kodagu: { cx: 1.5, cy: 5.5 },
  Mandya: { cx: 2.4, cy: 5.25 },
  Chamarajanagar: { cx: 2.6, cy: 5.85 },
  Chikkaballapura: { cx: 3.3, cy: 4.45 },
  Kolar: { cx: 3.65, cy: 4.9 },
  Bengaluru: { cx: 3.02, cy: 4.67 },
};
