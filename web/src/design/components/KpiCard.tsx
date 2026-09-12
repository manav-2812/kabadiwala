import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface KpiCardProps {
  label: string;
  value: string | number;
  delta?: string;
  isPositive?: boolean;
  unit?: string;
  icon?: React.ReactNode;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  label,
  value,
  delta,
  isPositive = true,
  unit,
  icon
}) => {
  return (
    <div className="flex flex-col p-4 rounded-2xl bg-white border border-[#E3E0D5] gap-2 shadow-xs">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#5B6B62]">
          {label}
        </span>
        {icon && <span className="text-[#14634A]">{icon}</span>}
      </div>

      <div className="flex items-baseline gap-2">
        <span className="text-2xl sm:text-3xl font-bold tabular-nums text-[#0B3D2E] tracking-tight">
          {value}
        </span>
        {unit && <span className="text-xs font-bold text-[#5B6B62]">{unit}</span>}
      </div>

      {delta && (
        <div className="flex items-center gap-1 mt-0.5">
          <span
            className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded-md text-xs font-bold ${
              isPositive
                ? 'bg-[#E4F4EA] text-[#0B3D2E]'
                : 'bg-[#FBE7E7] text-[#D64545]'
            }`}
          >
            {isPositive ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
            <span>{delta}</span>
          </span>
          <span className="text-[11px] text-[#5B6B62]">vs prior period</span>
        </div>
      )}
    </div>
  );
};
