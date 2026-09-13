/**
 * Audio Clip Composer
 * Kabadiwala Connect — SIH 2026 (PS SIH26229)
 *
 * Composes spoken feedback from pre-recorded audio clips.
 * Falls back to Web Speech API (window.speechSynthesis) if clips are missing.
 *
 * Audio manifest: public/audio/manifest.json
 * Clip directory: public/audio/<lang>/<token>.webm
 *
 * Clip naming: lowercase token with underscores.
 * Example: "photo_too_dark", "material_pcb", "price_rising"
 *
 * Section C8 of AI Integration Spec.
 */

export type SupportedLang = 'en' | 'hi' | 'mr' | 'pa';

interface AudioManifest {
  lang: SupportedLang;
  clips: Record<string, string>;  // token -> filename
  placeholder: boolean;
}

// Cached manifests and audio buffers
const manifestCache: Partial<Record<SupportedLang, AudioManifest>> = {};
const audioCache: Record<string, HTMLAudioElement> = {};

// Inline fallback text for speech synthesis (used when clip is missing)
const FALLBACK_TEXT: Record<string, Partial<Record<SupportedLang, string>>> = {
  photo_too_dark: {
    en: 'Photo is too dark. Please move to better light.',
    hi: 'फोटो बहुत अंधेरी है। रोशनी में जाएं।',
    mr: 'फोटो अंधारी आहे. प्रकाशात जा.',
    pa: 'ਫੋਟੋ ਹਨੇਰੀ ਹੈ। ਰੌਸ਼ਨੀ ਵਿੱਚ ਜਾਓ।',
  },
  photo_blurry: {
    en: 'Photo is blurry. Please hold steady.',
    hi: 'फोटो धुंधली है। स्थिर रखें।',
    mr: 'फोटो अस्पष्ट आहे. स्थिर ठेवा.',
    pa: 'ਫੋਟੋ ਧੁੰਦਲੀ ਹੈ। ਸਥਿਰ ਰੱਖੋ।',
  },
  suggestion_not_sure: {
    en: 'Not sure. Please select category.',
    hi: 'निश्चित नहीं। कृपया श्रेणी चुनें।',
    mr: 'खात्री नाही. कृपया श्रेणी निवडा.',
    pa: 'ਨਿਸ਼ਚਿਤ ਨਹੀਂ। ਕਿਰਪਾ ਕਰਕੇ ਸ਼੍ਰੇਣੀ ਚੁਣੋ।',
  },
  price_rising: {
    en: 'Price is rising this week.',
    hi: 'इस हफ्ते कीमत बढ़ रही है।',
    mr: 'या आठवड्यात किंमत वाढत आहे.',
    pa: 'ਇਸ ਹਫ਼ਤੇ ਕੀਮਤ ਵੱਧ ਰਹੀ ਹੈ।',
  },
  price_falling: {
    en: 'Price is falling this week.',
    hi: 'इस हफ्ते कीमत घट रही है।',
    mr: 'या आठवड्यात किंमत कमी होत आहे.',
    pa: 'ਇਸ ਹਫ਼ਤੇ ਕੀਮਤ ਘੱਟ ਰਹੀ ਹੈ।',
  },
  price_steady: {
    en: 'Price is steady.',
    hi: 'कीमत स्थिर है।',
    mr: 'किंमत स्थिर आहे.',
    pa: 'ਕੀਮਤ ਸਥਿਰ ਹੈ।',
  },
};

async function loadManifest(lang: SupportedLang): Promise<AudioManifest | null> {
  if (manifestCache[lang]) return manifestCache[lang]!;
  try {
    const res = await fetch(`/audio/manifest.json`);
    if (!res.ok) return null;
    const all: AudioManifest[] = await res.json();
    const m = all.find(x => x.lang === lang);
    if (m) manifestCache[lang] = m;
    return m ?? null;
  } catch {
    return null;
  }
}

function speechFallback(text: string, lang: SupportedLang): void {
  if (!('speechSynthesis' in window)) return;
  const utter = new SpeechSynthesisUtterance(text);
  const langMap: Record<SupportedLang, string> = {
    en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN', pa: 'pa-IN'
  };
  utter.lang = langMap[lang];
  utter.rate = 0.9;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utter);
}

/**
 * Play a single token as audio.
 * Falls back to TTS if clip not found.
 */
export async function playToken(token: string, lang: SupportedLang = 'en'): Promise<void> {
  const manifest = await loadManifest(lang);
  const clipFile = manifest?.clips?.[token];

  if (clipFile && !manifest?.placeholder) {
    const cacheKey = `${lang}/${clipFile}`;
    let audio = audioCache[cacheKey];
    if (!audio) {
      audio = new Audio(`/audio/${lang}/${clipFile}`);
      audioCache[cacheKey] = audio;
    }
    try {
      audio.currentTime = 0;
      await audio.play();
      return;
    } catch {
      // Fall through to TTS
    }
  }

  // TTS fallback
  const text = FALLBACK_TEXT[token]?.[lang] ?? FALLBACK_TEXT[token]?.['en'] ?? token;
  speechFallback(text, lang);
}

/**
 * Compose and play a sequence of tokens in order.
 * Waits for each clip to finish before playing the next.
 */
export async function playPhrase(tokens: string[], lang: SupportedLang = 'en'): Promise<void> {
  for (const token of tokens) {
    await playToken(token, lang);
    // Small gap between clips
    await new Promise(r => setTimeout(r, 120));
  }
}

/**
 * Cancel any currently playing audio/TTS.
 */
export function cancelAudio(): void {
  if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  Object.values(audioCache).forEach(a => { a.pause(); a.currentTime = 0; });
}

/**
 * Pre-built phrase composers for common UI events.
 */
export const phrases = {
  photoTooDark: (lang: SupportedLang) => playPhrase(['photo_too_dark'], lang),
  photoBlurry: (lang: SupportedLang) => playPhrase(['photo_blurry'], lang),
  notSure: (lang: SupportedLang) => playPhrase(['suggestion_not_sure'], lang),
  priceArrow: (arrow: 'Rising' | 'Falling' | 'Steady', lang: SupportedLang) =>
    playPhrase([`price_${arrow.toLowerCase()}`], lang),
};
