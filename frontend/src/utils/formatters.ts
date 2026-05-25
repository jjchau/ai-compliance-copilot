/**
 * Utility functions for parsing and safely formatting raw data fields
 * incoming from backend CSV structures.
 */

/**
 * Formats dirty or clean numbers/strings into comma-separated currency representations.
 */
export function formatCurrency(val: any): string {
  if (val === null || val === undefined) return "0";
  // Strip characters like commas, spaces, currency symbols
  const clean = String(val).replace(/[$\s,A-Z]/gi, "");
  const num = parseFloat(clean);
  if (isNaN(num)) return "0";
  return num.toLocaleString("en-US", { maximumFractionDigits: 2 });
}

/**
 * Updated: Formats the raw client income with clean commas instead of truncating to 'K'
 */
export function formatIncomeK(val: any): string {
  if (val === null || val === undefined || val === 0 || val === "0") return "—";
  return formatCurrency(val);
}

export const formatFloatString = (value: string | number | undefined | null, decimals = 3): string => {
  const parsed = Number(value);
  return isNaN(parsed) ? (0).toFixed(decimals) : parsed.toFixed(decimals);
};

export const cleanComplianceRisk = (probability: string | number | undefined | null): number => {
  const parsed = Number(probability);
  return probability === undefined || probability === null || isNaN(parsed) ? 1.0 : 1 - parsed;
};