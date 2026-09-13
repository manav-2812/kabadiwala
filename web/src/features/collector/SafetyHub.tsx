import React, { useState } from 'react';
import { ShieldAlert, ShieldCheck, Flame, PhoneCall, Volume2, CheckCircle2 } from 'lucide-react';
import { VoiceButton } from '../../design/components/VoiceButton';
import { apiRequest } from '../../lib/api';
import { useTranslation } from 'react-i18next';

const GUIDES = [
  {
    code: 'BATTERY_LI',
    title: 'Lithium-Ion Batteries (Mobiles & Laptops)',
    hazard: 'High fire and explosion risk. Can ignite spontaneously if punctured, bent, or wet.',
    rule1: 'Never crush, puncture, or open battery casing.',
    rule2: 'Insulate terminals with tape before transport.',
    rule3: 'Store in dry sand or non-flammable metal container.',
    bonus: 50,
    voice: 'Caution for lithium batteries: Never puncture or store near heat. Tape terminals and keep in sand bucket.'
  },
  {
    code: 'CRT',
    title: 'CRT Monitors & Heavy TV Screens',
    hazard: 'High vacuum implosion risk. Funnel glass contains 2 kg of toxic lead; screen contains toxic phosphor.',
    rule1: 'Do not smash or break the picture tube.',
    rule2: 'Wear heavy safety goggles and thick gloves.',
    rule3: 'Carry screen upright with two persons.',
    bonus: 50,
    voice: 'Caution for CRT screens: Never break glass. Lead and phosphor dust are toxic. Carry upright.'
  },
  {
    code: 'PCB',
    title: 'Printed Circuit Boards (PCBs)',
    hazard: 'Open burning or acid immersion releases toxic brominated dioxins and destroys valuable recovery yields.',
    rule1: 'Strictly zero burning or acid washing.',
    rule2: 'Wear N95 dust mask when de-soldering.',
    rule3: 'Keep completely dry to prevent solder corrosion.',
    bonus: 50,
    voice: 'Caution for circuit boards: Never burn or wash with acid. Sell directly for authorized recycling.'
  },
  {
    code: 'CABLE',
    title: 'Copper Cables & Wires',
    hazard: 'Burning PVC creates toxic cancer-causing smoke. Recyclers pay higher rates for clean unburnt copper.',
    rule1: 'Never burn wires in open yards.',
    rule2: 'Use mechanical wire strippers or sell insulated.',
    rule3: 'Bundle tightly to avoid tripping hazards.',
    bonus: 50,
    voice: 'Caution for copper wires: Do not burn. Burning ruins copper value and releases poisonous smoke.'
  }
];

