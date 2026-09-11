/**
 * Sync Engine
 * Kabadiwala Connect — SIH 2026 (PS SIH26229)
 *
 * Handles outbox sync on:
 * - App resume (foreground)
 * - Network reconnect
 * - User tap "Sync now"
 * - After successful login
 *
 * Idempotent via client_uuid (server deduplicates).
 * Processes items sequentially to preserve order.
 */

import { getDB } from './db';
import { removeQueuedAction, getQueuedActions } from './outbox';
import { onNetworkChange, getNetworkStatus, onAppStateChange } from '../lib/nativeBridge';

type SyncCallback = (status: SyncStatus) => void;

export interface SyncStatus {
  syncing: boolean;
  pending: number;
  lastSyncAt: number | null;
  lastError: string | null;
}

let _syncing = false;
let _lastSyncAt: number | null = null;
let _lastError: string | null = null;
const _listeners = new Set<SyncCallback>();

function notifyListeners() {
  getQueuedActions().then(items => {
    const status: SyncStatus = {
      syncing: _syncing,
      pending: items.length,
      lastSyncAt: _lastSyncAt,
      lastError: _lastError,
    };
    _listeners.forEach(cb => cb(status));
  });
}

/**
 * Subscribe to sync status changes. Returns unsubscribe function.
 */
export function onSyncStatusChange(cb: SyncCallback): () => void {
  _listeners.add(cb);
  return () => { _listeners.delete(cb); };
}

/**
 * Process all queued outbox items.
 * Called from multiple triggers but only runs one at a time.
 */
export async function syncOutbox(): Promise<void> {
  if (_syncing) return;

  const network = await getNetworkStatus();
  if (!network.connected) return;

  _syncing = true;
  _lastError = null;
  notifyListeners();

  const token = localStorage.getItem('kc_token');
  if (!token) {
    _syncing = false;
    notifyListeners();
    return;
  }

  const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || '';

  try {
    const items = await getQueuedActions();

    for (const item of items) {
      try {
        const url = item.action.startsWith('http')
          ? item.action
          : `${API_BASE}${item.action}`;

        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'X-Client-UUID': item.client_uuid,
          },
          body: JSON.stringify({
            ...item.payload,
            client_uuid: item.client_uuid,
          }),
        });

        if (response.ok || response.status === 409) {
          // 409 = duplicate (already processed), remove from outbox
          await removeQueuedAction(item.client_uuid);
        } else if (response.status >= 500) {
          // Server error — retry later, stop processing
          _lastError = `Server error ${response.status}`;
          break;
        } else {
          // Client error (4xx) — remove to prevent infinite retry
          console.warn(`Outbox item ${item.client_uuid} failed with ${response.status}, removing`);
          await removeQueuedAction(item.client_uuid);
        }
      } catch (err) {
        // Network error — stop and retry later
        _lastError = 'Network error during sync';
        break;
      }
    }

    _lastSyncAt = Date.now();
  } catch (err) {
    _lastError = 'Sync failed';
  } finally {
    _syncing = false;
    notifyListeners();
  }
}

/**
 * Get the current number of pending items.
 */
export async function getPendingCount(): Promise<number> {
  const items = await getQueuedActions();
  return items.length;
}

// ─── Auto-sync triggers ──────────────────────────────────────────

let _initialized = false;

/**
 * Initialize auto-sync triggers.
 * Call once at app startup.
 */
export function initSyncEngine(): void {
  if (_initialized) return;
  _initialized = true;

  // 1. Sync on app resume (foreground)
  onAppStateChange((isActive) => {
    if (isActive) {
      syncOutbox();
    }
  });

  // 2. Sync on network reconnect
  onNetworkChange((status) => {
    if (status.connected) {
      // Small delay to let network stabilize
      setTimeout(() => syncOutbox(), 1500);
    }
  });

  // 3. Sync on visibility change (web fallback)
  if (typeof document !== 'undefined') {
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        syncOutbox();
      }
    });

    // 4. Sync on online event (web fallback)
    window.addEventListener('online', () => {
      setTimeout(() => syncOutbox(), 1500);
    });
  }

  // 5. Initial sync on startup
  setTimeout(() => syncOutbox(), 3000);
}

/**
 * Request storage persistence (prevents browser from evicting IndexedDB).
 */
export async function requestStoragePersistence(): Promise<boolean> {
  if (navigator.storage && navigator.storage.persist) {
    return await navigator.storage.persist();
  }
  return false;
}

/**
 * Check storage quota and return usage info.
 */
export async function checkStorageQuota(): Promise<{
  used: number;
  quota: number;
  percentUsed: number;
  isAlmostFull: boolean;
}> {
  if (navigator.storage && navigator.storage.estimate) {
    const est = await navigator.storage.estimate();
    const used = est.usage || 0;
    const quota = est.quota || 0;
    const percentUsed = quota > 0 ? (used / quota) * 100 : 0;
    return {
      used,
      quota,
      percentUsed,
      isAlmostFull: percentUsed >= 85,
    };
  }
  return { used: 0, quota: 0, percentUsed: 0, isAlmostFull: false };
}

/**
 * Prune oldest cached photos of SYNCED lots to free space.
 * Never prune unsynced data.
 */
export async function pruneOldPhotos(): Promise<number> {
  // Implementation: remove cached photos older than 30 days
  // that belong to lots already synced
  const db = await getDB();
  const outboxItems = await db.getAll('outbox');
  const unsyncedIds = new Set(outboxItems.map(i => i.client_uuid));

  let pruned = 0;
  const allCache = await db.getAll('cache');
  const now = Date.now();
  const thirtyDays = 30 * 24 * 60 * 60 * 1000;

  for (const item of allCache) {
    if (
      item.key.startsWith('photo_') &&
      (now - item.cached_at) > thirtyDays &&
      !unsyncedIds.has(item.key)
    ) {
      await db.delete('cache', item.key);
      pruned++;
    }
  }

  return pruned;
}
