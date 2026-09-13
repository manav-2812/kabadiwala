import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiRequest } from '../../lib/api';
import { QRCodeSVG } from 'qrcode.react';
import { StepTimeline } from '../../design/components/StepTimeline';
import { StatusPill } from '../../design/components/StatusPill';
import { QuoteCard } from '../../design/components/QuoteCard';
import { BigButton } from '../../design/components/BigButton';
import { formatINR, formatWeight, formatDate } from '../../lib/format';
import { VoiceButton } from '../../design/components/VoiceButton';
import { Share2, MapPin, XCircle, Truck, ArrowRight, ShieldCheck } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export const LotDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [lot, setLot] = useState<any>(null);
  const [quotes, setQuotes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState('found_better_price');
  
  const navigate = useNavigate();
  const { t } = useTranslation();

  const fetchLot = () => {
    if (!id) return;
    apiRequest(`/api/lots/${id}`)
      .then((data) => {
        setLot(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    apiRequest(`/api/lots/${id}/quotes`)
      .then(setQuotes)
      .catch(() => {});
  };

  useEffect(() => {
    fetchLot();
  }, [id]);

  const handleAcceptQuote = async (quoteId: string) => {
    try {
      const res = await apiRequest(`/api/quotes/${quoteId}/accept`, { method: 'POST' });
      alert(res.message || 'Quote accepted!');
      fetchLot();
    } catch (err: any) {
      alert(err.detail?.message_key || 'Failed to accept quote');
    }
  };

  const handleCancelLot = async () => {
    if (!id) return;
    try {
      await apiRequest(`/api/lots/${id}/cancel`, {
        method: 'POST',
        body: JSON.stringify({ reason_code: cancelReason, note: 'Cancelled by collector' })
      });
      setShowCancelModal(false);
      fetchLot();
    } catch (err: any) {
      alert(err.detail?.message_key || 'Failed to cancel lot');
    }
  };

  const handleShareWhatsApp = () => {
    const text = `Kabadiwala Connect Lot ${lot.lot_code}: ${formatWeight(lot.est_total_weight_g)} e-waste formally listed. Check verification at: https://kabadiwala.gov.in/verify/${lot.lot_code}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
  };

  if (loading || !lot) {
    return <div className="p-6 text-center text-xs text-[#5B6B62]">{t('loading_scrap_lot')}</div>;
  }

  const isAcceptedOrBeyond = ['accepted', 'pickup_scheduled', 'in_transit', 'arrived', 'weighed', 'awaiting_confirm', 'payment_pending', 'completed'].includes(lot.status);

  return (
    <div className="flex flex-col gap-4 pb-6">
      {/* Top Header & Code */}
      <div className="flex items-center justify-between border-b border-[#E3E0D5] pb-2">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-black text-[#0B3D2E]">{lot.lot_code}</h2>
            <StatusPill status={lot.status} />
          </div>
          <span className="text-xs text-[#5B6B62]">{formatDate(lot.created_at)}</span>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={handleShareWhatsApp}
            className="p-2 rounded-xl text-[#2E9E5B] hover:bg-[#E4F4EA] cursor-pointer touch-target"
            title="Share lot on WhatsApp"
          >
            <Share2 size={20} />
          </button>
          <VoiceButton text={`Lot ${lot.lot_code}, status: ${lot.status}`} size={20} />
        </div>
      </div>

      {/* Step Timeline */}
      <StepTimeline currentStatus={lot.status} />

      {/* Live Handover / Tracking CTA if accepted */}
      {isAcceptedOrBeyond && lot.transaction && (
        <div className="p-4 rounded-2xl bg-[#E4F4EA] border border-[#2E9E5B]/40 flex items-center justify-between shadow-xs">
          <div>
            <span className="text-xs font-bold text-[#0B3D2E] block uppercase tracking-wider">
              {lot.status === 'completed' ? t('handover_complete') : t('handover_in_progress')}
            </span>
            <span className="text-sm font-black text-[#14201A]">
              {t('receipt_number_label', { receipt: lot.transaction.receipt_no })}
            </span>
          </div>
          <button
            onClick={() => {
              if (lot.status === 'in_transit' || lot.status === 'pickup_scheduled') {
                navigate(`/tracking/${lot.transaction.id}`);
              } else {
                navigate(`/handover/${lot.transaction.id}`);
              }
            }}
            className="px-4 py-2 rounded-xl bg-[#14634A] hover:bg-[#0B3D2E] text-white text-xs font-bold flex items-center gap-1.5 cursor-pointer touch-target"
          >
            <span>{lot.status === 'in_transit' ? t('btn_track_agent') : t('btn_view_handover')}</span>
            <ArrowRight size={14} />
          </button>
        </div>
      )}

      {/* QR Code and Value Summary Card */}
      <div className="flex items-center justify-between p-4 bg-white rounded-2xl border border-[#E3E0D5] gap-4">
        <div className="flex-1">
          <span className="text-xs font-bold uppercase tracking-wider text-[#5B6B62] block">
            {lot.final_amount_paise ? t('final_settled_payout') : t('valuation_range')}
          </span>
          <span className="text-2xl font-black tabular-nums text-[#0B3D2E]">
            {lot.final_amount_paise
              ? formatINR(lot.final_amount_paise)
              : `${formatINR(lot.est_total_min_paise)} - ${formatINR(lot.est_total_max_paise)}`}
          </span>
          <span className="text-xs text-[#5B6B62] block mt-1">
            {t('total_weight_label', { weight: formatWeight(lot.actual_total_weight_g || lot.est_total_weight_g) })}
          </span>
        </div>

        {/* Traceable QR Code */}
        <div className="p-2 bg-[#F7F5EF] rounded-xl border border-[#E3E0D5] shrink-0 flex flex-col items-center">
          <QRCodeSVG value={`https://kabadiwala.gov.in/verify/${lot.lot_code}`} size={72} />
          <span className="text-[9px] font-bold text-[#5B6B62] mt-1">{t('scan_for_audit')}</span>
        </div>
      </div>

      {/* Items in this Lot */}
      <div className="flex flex-col gap-2">
        <h3 className="text-xs font-bold uppercase tracking-wider text-[#5B6B62]">
          {t('items_in_lot', { count: lot.items.length })}
        </h3>
        {lot.items.map((item: any) => (
          <div key={item.id} className="flex items-center justify-between p-3 bg-white rounded-xl border border-[#E3E0D5]">
            <div>
              <h4 className="text-sm font-bold text-[#0B3D2E]">{String(t(`categories.${item.material_code}`, item.material_name || item.material_code))}</h4>
              <span className="text-xs text-[#5B6B62]">{formatWeight(item.actual_weight_g || item.est_weight_g)} • {String(t(`condition_${item.condition}`, item.condition))}</span>
            </div>
            <span className="text-sm font-extrabold text-[#14201A] tabular-nums">
              {formatINR(item.final_value_paise || item.est_value_max_paise)}
            </span>
          </div>
        ))}
      </div>

      {/* Quotes Section */}
      {!isAcceptedOrBeyond && (
        <div className="flex flex-col gap-3 pt-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-black text-[#0B3D2E]">
              {t('quotes_available')} ({quotes.length})
            </h3>
            <button
              onClick={() => navigate(`/find-buyers?lot_id=${lot.id}`)}
              className="text-xs font-bold text-[#14634A] hover:underline cursor-pointer"
            >
              {t('btn_find_buyers')}
            </button>
          </div>

          {quotes.length === 0 ? (
            <div className="p-6 bg-white rounded-2xl border border-[#E3E0D5] text-center text-xs text-[#5B6B62]">
              {t('waiting_recycler_quotes')}
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {quotes.map((q) => (
                <QuoteCard
                  key={q.id}
                  id={q.id}
                  recyclerName={q.recycler_name}
                  cpcbLicense={q.recycler_cpcb_license}
                  rating={q.recycler_rating}
                  pricePaise={q.price_paise_total}
                  pickupMode={q.pickup_mode}
                  etaHours={2}
                  isBestPrice={q.is_best_price}
                  isNearest={q.is_nearest}
                  onAccept={() => handleAcceptQuote(q.id)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Cancel Lot Action if active */}
      {['listed', 'quoted', 'accepted', 'pickup_scheduled'].includes(lot.status) && (
        <div className="pt-2">
          <button
            onClick={() => setShowCancelModal(true)}
            className="w-full py-3 rounded-xl border border-[#D64545] text-[#D64545] hover:bg-[#FBE7E7] text-xs font-bold transition-colors cursor-pointer touch-target"
          >
            {t('btn_cancel_lot')}
          </button>
        </div>
      )}

      {/* Cancel Reason Modal (Addendum 12A(C)) */}
      {showCancelModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-sm w-full border border-[#E3E0D5] shadow-2xl flex flex-col gap-4">
            <h3 className="text-base font-bold text-[#D64545]">{t('cancel_modal_title')}</h3>
            <p className="text-xs text-[#5B6B62]">{t('cancel_modal_sub')}</p>
            
            <div className="flex flex-col gap-2">
              {[
                { code: 'found_better_price', label: t('reason_better_price') },
                { code: 'sold_locally', label: t('reason_sold_locally') },
                { code: 'not_ready', label: t('reason_not_ready') },
                { code: 'wrong_weight', label: t('reason_wrong_weight') },
                { code: 'other', label: t('reason_other') },
              ].map((r) => (
                <label key={r.code} className="flex items-center gap-2 p-2.5 rounded-xl border border-[#E3E0D5] text-xs font-semibold cursor-pointer hover:bg-[#F7F5EF]">
                  <input
                    type="radio"
                    name="cancel_reason"
                    checked={cancelReason === r.code}
                    onChange={() => setCancelReason(r.code)}
                  />
                  <span>{r.label}</span>
                </label>
              ))}
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={() => setShowCancelModal(false)}
                className="flex-1 py-2.5 rounded-xl bg-[#F7F5EF] text-[#5B6B62] text-xs font-bold cursor-pointer"
              >
                {t('btn_keep_lot')}
              </button>
              <button
                onClick={handleCancelLot}
                className="flex-1 py-2.5 rounded-xl bg-[#D64545] text-white text-xs font-bold cursor-pointer"
              >
                {t('btn_confirm_cancel')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
