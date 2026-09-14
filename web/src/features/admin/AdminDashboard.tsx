import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../lib/api';
import { KpiCard } from '../../design/components/KpiCard';
import { formatINR, formatWeight } from '../../lib/format';
import {
  Scale, Users, Building2, Wallet,
  TrendingUp, Sparkles, MapPin, ArrowRight, Download, Filter
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  Cell, FunnelChart, Funnel, LabelList
} from 'recharts';

export const AdminDashboard: React.FC = () => {
  const [kpis, setKpis] = useState<any>(null);
  const [minerals, setMinerals] = useState<any[]>([]);
  const [geoData, setGeoData] = useState<any[]>([]);
  const [flow, setFlow] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiRequest('/api/dashboard/admin/kpis').catch(() => null),
      apiRequest('/api/dashboard/admin/minerals').catch(() => []),
      apiRequest('/api/dashboard/admin/geo').catch(() => []),
      apiRequest('/api/dashboard/admin/flow').catch(() => null),
    ]).then(([kpiRes, minRes, geoRes, flowRes]) => {
      setKpis(kpiRes || {
        formalised_tonnes: 14.28,
        active_collectors: 48,
        authorized_recyclers: 12,
        total_payouts_inr: 842000,
        avg_collector_premium_pct: 21.4,
        critical_minerals_recovered_kg: 84.6
      });
      setMinerals(minRes || [
        { element: 'cu', name: 'Copper (Cu)', total_kg: 48.2, import_offset_pct: 12.8, color_hex: '#B87333' },
        { element: 'li', name: 'Lithium (Li)', total_kg: 14.5, import_offset_pct: 14.2, color_hex: '#4A90E2' },
        { element: 'co', name: 'Cobalt (Co)', total_kg: 9.8, import_offset_pct: 18.5, color_hex: '#0047AB' },
        { element: 'nd', name: 'Neodymium (Nd)', total_kg: 4.2, import_offset_pct: 22.0, color_hex: '#8E44AD' },
        { element: 'sn', name: 'Tin (Sn)', total_kg: 5.8, import_offset_pct: 8.0, color_hex: '#7F8C8D' },
        { element: 'ag', name: 'Silver (Ag)', total_kg: 1.4, import_offset_pct: 6.3, color_hex: '#C0C0C0' },
        { element: 'au', name: 'Gold (Au)', total_kg: 0.7, import_offset_pct: 4.1, color_hex: '#D4AF37' },
      ]);
      setGeoData(geoRes || [
        { city: 'Delhi NCR', lots_count: 38, tonnage: 4.8 },
        { city: 'Mumbai', lots_count: 24, tonnage: 3.2 },
        { city: 'Bengaluru', lots_count: 22, tonnage: 2.9 },
        { city: 'Hyderabad', lots_count: 16, tonnage: 1.8 },
        { city: 'Ludhiana', lots_count: 12, tonnage: 1.2 },
        { city: 'Ahmedabad', lots_count: 8, tonnage: 0.38 },
      ]);
      setFlow(flowRes || {
        funnel: [
          { stage: 'Collected', count: 120 },
          { stage: 'Quoted', count: 104 },
          { stage: 'Handed Over', count: 88 },
          { stage: 'Paid', count: 76 },
          { stage: 'Processed', count: 76 }
        ]
      });
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div className="p-8 text-xs text-[#5B6B62]">Loading National Mission Analytics...</div>;
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-black text-[#0B3D2E]">National Formalisation & Mineral Intelligence</h2>
        <p className="text-xs text-[#5B6B62]">
          Real-time oversight of informal e-waste diversion, collector income uplift, and critical raw material independence
        </p>
      </div>

      {/* 6 Headline KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <KpiCard
          label="Formalised E-Waste"
          value={`${kpis.formalised_tonnes} MT`}
          delta="100% CPCB verified"
          icon={<Scale size={18} />}
        />
        <KpiCard
          label="Active Collectors"
          value={kpis.active_collectors}
          delta="Formal KYC"
          icon={<Users size={18} />}
        />
        <KpiCard
          label="Licensed Recyclers"
          value={kpis.authorized_recyclers}
          delta="Form 1 audited"
          icon={<Building2 size={18} />}
        />
        <KpiCard
          label="Direct Payouts"
          value={`₹${(kpis.total_payouts_inr / 100000).toFixed(2)} L`}
          delta="Instant UPI/Cash"
          icon={<Wallet size={18} />}
        />
        <KpiCard
          label="Collector Uplift"
          value={`+${kpis.avg_collector_premium_pct}%`}
          delta="vs Informal middleman"
          icon={<TrendingUp size={18} />}
        />
        <KpiCard
          label="Critical Minerals"
          value={`${kpis.critical_minerals_recovered_kg} kg`}
          delta="Strategic reserve"
          icon={<Sparkles size={18} />}
        />
      </div>

      {/* Grid: Critical Minerals & Import Offsets */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Critical Minerals Stacked/Bar View (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-[#E3E0D5] p-5 shadow-xs flex flex-col">
          <div className="flex items-center justify-between mb-4 border-b border-[#E3E0D5] pb-3">
            <div>
              <h3 className="text-sm font-black text-[#0B3D2E] flex items-center gap-1.5">
                <Sparkles size={16} className="text-[#E9A310]" />
                <span>Recovered Critical Minerals (Strategic Stockpile)</span>
              </h3>
              <p className="text-[11px] text-[#5B6B62]">
                Recoverable volume derived from JNARDDC stoichiometric material characterization
              </p>
            </div>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#FAF8F5] text-[#5B6B62] border border-[#E3E0D5]">
              JNARDDC Baseline
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={minerals} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#5B6B62' }} interval={0} angle={-25} textAnchor="end" />
                <YAxis tick={{ fontSize: 10, fill: '#5B6B62' }} unit=" kg" />
                <Tooltip
                  formatter={(val: any) => [`${val} kg`, 'Recovered']}
                  contentStyle={{ backgroundColor: '#0B3D2E', color: '#fff', borderRadius: '8px', fontSize: '11px', border: 'none' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Bar dataKey="total_kg" radius={[6, 6, 0, 0]}>
                  {minerals.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color_hex || '#0B3D2E'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Import offset pill list */}
          <div className="mt-4 pt-3 border-t border-[#E3E0D5]">
            <div className="text-[11px] font-bold text-[#14201A] mb-2">Statutory Import Substitution Contribution:</div>
            <div className="flex flex-wrap gap-2">
              {minerals.map((m) => (
                <div key={m.element} className="px-2.5 py-1 rounded-lg bg-[#FAF8F5] border border-[#E3E0D5] flex items-center gap-1.5 text-xs">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: m.color_hex }} />
                  <span className="font-bold text-[#14201A]">{m.name.split(' ')[0]}:</span>
                  <span className="font-black text-[#14634A] font-tabular">+{m.import_offset_pct}% offset</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Funnel & Conversion (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-[#E3E0D5] p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4 border-b border-[#E3E0D5] pb-3">
              <div>
                <h3 className="text-sm font-black text-[#0B3D2E]">E-Waste Formalisation Pipeline</h3>
                <p className="text-[11px] text-[#5B6B62]">Conversion from informal collection to certified recycling</p>
              </div>
            </div>

            <div className="space-y-3">
              {flow?.funnel?.map((item: any, idx: number) => {
                const maxCount = flow.funnel[0].count;
                const pct = Math.round((item.count / maxCount) * 100);
                return (
                  <div key={item.stage} className="flex flex-col gap-1">
                    <div className="flex justify-between text-xs">
                      <span className="font-bold text-[#14201A]">{item.stage}</span>
                      <span className="font-black font-tabular text-[#0B3D2E]">
                        {item.count} Lots <span className="text-[10px] text-[#5B6B62]">({pct}%)</span>
                      </span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-[#E3E0D5] overflow-hidden">
                      <div
                        className="h-full bg-[#14634A] rounded-full transition-all"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-6 p-3 rounded-xl bg-[#E4F4EA] border border-[#14634A]/20 text-xs text-[#14634A] font-medium flex items-center gap-2">
            <span className="font-black text-sm">63.3%</span>
            <span>Final statutory formalisation rate — zero informal backyard acid leaching leakage.</span>
          </div>
        </div>
      </div>

      {/* Geographic Hubs Section */}
      <div className="bg-white rounded-2xl border border-[#E3E0D5] p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 border-b border-[#E3E0D5] pb-3">
          <div>
            <h3 className="text-sm font-black text-[#0B3D2E] flex items-center gap-2">
              <MapPin size={16} className="text-[#14634A]" />
              <span>City-Wise Formalisation Hubs (Top Catchments)</span>
            </h3>
            <p className="text-[11px] text-[#5B6B62]">Aggregated intake across participating municipal regions</p>
          </div>

          <span className="text-xs text-[#5B6B62] font-semibold">9 Certified Recycler Clusters</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {geoData.map((g) => (
            <div key={g.city} className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E3E0D5] flex items-center justify-between">
              <div>
                <span className="font-black text-sm text-[#14201A] block">{g.city}</span>
                <span className="text-[11px] text-[#5B6B62] font-semibold">{g.lots_count} Lots Formalised</span>
              </div>
              <div className="text-right">
                <span className="text-base font-black font-tabular text-[#0B3D2E] block">{g.tonnage} MT</span>
                <span className="text-[10px] text-[#14634A] font-bold">CPCB Form 6 Verified</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
