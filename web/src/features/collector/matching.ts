/**
 * Recycler Matching — TypeScript Twin (offline-capable)
 * Kabadiwala Connect — SIH 2026 (PS SIH26229)
 *
 * Formula MUST stay identical to backend/app/services/matching.py.
 * Shared golden vectors: ml/golden/matching_golden.json
 */

export type ReasonCode =
  | 'NEAREST'
  | 'HIGHEST_PAYOUT'
  | 'PICKUP_AVAILABLE'
  | 'TRUSTED'
  | 'FAST_RESPONSE';

export interface MatchingWeights {
  payout: number;
  proximity: number;
  rate: number;
  pickup: number;
  reliability: number;
  response: number;
}

export const DEFAULT_WEIGHTS: MatchingWeights = {
  payout:      0.30,
  proximity:   0.25,
  rate:        0.20,
  pickup:      0.10,
  reliability: 0.10,
  response:    0.05,
};

export interface RecyclerCandidate {
  id: string;
  companyName: string;
  lat: number;
  lng: number;
  authorizationStatus: string;
  licenseValidTo: string | null;
  ratingAvg: number;
  reliabilityScore: number;
  pickupAvailable: boolean;
}

export interface RankedRecycler extends RecyclerCandidate {
  distanceKm: number;
  estimatedPayoutPaise: number;
  rankingScore: number;
  reasons: ReasonCode[];
  weightsVersion: string;
}

function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;
  return Math.round(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)) * 100) / 100;
}

function norm(vals: number[], val: number, invert = false): number {
  const lo = Math.min(...vals);
  const hi = Math.max(...vals);
  if (hi === lo) return 1;
  const n = (val - lo) / (hi - lo);
  return invert ? 1 - n : n;
}

function deriveReasons(
  normPayout: number,
  distKm: number,
  pickupAvailable: boolean,
  normReliability: number,
  normResponse: number,
): ReasonCode[] {
  const reasons: ReasonCode[] = [];
  if (normPayout >= 0.80) reasons.push('HIGHEST_PAYOUT');
  if (distKm <= 5.0) reasons.push('NEAREST');
  if (pickupAvailable && reasons.length < 3) reasons.push('PICKUP_AVAILABLE');
  if (normReliability >= 0.90 && reasons.length < 3) reasons.push('TRUSTED');
  if (normResponse >= 0.80 && reasons.length < 3) reasons.push('FAST_RESPONSE');
  if (reasons.length === 0) reasons.push(distKm <= 10 ? 'NEAREST' : 'HIGHEST_PAYOUT');
  return reasons.slice(0, 3);
}

export function rankRecyclersForLot(params: {
  collectorLat: number;
  collectorLng: number;
  lotEstPaise: number;
  recyclers: RecyclerCandidate[];
  weights?: MatchingWeights;
  weightsVersion?: string;
  now?: Date;
}): RankedRecycler[] {
  const {
    collectorLat, collectorLng, lotEstPaise,
    recyclers, weights = DEFAULT_WEIGHTS,
    weightsVersion = 'default',
    now = new Date(),
  } = params;

  // Hard filters
  const candidates = recyclers
    .filter((r) => r.authorizationStatus === 'verified')
    .filter((r) => {
      if (!r.licenseValidTo) return true;
      return new Date(r.licenseValidTo) >= now;
    })
    .map((r) => {
      const distKm = haversineKm(collectorLat, collectorLng, r.lat, r.lng);
      const rateModifier = 1 + (r.reliabilityScore - 80) / 200;
      const estPayout = Math.round(lotEstPaise * rateModifier);
      return { ...r, distKm, estPayout, responseSpeed: r.reliabilityScore / 100 };
    });

  if (!candidates.length) return [];

  const payouts = candidates.map((c) => c.estPayout);
  const dists = candidates.map((c) => c.distKm);
  const reliabilities = candidates.map((c) => c.reliabilityScore);
  const responses = candidates.map((c) => c.responseSpeed);

  const ranked: RankedRecycler[] = candidates.map((c) => {
    const normPayout = norm(payouts, c.estPayout);
    const normProx = norm(dists, c.distKm, true);
    const normRate = normPayout;
    const pickupScore = c.pickupAvailable ? 1.0 : 0.2;
    const normRel = norm(reliabilities, c.reliabilityScore);
    const normResp = norm(responses, c.responseSpeed);

    const score =
      weights.payout * normPayout +
      weights.proximity * normProx +
      weights.rate * normRate +
      weights.pickup * pickupScore +
      weights.reliability * normRel +
      weights.response * normResp;

    const reasons = deriveReasons(normPayout, c.distKm, c.pickupAvailable, normRel, normResp);

    return {
      id: c.id,
      companyName: c.companyName,
      lat: c.lat,
      lng: c.lng,
      authorizationStatus: c.authorizationStatus,
      licenseValidTo: c.licenseValidTo,
      ratingAvg: c.ratingAvg,
      reliabilityScore: c.reliabilityScore,
      pickupAvailable: c.pickupAvailable,
      distanceKm: c.distKm,
      estimatedPayoutPaise: c.estPayout,
      rankingScore: Math.round(score * 10000) / 10000,
      reasons,
      weightsVersion,
    };
  });

  return ranked.sort((a, b) => b.rankingScore - a.rankingScore);
}
