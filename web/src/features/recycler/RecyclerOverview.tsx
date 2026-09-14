import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../lib/api';
import { KpiCard } from '../../design/components/KpiCard';
import { formatINR, formatWeight } from '../../lib/format';
import { useNavigate } from 'react-router-dom';
import {
  PackageOpen, MessageSquareQuote, Scale,
  Truck, ArrowRight, ShieldCheck, AlertCircle
} from 'lucide-react';

export const RecyclerOverview: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    apiRequest('/api/dashboard/recycler/overview')
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return <div className="p-6 text-xs text-[#5B6B62]">Loading recycler metrics...</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#E3E0D5] pb-4">
        <div>
          <h2 className="text-2xl font-black text-[#0B3D2E]">Facility Overview</h2>
          <p className="text-xs text-[#5B6B62]">Live intake metrics under CPCB E-Waste Rules 2022</p>
        </div>

        <button
          onClick={() => navigate('/recycler/marketplace')}
          className="px-4 py-2 rounded-xl bg-[#14634A] hover:bg-[#0B3D2E] text-white text-xs font-bold flex items-center gap-1.5 cursor-pointer touch-target self-start"
        >
          <span>Bid on Open Lots</span>
          <ArrowRight size={14} />
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <KpiCard
          label="Open Lots Nearby"
          value={data.open_lots_nearby}
          delta="+8 today"
          icon={<PackageOpen size={18} />}
        />
        <KpiCard
          label="Active Quotes"
          value={data.active_quotes}
          delta="4 expiring"
          isPositive={false}
          icon={<MessageSquareQuote size={18} />}
        />
        <KpiCard
          label="Pending Handovers"
          value={data.pending_handovers}
          delta="3 en route"
          icon={<Truck size={18} />}
        />
        <KpiCard
          label="Tonnage Received MTD"
          value={data.tonnage_mtd}
          unit="tonnes"
          delta="+14.2%"
          icon={<Scale size={18} />}
        />
      </div>

      {/* Action Needed Queue */}
      <div className="p-5 rounded-2xl bg-white border border-[#E3E0D5] flex flex-col gap-3 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#0B3D2E]">
            <AlertCircle size={16} className="text-[#E9A310]" />
            <span>Action Required: Pending Weigh-In & Handovers</span>
          </div>
          <button
            onClick={() => navigate('/recycler/handovers')}
            className="text-xs font-bold text-[#14634A] hover:underline cursor-pointer"
          >
            Open Kanban Board &rarr;
          </button>
        </div>

        <div className="divide-y divide-[#E3E0D5]">
          {data.action_needed.map((item: any) => (
            <div
              key={item.id}
              onClick={() => navigate('/recycler/handovers')}
              className="py-3 flex items-center justify-between cursor-pointer hover:bg-[#F7F5EF] px-2 rounded-xl"
            >
              <div>
                <span className="text-xs font-bold text-[#0B3D2E] block">{item.lot_code}</span>
                <span className="text-[11px] text-[#5B6B62]">
                  Weight: {item.weight_kg} kg • Status: {item.status}
                </span>
              </div>
              <span className="text-xs font-bold px-2.5 py-1 rounded-lg bg-[#E4F4EA] text-[#0B3D2E]">
                Complete Weigh-In &rarr;
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