export const SafetyHub: React.FC = () => {
  const [activeIdx, setActiveIdx] = useState(0);
  const [acknowledged, setAcknowledged] = useState<Record<number, boolean>>({});
  const { t } = useTranslation();

  const handleAcknowledge = async (idx: number) => {
    const guide = GUIDES[idx];
    await apiRequest('/api/safety/acknowledge', {
      method: 'POST',
      body: JSON.stringify({ material_id: guide.code })
    });
    setAcknowledged((prev) => ({ ...prev, [idx]: true }));
    alert(`Safe protocol acknowledged for ${guide.title}! +₹50 safe handling credit logged.`);
  };

  const current = GUIDES[activeIdx];

  return (
    <div className="flex flex-col gap-4 pb-6">
      <div className="flex items-center justify-between border-b border-[#E3E0D5] pb-2">
        <div className="flex items-center gap-2">
          <ShieldAlert size={22} className="text-[#D64545]" />
          <h2 className="text-lg font-black text-[#0B3D2E]">
            {t('safety_hub_title')}
          </h2>
        </div>
        <VoiceButton text="Safety and Hazard Hub. Learn safe handling rules for dangerous scrap and earn extra bonus." size={20} />
      </div>

      {/* Selector Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {GUIDES.map((g, idx) => (
          <button
            key={g.code}
            onClick={() => setActiveIdx(idx)}
            className={`px-3 py-2 rounded-xl text-xs font-bold whitespace-nowrap cursor-pointer transition-all ${
              activeIdx === idx
                ? 'bg-[#14634A] text-white shadow-sm'
                : 'bg-white border border-[#E3E0D5] text-[#5B6B62] hover:bg-[#F7F5EF]'
            }`}
          >
            {t(`categories.${g.code}`, g.code.replace('_', ' '))}
          </button>
        ))}
      </div>

      {/* Active Guide Card */}
      <div className="p-5 rounded-3xl bg-white border border-[#E3E0D5] shadow-xs flex flex-col gap-4">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="text-base font-extrabold text-[#0B3D2E]">{t(`categories.${current.code}`, current.title)}</h3>
            <span className="text-xs text-[#D64545] font-bold block mt-0.5">{t('hazard_level_high')}</span>
          </div>
          <VoiceButton text={current.voice} size={22} />
        </div>

        {/* Hazard Note */}
        <div className="p-3 rounded-2xl bg-[#FBE7E7] border border-[#D64545]/40 text-xs text-[#14201A] font-medium leading-relaxed">
          <b>{t('risk_warning')}:</b> {current.hazard}
        </div>

        {/* 3 Golden Safety Rules */}
        <div className="flex flex-col gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-[#5B6B62]">
            {t('mandatory_safety_protocols')}
          </span>
          <div className="flex flex-col gap-1.5 text-xs text-[#14201A]">
            <div className="flex items-start gap-2 p-2 rounded-xl bg-[#F7F5EF]">
              <span className="w-5 h-5 rounded-full bg-[#14634A] text-white flex items-center justify-center font-bold text-[11px] shrink-0">1</span>
              <span>{current.rule1}</span>
            </div>
            <div className="flex items-start gap-2 p-2 rounded-xl bg-[#F7F5EF]">
              <span className="w-5 h-5 rounded-full bg-[#14634A] text-white flex items-center justify-center font-bold text-[11px] shrink-0">2</span>
              <span>{current.rule2}</span>
            </div>
            <div className="flex items-start gap-2 p-2 rounded-xl bg-[#F7F5EF]">
              <span className="w-5 h-5 rounded-full bg-[#14634A] text-white flex items-center justify-center font-bold text-[11px] shrink-0">3</span>
              <span>{current.rule3}</span>
            </div>
          </div>
        </div>

        {/* Acknowledge Button */}
        <button
          onClick={() => handleAcknowledge(activeIdx)}
          disabled={acknowledged[activeIdx]}
          className={`w-full py-3 px-4 rounded-xl font-bold text-xs flex items-center justify-center gap-2 cursor-pointer transition-all touch-target ${
            acknowledged[activeIdx]
              ? 'bg-[#E4F4EA] text-[#0B3D2E] border border-[#2E9E5B]'
              : 'bg-[#14634A] hover:bg-[#0B3D2E] text-white'
          }`}
        >
          <CheckCircle2 size={16} />
          <span>{acknowledged[activeIdx] ? 'Safety Protocol Acknowledged (+₹50 Bonus Added)' : 'I Understand & Will Follow Safety Rules (+₹50 Bonus)'}</span>
        </button>
      </div>

      {/* Emergency Card */}
      <div className="p-4 rounded-2xl bg-[#14201A] text-white flex items-center justify-between shadow-md">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-[#D64545]">
            <Flame size={20} />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">{t('chemical_fire_emergency')}</h4>
            <span className="text-[11px] text-white/70 block">{t('disaster_helpline')}</span>
          </div>
        </div>
        <a
          href="#"
          onClick={(e) => { e.preventDefault(); }}
          title="Calling is disabled in demo"
          className="px-3.5 py-2 rounded-xl bg-[#D64545] opacity-75 cursor-not-allowed text-white font-bold text-xs flex items-center gap-1 touch-target"
        >
          <PhoneCall size={14} />
          <span>{t('call_108')}</span>
        </a>
      </div>
    </div>
  );
};
