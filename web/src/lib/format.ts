import i18n from '../i18n/i18n';

export function formatINR(paise: number): string {
  const rupees = Math.round(paise / 100);
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(rupees);
}

export function formatINRFromRupees(rupees: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(rupees);
}

export function formatWeight(grams: number, customLang?: string): string {
  const lang = customLang || i18n.language || localStorage.getItem('kc_language') || 'mr';
  const kg = grams / 1000;
  const numStr = kg.toFixed(kg % 1 === 0 ? 0 : 1);
  if (lang === 'mr') {
    return kg < 1 ? `${grams} ग्रॅम` : `${numStr} किलो`;
  }
  if (lang === 'hi') {
    return kg < 1 ? `${grams} ग्राम` : `${numStr} किग्रा`;
  }
  if (lang === 'pa') {
    return kg < 1 ? `${grams} ਗ੍ਰਾਮ` : `${numStr} ਕਿਲੋ`;
  }
  return kg < 1 ? `${grams} g` : `${numStr} kg`;
}

export function formatDate(isoStr: string, customLang?: string): string {
  const lang = customLang || i18n.language || localStorage.getItem('kc_language') || 'mr';
  const locale = lang === 'mr' ? 'mr-IN' : lang === 'hi' ? 'hi-IN' : lang === 'pa' ? 'pa-IN' : 'en-IN';
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString(locale, {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  } catch {
    return isoStr;
  }
}
