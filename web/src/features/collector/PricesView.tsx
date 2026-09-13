import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../lib/api';
import { formatINR } from '../../lib/format';
import { VoiceButton } from '../../design/components/VoiceButton';
import { TrendingUp, ArrowUpRight, ArrowDownRight, Bell, AlertTriangle, MapPin, Volume2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { speakMaterialRate } from '../../lib/spokenPriceBoard';

export const PricesView: React.FC = () => {
  const [prices, setPrices] = useState<any[]>([]);
  const [city, setCity] = useState('Delhi NCR');
  const [loading, setLoading] = useState(true);
  const { t, i18n } = useTranslation();

  const CITIES = ['Delhi NCR', 'Chandigarh', 'Ludhiana', 'Amritsar', 'Jaipur', 'Lucknow', 'Mumbai', 'Bengaluru', 'Ranchi'];

  useEffect(() => {
    apiRequest(`/api/prices/summary?city=${encodeURIComponent(city)}`)
      .then((data) => {
        setPrices(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [city]);

  const handleSetAlert = (item: any) => {
    const threshold = prompt(`Set price alert for ${item.name_en}. Alert when price goes above (₹/kg):`, (item.current_price_paise_per_kg / 100).toString());
    if (threshold) {
      apiRequest('/api/price-alerts', {
        method: 'POST',
        body: JSON.stringify({
          material_id: item.material_id,
          direction: 'above',
          threshold_paise: parseInt(threshold) * 100
        })
      }).then(() => alert(`Price alert set for ${item.name_en} above ₹${threshold}/kg`));
    }
  };

  const getMatName = (p: any) => {
    if (i18n.language === 'mr') return t(`categories.${p.material_code}`, p.name_mr || p.name_en);
    if (i18n.language === 'hi') return t(`categories.${p.material_code}`, p.name_hi || p.name_en);
    if (i18n.language === 'pa') return t(`categories.${p.material_code}`, p.name_pa || p.name_en);
    return p.name_en || t(`categories.${p.material_code}`, '');
  };

  const getTrendReason = (p: any) => {
    if (i18n.language === 'mr') return p.trend_reason_mr || p.trend_reason_hi || p.trend_reason_en;
    if (i18n.language === 'hi') return p.trend_reason_hi;
    if (i18n.language === 'pa') return p.trend_reason_pa;
    return p.trend_reason_en;
  };

  return (
    <div className="flex flex-col gap-4 pb-6">
      {/* Header & City Selector */}
      <div className="flex items-center justify-between border-b border-[#E3E0D5] pb-2">
        <div className="flex items-center gap-2">
          <TrendingUp size={22} className="text-[#0B3D2E]" />
          <h2 className="text-lg font-black text-[#0B3D2E] tracking-tight">
            {t('nav_prices')}
          </h2>
        </div>

        <select
          value={city}
          onChange={(e) => setCity(e.target.value)}
          className="py-1 px-2.5 rounded-xl border border-[#E3E0D5] bg-white text-xs font-bold text-[#14201A] focus:outline-none focus:border-[#14634A]"
        >
          {CITIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="p-6 text-center text-xs text-[#5B6B62]">{t('loading_prices')}</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {prices.map((p) => {
            const isUp = p.change_pct_14d >= 0;
            const matName = getMatName(p);
            const trendReason = getTrendReason(p);

            return (
              <div
                key={p.material_code}
                className="flex flex-col p-4 rounded-2xl bg-white border border-[#E3E0D5] shadow-xs gap-2"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-1.5">
                      <h4 className="text-base font-bold text-[#0B3D2E]">{matName}</h4>
                      {p.is_hazardous && (
                        <span className="text-[#D64545]" title="Hazardous material">
                          <AlertTriangle size={14} />
                        </span>
                      )}
                    </div>
                    <span className="text-[11px] text-[#5B6B62]">
                      {t('formal_buyback_std', { city })}
                    </span>
                  </div>

                  <div className="text-right">
                    <span className="text-xl font-extrabold text-[#14201A] tabular-nums">
                      {formatINR(p.current_price_paise_per_kg)}
                    </span>
                    <span className="text-xs text-[#5B6B62] block">{t('unit_per_kg')}</span>
                  </div>
                </div>

                {/* 14-Day Delta & Mini Trend */}
                <div className="flex items-center justify-between pt-2 border-t border-[#E3E0D5]">
                  <div className="flex items-center gap-1.5">
                    <span
                      className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded-md text-xs font-bold ${
                        isUp ? 'bg-[#E4F4EA] text-[#0B3D2E]' : 'bg-[#FBE7E7] text-[#D64545]'
                      }`}
                    >
                      {isUp ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                      <span>{isUp ? `+${p.change_pct_14d}%` : `${p.change_pct_14d}%`} ({t('shift_14d')})</span>
                    </span>

                    <button
                      onClick={() => speakMaterialRate(p.material_code, matName, Math.round(p.current_price_paise_per_kg / 100), i18n.language)}
                      className="p-1.5 px-2 rounded-xl bg-[#F7F5EF] text-[#14634A] hover:bg-[#E7F3ED] cursor-pointer flex items-center gap-1 text-[11px] font-bold"
                      title="Speak Price Aloud in Vernacular"
                    >
                      <Volume2 size={14} />
                      <span>{t('btn_speak')}</span>
                    </button>
                  </div>

                  <button
                    onClick={() => handleSetAlert(p)}
                    className="flex items-center gap-1 text-xs font-bold text-[#14634A] hover:underline cursor-pointer"
                  >
                    <Bell size={13} />
                    <span>{t('btn_set_alert')}</span>
                  </button>
                </div>

                {/* Why It Changed One-Liner (Section 5.1(9)) */}
                <p className="text-xs text-[#5B6B62] italic bg-[#F7F5EF] p-2 rounded-xl mt-1">
                  "{trendReason}"
                </p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
