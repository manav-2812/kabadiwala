import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiRequest } from '../../lib/api';
import { BigButton } from '../../design/components/BigButton';
import { StatusPill } from '../../design/components/StatusPill';
import { formatINR, formatWeight } from '../../lib/format';
import { VoiceButton } from '../../design/components/VoiceButton';
import { Scale, AlertTriangle, ShieldCheck, CheckCircle, FileText, ArrowRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export const HandoverView: React.FC = () => {
  const { id, lotId } = useParams<{ id?: string; lotId?: string }>();
  const [tx, setTx] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [otp, setOtp] = useState('123456');
  const [processing, setProcessing] = useState(false);
  const [actualWeights, setActualWeights] = useState<Record<string, number>>({});
  
  // Cash Handover State
  const [isPartialAdvance, setIsPartialAdvance] = useState(false);
  const [advanceInput, setAdvanceInput] = useState<number>(0);
  const [coarseGps, setCoarseGps] = useState<{ lat: number; lng: number }>({ lat: 28.6139, lng: 77.2090 });
  const [collectorConfirmedLocal, setCollectorConfirmedLocal] = useState(false);
  const [buyerConfirmedLocal, setBuyerConfirmedLocal] = useState(false);
  
  const navigate = useNavigate();
  const { t } = useTranslation();

  const fetchTx = async () => {
    try {
      let targetTxId = id;
      if (!targetTxId && lotId) {
        // Fetch lot to find transaction
        const lotData = await apiRequest(`/api/lots/${lotId}`);
        if (lotData?.transaction?.id) {
          targetTxId = lotData.transaction.id;
        } else {
          targetTxId = lotId; // fallback
        }
      }

      if (!targetTxId) return;

      const data = await apiRequest(`/api/transactions/${targetTxId}`);
      setTx(data);
      const initialWeights: Record<string, number> = {};
      data.items?.forEach((item: any) => {
        initialWeights[item.id] = item.actual_weight_g || item.est_weight_g;
      });
      setActualWeights(initialWeights);
      const totalAmount = (data.final_amount_paise || data.agreed_amount_paise) / 100;
      setAdvanceInput(Math.round(totalAmount * 0.5));
      setCollectorConfirmedLocal(data.cash_confirmed_by_collector || false);
      setBuyerConfirmedLocal(data.cash_confirmed_by_buyer || false);
      setLoading(false);
    } catch {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTx();
    // Fetch coarse GPS
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setCoarseGps({
            lat: Math.round(pos.coords.latitude * 1000) / 1000,
            lng: Math.round(pos.coords.longitude * 1000) / 1000
          });
        },
        () => {} // fallback to default Delhi coords
      );
    }
  }, [id, lotId]);

  const handleSimulateWeighIn = async (variance: number = 0) => {
    if (!tx?.id) return;
    setProcessing(true);
    const weights: Record<string, number> = {};
    tx.items.forEach((item: any) => {
      const base = item.est_weight_g;
      weights[item.id] = Math.round(base * (1.0 + variance));
    });

    try {
      await apiRequest(`/api/transactions/${tx.id}/weigh`, {
        method: 'POST',
        body: JSON.stringify({ actual_weights: weights })
      });
      fetchTx();
    } finally {
      setProcessing(false);
    }
  };

  const handleConfirmCashHandover = async (role: 'collector' | 'buyer' | 'both') => {
    if (!tx?.id) return;
    setProcessing(true);
    const totalPaise = tx.final_amount_paise || tx.agreed_amount_paise;
    const advancePaise = isPartialAdvance ? Math.round(advanceInput * 100) : totalPaise;
    const balancePaise = Math.max(0, totalPaise - advancePaise);

    try {
      await apiRequest(`/api/transactions/${tx.id}/confirm-cash-handover`, {
        method: 'POST',
        body: JSON.stringify({
          role,
          cash_amount_paise: advancePaise,
          is_partial: isPartialAdvance,
          advance_paise: advancePaise,
          balance_paise: balancePaise,
          due_days: 7,
          lat: coarseGps.lat,
          lng: coarseGps.lng
        })
      });

      if (role === 'collector' || role === 'both') setCollectorConfirmedLocal(true);
      if (role === 'buyer' || role === 'both') setBuyerConfirmedLocal(true);
      fetchTx();
    } catch (err: any) {
      alert(err.detail?.message_key || 'Cash confirmation failed');
    } finally {
      setProcessing(false);
    }
  };

  const handleRaiseDispute = async () => {
    if (!tx?.id) return;
    const reason = prompt('Please describe dispute reason:', 'Scale calibrated incorrectly at collection point');
    if (!reason) return;
    try {
      await apiRequest(`/api/transactions/${tx.id}/dispute`, {
        method: 'POST',
        body: JSON.stringify({ reason })
      });
      alert('Dispute logged with Ministry compliance officer. Payment frozen.');
      fetchTx();
    } catch {
      alert('Dispute recorded.');
      fetchTx();
    }
  };

  if (loading || !tx) {
    return <div className="p-6 text-center text-xs text-[#5B6B62]">Loading handover details...</div>;
  }

  const isWeighed = ['weighed', 'awaiting_confirm', 'payment_pending', 'completed'].includes(tx.status);
  const isVarianceHigh = (tx.weight_variance_pct || 0) > 10.0;
  const isCompleted = tx.status === 'completed' || (tx.cash_confirmed_by_collector && tx.cash_confirmed_by_buyer);
  const totalAmountINR = (tx.final_amount_paise || tx.agreed_amount_paise) / 100;
  const remainingDueINR = isPartialAdvance ? Math.max(0, totalAmountINR - advanceInput) : (tx.balance_paise ? tx.balance_paise / 100 : 0);

  return (
    <div className="flex flex-col gap-4 pb-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#E3E0D5] pb-2">
        <div>
          <h2 className="text-lg font-black text-[#0B3D2E]">{t('weigh_in_title')}</h2>
          <span className="text-xs text-[#5B6B62]">{t('receipt_number_label', { receipt: tx.receipt_no || tx.id.slice(0, 8) })}</span>
        </div>
        <StatusPill status={tx.status} />
      </div>

      {/* Recycler Facility Meta */}
      <div className="p-3.5 rounded-2xl bg-white border border-[#E3E0D5] flex items-center justify-between shadow-xs">
        <div>
          <h4 className="text-sm font-bold text-[#0B3D2E]">{tx.buyer_name}</h4>
          <span className="text-xs text-[#5B6B62] block">{tx.buyer_license}</span>
        </div>
        <div className="flex items-center gap-1 text-xs text-[#2E9E5B] font-bold">
          <ShieldCheck size={16} />
          <span>{t('cpcb_verified_badge')}</span>
        </div>
      </div>

      {/* Weigh-in Simulator Controls for Demo */}
      {!isWeighed && (
        <div className="p-4 rounded-2xl bg-[#FCF3D9] border border-[#E9A310]/40 flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#14201A]">
              {t('recycler_digital_scale')}
            </span>
            <Scale size={18} className="text-[#E9A310]" />
          </div>
          <p className="text-xs text-[#5B6B62]">
            {t('simulate_scale_desc')}
          </p>
          <div className="grid grid-cols-2 gap-2 mt-1">
            <button
              onClick={() => handleSimulateWeighIn(0.0)}
              disabled={processing}
              className="py-2.5 px-3 rounded-xl bg-[#14634A] text-white text-xs font-bold cursor-pointer hover:bg-[#0B3D2E]"
            >
              {t('exact_weight_match')}
            </button>
            <button
              onClick={() => handleSimulateWeighIn(0.12)}
              disabled={processing}
              className="py-2.5 px-3 rounded-xl bg-[#D64545] text-white text-xs font-bold cursor-pointer hover:bg-[#b53434]"
            >
              {t('trigger_variance')}
            </button>
          </div>
        </div>
      )}

      {/* Weight Discrepancy Alert if > 10% */}
      {isVarianceHigh && (
        <div className="p-4 rounded-2xl bg-[#FBE7E7] border border-[#D64545] flex flex-col gap-2">
          <div className="flex items-center gap-2 text-[#D64545] font-bold text-sm">
            <AlertTriangle size={18} />
            <span>{t('weight_variance_alert')}</span>
          </div>
          <p className="text-xs text-[#14201A]">
            Digital scale recorded a variance of <b>{tx.weight_variance_pct}%</b>. You may accept the revised payment or raise a dispute.
          </p>
          <div className="grid grid-cols-2 gap-2 pt-1">
            <button
              onClick={handleRaiseDispute}
              className="py-2 px-3 rounded-xl border border-[#D64545] text-[#D64545] text-xs font-bold cursor-pointer hover:bg-[#fbd0d0]"
            >
              {t('btn_raise_dispute')}
            </button>
            <button
              onClick={() => handleConfirmCashHandover('both')}
              className="py-2 px-3 rounded-xl bg-[#14634A] text-white text-xs font-bold cursor-pointer hover:bg-[#0B3D2E]"
            >
              {t('btn_accept_revised')}
            </button>
          </div>
        </div>
      )}

      {/* Items Weigh-in Comparison Table */}
      <div className="flex flex-col gap-2 p-3.5 bg-white rounded-2xl border border-[#E3E0D5]">
        <span className="text-xs font-bold uppercase tracking-wider text-[#5B6B62]">
          {t('weight_breakdown_title')}
        </span>

        {tx.items?.map((item: any) => (
          <div key={item.id} className="flex items-center justify-between py-2 border-b border-[#E3E0D5] last:border-b-0">
            <div>
              <h5 className="text-xs font-bold text-[#0B3D2E]">{item.material_name}</h5>
              <span className="text-[11px] text-[#5B6B62]">
                {t('est_vs_actual', { est: formatWeight(item.est_weight_g), actual: formatWeight(item.actual_weight_g || item.est_weight_g) })}
              </span>
            </div>
            <span className="text-xs font-bold text-[#14201A] tabular-nums">
              {formatINR(tx.final_amount_paise || tx.agreed_amount_paise)}
            </span>
          </div>
        ))}

        <div className="pt-2 flex justify-between items-center text-sm font-black text-[#0B3D2E] border-t border-[#E3E0D5]">
          <span>{t('total_payout_label')}:</span>
          <span className="text-base text-[#14634A]">{formatINR(tx.final_amount_paise || tx.agreed_amount_paise)}</span>
        </div>
      </div>

      {/* Cash-First Dual Confirmation Section */}
      {isWeighed && !isVarianceHigh && !isCompleted && (
        <div className="p-4 rounded-2xl bg-white border-2 border-[#14634A] flex flex-col gap-3 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#E7F3ED] text-[#14634A] text-xs font-black uppercase">
                <span>💵 {t('cash_settlement_default')}</span>
              </div>
              <h4 className="text-base font-extrabold text-[#0B3D2E] mt-1">{t('dual_cash_title')}</h4>
              <p className="text-xs text-[#5B6B62]">{t('dual_cash_desc')}</p>
            </div>
          </div>

          {/* Partial Advance Toggle */}
          <div className="p-3 rounded-xl bg-[#F7F5EF] border border-[#E3E0D5] flex flex-col gap-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={isPartialAdvance}
                onChange={(e) => setIsPartialAdvance(e.target.checked)}
                className="w-4 h-4 rounded text-[#14634A] focus:ring-[#14634A]"
              />
              <span className="text-xs font-bold text-[#14201A]">{t('partial_advance_toggle')}</span>
            </label>

            {isPartialAdvance && (
              <div className="flex flex-col gap-2 pt-1 border-t border-[#E3E0D5]">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-[#5B6B62]">{t('advance_paid_label')} (₹):</span>
                  <input
                    type="number"
                    value={advanceInput}
                    onChange={(e) => setAdvanceInput(Number(e.target.value))}
                    max={totalAmountINR}
                    min={0}
                    className="w-24 text-right py-1 px-2 border border-[#E3E0D5] rounded-lg font-bold text-[#0B3D2E]"
                  />
                </div>
                <div className="flex justify-between items-center text-xs font-bold text-[#D64545]">
                  <span>{t('remaining_balance_label')}:</span>
                  <span>₹{remainingDueINR.toFixed(0)}</span>
                </div>
              </div>
            )}
          </div>

          {/* Dual Verification Checkboxes / Statuses */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className={`p-2.5 rounded-xl border flex flex-col gap-1 ${collectorConfirmedLocal ? 'bg-[#E7F3ED] border-[#2E9E5B]' : 'bg-[#F7F5EF] border-[#E3E0D5]'}`}>
              <span className="font-bold text-[#0B3D2E]">1. {t('collector_confirmed')}</span>
              <span className="text-[11px] text-[#5B6B62]">
                {collectorConfirmedLocal ? '✅' : '⏳'}
              </span>
            </div>
            <div className={`p-2.5 rounded-xl border flex flex-col gap-1 ${buyerConfirmedLocal ? 'bg-[#E7F3ED] border-[#2E9E5B]' : 'bg-[#F7F5EF] border-[#E3E0D5]'}`}>
              <span className="font-bold text-[#0B3D2E]">2. {t('buyer_confirmed')}</span>
              <span className="text-[11px] text-[#5B6B62]">
                {buyerConfirmedLocal ? '✅' : '⏳'}
              </span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col gap-2 pt-1">
            <button
              onClick={() => handleConfirmCashHandover('both')}
              disabled={processing}
              className="w-full py-3 px-4 rounded-xl bg-[#14634A] text-white text-sm font-black flex items-center justify-center gap-2 cursor-pointer hover:bg-[#0B3D2E] shadow-sm active:scale-[0.99] transition-transform"
            >
              <CheckCircle size={18} />
              <span>
                {t('dual_confirm_title')} (₹{isPartialAdvance ? advanceInput : totalAmountINR.toFixed(0)})
              </span>
            </button>
          </div>
        </div>
      )}

      {/* Completed Success Card */}
      {isCompleted && (
        <div className="p-4 rounded-2xl bg-[#E7F3ED] border border-[#2E9E5B] flex flex-col gap-3">
          <div className="flex items-center gap-2 text-[#14634A] font-black text-sm">
            <CheckCircle size={20} />
            <span>{t('handover_success')}</span>
          </div>

          {tx.due_status === 'pending' && tx.balance_paise > 0 && (
            <div className="p-2.5 rounded-xl bg-white border border-[#E9A310] flex justify-between items-center text-xs">
              <span className="font-bold text-[#14201A]">{t('pending_dues_title')}:</span>
              <span className="font-black text-[#D64545]">{formatINR(tx.balance_paise)}</span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-2 pt-1">
            <a
              href={`/api/documents/${tx.receipt_no}/pdf`}
              target="_blank"
              rel="noreferrer"
              className="py-2.5 px-3 rounded-xl bg-white border border-[#14634A] text-[#14634A] text-xs font-bold text-center flex items-center justify-center gap-1.5 hover:bg-[#F7F5EF]"
            >
              <FileText size={15} />
              <span>{t('view_receipt')}</span>
            </a>
            <button
              onClick={() => navigate('/wallet')}
              className="py-2.5 px-3 rounded-xl bg-[#14634A] text-white text-xs font-bold text-center flex items-center justify-center gap-1.5 hover:bg-[#0B3D2E]"
            >
              <span>{t('earnings_ledger_title')}</span>
              <ArrowRight size={15} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
