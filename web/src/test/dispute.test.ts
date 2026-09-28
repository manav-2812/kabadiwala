import { describe, it, expect } from 'vitest';

/**
 * Dispute logic from HandoverView.tsx (§3.2):
 * A scale discrepancy triggers a dispute alert when variance > 10.0%.
 */
function shouldTriggerVarianceDispute(weightVariancePct: number): boolean {
  return weightVariancePct > 10.0;
}

describe('Scale Variance Dispute Boundary (§3.2)', () => {
  it('does NOT trigger dispute when variance is 9.9%', () => {
    expect(shouldTriggerVarianceDispute(9.9)).toBe(false);
  });

  it('does NOT trigger dispute when variance is exactly 10.0%', () => {
    expect(shouldTriggerVarianceDispute(10.0)).toBe(false);
  });

  it('TRIGGERS dispute when variance is 10.1%', () => {
    expect(shouldTriggerVarianceDispute(10.1)).toBe(true);
  });

  it('TRIGGERS dispute when variance is 15.0%', () => {
    expect(shouldTriggerVarianceDispute(15.0)).toBe(true);
  });
});
