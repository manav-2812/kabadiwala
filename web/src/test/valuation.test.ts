import { describe, it, expect } from 'vitest';
import { computeRulesValuation } from '../features/collector/valuation';
import goldenData from '../../../ml/golden/valuation_golden.json';

describe('Layer-1 Valuation Rules (TypeScript Twin)', () => {
  it('passes all golden test vectors from ml/golden/valuation_golden.json', () => {
    const vectors = goldenData.vectors;
    expect(vectors.length).toBeGreaterThan(0);

    for (const v of vectors) {
      const { base_price_paise_per_kg, weight_g, condition } = v.input;
      const expected = v.expected;

      const result = computeRulesValuation(
        base_price_paise_per_kg,
        weight_g,
        condition
      );

      expect(Math.abs(result.minPaise - expected.min_paise)).toBeLessThanOrEqual(
        goldenData.tolerance_paise
      );
      expect(Math.abs(result.maxPaise - expected.max_paise)).toBeLessThanOrEqual(
        goldenData.tolerance_paise
      );
      expect(Math.abs(result.p50Paise - expected.p50_paise)).toBeLessThanOrEqual(
        goldenData.tolerance_paise
      );
      expect(result.conditionFactor).toBeCloseTo(expected.condition_factor, 2);
    }
  });

  it('guarantees minPaise <= p50Paise <= maxPaise', () => {
    const result = computeRulesValuation(50000, 2500, 'working');
    expect(result.minPaise).toBeLessThanOrEqual(result.p50Paise);
    expect(result.p50Paise).toBeLessThanOrEqual(result.maxPaise);
  });

  it('correctly handles zero weight', () => {
    const result = computeRulesValuation(50000, 0, 'working');
    expect(result.minPaise).toBe(0);
    expect(result.p50Paise).toBe(0);
    expect(result.maxPaise).toBe(0);
  });
});
