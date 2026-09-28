import { describe, it, expect } from 'vitest';
import { rankRecyclersForLot, RecyclerCandidate } from '../features/collector/matching';

describe('Recycler Matching Engine (TypeScript Twin §2.4)', () => {
  const baseRecyclers: RecyclerCandidate[] = [
    {
      id: 'rec-valid-1',
      companyName: 'GreenPulse Metals & E-Waste Ltd',
      lat: 28.62,
      lng: 77.21,
      authorizationStatus: 'verified',
      licenseValidTo: '2028-12-31T00:00:00Z',
      ratingAvg: 4.8,
      reliabilityScore: 95,
      pickupAvailable: true,
    },
    {
      id: 'rec-malwa-expired',
      companyName: 'Malwa Materials Recovery',
      lat: 28.60,
      lng: 77.20,
      authorizationStatus: 'verified',
      licenseValidTo: '2023-01-01T00:00:00Z', // Expired!
      ratingAvg: 4.5,
      reliabilityScore: 90,
      pickupAvailable: true,
    },
    {
      id: 'rec-pending-signup',
      companyName: 'Unverified New Recycler',
      lat: 28.61,
      lng: 77.22,
      authorizationStatus: 'pending', // §2.4: self-signup is pending by default
      licenseValidTo: '2028-12-31T00:00:00Z',
      ratingAvg: 0,
      reliabilityScore: 80,
      pickupAvailable: false,
    },
  ];

  it('excludes recyclers with authorizationStatus != verified (§2.4)', () => {
    const results = rankRecyclersForLot({
      collectorLat: 28.6139,
      collectorLng: 77.2090,
      lotEstPaise: 50000,
      recyclers: baseRecyclers,
      now: new Date('2026-01-01T00:00:00Z'),
    });

    const pendingFound = results.some((r) => r.id === 'rec-pending-signup');
    expect(pendingFound).toBe(false);
  });

  it('excludes recyclers with expired CPCB license (Malwa Materials Recovery §2.4)', () => {
    const results = rankRecyclersForLot({
      collectorLat: 28.6139,
      collectorLng: 77.2090,
      lotEstPaise: 50000,
      recyclers: baseRecyclers,
      now: new Date('2026-01-01T00:00:00Z'),
    });

    const expiredFound = results.some((r) => r.id === 'rec-malwa-expired');
    expect(expiredFound).toBe(false);
  });

  it('includes verified active recyclers and calculates ranking scores', () => {
    const results = rankRecyclersForLot({
      collectorLat: 28.6139,
      collectorLng: 77.2090,
      lotEstPaise: 50000,
      recyclers: baseRecyclers,
      now: new Date('2026-01-01T00:00:00Z'),
    });

    expect(results.length).toBe(1);
    expect(results[0].id).toBe('rec-valid-1');
    expect(results[0].distanceKm).toBeGreaterThan(0);
    expect(results[0].rankingScore).toBeGreaterThan(0);
    expect(results[0].reasons.length).toBeGreaterThan(0);
  });
});
