import React from 'react';

interface InitialsAvatarProps {
  name: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const PALETTE = [
  { bg: '#0B3D2E', text: '#FFFFFF' }, // Forest Green
  { bg: '#1E3A8A', text: '#FFFFFF' }, // Deep Blue
  { bg: '#7C2D12', text: '#FFFFFF' }, // Rich Umber
  { bg: '#581C87', text: '#FFFFFF' }, // Royal Purple
  { bg: '#0E7490', text: '#FFFFFF' }, // Teal
  { bg: '#9A3412', text: '#FFFFFF' }, // Terracotta
  { bg: '#365314', text: '#FFFFFF' }, // Olive
  { bg: '#831843', text: '#FFFFFF' }, // Berry
];

export const InitialsAvatar: React.FC<InitialsAvatarProps> = ({
  name,
  size = 'md',
  className = ''
}) => {
  // Extract initials (first letters of first and last name)
  const cleanName = (name || '').trim();
  const parts = cleanName.split(/\s+/).filter(Boolean);
  let initials = 'KC';
  if (parts.length >= 2) {
    initials = (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  } else if (parts.length === 1 && parts[0].length >= 1) {
    initials = parts[0].slice(0, 2).toUpperCase();
  }

  // Deterministic color from name
  let hash = 0;
  for (let i = 0; i < cleanName.length; i++) {
    hash = cleanName.charCodeAt(i) + ((hash << 5) - hash);
  }
  const color = PALETTE[Math.abs(hash) % PALETTE.length];

  const sizeClasses = {
    sm: 'w-7 h-7 text-xs',
    md: 'w-10 h-10 text-sm font-bold',
    lg: 'w-14 h-14 text-lg font-bold',
    xl: 'w-20 h-20 text-2xl font-black'
  };

  return (
    <div
      className={`inline-flex items-center justify-center rounded-full shrink-0 select-none shadow-xs ${sizeClasses[size]} ${className}`}
      style={{ backgroundColor: color.bg, color: color.text }}
      aria-label={cleanName}
      title={cleanName}
    >
      <span>{initials}</span>
    </div>
  );
};
