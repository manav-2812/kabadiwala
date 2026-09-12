import React from 'react';
import { useTranslation } from 'react-i18next';

interface StatusPillProps {
  status: string;
  className?: string;
}

export const StatusPill: React.FC<StatusPillProps> = ({ status, className = '' }) => {
  const { t } = useTranslation();
  const norm = (status || '').toLowerCase();

  let styles = 'bg-[#F7F5EF] text-[#5B6B62] border-[#E3E0D5]';
  const defaultLabel = (status || '').replace(/_/g, ' ');
  const label = t(`status_${norm}`, defaultLabel);

  if (norm.includes('complete') || norm.includes('verified') || norm.includes('success')) {
    styles = 'bg-[#E4F4EA] text-[#0B3D2E] border-[#2E9E5B]/40 font-semibold';
  } else if (norm.includes('dispute') || norm.includes('failed') || norm.includes('cancel') || norm.includes('tamper')) {
    styles = 'bg-[#FBE7E7] text-[#D64545] border-[#D64545]/40 font-semibold';
  } else if (norm.includes('transit') || norm.includes('arrived') || norm.includes('schedule') || norm.includes('confirm')) {
    styles = 'bg-[#E5EEFC] text-[#2F6FDE] border-[#2F6FDE]/40 font-semibold';
  } else if (norm.includes('quote') || norm.includes('listed') || norm.includes('pending')) {
    styles = 'bg-[#FCF3D9] text-[#14201A] border-[#E9A310]/40 font-semibold';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs border uppercase tracking-wider ${styles} ${className}`}>
      {label}
    </span>
  );
};
