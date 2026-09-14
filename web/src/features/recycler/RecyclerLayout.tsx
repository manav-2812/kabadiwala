import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, ShoppingCart, MessageSquareCode,
  Scale, Boxes, ShieldCheck, TrendingUp, LogOut
} from 'lucide-react';
import { DemoRoleSwitcher } from '../../design/components/DemoRoleSwitcher';
import { useAuthStore } from '../auth/authStore';

export const RecyclerLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const NAV_ITEMS = [
    { path: '/recycler', label: 'Overview', icon: <LayoutDashboard size={18} /> },
    { path: '/recycler/marketplace', label: 'Marketplace', icon: <ShoppingCart size={18} /> },
    { path: '/recycler/handovers', label: 'Handovers & Weigh-In', icon: <Scale size={18} /> },
    { path: '/recycler/inventory', label: 'EPR Inventory & Manifest', icon: <Boxes size={18} /> },
    { path: '/recycler/compliance', label: 'Compliance & Audit', icon: <ShieldCheck size={18} /> },
    { path: '/recycler/prices', label: 'Buy-Back Rates', icon: <TrendingUp size={18} /> }
  ];

  return (
    <div className="min-h-screen bg-[#F7F5EF] flex text-[#14201A]">
      {/* Sidebar (Section 4.1 --forest-900 background) */}
      <aside className="w-64 bg-[#0B3D2E] text-white flex flex-col shrink-0 hidden md:flex min-h-screen sticky top-0">
        <div className="p-5 border-b border-white/10 flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[#E4F4EA] text-[#0B3D2E] flex items-center justify-center font-black text-lg">
            KC
          </div>
          <div>
            <h1 className="text-sm font-black tracking-tight text-white">Recycler Portal</h1>
            <span className="text-[10px] text-white/60 font-semibold block">CPCB Authorized Hub</span>
          </div>
        </div>

        {/* Navigation links */}
        <nav className="flex-1 p-3 flex flex-col gap-1">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-bold text-left transition-colors cursor-pointer relative ${
                  isActive
                    ? 'bg-white/10 text-white font-black'
                    : 'text-white/70 hover:bg-white/5 hover:text-white'
                }`}
              >
                {isActive && (
                  <span className="absolute left-0 top-1 bottom-1 w-1 bg-[#E9A310] rounded-r" />
                )}
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* User Card */}
        <div className="p-4 border-t border-white/10 flex items-center justify-between text-xs">
          <div>
            <span className="font-bold text-white block truncate max-w-[140px]">
              {user?.name || 'EcoBirba Recyclers'}
            </span>
            <span className="text-[10px] text-white/60">DL/2023/042</span>
          </div>
          <button
            onClick={() => navigate('/')}
            className="p-1.5 rounded-lg text-white/60 hover:text-white hover:bg-white/10 cursor-pointer"
            title="Switch View"
          >
            <LogOut size={16} />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Header */}
        <header className="md:hidden bg-[#0B3D2E] text-white p-3 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-2">
            <span className="font-black text-sm">Recycler Portal</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate('/recycler/marketplace')}
              className="text-xs px-2.5 py-1 rounded-lg bg-white/10 font-bold"
            >
              Marketplace
            </button>
            <button
              onClick={() => navigate('/recycler/handovers')}
              className="text-xs px-2.5 py-1 rounded-lg bg-[#E9A310] text-black font-bold"
            >
              Handovers
            </button>
          </div>
        </header>

        {/* Main Content — Full Screen */}
        <main className="flex-1 w-full px-4 sm:px-6 lg:px-8 xl:px-12 py-6 md:py-8">
          <Outlet />
        </main>
      </div>

      <DemoRoleSwitcher />
    </div>
  );
};
