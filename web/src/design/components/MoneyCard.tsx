import React from 'react';
import { formatINR } from '../../lib/format';
import { VoiceButton } from './VoiceButton';

interface MoneyCardProps {
  label: string;
  amountPaise: number;
  subtitle?: string;
  badgeText?: string;
  className?: string;
}

export const MoneyCard: React.FC<MoneyCardProps> = ({
  label,
  amountPaise,
  subtitle,
  badgeText,
  className = ''
}) => {
  const formatted = formatINR(amountPaise);

  return (
    <div className={`relative flex flex-col p-4 rounded-2xl bg-[#FCF3D9] border border-[#E9A310]/40 shadow-sm ${className}`}>
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-bold uppercase tracking-wider text-[#14201A]/70">
          {label}
        </span>
        {badgeText && (
          <span className="px-2 py-0.5 rounded-md bg-[#2E9E5B] text-white text-[11px] font-bold">
            {badgeText}
          </span>
        )}
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-baseline gap-1">
          <span className="text-3xl font-extrabold text-[#14201A] tabular-nums tracking-tight">
            {formatted}
          </span>
        </div>
        <VoiceButton text={`${label}: ${formatted}`} size={20} />
      </div>

      {subtitle && (
        <span className="text-xs text-[#5B6B62] mt-1 font-medium">
          {subtitle}
        </span>
      )}
    </div>
  );
};
