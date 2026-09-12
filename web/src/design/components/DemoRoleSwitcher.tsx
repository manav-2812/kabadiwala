import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../features/auth/authStore';
import { useOfflineStore } from '../../features/offline/offlineStore';
import { UserCheck, Shield, Building, Truck, Wifi, WifiOff, RefreshCw, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../lib/api';

export const DemoRoleSwitcher: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { t } = useTranslation();
  const { user, logout } = useAuthStore();
  const { isSimulatedOffline, toggleSimulateOffline } = useOfflineStore();
  const navigate = useNavigate();

  const handleSwitch = async (role: 'collector' | 'aggregator' | 'recycler' | 'admin') => {
    // In production: logout and prompt real login
    logout();
    setIsOpen(false);
    navigate('/login');
  };

  const handleTamper = async () => {
    await apiRequest('/api/demo/tamper', { method: 'POST' });
    alert('Simulated tampering on Lot KC-LOT-0001! View in Admin Traceability Explorer.');
    setIsOpen(false);
  };

  const handleRepair = async () => {
    await apiRequest('/api/demo/repair', { method: 'POST' });
    alert('Cryptographic audit chain repaired successfully for KC-LOT-0001!');
    setIsOpen(false);
  };

  const handleReset = async () => {
    if (confirm('Reset demo database to fresh pristine state?')) {
      await apiRequest('/api/demo/reset', { method: 'POST' });
      window.location.reload();
    }
  };

  return (
    <>
      {/* Floating Demo Trigger Button */}
      <div className="fixed bottom-20 right-4 z-50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 px-3.5 py-2.5 rounded-full bg-[#0B3D2E] text-white shadow-xl hover:bg-[#14634A] border-2 border-[#E9A310] cursor-pointer transition-transform active:scale-95"
          title="Demo Role Switcher & Tools"
        >
          <UserCheck size={18} className="text-[#E9A310]" />
          <span className="text-xs font-bold uppercase tracking-wider">
            {t('demo_prefix')}: {t(`role_${user?.role || 'collector'}`)}
          </span>
        </button>
      </div>

      {/* Demo Modal Drawer */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white border border-[#E3E0D5] rounded-3xl p-6 max-w-sm w-full shadow-2xl flex flex-col gap-4 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b border-[#E3E0D5] pb-3">
              <div>
                <h3 className="text-lg font-bold text-[#0B3D2E]">{t('demo_switcher_title')}</h3>
                <p className="text-xs text-[#5B6B62]">{t('demo_switcher_desc')}</p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 rounded-full text-[#5B6B62] hover:bg-[#F7F5EF] cursor-pointer"
              >
                <X size={20} />
              </button>
            </div>

            {/* Persona Grid */}
            <div className="grid grid-cols-2 gap-2.5">
              <button
                onClick={() => handleSwitch('collector')}
                className={`p-3 rounded-2xl flex flex-col items-center gap-1.5 border text-center transition-all cursor-pointer ${
                  user?.role === 'collector'
                    ? 'bg-[#E4F4EA] border-[#14634A] text-[#0B3D2E] font-bold ring-2 ring-[#14634A]'
                    : 'bg-white border-[#E3E0D5] text-[#14201A] hover:bg-[#F7F5EF]'
                }`}
              >
                <Truck size={22} className="text-[#14634A]" />
                <span className="text-xs font-bold">{t('role_collector')}</span>
                <span className="text-[10px] text-[#5B6B62]">{t('role_collector_sub')}</span>
              </button>

              <button
                onClick={() => handleSwitch('recycler')}
                className={`p-3 rounded-2xl flex flex-col items-center gap-1.5 border text-center transition-all cursor-pointer ${
                  user?.role === 'recycler'
                    ? 'bg-[#E4F4EA] border-[#14634A] text-[#0B3D2E] font-bold ring-2 ring-[#14634A]'
                    : 'bg-white border-[#E3E0D5] text-[#14201A] hover:bg-[#F7F5EF]'
                }`}
              >
                <Building size={22} className="text-[#2F6FDE]" />
                <span className="text-xs font-bold">{t('role_recycler')}</span>
                <span className="text-[10px] text-[#5B6B62]">{t('role_recycler_sub')}</span>
              </button>

              <button
                onClick={() => handleSwitch('admin')}
                className={`p-3 rounded-2xl flex flex-col items-center gap-1.5 border text-center transition-all cursor-pointer ${
                  user?.role === 'admin'
                    ? 'bg-[#E4F4EA] border-[#14634A] text-[#0B3D2E] font-bold ring-2 ring-[#14634A]'
                    : 'bg-white border-[#E3E0D5] text-[#14201A] hover:bg-[#F7F5EF]'
                }`}
              >
                <Shield size={22} className="text-[#E9A310]" />
                <span className="text-xs font-bold">{t('role_admin')}</span>
                <span className="text-[10px] text-[#5B6B62]">{t('role_admin_sub')}</span>
              </button>

              <button
                onClick={() => handleSwitch('aggregator')}
                className={`p-3 rounded-2xl flex flex-col items-center gap-1.5 border text-center transition-all cursor-pointer ${
                  user?.role === 'aggregator'
                    ? 'bg-[#E4F4EA] border-[#14634A] text-[#0B3D2E] font-bold ring-2 ring-[#14634A]'
                    : 'bg-white border-[#E3E0D5] text-[#14201A] hover:bg-[#F7F5EF]'
                }`}
              >
                <RefreshCw size={22} className="text-[#5B6B62]" />
                <span className="text-xs font-bold">{t('role_aggregator')}</span>
                <span className="text-[10px] text-[#5B6B62]">{t('role_aggregator_sub')}</span>
              </button>
            </div>

            {/* Judging Demo Tools */}
            <div className="border-t border-[#E3E0D5] pt-3 flex flex-col gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#5B6B62]">
                {t('demo_judge_controls')}
              </span>

              <button
                onClick={toggleSimulateOffline}
                className={`flex items-center justify-between px-3 py-2 rounded-xl text-xs font-bold border transition-colors cursor-pointer ${
                  isSimulatedOffline
                    ? 'bg-[#FBE7E7] border-[#D64545] text-[#D64545]'
                    : 'bg-white border-[#E3E0D5] text-[#14201A] hover:bg-[#F7F5EF]'
                }`}
              >
                <div className="flex items-center gap-2">
                  {isSimulatedOffline ? <WifiOff size={16} /> : <Wifi size={16} />}
                  <span>{t('demo_simulate_offline')}</span>
                </div>
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-black/10">
                  {isSimulatedOffline ? t('offline_badge') : t('online_badge')}
                </span>
              </button>

              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={handleTamper}
                  className="px-2.5 py-2 rounded-xl bg-[#FBE7E7] hover:bg-[#fcd0d0] text-[#D64545] text-xs font-bold cursor-pointer"
                >
                  {t('demo_tamper_chain')}
                </button>
                <button
                  onClick={handleRepair}
                  className="px-2.5 py-2 rounded-xl bg-[#E4F4EA] hover:bg-[#c9ebd5] text-[#0B3D2E] text-xs font-bold cursor-pointer"
                >
                  {t('demo_repair_chain')}
                </button>
              </div>

              <button
                onClick={handleReset}
                className="w-full py-2 rounded-xl bg-[#F7F5EF] hover:bg-[#E3E0D5] text-[#5B6B62] text-xs font-medium cursor-pointer"
              >
                {t('demo_reset_db')}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
