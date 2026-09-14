import React, { useState } from 'react';
import {
  TrendingUp, Save, CheckCircle2, RotateCcw,
  Percent, ShieldCheck, ArrowUpRight, HelpCircle
} from 'lucide-react';
import { formatINR } from '../../lib/format';

interface RateRow {
  id: string;
  materialName: string;
  category: string;
  mspFloor: number; // in INR/kg
  regionalMedian: number; // in INR/kg
  offeredRate: number; // in INR/kg
  rank: number;
}

export const RecyclerPrices: React.FC = () => {
  const [savedToast, setSavedToast] = useState(false);
  const [rates, setRates] = useState<RateRow[]>([
    { id: '1', materialName: 'Printed Circuit Boards (High Grade)', category: 'High Value', mspFloor: 380, regionalMedian: 410, offeredRate: 435, rank: 1 },
    { id: '2', materialName: 'Lithium-Ion Battery Packs', category: 'Batteries', mspFloor: 160, regionalMedian: 180, offeredRate: 195, rank: 1 },
    { id: '3', materialName: 'Pure Copper Wire & Cables', category: 'Metals', mspFloor: 460, regionalMedian: 500, offeredRate: 520, rank: 1 },
    { id: '4', materialName: 'Rare-Earth Magnets (Neodymium)', category: 'Strategic', mspFloor: 210, regionalMedian: 235, offeredRate: 245, rank: 2 },
    { id: '5', materialName: 'Smartphones & Feature Phones', category: 'Devices', mspFloor: 140, regionalMedian: 165, offeredRate: 175, rank: 2 },
    { id: '6', materialName: 'Desktop & Server Motherboards', category: 'Computing', mspFloor: 290, regionalMedian: 320, offeredRate: 340, rank: 1 },
    { id: '7', materialName: 'Cathode Ray Tubes (CRT/Monitors)', category: 'Displays', mspFloor: 25, regionalMedian: 35, offeredRate: 40, rank: 1 },
    { id: '8', materialName: 'Flat Screen Displays (LED/LCD)', category: 'Displays', mspFloor: 55, regionalMedian: 65, offeredRate: 70, rank: 2 },
    { id: '9', materialName: 'Mixed Low-Grade Electronic Scrap', category: 'General', mspFloor: 40, regionalMedian: 48, offeredRate: 52, rank: 2 },
    { id: '10', materialName: 'E-Waste Engineered Polymers (ABS)', category: 'Plastics', mspFloor: 28, regionalMedian: 34, offeredRate: 38, rank: 1 },
  ]);

  const handleRateChange = (id: string, newRate: number) => {
    setRates(prev => prev.map(r => {
      if (r.id === id) {
        return { ...r, offeredRate: Math.max(r.mspFloor, newRate) };
      }
      return r;
    }));
  };

  const handleBatchAdjust = (pct: number) => {
    setRates(prev => prev.map(r => ({
      ...r,
      offeredRate: Math.max(r.mspFloor, Math.round(r.offeredRate * (1 + pct / 100)))
    })));
  };

  const handleSave = () => {
    setSavedToast(true);
    setTimeout(() => setSavedToast(false), 3000);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E3E0D5] pb-4">
        <div>
          <h2 className="text-2xl font-black text-[#0B3D2E]">Buy-Back Rate Management</h2>
          <p className="text-xs text-[#5B6B62]">
            Configure live quotes for informal collectors. Rates cannot fall below statutory MSP floors.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => handleBatchAdjust(5)}
            className="px-3 py-1.5 rounded-xl bg-white border border-[#D1CEBF] hover:bg-[#F2EFE9] text-[#14201A] text-xs font-bold cursor-pointer touch-target"
          >
            +5% All Rates
          </button>
          <button
            onClick={() => handleBatchAdjust(-5)}
            className="px-3 py-1.5 rounded-xl bg-white border border-[#D1CEBF] hover:bg-[#F2EFE9] text-[#14201A] text-xs font-bold cursor-pointer touch-target"
          >
            -5% All Rates
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 rounded-xl bg-[#0B3D2E] hover:bg-[#14634A] text-white text-xs font-bold flex items-center gap-1.5 cursor-pointer shadow-sm touch-target"
          >
            <Save size={14} />
            <span>Publish Rate Sheet</span>
          </button>
        </div>
      </div>

      {/* Success Toast */}
      {savedToast && (
        <div className="p-3.5 rounded-xl bg-[#E4F4EA] border border-[#14634A]/30 text-[#14634A] text-xs font-bold flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 size={16} />
          <span>Rates successfully published. Real-time quote engine now offering your updated prices to 28 nearby collectors.</span>
        </div>
      )}

      {/* Info Callout */}
      <div className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E3E0D5] flex items-start gap-3 text-xs">
        <ShieldCheck size={18} className="text-[#14634A] shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-[#14201A]">Statutory Minimum Support Price (MSP) Protection</span>
          <p className="text-[#5B6B62] mt-0.5">
            Under Ministry of Mines guidelines, all licensed recyclers must guarantee at least the statutory floor price to eliminate informal middleman exploitation. Kabadiwala Connect enforces this programmatically.
          </p>
        </div>
      </div>

      {/* Pricing Table */}
      <div className="bg-white rounded-2xl border border-[#E3E0D5] overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#FAF8F5] border-b border-[#E3E0D5] text-[#5B6B62] font-black uppercase tracking-wider text-[11px]">
                <th className="p-3.5">Material Specification</th>
                <th className="p-3.5 text-right">Statutory MSP Floor</th>
                <th className="p-3.5 text-right">Regional Median</th>
                <th className="p-3.5 text-right">Your Offer Rate (₹/kg)</th>
                <th className="p-3.5 text-center">Collector Incentive</th>
                <th className="p-3.5 text-center">Catchment Rank</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E3E0D5]">
              {rates.map((row) => {
                const diffPct = Math.round(((row.offeredRate - row.mspFloor) / row.mspFloor) * 100);
                return (
                  <tr key={row.id} className="hover:bg-[#FAF8F5] transition-colors">
                    <td className="p-3.5 font-bold text-[#14201A]">
                      <div>{row.materialName}</div>
                      <span className="text-[10px] text-[#5B6B62] font-semibold">{row.category}</span>
                    </td>
                    <td className="p-3.5 text-right font-tabular text-[#5B6B62]">
                      ₹{row.mspFloor}
                    </td>
                    <td className="p-3.5 text-right font-tabular text-[#5B6B62]">
                      ₹{row.regionalMedian}
                    </td>
                    <td className="p-3.5 text-right">
                      <div className="inline-flex items-center gap-1">
                        <span className="text-xs text-[#5B6B62] font-bold">₹</span>
                        <input
                          type="number"
                          value={row.offeredRate}
                          onChange={(e) => handleRateChange(row.id, parseInt(e.target.value) || row.mspFloor)}
                          className="w-20 px-2 py-1 rounded-lg border border-[#D1CEBF] font-black font-tabular text-right text-[#0B3D2E] focus:outline-none focus:border-[#14634A]"
                        />
                      </div>
                    </td>
                    <td className="p-3.5 text-center">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#E4F4EA] text-[#14634A]">
                        +{diffPct}% over MSP
                      </span>
                    </td>
                    <td className="p-3.5 text-center">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-black ${
                        row.rank === 1 ? 'bg-[#FFF3D6] text-[#A66F00]' : 'bg-[#F2EFE9] text-[#5B6B62]'
                      }`}>
                        Rank #{row.rank}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
