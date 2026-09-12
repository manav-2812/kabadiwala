import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Home, Layers, TrendingUp, Wallet, Plus, ShoppingBag, Bell, Timer, Play, Pause, RotateCcw, Check, Sun, Moon, Download, X as XIcon } from 'lucide-react';
import { OfflineBar } from '../../design/components/OfflineBar';
import { LanguageSwitch } from '../../design/components/LanguageSwitch';
import { DemoRoleSwitcher } from '../../design/components/DemoRoleSwitcher';
import { apiRequest } from '../../lib/api';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../auth/authStore';
import { onBackButton, exitApp, isAndroid, shareText } from '../../lib/nativeBridge';
import { useSunlightMode } from '../../lib/sunlightMode';

export const CollectorLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const { user } = useAuthStore();
  const [basketCount, setBasketCount] = useState(0);

  // Sunlight Mode
  const [sunlight, setSunlight] = useSunlightMode();

  // Exit App Confirmation Modal (Android Back button on Home)
  const [showExitConfirm, setShowExitConfirm] = useState(false);

  // Usability Test Mode & Stopwatch State
  const [testMode, setTestMode] = useState(false);
  const [timerRunning, setTimerRunning] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [selectedTask, setSelectedTask] = useState('Task 1: Check Price');
  const [testLogs, setTestLogs] = useState<any[]>([]);

  // Hardware Back button handling
  useEffect(() => {
    const unsub = onBackButton(() => {
      if (showExitConfirm) {
        setShowExitConfirm(false);
        return;
      }
      if (location.pathname === '/' || location.pathname === '') {
        setShowExitConfirm(true);
      } else {
        navigate(-1);
      }
    });
    return unsub;
  }, [location.pathname, showExitConfirm, navigate]);

  useEffect(() => {
    let interval: any = null;
    if (timerRunning) {
      interval = setInterval(() => setTimerSeconds((s) => s + 1), 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [timerRunning]);

  const handleLogTask = () => {
    const log = { task: selectedTask, seconds: timerSeconds, timestamp: new Date().toLocaleTimeString() };
    setTestLogs((prev) => [log, ...prev]);
    setTimerRunning(false);
    setTimerSeconds(0);
  };

  const handleExportCsv = async () => {
    if (testLogs.length === 0) {
      alert('No test logs recorded yet. Run and log some tasks first.');
      return;
    }
    const header = 'Task,Duration_Seconds,Timestamp\n';
    const rows = testLogs.map((l) => `"${l.task}",${l.seconds},"${l.timestamp}"`).join('\n');
    const csvContent = header + rows;

    try {
      await shareText('Kabadiwala Connect - Usability Test Timings', csvContent);
    } catch {
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `usability_test_${Date.now()}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  useEffect(() => {
    apiRequest('/api/basket')
      .then((data) => setBasketCount(data.total_items || 0))
      .catch(() => {});
  }, [location.pathname]);

  const navItems = [
    { path: '/', label: t('nav_home'), icon: <Home size={22} /> },
    { path: '/lots', label: t('nav_lots'), icon: <Layers size={22} /> },
    { path: '/prices', label: t('nav_prices'), icon: <TrendingUp size={22} /> },
    { path: '/wallet', label: t('nav_wallet'), icon: <Wallet size={22} /> },
  ];

  return (
    <div className="min-h-screen bg-[#F8FAF9] flex flex-col text-[#14201A] font-sans antialiased">
      {/* Offline sync alert banner */}
      <OfflineBar />

      {/* Top Header — Full screen spanning */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-[#E3E0D5] shadow-xs w-full">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#0B3D2E] to-[#14634A] flex items-center justify-center text-white font-black text-lg shadow-xs">
              KC
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base sm:text-lg font-black text-[#0B3D2E] leading-tight">
                  {t('app_name')}
                </h1>
                <span className="hidden sm:inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#E4F4EA] text-[#14634A] border border-[#2E9E5B]/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#2E9E5B] animate-pulse" />
                  {t('header_live_grid')}
                </span>
              </div>
              <span className="text-[11px] text-[#5B6B62] font-semibold block">
                {t('header_portal_subtitle')}
              </span>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 bg-[#F7F5EF] p-1 rounded-xl border border-[#E3E0D5]">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    isActive
                      ? 'bg-[#0B3D2E] text-white shadow-xs'
                      : 'text-[#5B6B62] hover:text-[#14201A]'
                  }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          <div className="flex items-center gap-2 sm:gap-3">
            {/* Usability Test Mode Toggle */}
            <button
              onClick={() => setTestMode(!testMode)}
              className={`p-2 rounded-xl text-xs font-bold flex items-center gap-1 cursor-pointer transition-colors ${
                testMode ? 'bg-[#14634A] text-white shadow-xs' : 'text-[#5B6B62] hover:bg-[#F7F5EF]'
              }`}
              title="Toggle Usability Test Mode Stopwatch"
            >
              <Timer size={18} />
              <span className="hidden sm:inline">{t('btn_test_mode')}</span>
            </button>

            {/* Sunlight / Outdoor High-Contrast Mode Toggle */}
            <button
              onClick={() => setSunlight(!sunlight)}
              className={`p-2 rounded-xl text-xs font-bold flex items-center gap-1 cursor-pointer transition-colors ${
                sunlight ? 'bg-yellow-400 text-black shadow-xs font-black' : 'text-[#5B6B62] hover:bg-[#F7F5EF]'
              }`}
              title="Toggle Sunlight High-Contrast Mode (7:1+ contrast outdoors)"
            >
              {sunlight ? <Sun size={18} className="text-black" /> : <Sun size={18} />}
              <span className="hidden sm:inline">{sunlight ? 'Sunlight' : 'Sunlight'}</span>
            </button>

            <LanguageSwitch compact />

            {/* Desktop "+ Add Scrap" Button */}
            <button
              onClick={() => navigate('/add-scrap')}
              className="hidden md:flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#14634A] hover:bg-[#0B3D2E] text-white font-bold text-xs shadow-xs cursor-pointer transition-all touch-target"
            >
              <Plus size={16} />
              <span>{t('btn_add_scrap')}</span>
            </button>

            {/* Notifications Bell */}
            <button
              onClick={() => navigate('/notifications')}
              className="relative p-2 rounded-xl text-[#5B6B62] hover:bg-[#F7F5EF] cursor-pointer touch-target flex items-center justify-center"
              title="Notifications"
            >
              <Bell size={20} />
              <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#E9A310]" />
            </button>

            {/* Scrap Basket Bag with Count Badge */}
            <button
              onClick={() => navigate('/basket')}
              className="relative p-2 rounded-xl bg-[#FCF3D9] text-[#14201A] hover:bg-[#faeac0] cursor-pointer touch-target flex items-center justify-center border border-[#E9A310]/40"
              title="Scrap Basket"
            >
              <ShoppingBag size={20} className="text-[#0B3D2E]" />
              {basketCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-[#E9A310] text-black text-[11px] font-black flex items-center justify-center tabular-nums shadow-xs">
                  {basketCount}
                </span>
              )}
            </button>

            {/* Login / Profile Button */}
            <button
              onClick={() => navigate('/login')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#FAF8F5] hover:bg-[#E4F4EA] border border-[#E3E0D5] text-xs font-bold text-[#0B3D2E] transition-colors cursor-pointer"
              title="Log In or Sign Up"
            >
              <div className="w-5 h-5 rounded-full bg-[#0B3D2E] text-white flex items-center justify-center text-[10px] font-black">
                {user?.name ? user.name.charAt(0) : 'U'}
              </div>
              <span className="hidden sm:inline">
                {user?.name
                  ? (user.name.startsWith('Collector')
                      ? `${t('role_collector')} ${user.name.replace('Collector', '').trim()}`.trim()
                      : user.name.split(' ')[0])
                  : t('btn_login')}
              </span>
            </button>
          </div>
        </div>
      </header>

      {/* Usability Test Mode Stopwatch Bar */}
      {testMode && (
        <div className="bg-[#0B3D2E] text-white border-b border-white/10 z-30 shadow-xs w-full">
          <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 py-2.5 flex flex-wrap items-center justify-between gap-2 text-xs">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded bg-white/20 font-mono font-bold text-sm tabular-nums">
                  {Math.floor(timerSeconds / 60).toString().padStart(2, '0')}:{(timerSeconds % 60).toString().padStart(2, '0')}s
                </span>
                <button
                  onClick={() => setTimerRunning(!timerRunning)}
                  className="py-1 px-2.5 rounded bg-[#2E9E5B] hover:bg-[#27864d] text-white font-bold flex items-center gap-1 cursor-pointer"
                >
                  {timerRunning ? <Pause size={12} /> : <Play size={12} />}
                  <span>{timerRunning ? t('btn_pause') : t('btn_start')}</span>
                </button>
                <button
                  onClick={() => { setTimerRunning(false); setTimerSeconds(0); }}
                  className="py-1 px-2 rounded bg-white/20 hover:bg-white/30 text-white font-semibold cursor-pointer"
                  title="Reset Timer"
                >
                  <RotateCcw size={12} />
                </button>
              </div>

              <div className="flex items-center gap-2">
                <select
                  value={selectedTask}
                  onChange={(e) => setSelectedTask(e.target.value)}
                  className="bg-white/10 text-white border border-white/20 rounded-lg px-2 py-1 text-xs focus:outline-none"
                >
                  <option value="Task 1: Check Price" className="text-black">{t('task_check_price')}</option>
                  <option value="Task 2: Build Lot" className="text-black">{t('task_build_lot')}</option>
                  <option value="Task 3: Dual Handover" className="text-black">{t('task_dual_handover')}</option>
                  <option value="Task 4: Settle Dues" className="text-black">{t('task_settle_dues')}</option>
                  <option value="Task 5: Safety Hub" className="text-black">{t('task_safety_hub')}</option>
                </select>
                <button
                  onClick={handleLogTask}
                  className="py-1 px-2.5 rounded bg-[#E9A310] text-black font-bold flex items-center gap-1 cursor-pointer"
                >
                  <Check size={12} />
                  <span>{t('btn_log_task')} ({testLogs.length})</span>
                </button>
                <button
                  onClick={handleExportCsv}
                  className="py-1 px-2 rounded bg-white/20 hover:bg-white/30 text-white font-bold flex items-center gap-1 cursor-pointer"
                  title="Export Usability Timing CSV via Share Sheet"
                >
                  <Download size={12} />
                  <span>CSV</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Main Scrollable Content — 100% Full Screen Expansive Canvas */}
        <main className="flex-1 w-full px-4 sm:px-6 lg:px-8 xl:px-12 py-6 md:py-8 pb-28 md:pb-12 safe-bottom">
          <Outlet />
        </main>

        {/* Mobile Floating Big "+ Add Scrap" Button (Hidden on Desktop) */}
        <div className="md:hidden fixed bottom-18 left-0 right-0 px-4 pointer-events-none z-30 flex justify-center">
          <button
            onClick={() => navigate('/add-scrap')}
            className="pointer-events-auto flex items-center gap-2 px-6 py-3.5 rounded-full bg-[#14634A] hover:bg-[#0B3D2E] active:scale-95 text-white font-bold text-base shadow-lg border-2 border-white cursor-pointer transition-all touch-target"
          >
            <Plus size={22} />
            <span>{t('btn_add_scrap')}</span>
          </button>
        </div>

        {/* Floating Demo Persona Switcher */}
        <DemoRoleSwitcher />

        {/* Mobile Bottom Navigation (Hidden on Desktop) */}
        <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-[#E3E0D5] z-40 px-2 py-1.5 flex items-center justify-around shadow-sm safe-bottom">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`flex flex-col items-center justify-center py-1 px-3 rounded-xl transition-colors cursor-pointer touch-target ${
                  isActive ? 'text-[#0B3D2E]' : 'text-[#5B6B62] hover:text-[#14201A]'
                }`}
              >
                <div className={`p-1 rounded-lg ${isActive ? 'bg-[#E4F4EA]' : ''}`}>
                  {item.icon}
                </div>
                <span className={`text-[11px] font-bold mt-0.5 ${isActive ? 'text-[#0B3D2E]' : ''}`}>
                  {item.label}
                </span>
              </button>
            );
          })}
        </nav>

        {/* Big Android Exit Confirmation Modal */}
        {showExitConfirm && (
          <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-sm w-full text-center shadow-2xl border-2 border-[#0B3D2E]">
              <div className="w-16 h-16 rounded-full bg-[#FCF3D9] text-[#E9A310] mx-auto mb-4 flex items-center justify-center text-3xl font-black">
                🚪
              </div>
              <h3 className="text-xl font-black text-[#14201A] mb-2">
                {i18n.language === 'mr'
                  ? 'कबाडीवाला कनेक्ट बंद करायचे आहे का?'
                  : i18n.language === 'pa'
                  ? 'ਕੀ ਤੁਸੀਂ ਐਪ ਬੰਦ ਕਰਨਾ ਚਾਹੁੰਦੇ ਹੋ?'
                  : i18n.language === 'hi'
                  ? 'क्या आप बाहर निकलना चाहते हैं?'
                  : 'Exit Kabadiwala Connect?'}
              </h3>
              <p className="text-xs text-[#5B6B62] mb-6 font-semibold">
                {i18n.language === 'mr'
                  ? 'आपला डेटा सुरक्षित सेव्ह झालेला आहे.'
                  : i18n.language === 'hi'
                  ? 'आपका ड्राफ्ट और डेटा सुरक्षित है।'
                  : 'Your work and offline drafts are securely saved.'}
              </p>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setShowExitConfirm(false)}
                  className="py-3.5 px-4 rounded-2xl border-2 border-[#D4D9D6] text-[#14201A] font-bold text-sm hover:bg-gray-100 flex items-center justify-center gap-2 cursor-pointer touch-target"
                >
                  <XIcon size={18} />
                  <span>{i18n.language === 'mr' ? 'नाही, थांबा' : i18n.language === 'hi' ? 'नहीं' : 'Stay'}</span>
                </button>
                <button
                  onClick={() => exitApp()}
                  className="py-3.5 px-4 rounded-2xl bg-[#0B3D2E] text-white font-black text-sm hover:bg-[#14634A] flex items-center justify-center gap-2 shadow-lg cursor-pointer touch-target"
                >
                  <Check size={18} />
                  <span>{i18n.language === 'mr' ? 'होय, बंद करा' : i18n.language === 'hi' ? 'हाँ, बाहर निकलें' : 'Exit'}</span>
                </button>
              </div>
            </div>
          </div>
        )}
    </div>
  );
};
