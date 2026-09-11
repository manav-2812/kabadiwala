/**
 * Spoken Vernacular Price Board & Voice Audio Engine
 * Smart India Hackathon 2026 — PS SIH26229
 * Supports mr-IN (मराठी), hi-IN (हिन्दी), pa-IN (ਪੰਜਾਬੀ), en-IN (English)
 */

const BCP47_MAP: Record<string, string> = {
  mr: 'mr-IN',
  hi: 'hi-IN',
  pa: 'pa-IN',
  en: 'en-IN'
};

const PHRASES: Record<string, Record<string, (name: string, rate: number) => string>> = {
  mr: {
    rate: (name, rate) => `${name}, दर ${rate} रुपये प्रति किलो. अधिकृत पुनर्वापरकर्ता अधिक भाव देईल.`,
  },
  hi: {
    rate: (name, rate) => `${name}, भाव ${rate} रुपये प्रति किलो. सीपीसीबी खरीदार से अतिरिक्त मुनाफा.`,
  },
  pa: {
    rate: (name, rate) => `${name}, ਭਾਅ ${rate} ਰੁਪਏ ਪ੍ਰਤੀ ਕਿਲੋ. ਅਧਿਕਾਰਤ ਖਰੀਦਦਾਰ ਤੋਂ ਵਧੇਰੇ ਮੁਨਾਫਾ.`,
  },
  en: {
    rate: (name, rate) => `${name}, current rate ${rate} rupees per kilogram with authorized recycler premium.`,
  }
};

export const speakMaterialRate = (
  materialCode: string,
  materialName: string,
  rateInr: number,
  lang: string = 'mr'
): void => {
  const cleanLang = lang.split('-')[0].toLowerCase();
  const audioClipUrl = `/audio/${cleanLang}/materials/${materialCode.toLowerCase()}.mp3`;

  // Attempt pre-recorded audio first
  const audio = new Audio(audioClipUrl);
  
  audio.play().catch(() => {
    // Graceful fallback to browser Web Speech API
    if (!('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel(); // cancel any ongoing speech

    const phraseGenerator = PHRASES[cleanLang]?.rate || PHRASES.mr.rate;
    const textToSpeak = phraseGenerator(materialName, rateInr);

    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.lang = BCP47_MAP[cleanLang] || 'mr-IN';
    utterance.rate = 0.92; // Slightly slower for enhanced clarity
    utterance.pitch = 1.0;

    // Try finding exact regional voice if installed
    const voices = window.speechSynthesis.getVoices();
    const targetLang = utterance.lang;
    const matchedVoice = voices.find((v) => v.lang === targetLang || v.lang.startsWith(cleanLang));
    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    window.speechSynthesis.speak(utterance);
  });
};
