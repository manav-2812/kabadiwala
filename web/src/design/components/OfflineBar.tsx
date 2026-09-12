import React, { useEffect } from 'react';
import { Wifi, WifiOff, RefreshCw } from 'lucide-react';
import { useOfflineStore } from '../../features/offline/offlineStore';
import { VoiceButton } from './VoiceButton';
import { useTranslation } from 'react-i18next';

export const OfflineBar: React.FC = () => {
  const { isOnline, isSimulatedOffline, isSyncing, pendingCount, updatePendingCount, syncNow } = useOfflineStore();
  const { t } = useTranslation();

  useEffect(() => {
    updatePendingCount();
    const interval = setInterval(updatePendingCount, 5000);
    return () => clearInterval(interval);
  }, []);

  const isActuallyOffline = isSimulatedOffline || !isOnline;

  if (!isActuallyOffline && pendingCount === 0) {
    return null; // Silent when fully online and synced
  }

  const statusText = isActuallyOffline
    ? (isSimulatedOffline ? t('simulated_offline_active') : t('offline_local_saved'))
    : (isSyncing ? t('syncing_server') : t('items_waiting_sync', { count: pendingCount }));

  return (
    <div className="w-full bg-[#14201A] text-white px-4 py-2 flex items-center justify-between text-xs z-50">
      <div className="flex items-center gap-2">
        {isActuallyOffline ? (
          <WifiOff size={16} className="text-[#E9A310] shrink-0" />
        ) : (
          <Wifi size={16} className="text-[#2E9E5B] shrink-0" />
        )}
        <span className="font-medium">{statusText}</span>
        <VoiceButton text={statusText} size={14} className="text-white/80 hover:text-white p-1" />
      </div>

      {!isActuallyOffline && pendingCount > 0 && (
        <button
          onClick={() => syncNow()}
          disabled={isSyncing}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#14634A] hover:bg-[#0B3D2E] text-white font-semibold cursor-pointer disabled:opacity-50"
        >
          <RefreshCw size={12} className={isSyncing ? 'animate-spin' : ''} />
          <span>{t('btn_sync')}</span>
        </button>
      )}
    </div>
  );
};
