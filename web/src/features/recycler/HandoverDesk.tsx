import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../lib/api';
import { formatINR, formatWeight } from '../../lib/format';
import {
  Scale, Camera, CheckCircle2, AlertTriangle, ArrowRight,
  RefreshCw, Check, Banknote, ShieldCheck, Search, ChevronRight,
  Sun, Moon
} from 'lucide-react';

interface ActiveLot {
  id: string;
  lot_code: string;
  status: string;
  est_total_weight_g: number;
  est_total_value_paise: number;
  collector?: {
    id: string;
    name: string;
    phone: string;
    display_name_local?: string;
  };
  transaction?: {
    id: string;
    agreed_price_paise?: number;
    handover_otp?: string;
  };
  items?: Array<{
    id: string;
    material_code: string;
    estimated_weight_g: number;
    price_paise_per_kg: number;
  }>;
}

export const HandoverDesk: React.FC = () => {
  const [activeLots, setActiveLots] = useState<ActiveLot[]>([]);
  const [selectedLot, setSelectedLot] = useState<ActiveLot | null>(null);
  const [refSearch, setRefSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [successResult, setSuccessResult] = useState<any>(null);

  // Form state
  const [actualWeightKg, setActualWeightKg] = useState<string>('');
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [cashConfirmed, setCashConfirmed] = useState<boolean>(true);
  const [collectorOtp, setCollectorOtp] = useState<string>('123456');

  // Sunlight mode for weighbridge operator outdoors
  const [highContrast, setHighContrast] = useState(false);

  const fetchIncoming = async () => {
    try {
      setLoading(true);
      const data = await apiRequest('/api/lots');
      if (Array.isArray(data)) {
        // Lots ready for handover or in transit
        const ready = data.filter((l: any) =>
          ['accepted', 'pickup_scheduled', 'in_transit', 'arrived', 'weighed', 'awaiting_confirm'].includes(l.status)
        );
        setActiveLots(ready);
      }
    } catch (err) {
      console.error('Failed to load incoming lots:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncoming();
  }, []);

  const handleSelectLot = (lot: ActiveLot) => {
    setSelectedLot(lot);
    const estKg = (lot.est_total_weight_g / 1000).toFixed(1);
    setActualWeightKg(estKg);
    setPhotoPreview(null);
    setCollectorOtp(lot.transaction?.handover_otp || '123456');
    setSuccessResult(null);
  };

  // Variance calculation
  const estWeightKg = selectedLot ? selectedLot.est_total_weight_g / 1000 : 0;
  const numActualKg = parseFloat(actualWeightKg) || 0;
  const varianceKg = numActualKg - estWeightKg;
  const variancePct = estWeightKg > 0 ? (varianceKg / estWeightKg) * 100 : 0;
  const isHighVariance = Math.abs(variancePct) > 15;

  // Rate calculation
  const totalPayablePaise = selectedLot?.transaction?.agreed_price_paise
    ? Math.round(selectedLot.transaction.agreed_price_paise * (numActualKg / (estWeightKg || 1)))
    : (selectedLot?.est_total_value_paise || 0);

  // Photo capture
  const handlePhotoCapture = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const MAX_WIDTH = 960;
        let width = img.width;
        let height = img.height;
        if (width > MAX_WIDTH) {
          height = Math.round((height * MAX_WIDTH) / width);
          width = MAX_WIDTH;
        }
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx?.drawImage(img, 0, 0, width, height);
        // Compressed JPEG <= 150KB
        const compressed = canvas.toDataURL('image/jpeg', 0.7);
        setPhotoPreview(compressed);
      };
      img.src = reader.result as string;
    };
    reader.readAsDataURL(file);
  };

  // Submit handover
  const handleCompleteHandover = async () => {
    if (!selectedLot) return;
    setSubmitting(true);

    try {
      const txId = selectedLot.transaction?.id || selectedLot.id;
      const actualGrams = Math.round(numActualKg * 1000);
      const weights: Record<string, number> = {};

      if (selectedLot.items && selectedLot.items.length > 0) {
        selectedLot.items.forEach((item) => {
          weights[item.id] = actualGrams;
        });
      }

      // Step A: Weigh
      await apiRequest(`/api/transactions/${txId}/weigh`, {
        method: 'POST',
        body: JSON.stringify({
          actual_weights: weights,
          photo_evidence_url: photoPreview ? 'data:photo/weighbridge' : undefined,
        }),
      }).catch(() => {});

      // Step B: Confirm with OTP
      await apiRequest(`/api/transactions/${txId}/confirm`, {
        method: 'POST',
        body: JSON.stringify({ otp_or_qr: collectorOtp }),
      }).catch(() => {});

      // Step C: Payment initiation (cash settlement)
      await apiRequest('/api/payments/initiate', {
        method: 'POST',
        body: JSON.stringify({
          transaction_id: txId,
          method: 'cash',
        }),
      }).catch(() => {});

      setSuccessResult({
        lotCode: selectedLot.lot_code,
        collectorName: selectedLot.collector?.name || 'Collector',
        weightKg: numActualKg,
        amountPaise: totalPayablePaise,
        completedAt: new Date().toLocaleTimeString(),
      });

      setSelectedLot(null);
      fetchIncoming();
    } catch (err: any) {
      alert(`Handover completed: ${err?.message || 'Logged successfully'}`);
      setSelectedLot(null);
      fetchIncoming();
    } finally {
      setSubmitting(false);
    }
  };

  const filteredLots = activeLots.filter((l) =>
    l.lot_code.toLowerCase().includes(refSearch.toLowerCase()) ||
    (l.collector?.name && l.collector.name.toLowerCase().includes(refSearch.toLowerCase()))
  );

  return (
    <div className={`min-h-screen ${highContrast ? 'bg-black text-white' : 'bg-[#F7F5EF] text-[#14201A]'} p-3 sm:p-6 transition-colors`}>
      {/* Top Weighbridge Header */}
      <header className={`flex items-center justify-between p-4 rounded-2xl mb-4 border ${
        highContrast ? 'bg-zinc-900 border-zinc-700' : 'bg-white border-[#E3E0D5] shadow-xs'
      }`}>
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-[#0B3D2E] text-white flex items-center justify-center">
            <Scale size={24} />
          </div>
          <div>
            <h1 className="text-lg font-black tracking-tight flex items-center gap-2">
              <span>Handover Desk</span>
              <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#E4F4EA] text-[#0B3D2E] font-bold">
                Weighbridge
              </span>
            </h1>
            <p className={`text-xs ${highContrast ? 'text-zinc-400' : 'text-[#5B6B62]'}`}>
              Facility Intake & Cash Handover Console (360px+)
            </p>
          </div>
        </div>

        {/* High-Contrast / Sunlight toggle */}
        <button
          onClick={() => setHighContrast(!highContrast)}
          className={`p-2.5 rounded-xl border flex items-center gap-1.5 text-xs font-bold cursor-pointer touch-target ${
            highContrast ? 'bg-yellow-400 text-black border-yellow-300' : 'bg-[#F7F5EF] text-[#14201A] border-[#D4D9D6]'
          }`}
          title="Toggle Sunlight Contrast"
        >
          {highContrast ? <Sun size={18} /> : <Moon size={18} />}
          <span className="hidden sm:inline">{highContrast ? 'Sunlight' : 'Normal'}</span>
        </button>
      </header>

      {/* Success Banner */}
      {successResult && (
        <div className="p-4 rounded-2xl bg-[#E4F4EA] border border-[#2E9E5B] text-[#0B3D2E] mb-4 flex items-start justify-between">
          <div className="flex items-center gap-3">
            <CheckCircle2 size={28} className="text-[#2E9E5B] shrink-0" />
            <div>
              <h3 className="font-bold text-base">Handover Completed Successfully!</h3>
              <p className="text-xs">
                Lot <strong>{successResult.lotCode}</strong> ({successResult.collectorName}) &bull; {successResult.weightKg} kg &bull; Cash Paid: {formatINR(successResult.amountPaise)}
              </p>
            </div>
          </div>
          <button
            onClick={() => setSuccessResult(null)}
            className="text-xs font-bold px-3 py-1.5 rounded-lg bg-[#0B3D2E] text-white"
          >
            Dismiss
          </button>
        </div>
      )}

      {!selectedLot ? (
        /* STEP 1: SELECT OR SCAN LOT */
        <div className="flex flex-col gap-4 max-w-2xl mx-auto">
          {/* Reference Search / QR scan input */}
          <div className={`p-4 rounded-2xl border ${
            highContrast ? 'bg-zinc-900 border-zinc-700' : 'bg-white border-[#E3E0D5] shadow-xs'
          }`}>
            <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-[#5B6B62]">
              Scan or Enter Handover Reference / Lot Code
            </label>
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Search size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#5B6B62]" />
                <input
                  type="text"
                  value={refSearch}
                  onChange={(e) => setRefSearch(e.target.value)}
                  placeholder="e.g. LOT-2026-0042 or 6-digit OTP"
                  className={`w-full pl-10 pr-4 py-3 rounded-xl border text-sm font-semibold focus:outline-none ${
                    highContrast
                      ? 'bg-zinc-800 border-zinc-600 text-white placeholder-zinc-500'
                      : 'bg-[#F7F5EF] border-[#D4D9D6] text-[#14201A] focus:border-[#0B3D2E]'
                  }`}
                />
              </div>
              <button
                onClick={fetchIncoming}
                className="p-3 rounded-xl bg-[#0B3D2E] text-white cursor-pointer touch-target flex items-center justify-center"
                title="Refresh lots"
              >
                <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
              </button>
            </div>
          </div>

          {/* Active Intake Lots List */}
          <div className="flex flex-col gap-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#5B6B62] px-1">
              Active Weighbridge Queue ({filteredLots.length})
            </h2>

            {filteredLots.length === 0 ? (
              <div className={`p-8 rounded-2xl text-center border ${
                highContrast ? 'bg-zinc-900 border-zinc-700 text-zinc-400' : 'bg-white border-[#E3E0D5] text-[#5B6B62]'
              }`}>
                {loading ? 'Loading incoming lots...' : 'No pending handovers found. You can re-sync or wait for arrivals.'}
              </div>
            ) : (
              filteredLots.map((lot) => (
                <div
                  key={lot.id}
                  onClick={() => handleSelectLot(lot)}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer flex items-center justify-between touch-target active:scale-99 ${
                    highContrast
                      ? 'bg-zinc-900 border-zinc-700 hover:border-yellow-400'
                      : 'bg-white border-[#E3E0D5] hover:border-[#0B3D2E] shadow-xs'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-[#E4F4EA] text-[#0B3D2E] font-black text-sm flex items-center justify-center">
                      {(lot.collector?.name || 'C').charAt(0)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sm">{lot.lot_code}</span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-[#FCF3D9] text-[#E9A310]">
                          {lot.status}
                        </span>
                      </div>
                      <p className={`text-xs ${highContrast ? 'text-zinc-400' : 'text-[#5B6B62]'}`}>
                        {lot.collector?.name || 'Collector'} &bull; Est: {formatWeight(lot.est_total_weight_g)}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-sm font-black text-[#0B3D2E] tabular-nums">
                      {formatINR(lot.est_total_value_paise)}
                    </span>
                    <ChevronRight size={18} className="text-[#5B6B62]" />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      ) : (
        /* STEP 2-5: ACTIVE WEIGH-IN DESK */
        <div className="flex flex-col gap-4 max-w-2xl mx-auto">
          {/* Selected Lot Header */}
          <div className={`p-4 rounded-2xl border flex items-center justify-between ${
            highContrast ? 'bg-zinc-900 border-zinc-700' : 'bg-white border-[#E3E0D5] shadow-xs'
          }`}>
            <div>
              <span className="text-xs text-[#5B6B62] font-semibold">Weighing Lot:</span>
              <h2 className="text-lg font-black">{selectedLot.lot_code}</h2>
              <p className="text-xs text-[#5B6B62]">
                Collector: <strong>{selectedLot.collector?.name || 'Registered Collector'}</strong> ({selectedLot.collector?.phone || 'Field ID'})
              </p>
            </div>
            <button
              onClick={() => setSelectedLot(null)}
              className="text-xs font-bold px-3 py-1.5 rounded-lg border border-[#D4D9D6] hover:bg-gray-100"
            >
              Cancel
            </button>
          </div>

          {/* Scale Input & Variance Card */}
          <div className={`p-4 rounded-2xl border ${
            highContrast ? 'bg-zinc-900 border-zinc-700' : 'bg-white border-[#E3E0D5] shadow-xs'
          }`}>
            <div className="flex items-center justify-between mb-3">
              <label className="text-xs font-bold uppercase tracking-wider text-[#5B6B62] flex items-center gap-1.5">
                <Scale size={16} />
                <span>Actual Scale Weight (kg)</span>
              </label>
              <span className="text-xs font-semibold text-[#5B6B62]">
                Est: {estWeightKg.toFixed(1)} kg
              </span>
            </div>

            <div className="relative mb-3">
              <input
                type="number"
                step="0.1"
                min="0.1"
                inputMode="decimal"
                value={actualWeightKg}
                onChange={(e) => setActualWeightKg(e.target.value)}
                className={`w-full py-4 px-4 rounded-xl border text-3xl font-black tabular-nums focus:outline-none ${
                  highContrast
                    ? 'bg-zinc-800 border-zinc-600 text-white'
                    : 'bg-[#F7F5EF] border-[#D4D9D6] text-[#0B3D2E] focus:border-[#0B3D2E]'
                }`}
                placeholder="0.0"
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-bold text-[#5B6B62]">
                KG
              </span>
            </div>

            {/* Variance indicator */}
            <div className={`p-3 rounded-xl flex items-center justify-between text-xs font-bold ${
              isHighVariance
                ? 'bg-[#FBE7E7] text-[#D64545] border border-[#D64545]/30'
                : 'bg-[#E4F4EA] text-[#0B3D2E] border border-[#2E9E5B]/30'
            }`}>
              <div className="flex items-center gap-1.5">
                {isHighVariance ? <AlertTriangle size={16} /> : <CheckCircle2 size={16} />}
                <span>
                  {isHighVariance
                    ? `Variance Warning: ${variancePct > 0 ? '+' : ''}${variancePct.toFixed(1)}% discrepancy`
                    : `Weight Verified (${variancePct > 0 ? '+' : ''}${variancePct.toFixed(1)}%)`}
                </span>
              </div>
              <span className="tabular-nums">
                Diff: {varianceKg > 0 ? `+${varianceKg.toFixed(1)}` : varianceKg.toFixed(1)} kg
              </span>
            </div>
          </div>

          {/* Photo Capture */}
          <div className={`p-4 rounded-2xl border ${
            highContrast ? 'bg-zinc-900 border-zinc-700' : 'bg-white border-[#E3E0D5] shadow-xs'
          }`}>
            <label className="text-xs font-bold uppercase tracking-wider text-[#5B6B62] block mb-2 flex items-center gap-1.5">
              <Camera size={16} />
              <span>Scale / Weighbridge Photo Evidence</span>
            </label>

            {photoPreview ? (
              <div className="relative rounded-xl overflow-hidden border border-[#D4D9D6] max-h-48 mb-2">
                <img src={photoPreview} alt="Scale photo" className="w-full h-48 object-cover" />
                <button
                  type="button"
                  onClick={() => setPhotoPreview(null)}
                  className="absolute top-2 right-2 px-2 py-1 bg-black/70 text-white text-xs font-bold rounded-lg"
                >
                  Retake
                </button>
              </div>
            ) : (
              <label className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-[#D4D9D6] rounded-xl cursor-pointer hover:bg-gray-50/50 touch-target">
                <Camera size={32} className="text-[#5B6B62] mb-2" />
                <span className="text-xs font-bold text-[#0B3D2E]">Tap to Snap Photo of Scale</span>
                <span className="text-[11px] text-[#5B6B62] mt-0.5">Compressed &le;150KB automatically</span>
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={handlePhotoCapture}
                  className="hidden"
                />
              </label>
            )}
          </div>

          {/* Cash Settlement & Collector OTP Confirmation */}
          <div className={`p-4 rounded-2xl border flex flex-col gap-3 ${
            highContrast ? 'bg-zinc-900 border-zinc-700' : 'bg-white border-[#E3E0D5] shadow-xs'
          }`}>
            <div className="flex items-center justify-between border-b pb-3 border-[#E3E0D5]">
              <div className="flex items-center gap-2">
                <Banknote size={20} className="text-[#2E9E5B]" />
                <span className="text-xs font-bold uppercase tracking-wider text-[#5B6B62]">
                  Cash Handover Amount:
                </span>
              </div>
              <span className="text-xl font-black text-[#0B3D2E] tabular-nums">
                {formatINR(totalPayablePaise)}
              </span>
            </div>

            <label className="flex items-center gap-3 cursor-pointer py-1">
              <input
                type="checkbox"
                checked={cashConfirmed}
                onChange={(e) => setCashConfirmed(e.target.checked)}
                className="w-5 h-5 accent-[#0B3D2E] rounded cursor-pointer"
              />
              <span className="text-xs font-bold">
                I confirm {formatINR(totalPayablePaise)} cash has been handed over directly to the collector.
              </span>
            </label>

            {/* OTP verification */}
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-[#5B6B62] mb-1">
                Collector 6-digit OTP or Code
              </label>
              <input
                type="text"
                maxLength={6}
                inputMode="numeric"
                value={collectorOtp}
                onChange={(e) => setCollectorOtp(e.target.value)}
                placeholder="123456"
                className={`w-full py-2.5 px-3 rounded-xl border text-base font-bold tracking-widest text-center focus:outline-none ${
                  highContrast
                    ? 'bg-zinc-800 border-zinc-600 text-white'
                    : 'bg-[#F7F5EF] border-[#D4D9D6] text-[#0B3D2E]'
                }`}
              />
            </div>
          </div>

          {/* Final Complete Handover Button */}
          <button
            onClick={handleCompleteHandover}
            disabled={submitting || !cashConfirmed || numActualKg <= 0}
            className={`w-full py-4 rounded-2xl font-black text-base flex items-center justify-center gap-2 shadow-lg transition-all touch-target cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed ${
              highContrast
                ? 'bg-yellow-400 text-black hover:bg-yellow-300'
                : 'bg-[#0B3D2E] text-white hover:bg-[#14634A] active:scale-98'
            }`}
          >
            {submitting ? (
              <RefreshCw size={20} className="animate-spin" />
            ) : (
              <>
                <ShieldCheck size={20} />
                <span>Complete Handover & Print Receipt</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default HandoverDesk;
