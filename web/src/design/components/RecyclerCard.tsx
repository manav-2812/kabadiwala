import React from 'react';
import { ShieldCheck, MapPin, Star, Truck, Calendar } from 'lucide-react';
import { formatINR } from '../../lib/format';
import { formatDate } from '../../lib/format';
import { VoiceButton } from './VoiceButton';
import { useTranslation } from 'react-i18next';

interface RecyclerCardProps {
  companyName: string;
  contactPerson: string;
  address: string;
  distanceKm: number;
  cpcbLicense: string;
  validTo: string;
  ratingAvg: number;
  reliabilityScore: number;
  pickupAvailable: boolean;
  estPayoutPaise: number;
  rankingReason?: string;
  onSelect?: () => void;
}

export const RecyclerCard: React.FC<RecyclerCardProps> = ({
  companyName,
  address,
  distanceKm,
  cpcbLicense,
  validTo,
  ratingAvg,
  reliabilityScore,
  pickupAvailable,
  estPayoutPaise,
  rankingReason,
  onSelect
}) => {
  const { t } = useTranslation();

  return (
    <div className="flex flex-col p-4 rounded-2xl bg-white border border-[#E3E0D5] hover:border-[#14634A] transition-all shadow-xs gap-3">
      {rankingReason && (
        <div className="flex items-center justify-between bg-[#FCF3D9] text-[#14201A] px-2.5 py-1 rounded-lg text-xs font-bold">
          <span>{rankingReason}</span>
          <span className="text-[11px] text-[#5B6B62]">{t('reliability_score_label', { score: reliabilityScore })}</span>
        </div>
      )}

      <div className="flex items-start justify-between gap-2">
        <div>
          <h4 className="text-base font-bold text-[#0B3D2E] leading-snug">
            {companyName}
          </h4>
          <div className="flex items-center gap-1.5 text-xs text-[#5B6B62] mt-0.5">
            <MapPin size={13} className="text-[#5B6B62]" />
            <span>{t('distance_km_away', { distance: distanceKm })} • {address}</span>
          </div>
        </div>

        <div className="flex flex-col items-end shrink-0">
          <span className="text-lg font-black tabular-nums text-[#E9A310]">
            {formatINR(estPayoutPaise)}
          </span>
          <span className="text-[10px] text-[#5B6B62]">{t('est_net_payout')}</span>
        </div>
      </div>

      {/* CPCB Verified Badge */}
      <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#E3E0D5]">
        <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#E4F4EA] text-[#0B3D2E] text-[11px] font-bold border border-[#2E9E5B]/40">
          <ShieldCheck size={13} className="text-[#2E9E5B]" />
          <span>CPCB: {cpcbLicense}</span>
        </div>

        <div className="flex items-center gap-1 text-xs text-[#14201A] font-semibold">
          <Star size={13} className="text-[#E9A310] fill-[#E9A310]" />
          <span>{ratingAvg.toFixed(1)}</span>
        </div>

        <div className="flex items-center gap-1 text-[11px] text-[#5B6B62]">
          <Calendar size={12} />
          <span>{t('license_valid_until', { date: formatDate(validTo) })}</span>
        </div>

        {pickupAvailable && (
          <div className="flex items-center gap-1 text-[11px] text-[#0B3D2E] font-medium ml-auto">
            <Truck size={12} className="text-[#14634A]" />
            <span>{t('pickup_doorstep')}</span>
          </div>
        )}
      </div>

      {onSelect && (
        <button
          onClick={onSelect}
          className="w-full py-2.5 rounded-xl bg-[#14634A] hover:bg-[#0B3D2E] text-white text-sm font-bold transition-colors cursor-pointer touch-target"
        >
          {t('btn_request_quote')}
        </button>
      )}
    </div>
  );
};
