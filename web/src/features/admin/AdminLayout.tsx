import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  BarChart3, ShieldAlert, GitCommit, Headphones,
  Download, Maximize2, Minimize2, LogOut, CheckCircle2,
  Database, Calculator, BrainCircuit, SlidersHorizontal,
  FlaskConical, ListChecks, TrendingUp, Users, ShieldCheck
} from 'lucide-react';
import { DemoRoleSwitcher } from '../../design/components/DemoRoleSwitcher';
import { useAuthStore } from '../auth/authStore';

export const AdminLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuthStore();
  const [isPresentationMode, setIsPresentationMode] = useState(false);

  const NAV_ITEMS = [
    { path: '/admin', label: 'Overview & Minerals', icon: <BarChart3 size={16} /> },
    { path: '/admin/collectors', label: 'Collector 360', icon: <Users size={16} /> },
    { path: '/admin/data-health', label: 'Data Health', icon: <Database size={16} /> },
    { path: '/admin/unit-economics', label: 'Unit Economics', icon: <Calculator size={16} /> },
    { path: '/admin/trace', label: 'Traceability', icon: <GitCommit size={16} /> },
    { path: '/admin/support', label: 'Support', icon: <Headphones size={16} /> },
    { path: '/admin/compliance', label: 'Compliance', icon: <ShieldAlert size={16} /> },
    // AI & Data group
    { path: '/admin/ai', label: 'AI Overview', icon: <BrainCircuit size={16} />, group: 'AI & Data' },
    { path: '/admin/ai/classifier', label: 'Classifier', icon: <FlaskConical size={16} />, group: 'AI & Data' },
    { path: '/admin/ai/labels', label: 'Labels', icon: <ListChecks size={16} />, group: 'AI & Data' },
    { path: '/admin/ai/predictions', label: 'Predictions', icon: <TrendingUp size={16} />, group: 'AI & Data' },
    { path: '/admin/ai/valuation', label: 'Valuation ML', icon: <Calculator size={16} />, group: 'AI & Data' },
    { path: '/admin/ai/weights', label: 'Match Weights', icon: <SlidersHorizontal size={16} />, group: 'AI & Data' },
    { path: '/admin/ai/drift', label: 'Drift', icon: <TrendingUp size={16} />, group: 'AI & Data' },
  ];

  // Separate main nav from AI nav
  const mainNav = NAV_ITEMS.filter(i => !i.group);
  const aiNav = NAV_ITEMS.filter(i => i.group === 'AI & Data');


  return (
    <div className={`min-h-screen bg-[#F7F5EF] flex flex-col text-[#14201A] ${isPresentationMode ? 'text-base' : ''}`}>
      {/* Top Banner: Ministry of Mines / SIH 2026 */}
      <div className="bg-[#0B3D2E] text-white px-4 py-2 flex items-center justify-between text-xs border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="font-black text-sm tracking-wider text-[#E9A310]">GOVERNMENT OF INDIA</span>
            <span className="text-white/40">|</span>
            <span className="font-semibold text-white/90">Ministry of Mines & JNARDDC</span>
          </div>
          <span className="hidden md:inline-block px-2 py-0.5 rounded bg-white/10 text-[10px] font-bold tracking-wide text-white/80">
            SIH 2026: PS SIH26229
          </span>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsPresentationMode(!isPresentationMode)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-white/10 hover:bg-white/20 text-[11px] font-bold cursor-pointer transition-colors"
            title="Toggle Presentation Mode"
          >
            {isPresentationMode ? <Minimize2 size={13} /> : <Maximize2 size={13} />}
            <span className="hidden sm:inline">{isPresentationMode ? 'Exit Presentation' : 'Presentation Mode'}</span>
          </button>

          <span className="text-white/60 text-[11px]">Admin: Dr. V. Sharma</span>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <header className="bg-white border-b border-[#E3E0D5] sticky top-0 z-30 px-4 sm:px-8 py-3 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/admin')}>
            <div className="w-8 h-8 rounded-xl bg-[#0B3D2E] text-white flex items-center justify-center font-black text-base">
              KC
            </div>
            <div>
              <h1 className="text-sm font-black text-[#0B3D2E] leading-tight">National E-Waste Portal</h1>
              <span className="text-[10px] text-[#5B6B62] font-semibold block">Critical Mineral Intelligence Hub</span>
            </div>
          </div>

          {/* Nav tabs - main group */}
          <nav className="hidden md:flex items-center gap-1 bg-[#F7F5EF] p-1 rounded-xl border border-[#E3E0D5]">
            {mainNav.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    isActive
                      ? 'bg-white text-[#0B3D2E] shadow-xs font-black'
                      : 'text-[#5B6B62] hover:text-[#14201A]'
                  }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => window.open('/api/dashboard/admin/export?format=csv', '_blank')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#0B3D2E] hover:bg-[#14634A] text-white text-xs font-bold cursor-pointer shadow-xs touch-target"
          >
            <Download size={13} />
            <span className="hidden sm:inline">Export Audit CSV</span>
          </button>
        </div>
      </header>

      {/* Mobile Nav - all items */}
      <div className="md:hidden flex items-center overflow-x-auto gap-1 p-2 bg-[#FAF8F5] border-b border-[#E3E0D5]">
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs whitespace-nowrap font-bold ${
                isActive ? 'bg-[#0B3D2E] text-white' : 'text-[#5B6B62]'
              }`}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* AI & Data secondary nav strip */}
      <div className="hidden md:flex items-center gap-1 px-6 py-1.5 bg-[#0d1a14] border-b border-white/10">
        <span className="text-[10px] text-white/40 font-bold mr-2 uppercase tracking-wider">AI &amp; Data</span>
        {aiNav.map((item) => {
          const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
          return (
            <button
              key={item.path}
              id={`ai-nav-${item.path.split('/').pop()}`}
              onClick={() => navigate(item.path)}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                isActive
                  ? 'bg-white/15 text-white'
                  : 'text-white/50 hover:text-white/80'
              }`}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Main Page Content — Full Screen */}
      <main className="flex-1 w-full px-4 sm:px-6 lg:px-8 xl:px-12 py-6 md:py-8">
        <Outlet />
      </main>

      {/* Demo Data Notice & Layer-A Chip */}
      <footer className="w-full bg-[#EAE7DC] border-t border-[#D8D4C5] px-4 py-2 flex flex-wrap items-center justify-between text-[11px] text-[#5B6B62]">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#14634A] text-white font-bold text-[10px]">
            DEMO MODE (Layer A)
          </span>
          <span className="font-semibold text-[#14201A]">
            Fictional Composite Demo Data Active
          </span>
          <span>•</span>
          <span>49 Accounts (34 Collectors, 4 Hubs, 8 Recyclers, 8 Agents, 3 Staff)</span>
        </div>
        <div className="flex items-center gap-3">
          <span>Zero real entities / Aadhaar / PII • 100% Deterministic Seed</span>
          <span className="font-mono text-[10px] text-[#0B3D2E]">PS SIH26229</span>
        </div>
      </footer>

      <DemoRoleSwitcher />
    </div>
  );
};
