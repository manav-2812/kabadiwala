import { create } from 'zustand';
import { getQueuedActions, removeQueuedAction } from '../../offline/outbox';
import { apiRequest } from '../../lib/api';

interface OfflineState {
  isOnline: boolean;
  isSimulatedOffline: boolean;
  isSyncing: boolean;
  pendingCount: number;
  toggleSimulateOffline: () => void;
  updatePendingCount: () => Promise<void>;
  syncNow: () => Promise<void>;
}

export const useOfflineStore = create<OfflineState>((set, get) => ({
  isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
  isSimulatedOffline: localStorage.getItem('kc_simulate_offline') === 'true',
  isSyncing: false,
  pendingCount: 0,

  toggleSimulateOffline: () => {
    const nextVal = !get().isSimulatedOffline;
    localStorage.setItem('kc_simulate_offline', String(nextVal));
    set({ isSimulatedOffline: nextVal });
    if (!nextVal) {
      get().syncNow();
    }
  },

  updatePendingCount: async () => {
    try {
      const actions = await getQueuedActions();
      set({ pendingCount: actions.length });
    } catch {
      set({ pendingCount: 0 });
    }
  },

  syncNow: async () => {
    if (get().isSimulatedOffline) return;
    set({ isSyncing: true });
    try {
      const actions = await getQueuedActions();
      if (actions.length > 0) {
        await apiRequest('/api/sync/batch', {
          method: 'POST',
          body: JSON.stringify(actions)
        });
        for (const a of actions) {
          await removeQueuedAction(a.client_uuid);
        }
      }
      set({ isSyncing: false, pendingCount: 0 });
    } catch (err) {
      console.warn('Sync failed, will retry:', err);
      set({ isSyncing: false });
    }
  }
}));
