import { describe, it, expect } from "vitest"; // Use 'jest' if your setup runs on Jest instead
import { 
  formatCurrency, 
  formatIncomeK, 
  formatFloatString, 
  cleanComplianceRisk 
} from "../utils/formatters";

describe("Triage Utility Formatters", () => {
  
  describe("formatCurrency", () => {
    it("should format clean numeric inputs properly", () => {
      expect(formatCurrency(125000)).toBe("125,000");
      expect(formatCurrency(0)).toBe("0");
    });

    it("should strip out currency symbols and dirty string characters", () => {
      expect(formatCurrency("$80,000.00")).toBe("80,000");
      expect(formatCurrency("CA$ 5,230")).toBe("5,230");
    });

    it("should handle negative financial balances gracefully", () => {
      expect(formatCurrency("-$1,500")).toBe("-1,500");
    });

    it("should return '0' fallback for missing or completely invalid data", () => {
      expect(formatCurrency(null)).toBe("0");
      expect(formatCurrency(undefined)).toBe("0");
      expect(formatCurrency("Missing Data")).toBe("0");
    });
  });

  describe("formatIncomeK", () => {
    it("should convert exact thousands to standard 'k' abbreviations", () => {
      expect(formatIncomeK(90000)).toBe("90k");
      expect(formatIncomeK("150000")).toBe("150k");
    });

    it("should round up or down to the nearest integer index", () => {
      expect(formatIncomeK("$84,600")).toBe("85k");
      expect(formatIncomeK("112300")).toBe("112k");
    });

    it("should return an em-dash fallback for zero or completely invalid profiles", () => {
      expect(formatIncomeK(0)).toBe("—");
      expect(formatIncomeK("0")).toBe("—");
      expect(formatIncomeK(null)).toBe("—");
      expect(formatIncomeK(undefined)).toBe("—");
    });
  });

  describe("formatFloatString", () => {
    it("should safely match fixed precision constraints", () => {
      expect(formatFloatString(0.87654, 3)).toBe("0.877");
      expect(formatFloatString("0.4", 2)).toBe("0.40");
    });

    it("should default to 3 decimals when no limit argument is passed", () => {
      expect(formatFloatString(0.1234)).toBe("0.123");
    });

    it("should handle null pointer elements gracefully", () => {
      expect(formatFloatString(null)).toBe("0.000");
    });
  });

  describe("cleanComplianceRisk", () => {
    it("should invert compliance probability to resolve absolute risk score", () => {
      // Risk = 1 - Compliance Probability
      expect(cleanComplianceRisk(0.85)).toBeCloseTo(0.15);
      expect(cleanComplianceRisk("0.10")).toBeCloseTo(0.90);
    });

    it("should resolve safely if string metrics are unparsed", () => {
      expect(cleanComplianceRisk(null)).toBe(1.0);
      expect(cleanComplianceRisk("N/A")).toBe(1.0);
    });
  });
});