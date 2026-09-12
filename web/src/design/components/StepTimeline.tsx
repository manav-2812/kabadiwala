import React from 'react';
import { Check, Clock, Truck, Scale, DollarSign, Package } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface StepTimelineProps {
  currentStatus: string;
}

export const StepTimeline: React.FC<StepTimelineProps> = ({ currentStatus }) => {
  const { t } = useTranslation();
  const norm = currentStatus.toLowerCase();

  const STEPS = [
    { key: 'listed', label: t('timeline_listed'), icon: <Package size={16} /> },
    { key: 'quoted', label: t('timeline_quoted'), icon: <Clock size={16} /> },
    { key: 'accepted', label: t('timeline_accepted'), icon: <Check size={16} /> },
    { key: 'pickup', label: t('timeline_pickup'), icon: <Truck size={16} /> },
    { key: 'weighed', label: t('timeline_weighed'), icon: <Scale size={16} /> },
    { key: 'paid', label: t('timeline_paid'), icon: <DollarSign size={16} /> },
  ];

  const getStepIndex = (status: string) => {
    if (status.includes('complete')) return 5;
    if (status.includes('weighed') || status.includes('awaiting')) return 4;
    if (status.includes('transit') || status.includes('arrived') || status.includes('schedule')) return 3;
    if (status.includes('accept')) return 2;
    if (status.includes('quote')) return 1;
    return 0;
  };

  const activeIdx = getStepIndex(norm);

  return (
    <div className="w-full py-2">
      <div className="flex items-center justify-between relative">
        {/* Track */}
        <div className="absolute top-1/2 left-4 right-4 -translate-y-1/2 h-1 bg-[#E3E0D5] z-0" />
        <div
          className="absolute top-1/2 left-4 -translate-y-1/2 h-1 bg-[#2E9E5B] z-0 transition-all duration-500"
          style={{ width: `${(activeIdx / (STEPS.length - 1)) * 90}%` }}
        />

        {STEPS.map((step, idx) => {
          const isDone = idx < activeIdx;
          const isCurrent = idx === activeIdx;

          return (
            <div key={step.key} className="relative z-10 flex flex-col items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all ${
                  isDone
                    ? 'bg-[#2E9E5B] border-[#2E9E5B] text-white'
                    : isCurrent
                    ? 'bg-white border-[#0B3D2E] text-[#0B3D2E] ring-4 ring-[#E4F4EA]'
                    : 'bg-white border-[#E3E0D5] text-[#5B6B62]'
                }`}
              >
                {isDone ? <Check size={14} /> : step.icon}
              </div>
              <span
                className={`text-[11px] mt-1 font-semibold whitespace-nowrap ${
                  isCurrent ? 'text-[#0B3D2E]' : 'text-[#5B6B62]'
                }`}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
