import React from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';
import { VoiceButton } from './VoiceButton';

interface SafetyBannerProps {
  hazardNote: string;
  safetyTip: string;
  bonusINR?: number;
}

export const SafetyBanner: React.FC<SafetyBannerProps> = ({
  hazardNote,
  safetyTip,
  bonusINR = 50
}) => {
  return (
    <div className="flex flex-col gap-2 p-3.5 rounded-2xl bg-[#FBE7E7] border border-[#D64545]/40 text-[#14201A]">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-[#D64545] font-bold text-sm">
          <AlertTriangle size={18} className="shrink-0" />
          <span>Hazardous Scrap Handling Warning</span>
        </div>
        <VoiceButton text={`${hazardNote}. Safety Tip: ${safetyTip}`} size={16} />
      </div>

      <p className="text-xs text-[#14201A] leading-relaxed font-medium">
        {hazardNote}
      </p>

      <div className="flex items-center justify-between pt-2 border-t border-[#D64545]/20 mt-1">
        <div className="flex items-center gap-1.5 text-xs text-[#0B3D2E] font-semibold">
          <ShieldCheck size={16} className="text-[#2E9E5B]" />
          <span>Safe Handling Bonus: +₹{bonusINR}</span>
        </div>
        <span className="text-[11px] text-[#5B6B62]">Ministry of Mines Safe Protocol</span>
      </div>
    </div>
  );
};
