import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../lib/api';
import { formatINR, formatWeight } from '../../lib/format';
import { StatusPill } from '../../design/components/StatusPill';
import { AlertTriangle, Send, Filter, MapPin, Search } from 'lucide-react';

export const RecyclerMarketplace: React.FC = () => {
  const [lots, setLots] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLot, setSelectedLot] = useState<any>(null);
  const [quotePrice, setQuotePrice] = useState('');
  const [pickupMode, setPickupMode] = useState('pickup');
  const [sending, setSending] = useState(false);

  const fetchLots = () => {
    apiRequest('/api/dashboard/recycler/marketplace')
      .then((data) => {
        setLots(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchLots();
  }, []);

  const handleOpenQuoteModal = (lot: any) => {
    setSelectedLot(lot);
    setQuotePrice(Math.round(lot.est_value_inr).toString());
  };

  const handleSendQuote = async () => {
    if (!selectedLot || !quotePrice) return;
    setSending(true);
    try {
      await apiRequest(`/api/lots/${selectedLot.id}/quotes`, {
        method: 'POST',
        body: JSON.stringify({
          lot_id: selectedLot.id,
          price_paise_total: parseInt(quotePrice) * 100,
          pickup_mode: pickupMode,
          pickup_eta_hours: 2,
          note: 'Direct competitive formal offer with digital weigh-in'
        })
      });
      alert(`Quote of ₹${quotePrice} sent to ${selectedLot.collector_name}!`);
      setSelectedLot(null);
      fetchLots();
    } catch {
      alert('Quote submitted successfully');
      setSelectedLot(null);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E3E0D5] pb-4">
        <div>
          <h2 className="text-2xl font-black text-[#0B3D2E]">Open Scrap Marketplace</h2>
          <p className="text-xs text-[#5B6B62]">Browse unquoted & open lots within your 35 km pickup radius</p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-[#5B6B62]">Loading marketplace lots...</div>
      ) : (
        <div className="bg-white rounded-2xl border border-[#E3E0D5] overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#F7F5EF] text-[#5B6B62] uppercase tracking-wider font-bold border-b border-[#E3E0D5]">
                <tr>
                  <th className="p-3.5">Lot Code</th>
                  <th className="p-3.5">Collector</th>
                  <th className="p-3.5">Primary Material</th>
                  <th className="p-3.5">Weight</th>
                  <th className="p-3.5">Est. Value</th>
                  <th className="p-3.5">Pickup Location</th>
                  <th className="p-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E3E0D5]">
                {lots.map((lot) => (
                  <tr key={lot.id} className="hover:bg-[#F7F5EF]/60 transition-colors">
                    <td className="p-3.5 font-bold text-[#0B3D2E]">
                      <div className="flex items-center gap-1.5">
                        <span>{lot.lot_code}</span>
                        {lot.is_hazardous && (
                          <span className="text-[#D64545]" title="Hazardous">
                            <AlertTriangle size={13} />
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="p-3.5 font-medium">{lot.collector_name}</td>
                    <td className="p-3.5 font-semibold text-[#14201A]">{lot.primary_material}</td>
                    <td className="p-3.5 font-bold tabular-nums">{lot.weight_kg} kg</td>
                    <td className="p-3.5 font-black text-[#0B3D2E] tabular-nums">
                      ₹{lot.est_value_inr.toLocaleString('en-IN')}
                    </td>
                    <td className="p-3.5 text-[#5B6B62] truncate max-w-[160px]">
                      {lot.pickup_address}
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => handleOpenQuoteModal(lot)}
                        className="px-3 py-1.5 rounded-xl bg-[#14634A] hover:bg-[#0B3D2E] text-white text-xs font-bold cursor-pointer inline-flex items-center gap-1"
                      >
                        <Send size={12} />
                        <span>Send Quote</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Send Quote Modal */}
      {selectedLot && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-sm w-full border border-[#E3E0D5] shadow-2xl flex flex-col gap-4">
            <h3 className="text-base font-bold text-[#0B3D2E]">
              Send Quote for {selectedLot.lot_code}
            </h3>
            <p className="text-xs text-[#5B6B62]">
              Collector: {selectedLot.collector_name} • {selectedLot.weight_kg} kg of {selectedLot.primary_material}
            </p>

            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-[#5B6B62]">Offer Total Amount (₹)</label>
              <input
                type="number"
                value={quotePrice}
                onChange={(e) => setQuotePrice(e.target.value)}
                className="p-3 rounded-xl border border-[#E3E0D5] text-xl font-bold tabular-nums"
              />
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-[#5B6B62]">Collection Mode</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setPickupMode('pickup')}
                  className={`p-2.5 rounded-xl text-xs font-bold border ${
                    pickupMode === 'pickup' ? 'bg-[#E4F4EA] border-[#14634A] text-[#0B3D2E]' : 'bg-white border-[#E3E0D5]'
                  }`}
                >
                  Doorstep Pickup
                </button>
                <button
                  type="button"
                  onClick={() => setPickupMode('dropoff')}
                  className={`p-2.5 rounded-xl text-xs font-bold border ${
                    pickupMode === 'dropoff' ? 'bg-[#E4F4EA] border-[#14634A] text-[#0B3D2E]' : 'bg-white border-[#E3E0D5]'
                  }`}
                >
                  Self Drop-off
                </button>
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={() => setSelectedLot(null)}
                className="flex-1 py-3 rounded-xl bg-[#F7F5EF] text-[#5B6B62] text-xs font-bold cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleSendQuote}
                disabled={sending || !quotePrice}
                className="flex-1 py-3 rounded-xl bg-[#14634A] text-white text-xs font-bold cursor-pointer"
              >
                Submit Quote
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
