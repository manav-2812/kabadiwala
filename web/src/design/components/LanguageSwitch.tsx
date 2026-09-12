import React from 'react';
import { useTranslation } from 'react-i18next';
import { Volume2, CheckCircle2 } from 'lucide-react';
import { useAuthStore } from '../../features/auth/authStore';
import { speakText } from '../../lib/voice';

export const LanguageSwitch: React.FC<{ compact?: boolean }> = ({ compact = false }) => {
  const { t, i18n } = useTranslation();
  const { setLanguage } = useAuthStore();

  const LANGUAGES = [
    { code: 'mr', label: 'मराठी', sub: 'मराठी', greeting: 'कबाडीवाला कनेक्ट मध्ये आपले स्वागत आहे' },
    { code: 'hi', label: 'हिन्दी', sub: 'हिन्दी', greeting: 'कबाड़ीवाला कनेक्ट में आपका स्वागत है' },
    { code: 'pa', label: 'ਪੰਜਾਬੀ', sub: 'ਪੰਜਾਬੀ', greeting: 'ਕਬਾੜੀਵਾਲਾ ਕਨੈਕਟ ਵਿੱਚ ਜੀ ਆਇਆਂ ਨੂੰ' },
    { code: 'en', label: 'English', sub: 'English', greeting: 'Welcome to Kabadiwala Connect' },
  ];

  const handleSelect = (code: string, greeting: string) => {
    i18n.changeLanguage(code);
    setLanguage(code);
    localStorage.setItem('kc_language', code);
    speakText(greeting, code);
  };

  if (compact) {
    return (
      <div className="flex items-center gap-1 bg-white p-1 rounded-xl border border-[#E3E0D5]">
        {LANGUAGES.map((lang) => (
          <button
            key={lang.code}
            onClick={() => handleSelect(lang.code, lang.greeting)}
            className={`px-2.5 py-1 text-xs font-bold rounded-lg cursor-pointer transition-colors ${
              i18n.language === lang.code
                ? 'bg-[#0B3D2E] text-white'
                : 'text-[#5B6B62] hover:text-[#14201A]'
            }`}
          >
            {lang.label}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full">
      {LANGUAGES.map((lang) => {
        const isSelected = i18n.language === lang.code;
        return (
          <button
            key={lang.code}
            onClick={() => handleSelect(lang.code, lang.greeting)}
            className={`relative flex flex-col items-center justify-center p-3.5 rounded-2xl border-2 transition-all cursor-pointer min-h-[76px] touch-target ${
              isSelected
                ? 'bg-[#E4F4EA] border-[#14634A] text-[#0B3D2E] shadow-sm ring-2 ring-[#14634A]/20'
                : 'bg-white border-[#E3E0D5] text-[#14201A] hover:border-[#5B6B62]'
            }`}
          >
            {isSelected && (
              <span className="absolute top-2 right-2 text-[#14634A]">
                <CheckCircle2 size={14} />
              </span>
            )}
            <span className="text-lg font-black tracking-tight">{lang.label}</span>
            <span className="text-[11px] font-semibold text-[#5B6B62] mt-0.5">{lang.sub}</span>
            <div className="flex items-center gap-1 text-[10px] text-[#14634A] mt-1 font-bold">
              <Volume2 size={12} />
              <span>{t('btn_listen')}</span>
            </div>
          </button>
        );
      })}
    </div>
  );
};
