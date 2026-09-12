import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../lib/api';
import { formatINR, formatWeight } from '../../lib/format';
import { BigButton } from '../../design/components/BigButton';
import { SafetyBanner } from '../../design/components/SafetyBanner';
import { Trash2, Plus, ShoppingBag, AlertTriangle, ArrowRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export const Basket: React.FC = () => {
  const [basket, setBasket] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selling, setSelling] = useState(false);
  const navigate = useNavigate();
  const { t } = useTranslation();

  const fetchBasket = () => {
    apiRequest('/api/basket')
      .then((data) => {
        setBasket(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchBasket();
  }, []);

  const handleDeleteItem = async (itemId: string) => {
    await apiRequest(`/api/basket/items/${itemId}`, { method: 'DELETE' });
    fetchBasket();
  };

  const handleSellBasket = async () => {
    setSelling(true);
    try {
      const res = await apiRequest('/api/basket/sell', { method: 'POST' });
      navigate(`/lots/${res.lot_id}`);
    } catch (err: any) {
      alert(err.detail?.message_key || 'Failed to list basket');
      setSelling(false);
    }
  };

  if (loading) {
    return <div className="p-6 text-center text-xs text-[#5B6B62]">{t('loading_basket')}</div>;
  }

  const items = basket?.items || [];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between border-b border-[#E3E0D5] pb-2">
        <div className="flex items-center gap-2">
          <ShoppingBag size={22} className="text-[#0B3D2E]" />
          <h2 className="text-lg font-black text-[#0B3D2E] tracking-tight">
            {t('nav_basket')} ({items.length})
          </h2>
        </div>
        <button
          onClick={() => navigate('/add-scrap')}
          className="flex items-center gap-1 text-xs font-bold text-[#14634A] hover:underline cursor-pointer"
        >
          <Plus size={15} />
          <span>{t('btn_add_more_scrap')}</span>
        </button>
      </div>

      {items.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-8 text-center bg-white rounded-3xl border border-[#E3E0D5] gap-3">
          <div className="w-16 h-16 rounded-full bg-[#F7F5EF] flex items-center justify-center text-[#5B6B62]">
            <ShoppingBag size={32} />
          </div>
          <h3 className="text-base font-bold text-[#14201A]">{t('empty_basket')}</h3>
          <p className="text-xs text-[#5B6B62] max-w-xs">{t('empty_basket_sub')}</p>
          <button
            onClick={() => navigate('/add-scrap')}
            className="mt-2 px-6 py-3 rounded-xl bg-[#14634A] text-white text-sm font-bold cursor-pointer"
          >
            {t('btn_add_scrap')}
          </button>
        </div>
      ) : (
        <>
          {/* Running Totals Card */}
          <div className="p-4 rounded-2xl bg-[#FCF3D9] border border-[#E9A310]/40 flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-[#5B6B62] block">
                {t('total_estimated_value')} ({formatWeight(basket.est_total_weight_g)})
              </span>
              <span className="text-2xl font-black tabular-nums text-[#14201A]">
                {formatINR(basket.est_total_min_paise)} - {formatINR(basket.est_total_max_paise)}
              </span>
            </div>
            <span className="text-xs font-bold px-2 py-1 bg-[#2E9E5B] text-white rounded-lg">
              {t('badge_doorstep_free')}
            </span>
          </div>

          {/* Recoverable Minerals Chips */}
          {basket.recoverable_minerals && basket.recoverable_minerals.length > 0 && (
            <div className="flex flex-col gap-1.5 p-3 rounded-2xl bg-white border border-[#E3E0D5]">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#5B6B62]">
                {t('minerals_recoverable_est')}
              </span>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {basket.recoverable_minerals.map((m: any) => (
                  <span
                    key={m.element}
                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold ${
                      m.is_strategic
                        ? 'bg-[#E4F4EA] text-[#0B3D2E] border border-[#2E9E5B]/30'
                        : 'bg-[#F7F5EF] text-[#5B6B62]'
                    }`}
                  >
                    <span>{m.name}:</span>
                    <span className="tabular-nums font-black">{m.grams.toFixed(1)} g</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Hazard Notice if any item is hazardous */}
          {basket.is_hazardous && (
            <SafetyBanner
              hazardNote={t('safety_tip_body')}
              safetyTip={t('safety_tip_voice')}
              bonusINR={50}
            />
          )}

          {/* Items List */}
          <div className="flex flex-col gap-2.5">
            {items.map((item: any) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-3.5 bg-white rounded-2xl border border-[#E3E0D5] gap-3"
              >
                <div className="flex-1">
                  <h4 className="text-sm font-bold text-[#0B3D2E]">
                    {String(t(`categories.${item.material_code}`, item.material_name || item.material_code))}
                  </h4>
                  <div className="flex items-center gap-2 text-xs text-[#5B6B62] mt-0.5">
                    <span>{formatWeight(item.est_weight_g)}</span>
                    <span>•</span>
                    <span className="capitalize">{String(t(`condition_${item.condition}`, item.condition))}</span>
                  </div>
                  <span className="text-sm font-extrabold text-[#14201A] tabular-nums mt-1 block">
                    {formatINR(item.est_value_min_paise)} - {formatINR(item.est_value_max_paise)}
                  </span>
                </div>

                <button
                  onClick={() => handleDeleteItem(item.id)}
                  className="p-2.5 rounded-xl text-[#D64545] hover:bg-[#FBE7E7] cursor-pointer touch-target"
                  title="Remove from basket"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            ))}
          </div>

          {/* Sell Basket CTA */}
          <div className="pt-2">
            <BigButton
              label={t('btn_sell_basket')}
              onClick={handleSellBasket}
              disabled={selling}
              variant="scrap"
              icon={<ArrowRight size={20} />}
            />
          </div>
        </>
      )}
    </div>
  );
};
