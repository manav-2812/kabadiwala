/**
 * Layer-1 Valuation Rules — TypeScript Twin
 * Kabadiwala Connect — SIH 2026 (PS SIH26229)
 *
 * Formula MUST stay identical to backend/app/services/valuation.py.
 * Shared golden vectors: ml/golden/valuation_golden.json
 * Tolerance: ±1 paise (integer rounding).
 *
 * Used offline (no network) with last-synced price board.
 */

export interface ValuationBasis {
  layer: 'rules' | 'model';
  nRecentSales: number;
  scope: 'city' | 'national';
  asOf: string;
  text: string;
  gateMet: boolean;
}

export interface ValuationResult {
  minPaise: number;
  p50Paise: number;
  maxPaise: number;
  conditionFactor: number;
  basis: ValuationBasis;
  demoOnly: boolean;
}

/** Condition factors — MUST match CONDITION_FACTORS in valuation.py */
const CONDITION_FACTORS: Record<string, number> = {
  working: 1.10,
  broken: 1.00,
  burnt: 0.70,
  unknown: 0.95,
  repairable: 1.05,
  scrap: 1.00,
};

function conditionFactor(condition: string): number {
  return CONDITION_FACTORS[condition.toLowerCase().trim()] ?? 0.95;
}

/**
 * Pure deterministic Layer-1 rule computation.
 * No I/O — safe to call from tests with golden vectors.
 */
export function computeRulesValuation(
  basePaisePerKg: number,
  weightG: number,
  condition: string,
): { minPaise: number; p50Paise: number; maxPaise: number; conditionFactor: number } {
  const weightKg = weightG / 1000;
  const factor = conditionFactor(condition);
  const p50 = Math.round(basePaisePerKg * weightKg * factor);
  const min = Math.round(p50 * 0.90);
  const max = Math.round(p50 * 1.10);
  return { minPaise: min, p50Paise: p50, maxPaise: max, conditionFactor: factor };
}

export interface PriceBoardEntry {
  materialCode: string;
  basePaisePerKg: number;
  updatedAt: string;
}

/**
 * Full valuation with basis metadata.
 * Uses cached price board (synced from /prices/summary).
 * Fully offline-capable.
 */
export function valuateItem(params: {
  materialCode: string;
  weightG: number;
  condition: string;
  priceBoard: PriceBoardEntry[];
  nRecentSales?: number;
  minRowsForModel?: number;
}): ValuationResult {
  const {
    materialCode,
    weightG,
    condition,
    priceBoard,
    nRecentSales = 0,
    minRowsForModel = 200,
  } = params;

  const entry = priceBoard.find((e) => e.materialCode === materialCode);
  const basePaise = entry?.basePaisePerKg ?? 5000;
  const asOf = entry?.updatedAt ?? new Date().toISOString();

  const rules = computeRulesValuation(basePaise, weightG, condition);

  const gateMet = nRecentSales >= minRowsForModel;
  const basisText =
    nRecentSales > 0
      ? `Based on ${nRecentSales} recent transaction(s) in your city`
      : "Based on today's price board (no recent local sales yet)";

  return {
    ...rules,
    basis: {
      layer: 'rules',
      nRecentSales,
      scope: 'national',
      asOf,
      text: basisText,
      gateMet,
    },
    demoOnly: true, // Layer-2 not yet active
  };
}
