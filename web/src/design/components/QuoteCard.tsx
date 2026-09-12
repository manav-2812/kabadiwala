import React from 'react';
import { formatINR } from '../../lib/format';
import { ShieldCheck, Star, Clock, CheckCircle } from 'lucide-react';
import { VoiceButton } from './VoiceButton';
import { useTranslation } from 'react-i18next';

interface QuoteCardProps {
  id: string;
  recyclerName: string;
  cpcbLicense: string;
  rating: number;
  pricePaise: number;
  pickupMode: string;
  etaHours: number;
  isBestPrice?: boolean;
  isNearest?: boolean;
  onAccept: () => void;
}

export const QuoteCard: React.FC<QuoteCardProps> = ({
  recyclerName,
  cpcbLicense,
  rating,
  pricePaise,
  pickupMode,
  etaHours,
  isBestPrice = false,
  isNearest = false,
  onAccept
}) => {
  const { t } = useTranslation();
  const formattedPrice = formatINR(pricePaise);

  return (
    <div className="flex flex-col p-4 rounded-2xl bg-white border border-[#E3E0D5] hover:border-[#14634A] transition-all gap-3 shadow-xs">
      {/* Badges */}
      <div className="flex items-center gap-2">
        {isBestPrice && (
          <span className="px-2 py-0.5 rounded-md bg-[#2E9E5B] text-white text-[11px] font-extrabold uppercase tracking-wide">
            {t('best_price')}
          </span>
        )}
        {isNearest && (
          <span className="px-2 py-0.5 rounded-md bg-[#2F6FDE] text-white text-[11px] font-extrabold uppercase tracking-wide">
            {t('nearest')}
          </span>
        )}
        <div className="ml-auto">
          <VoiceButton text={`Offer from ${recyclerName}: ${formattedPrice}`} size={16} />
        </div>
      </div>

      <div className="flex items-start justify-between">
        <div>
          <h4 className="text-base font-bold text-[#0B3D2E]">{recyclerName}</h4>
          <div className="flex items-center gap-2 text-xs text-[#5B6B62] mt-0.5">
            <span className="flex items-center gap-1 font-semibold text-[#14201A]">
              <Star size={12} className="text-[#E9A310] fill-[#E9A310]" />
              {rating.toFixed(1)}
            </span>
            <span>•</span>
            <span className="truncate">{cpcbLicense}</span>
          </div>
        </div>

        <div className="text-right">
          <span className="text-2xl font-extrabold tabular-nums text-[#0B3D2E]">
            {formattedPrice}
          </span>
          <span className="block text-[11px] text-[#5B6B62]">{pickupMode === 'pickup' ? t('pickup_doorstep') : t('pickup_dropoff')}</span>
        </div>
      </div>

      <div className="flex items-center gap-1 text-xs text-[#5B6B62] pt-1 border-t border-[#E3E0D5]">
        <Clock size={13} className="text-[#14634A]" />
        <span>{t('pickup_eta_desc', { hours: etaHours })}</span>
      </div>

      <button
        onClick={onAccept}
        className="w-full min-h-[50px] py-2.5 px-4 rounded-xl bg-[#14634A] hover:bg-[#0B3D2E] active:scale-98 text-white font-bold text-base flex items-center justify-center gap-2 transition-all cursor-pointer touch-target shadow-sm"
      >
        <CheckCircle size={18} />
        <span>{t('btn_accept')}</span>
      </button>
    </div>
  );
};
