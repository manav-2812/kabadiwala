import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../lib/api';
import { formatINR, formatWeight, formatDate } from '../../lib/format';
import { StatusPill } from '../../design/components/StatusPill';
import { DemoRoleSwitcher } from '../../design/components/DemoRoleSwitcher';
import { RefreshCw, Package, ArrowRight, Check, Users, Layers } from 'lucide-react';

export const AggregatorDashboard: React.FC = () => {
  const [lots, setLots] = useState<any[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [consolidating, setConsolidating] = useState(false);

  useEffect(() => {
    apiRequest('/api/lots')
      .then((data) => {
        setLots(data.slice(0, 15));
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleToggleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleConsolidate = () => {
    if (selectedIds.length === 0) return;
    setConsolidating(true);
    setTimeout(() => {
      alert(`Consolidated ${selectedIds.length} collector lots into batch lot KC-BATCH-${Date.now().toString().slice(-4)}! Forwarded to CPCB Recycler.`);
      setSelectedIds([]);
      setConsolidating(false);
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-[#F7F5EF] p-4 sm:p-6 text-[#14201A]">
      <div className="max-w-4xl mx-auto flex flex-col gap-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E3E0D5] pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-8 h-8 rounded-xl bg-[#0B3D2E] text-white flex items-center justify-center font-bold">
                AH
              </span>
              <h1 className="text-xl font-black text-[#0B3D2E]">Harit Aggregation Hub</h1>
            </div>
            <p className="text-xs text-[#5B6B62] mt-0.5">
              Local Consolidation Point • Nehru Place, Delhi • Commission Rate: 5%
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full bg-[#E4F4EA] text-[#0B3D2E] text-xs font-bold border border-[#2E9E5B]/40">
              12 Collectors Linked
            </span>
          </div>
        </div>

        {/* Action Callout */}
        <div className="p-4 rounded-2xl bg-white border border-[#E3E0D5] flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs">
          <div>
            <h3 className="text-sm font-bold text-[#0B3D2E]">Batch Merge Lots</h3>
            <p className="text-xs text-[#5B6B62]">
              Select multiple collector lots to bundle into higher-value tonnage lots for recyclers.
            </p>
          </div>

          <button
            onClick={handleConsolidate}
            disabled={selectedIds.length === 0 || consolidating}
            className="px-5 py-2.5 rounded-xl bg-[#14634A] hover:bg-[#0B3D2E] text-white text-xs font-bold disabled:opacity-40 cursor-pointer flex items-center gap-2 touch-target"
          >
            <RefreshCw size={14} className={consolidating ? 'animate-spin' : ''} />
            <span>Consolidate {selectedIds.length} Selected Lots</span>
          </button>
        </div>

        {/* Incoming Lots Table */}
        <div className="bg-white rounded-2xl border border-[#E3E0D5] overflow-hidden shadow-xs">
          <div className="p-4 border-b border-[#E3E0D5]">
            <h3 className="text-sm font-black text-[#0B3D2E]">Incoming Collector Lots</h3>
          </div>

          <div className="divide-y divide-[#E3E0D5]">
            {lots.map((lot) => {
              const isSelected = selectedIds.includes(lot.id);
              return (
                <div
                  key={lot.id}
                  onClick={() => handleToggleSelect(lot.id)}
                  className={`p-4 flex items-center justify-between gap-3 cursor-pointer transition-colors ${
                    isSelected ? 'bg-[#E4F4EA]/40' : 'hover:bg-[#F7F5EF]'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => {}}
                      className="w-4 h-4 rounded text-[#14634A]"
                    />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-[#0B3D2E]">{lot.lot_code}</span>
                        <StatusPill status={lot.status} />
                      </div>
                      <span className="text-xs text-[#5B6B62] block mt-0.5">
                        Collector: {lot.collector_name} • {formatWeight(lot.est_total_weight_g)}
                      </span>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-sm font-black text-[#14201A] tabular-nums block">
                      {formatINR(lot.est_total_max_paise)}
                    </span>
                    <span className="text-[11px] text-[#2E9E5B] font-bold">
                      Est. Commission: {formatINR(Math.round(lot.est_total_max_paise * 0.05))}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <DemoRoleSwitcher />
    </div>
  );
};
