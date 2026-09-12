import React from 'react';
import { useTranslation } from 'react-i18next';
import { StatusPill } from './StatusPill';
import { formatINR, formatWeight } from '../../lib/format';
import { ArrowRight, AlertTriangle, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface LotCardProps {
  id: string;
  lotCode: string;
  status: string;
  estMinPaise: number;
  estMaxPaise: number;
  finalPaise?: number;
  weightGrams: number;
  isHazardous?: boolean;
  itemCount: number;
  createdAt: string;
}

export const LotCard: React.FC<LotCardProps> = ({
  id,
  lotCode,
  status,
  estMinPaise,
  estMaxPaise,
  finalPaise,
  weightGrams,
  isHazardous = false,
  itemCount,
  createdAt
}) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const displayAmount = finalPaise
    ? formatINR(finalPaise)
    : `${formatINR(estMinPaise)} - ${formatINR(estMaxPaise)}`;

  return (
    <div
      onClick={() => navigate(`/lots/${id}`)}
      className="flex flex-col p-4 rounded-2xl bg-white border border-[#E3E0D5] hover:border-[#14634A] transition-all cursor-pointer shadow-xs gap-3 select-none"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-extrabold text-[#0B3D2E] tracking-tight">
            {lotCode}
          </span>
          {isHazardous && (
            <span className="text-[#D64545]" title="Hazardous scrap present">
              <AlertTriangle size={15} />
            </span>
          )}
        </div>
        <StatusPill status={status} />
      </div>

      <div className="flex items-end justify-between">
        <div>
          <span className="text-xs text-[#5B6B62] block mb-0.5">
            {t('items_count', { count: itemCount })} • {formatWeight(weightGrams)}
          </span>
          <span className="text-xl font-black tabular-nums text-[#14201A]">
            {displayAmount}
          </span>
        </div>

        <div className="w-8 h-8 rounded-full bg-[#F7F5EF] flex items-center justify-center text-[#14634A] group-hover:translate-x-1 transition-transform">
          <ArrowRight size={16} />
        </div>
      </div>
    </div>
  );
};
