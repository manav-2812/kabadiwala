import React from 'react';
import { VoiceButton } from './VoiceButton';
import { AlertTriangle } from 'lucide-react';

interface IconTileProps {
  icon: React.ReactNode;
  label: string;
  selected?: boolean;
  isHazardous?: boolean;
  onClick: () => void;
}

export const IconTile: React.FC<IconTileProps> = ({
  icon,
  label,
  selected = false,
  isHazardous = false,
  onClick
}) => {
  return (
    <div
      onClick={onClick}
      role="button"
      tabIndex={0}
      className={`relative flex flex-col items-center justify-center p-3.5 min-h-[104px] rounded-2xl cursor-pointer transition-all border select-none ${
        selected
          ? 'bg-[#E4F4EA] border-[#14634A] ring-2 ring-[#14634A] shadow-sm'
          : 'bg-white border-[#E3E0D5] hover:border-[#5B6B62]'
      }`}
    >
      {isHazardous && (
        <span className="absolute top-2 left-2 text-[#D64545]" title="Hazardous Material">
          <AlertTriangle size={15} />
        </span>
      )}

      <div className="absolute top-1 right-1">
        <VoiceButton text={label} size={15} />
      </div>

      <div className={`p-2 rounded-xl mb-1.5 ${selected ? 'text-[#0B3D2E]' : 'text-[#5B6B62]'}`}>
        {icon}
      </div>

      <span className="text-sm font-semibold text-center text-[#14201A] line-clamp-2 px-1">
        {label}
      </span>
    </div>
  );
};
