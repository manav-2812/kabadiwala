// [SIH-2026-PS-SIH26229] Iteration 71 polish
/**
 * Draft Persistence — Process-Death Safety
 * Kabadiwala Connect — SIH 2026 (PS SIH26229)
 *
 * On low-RAM Android devices, the OS may kill the app while the camera
 * activity is open. This module persists the LotBuilder draft (step,
 * items, weights, photos) to IndexedDB after every state change and
 * before launching the camera, so it can be restored on relaunch.
 *
 * Also handles basket drafts and other in-progress forms.
 */

import { getDB } from '../offline/db';

export interface LotDraft {
  id: string;
  step: number;
  materialCode: string | null;
  materialId: string | null;
  photos: string[];       // base64 data URLs
  thumbnails: string[];   // base64 thumbnails
  weightGrams: number;
  condition: string;
  aiSuggestion: any | null;
  userOverridden: boolean;
  geoFix: { lat: number; lng: number; accuracy: number; isApproximate: boolean } | null;
  updatedAt: number;
}

const DRAFT_KEY = 'lot_builder_draft';
const HANDOVER_DRAFT_KEY = 'handover_draft';

/**
 * Save the current LotBuilder state.
 * Called after every step change, photo capture, weight change, etc.
 */
export async function saveLotDraft(draft: LotDraft): Promise<void> {
  try {
    const db = await getDB();
    await db.put('cache', {
      key: DRAFT_KEY,
      data: draft,
      cached_at: Date.now(),
    });
  } catch (err) {
    console.warn('Failed to save lot draft:', err);
  }
}

/**
 * Restore a saved LotBuilder draft.
 * Returns null if no draft exists.
 */
export async function restoreLotDraft(): Promise<LotDraft | null> {
  try {
    const db = await getDB();
    const entry = await db.get('cache', DRAFT_KEY);
    if (entry?.data) {
      return entry.data as LotDraft;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Clear the saved draft (after successful submission).
 */
export async function clearLotDraft(): Promise<void> {
  try {
    const db = await getDB();
    await db.delete('cache', DRAFT_KEY);
  } catch {
    // ignore
  }
}

/**
 * Check if a draft exists and is recent (within 24 hours).
 */
export async function hasRecentDraft(): Promise<boolean> {
  const draft = await restoreLotDraft();
  if (!draft) return false;
  const age = Date.now() - draft.updatedAt;
  return age < 24 * 60 * 60 * 1000; // 24 hours
}

// ─── Handover Draft ───────────────────────────────────────────────
export interface HandoverDraft {
  transactionId: string;
  actualWeights: Record<string, number>;
  otp: string;
  collectorConfirmed: boolean;
  buyerConfirmed: boolean;
  geoFix: { lat: number; lng: number } | null;
  updatedAt: number;
}

export async function saveHandoverDraft(draft: HandoverDraft): Promise<void> {
  try {
    const db = await getDB();
    await db.put('cache', {
      key: HANDOVER_DRAFT_KEY,
      data: draft,
      cached_at: Date.now(),
    });
  } catch {
    // ignore
  }
}

export async function restoreHandoverDraft(): Promise<HandoverDraft | null> {
  try {
    const db = await getDB();
    const entry = await db.get('cache', HANDOVER_DRAFT_KEY);
    return entry?.data as HandoverDraft ?? null;
  } catch {
    return null;
  }
}

export async function clearHandoverDraft(): Promise<void> {
  try {
    const db = await getDB();
    await db.delete('cache', HANDOVER_DRAFT_KEY);
  } catch {
    // ignore
  }
}
