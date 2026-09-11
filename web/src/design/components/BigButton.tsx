import React from 'react';
import { VoiceButton } from './VoiceButton';

interface BigButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: React.ReactNode;
  label: string;
  variant?: 'primary' | 'secondary' | 'scrap' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  voiceText?: string;
  showVoice?: boolean;
}

export const BigButton: React.FC<BigButtonProps> = ({
  icon,
  label,
  variant = 'primary',
  size = 'lg',
  voiceText,
  showVoice = true,
  className = '',
  disabled,
  ...props
}) => {
  const variantStyles = {
    primary: 'bg-[#14634A] hover:bg-[#0B3D2E] text-white shadow-sm',
    secondary: 'bg-white hover:bg-[#F7F5EF] text-[#14201A] border border-[#E3E0D5]',
    scrap: 'bg-[#E9A310] hover:bg-[#c98907] text-[#14201A] font-bold shadow-sm',
    danger: 'bg-[#D64545] hover:bg-[#b03030] text-white shadow-sm'
  };

  const sizeStyles = {
    sm: 'min-h-[44px] px-4 py-2 text-sm',
    md: 'min-h-[50px] px-5 py-3 text-base',
    lg: 'min-h-[56px] px-6 py-3.5 text-lg font-semibold'
  };

  return (
    <div className="relative inline-flex items-center w-full">
      <button
        disabled={disabled}
        className={`w-full flex items-center justify-center gap-3 rounded-xl transition-all select-none active:scale-[0.99] disabled:opacity-50 disabled:pointer-events-none cursor-pointer ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
        {...props}
      >
        {icon && <span className="shrink-0">{icon}</span>}
        <span className="truncate">{label}</span>
      </button>

      {showVoice && (
        <div className="absolute right-2 shrink-0">
          <VoiceButton text={voiceText || label} size={18} className={variant === 'primary' || variant === 'danger' ? 'text-white/80 hover:text-white hover:bg-white/20' : ''} />
        </div>
      )}
    </div>
  );
};
