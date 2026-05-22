/**
 * Utility functions for parsing and safely formatting raw data fields
 * incoming from backend CSV structures.
 */

export const formatCurrency = (value: string | number | undefined | null): string => {
  if (value === undefined || value === null) return "0";
  const cleaned = Number(String(value).replace(/[^0-9.-]/g, ""));
  return isNaN(cleaned) ? "0" : cleaned.toLocaleString();
};

export const formatIncomeK = (value: string | number | undefined | null): string => {
  if (value === undefined || value === null) return "—";
  const cleaned = Number(String(value).replace(/[^0-9.-]/g, ""));
  return isNaN(cleaned) || cleaned === 0 ? "—" : `${Math.round(cleaned / 1000)}k`;
};

export const formatFloatString = (value: string | number | undefined | null, decimals = 3): string => {
  const parsed = Number(value);
  return isNaN(parsed) ? (0).toFixed(decimals) : parsed.toFixed(decimals);
};

export const cleanComplianceRisk = (probability: string | number | undefined | null): number => {
  const parsed = Number(probability);
  return probability === undefined || probability === null || isNaN(parsed) ? 1.0 : 1 - parsed;
};