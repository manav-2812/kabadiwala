import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../lib/api';
import { formatINR, formatDate } from '../../lib/format';
import { MoneyCard } from '../../design/components/MoneyCard';
import { BigButton } from '../../design/components/BigButton';
import { StatusPill } from '../../design/components/StatusPill';
import { 
  Wallet, ArrowDownLeft, ShieldCheck, FileText, Download, 
  Building, Phone, AlertCircle, CheckCircle2, DollarSign, ToggleLeft, ToggleRight
} from 'lucide-react';
import { useTranslation } from 'react-i18next';

export const WalletView: React.FC = () => {
  const [wallet, setWallet] = useState<any>(null);
  const [dues, setDues] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [enableDigital, setEnableDigital] = useState(false);
  const [showWithdraw, setShowWithdraw] = useState(false);
  const [withdrawAmt, setWithdrawAmt] = useState('500');
  const [withdrawing, setWithdrawing] = useState(false);
  const [settlingId, setSettlingId] = useState<string | null>(null);
  const { t } = useTranslation();

  const fetchWallet = () => {
    apiRequest('/api/wallet')
      .then((data) => {
        setWallet(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    apiRequest('/api/wallet/dues')
      .then(setDues)
      .catch(() => {});

    apiRequest('/api/wallet/history')
      .then(setHistory)
      .catch(() => {});
  };

  useEffect(() => {
    fetchWallet();
  }, []);

  const handleSettleDue = async (transactionId: string) => {
    setSettlingId(transactionId);
    try {
      await apiRequest(`/api/transactions/${transactionId}/settle-due`, {
        method: 'POST'
      });
      alert('Cash payment confirmed and recorded in Earnings Ledger!');
      fetchWallet();
    } catch (err: any) {
      alert(err.detail?.message_key || 'Failed to settle due');
    } finally {
      setSettlingId(null);
    }
  };

  const handleWithdraw = async () => {
    const paise = parseInt(withdrawAmt) * 100;
    setWithdrawing(true);
    try {
      await apiRequest('/api/wallet/withdraw', {
        method: 'POST',
        body: JSON.stringify({ amount_paise: paise })
      });
      alert(`Withdrawal of ₹${withdrawAmt} initiated to ${wallet.upi_id}`);
      setShowWithdraw(false);
      fetchWallet();
    } catch (err: any) {
      alert(err.detail?.message_key || 'Withdrawal failed. Minimum amount is ₹50.');
    } finally {
      setWithdrawing(false);
    }
  };

  if (loading || !wallet) {
    return <div className="p-6 text-center text-xs text-[#5B6B62]">{t('earnings_ledger_title')}...</div>;
  }

  const totalDuesPaise = wallet.pending_dues_paise || dues.reduce((acc, d) => acc + (d.balance_paise || 0), 0);

  return (
    <div className="flex flex-col gap-5 pb-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#E3E0D5] pb-3">
        <div className="flex items-center gap-2">
          <Wallet size={22} className="text-[#0B3D2E]" />
          <div>
            <h2 className="text-lg font-black text-[#0B3D2E] tracking-tight">
              {t('earnings_ledger_title')}
            </h2>
            <span className="text-xs text-[#5B6B62]">{t('earnings_ledger_desc')}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-1.5 cursor-pointer text-xs font-semibold text-[#5B6B62] bg-white px-2.5 py-1 rounded-xl border border-[#E3E0D5]">
            <input
              type="checkbox"
              checked={enableDigital}
              onChange={(e) => setEnableDigital(e.target.checked)}
              className="w-3.5 h-3.5 text-[#14634A] rounded"
            />
            <span>{t('digital_payments_toggle')}</span>
          </label>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-5">
        {/* Left Col: Cash Earnings & Formal Premium */}
        <div className="md:col-span-5 flex flex-col gap-4">
          <MoneyCard
            label={t('cash_in_hand_label')}
            amountPaise={wallet.total_earned_paise || wallet.wallet_balance_paise}
            subtitle={t('cash_in_hand_sub')}
            badgeText={t('trust_score_label', { score: wallet.trust_score })}
          />

          {/* Digital Withdrawal (Behind explicit toggle) */}
          {enableDigital ? (
            <div className="p-4 rounded-2xl bg-white border border-[#2F6FDE]/40 flex flex-col gap-2.5 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-[#2F6FDE] uppercase">{t('digital_payout_title')}</span>
                <span className="text-xs font-mono text-[#5B6B62]">{wallet.upi_id}</span>
              </div>
              <BigButton
                label={t('btn_withdraw')}
                onClick={() => setShowWithdraw(true)}
                variant="primary"
                icon={<ArrowDownLeft size={20} />}
              />
            </div>
          ) : (
            <div className="p-3.5 rounded-2xl bg-[#F7F5EF] border border-[#E3E0D5] text-xs text-[#5B6B62] flex items-center justify-between">
              <span>{t('payment_mode_cash')}</span>
              <span className="text-[11px] text-[#14634A] font-bold">{t('cash_first_handover')}</span>
            </div>
          )}

          {/* Formal vs Informal Premium Card */}
          <div className="p-4 rounded-2xl bg-[#E4F4EA] border border-[#2E9E5B]/40 flex flex-col gap-1.5 shadow-xs">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-xs font-bold text-[#0B3D2E] uppercase tracking-wider">
                <ShieldCheck size={16} className="text-[#2E9E5B]" />
                <span>{t('formal_premium')}</span>
              </div>
              <span className="text-xs font-bold text-[#2E9E5B] bg-white px-2 py-0.5 rounded-md">
                {t('value_boost_label')}
              </span>
            </div>
            <span className="text-2xl font-black tabular-nums text-[#0B3D2E]">
              {formatINR(wallet.formal_premium_paise)}
            </span>
            <p className="text-xs text-[#14201A] leading-relaxed">
              {t('formal_premium_note')} {t('formal_channels_benefit')}
            </p>
          </div>
        </div>

        {/* Right Col: Pending Buyer Dues & Handover History */}
        <div className="md:col-span-7 flex flex-col gap-4">
          {/* Prominent Pending Buyer Dues Card */}
          <div className="p-4 rounded-2xl bg-[#FFF8E7] border-2 border-[#E9A310] flex flex-col gap-3 shadow-xs">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle size={20} className="text-[#E9A310]" />
                <div>
                  <h3 className="text-sm font-extrabold text-[#0B3D2E]">{t('pending_dues_title')}</h3>
                  <span className="text-[11px] text-[#5B6B62]">{t('pending_dues_detail')}</span>
                </div>
              </div>
              <span className="text-base font-black text-[#D64545] tabular-nums">
                {formatINR(totalDuesPaise)}
              </span>
            </div>

            {dues.length === 0 ? (
              <div className="p-3 bg-white rounded-xl border border-[#E3E0D5] text-center text-xs text-[#5B6B62]">
                ✅ {t('all_settled_msg')}
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                {dues.map((due) => (
                  <div
                    key={due.transaction_id}
                    className="p-3 bg-white rounded-xl border border-[#E3E0D5] flex flex-col gap-2"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="text-xs font-bold text-[#0B3D2E]">{due.buyer_name}</h4>
                        <span className="text-[11px] text-[#5B6B62] block">
                          Lot: {due.lot_code} • {t('due_by_date', { date: due.due_date ? formatDate(due.due_date) : '7d' })}
                        </span>
                      </div>
                      <span className="text-xs font-black text-[#D64545] tabular-nums">
                        {formatINR(due.balance_paise)}
                      </span>
                    </div>

                    <div className="flex items-center justify-between pt-1 border-t border-[#F7F5EF]">
                      <a
                        href="#"
                        onClick={(e) => { e.preventDefault(); }}
                        title="Calling is disabled in demo"
                        className="inline-flex items-center gap-1.5 text-xs font-bold text-[#14634A] opacity-75 cursor-not-allowed hover:underline"
                      >
                        <Phone size={13} />
                        <span>{t('btn_call_buyer', { phone: due.buyer_phone })}</span>
                      </a>

                      <button
                        onClick={() => handleSettleDue(due.transaction_id)}
                        disabled={settlingId === due.transaction_id}
                        className="py-1.5 px-3 rounded-lg bg-[#14634A] text-white text-xs font-bold flex items-center gap-1 hover:bg-[#0B3D2E] cursor-pointer"
                      >
                        <CheckCircle2 size={13} />
                        <span>{t('btn_mark_cash_received')}</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Payout & Handover History */}
          <div className="flex flex-col gap-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#5B6B62]">
              {t('cash_history_title', { count: history.length })}
            </h3>

            {history.length === 0 ? (
              <div className="p-6 bg-white rounded-2xl border border-[#E3E0D5] text-center text-xs text-[#5B6B62]">
                {t('no_handovers_yet')}
              </div>
            ) : (
              <div className="space-y-2.5">
                {history.map((h) => (
                  <div
                    key={h.id}
                    className="flex items-center justify-between p-3.5 bg-white rounded-2xl border border-[#E3E0D5] shadow-xs"
                  >
                    <div>
                      <div className="flex items-center gap-1.5">
                        <h4 className="text-sm font-bold text-[#0B3D2E]">{h.lot_code}</h4>
                        <StatusPill status={h.status} />
                      </div>
                      <span className="text-xs text-[#5B6B62] block mt-0.5">
                        {formatDate(h.paid_at)} • {t('receipt_number_label', { receipt: h.receipt_no || h.upi_ref })}
                      </span>
                    </div>

                    <div className="text-right">
                      <span className="text-sm font-extrabold text-[#14201A] tabular-nums block">
                        {formatINR(h.amount_paise)}
                      </span>
                      <span className="text-[10px] font-bold text-[#14634A]">💵 {t('cash_confirmed_buyer')}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Withdrawal Modal (Only when toggle enabled) */}
      {showWithdraw && enableDigital && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-sm w-full border border-[#E3E0D5] shadow-2xl flex flex-col gap-4">
            <h3 className="text-base font-bold text-[#0B3D2E]">Withdraw to Bank / UPI</h3>
            <p className="text-xs text-[#5B6B62]">Funds will transfer immediately to {wallet.upi_id}</p>

            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-[#5B6B62]">Amount (₹)</label>
              <input
                type="number"
                min="50"
                value={withdrawAmt}
                onChange={(e) => setWithdrawAmt(e.target.value)}
                className="text-2xl font-bold p-3 rounded-xl border border-[#E3E0D5] text-[#14201A] tabular-nums"
              />
              <span className="text-[11px] text-[#5B6B62]">Min ₹50 • Zero withdrawal fee</span>
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={() => setShowWithdraw(false)}
                className="flex-1 py-3 rounded-xl bg-[#F7F5EF] text-[#5B6B62] text-xs font-bold cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleWithdraw}
                disabled={withdrawing}
                className="flex-1 py-3 rounded-xl bg-[#14634A] text-white text-xs font-bold cursor-pointer"
              >
                Confirm Transfer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
