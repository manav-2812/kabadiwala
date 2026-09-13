import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiRequest } from '../../lib/api';
import { formatINR } from '../../lib/format';
import { BigButton } from '../../design/components/BigButton';
import { Check, ArrowRight, FileText, Wallet, ShieldCheck } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { VoiceButton } from '../../design/components/VoiceButton';

export const PaymentSuccess: React.FC = () => {
  const { id } = useParams<{ id: string }>(); // transaction_id
  const [tx, setTx] = useState<any>(null);
  const [payment, setPayment] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const navigate = useNavigate();
  const { t } = useTranslation();

  useEffect(() => {
    if (!id) return;
    apiRequest(`/api/transactions/${id}`)
      .then((data) => {
        setTx(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  const handlePayNow = async (method: string = 'upi') => {
    if (!id) return;
    setProcessing(true);
    try {
      const res = await apiRequest('/api/payments/initiate', {
        method: 'POST',
        body: JSON.stringify({ transaction_id: id, method })
      });
      setPayment(res);
      setProcessing(false);
    } catch {
      setProcessing(false);
    }
  };

  if (loading || !tx) {
    return <div className="p-6 text-center text-xs text-[#5B6B62]">{t('loading_payment')}</div>;
  }

  const amountPaise = tx.final_amount_paise || tx.agreed_amount_paise || 240000;
  const formattedAmount = formatINR(amountPaise);

  return (
    <div className="flex flex-col items-center text-center gap-5 pt-4 pb-8">
      {/* Checkmark draw / Success State */}
      <div className="w-20 h-20 rounded-full bg-[#E4F4EA] border-4 border-[#2E9E5B] flex items-center justify-center text-[#2E9E5B] shadow-lg animate-in zoom-in-50 duration-300">
        <Check size={44} strokeWidth={3} />
      </div>

      <div>
        <h2 className="text-2xl font-black text-[#0B3D2E] tracking-tight">
          {payment ? t('payment_success') : t('payment_ready_transfer')}
        </h2>
        <p className="text-xs text-[#5B6B62] mt-1">
          {t('epr_compliant_settled')}
        </p>
      </div>

      {/* Big Money Card */}
      <div className="w-full p-6 rounded-3xl bg-[#FCF3D9] border-2 border-[#E9A310] flex flex-col items-center gap-1 shadow-sm">
        <span className="text-xs font-bold uppercase tracking-wider text-[#14201A]/70">
          {t('total_net_payout')}
        </span>
        <div className="flex items-center gap-2">
          <span className="text-4xl sm:text-5xl font-extrabold text-[#14201A] tabular-nums tracking-tight">
            {formattedAmount}
          </span>
          <VoiceButton text={`Amount: ${formattedAmount}`} size={24} />
        </div>
        <div className="flex items-center gap-1.5 mt-2 px-3 py-1 rounded-full bg-[#2E9E5B] text-white text-xs font-bold">
          <ShieldCheck size={14} />
          <span>{t('platform_fee_zero')}</span>
        </div>
      </div>

      {/* Payment Reference Details */}
      {payment && (
        <div className="w-full p-4 rounded-2xl bg-white border border-[#E3E0D5] flex flex-col gap-2 text-left text-xs">
          <div className="flex justify-between">
            <span className="text-[#5B6B62]">{t('payment_reference')}:</span>
            <span className="font-mono font-bold text-[#14201A]">{payment.upi_ref}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-[#5B6B62]">{t('receipt_number')}:</span>
            <span className="font-bold text-[#14201A]">{tx.receipt_no}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-[#5B6B62]">{t('authorized_buyer_label')}:</span>
            <span className="font-bold text-[#0B3D2E]">{tx.buyer_name}</span>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="w-full flex flex-col gap-2.5 pt-2">
        {!payment ? (
          <>
            <BigButton
              label={t('btn_instant_upi')}
              onClick={() => handlePayNow('upi')}
              disabled={processing}
              variant="scrap"
              icon={<Check size={20} />}
            />
            <button
              onClick={() => handlePayNow('cash')}
              disabled={processing}
              className="py-3 px-4 rounded-xl border border-[#E3E0D5] bg-white text-[#14201A] text-xs font-bold hover:bg-[#F7F5EF] cursor-pointer touch-target"
            >
              {t('btn_collect_cash')}
            </button>
          </>
        ) : (
          <>
            <a
              href={`/api/documents/${tx.receipt_no}/pdf`}
              target="_blank"
              rel="noreferrer"
              className="w-full min-h-[50px] py-3 rounded-xl bg-[#14634A] hover:bg-[#0B3D2E] text-white text-sm font-bold flex items-center justify-center gap-2 cursor-pointer shadow-sm touch-target"
            >
              <FileText size={18} />
              <span>{t('view_receipt')}</span>
            </a>

            <button
              onClick={() => navigate('/wallet')}
              className="w-full py-3 rounded-xl bg-white border border-[#E3E0D5] text-[#0B3D2E] text-xs font-bold hover:bg-[#F7F5EF] cursor-pointer touch-target"
            >
              {t('btn_go_wallet')}
            </button>
          </>
        )}
      </div>
    </div>
  );
};
