import React from 'react';
import { Volume2 } from 'lucide-react';
import { speakText } from '../../lib/voice';
import { useTranslation } from 'react-i18next';

interface VoiceButtonProps {
  text: string;
  className?: string;
  size?: number;
}

export const VoiceButton: React.FC<VoiceButtonProps> = ({ text, className = '', size = 18 }) => {
  const { i18n } = useTranslation();

  const handleSpeak = (e: React.MouseEvent) => {
    e.stopPropagation();
    speakText(text, i18n.language);
  };

  return (
    <button
      type="button"
      onClick={handleSpeak}
      title="Listen"
      aria-label="Read aloud"
      className={`inline-flex items-center justify-center p-2 rounded-full text-ink-500 hover:text-forest-900 hover:bg-leaf-100 transition-colors cursor-pointer touch-target ${className}`}
    >
      <Volume2 size={size} className="shrink-0" />
    </button>
  );
};
