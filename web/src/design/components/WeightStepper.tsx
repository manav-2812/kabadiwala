import React from 'react';
import { Minus, Plus } from 'lucide-react';
import { VoiceButton } from './VoiceButton';

interface WeightStepperProps {
  valueGrams: number;
  onChange: (grams: number) => void;
  minGrams?: number;
  maxGrams?: number;
}

export const WeightStepper: React.FC<WeightStepperProps> = ({
  valueGrams,
  onChange,
  minGrams = 500, // 0.5 kg
  maxGrams = 500000 // 500 kg
}) => {
  const PRESETS = [1, 2, 5, 10, 25]; // in kg
  const currentKg = valueGrams / 1000;

  const handleStep = (deltaKg: number) => {
    const nextKg = Math.max(minGrams / 1000, Math.min(maxGrams / 1000, currentKg + deltaKg));
    onChange(Math.round(nextKg * 1000));
  };

  const handleSetPreset = (kg: number) => {
    onChange(kg * 1000);
  };

  return (
    <div className="w-full flex flex-col gap-3">
      <div className="flex items-center justify-between bg-white border border-[#E3E0D5] rounded-2xl p-2">
        <button
          type="button"
          onClick={() => handleStep(-0.5)}
          disabled={valueGrams <= minGrams}
          className="w-14 h-14 flex items-center justify-center rounded-xl bg-[#F7F5EF] text-[#14201A] hover:bg-[#E3E0D5] active:scale-95 disabled:opacity-40 cursor-pointer touch-target"
        >
          <Minus size={24} />
        </button>

        <div className="flex flex-col items-center justify-center px-4">
          <div className="flex items-baseline gap-1.5">
            <span className="text-3xl font-bold tabular-nums text-[#0B3D2E]">
              {currentKg.toFixed(currentKg % 1 === 0 ? 0 : 1)}
            </span>
            <span className="text-base font-semibold text-[#5B6B62]">kg</span>
            <VoiceButton text={`${currentKg} kilogram`} size={16} />
          </div>
          <span className="text-xs text-[#5B6B62]">approximate weight</span>
        </div>

        <button
          type="button"
          onClick={() => handleStep(0.5)}
          disabled={valueGrams >= maxGrams}
          className="w-14 h-14 flex items-center justify-center rounded-xl bg-[#14634A] text-white hover:bg-[#0B3D2E] active:scale-95 disabled:opacity-40 cursor-pointer touch-target"
        >
          <Plus size={24} />
        </button>
      </div>

      {/* Presets Row */}
      <div className="flex items-center justify-between gap-1.5">
        {PRESETS.map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => handleSetPreset(p)}
            className={`flex-1 py-2 rounded-xl text-sm font-bold border transition-colors touch-target cursor-pointer ${
              currentKg === p
                ? 'bg-[#E4F4EA] border-[#14634A] text-[#0B3D2E]'
                : 'bg-white border-[#E3E0D5] text-[#5B6B62] hover:bg-[#F7F5EF]'
            }`}
          >
            {p} kg
          </button>
        ))}
      </div>
    </div>
  );
};
