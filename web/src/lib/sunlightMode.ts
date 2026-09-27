// [SIH-2026-PS-SIH26229] Iteration 100 polish
/**
 * Sunlight / Outdoor High-Contrast Mode Manager
 * Kabadiwala Connect — SIH 2026 (PS SIH26229)
 *
 * For collectors working under direct Indian sunlight.
 * Enforces 7:1+ contrast, deep black on white, bold text.
 */

import { useState, useEffect } from 'react';

const STORAGE_KEY = 'kc_sunlight_mode';

export function getSunlightMode(): boolean {
  if (typeof window === 'undefined') return false;
  return localStorage.getItem(STORAGE_KEY) === 'true';
}

export function setSunlightMode(enabled: boolean): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(STORAGE_KEY, enabled ? 'true' : 'false');
  if (enabled) {
    document.documentElement.classList.add('sunlight-mode');
  } else {
    document.documentElement.classList.remove('sunlight-mode');
  }
}

export function initSunlightMode(): void {
  if (typeof window === 'undefined') return;
  if (getSunlightMode()) {
    document.documentElement.classList.add('sunlight-mode');
  }
}

export function useSunlightMode(): [boolean, (val: boolean) => void] {
  const [active, setActive] = useState<boolean>(getSunlightMode());

  useEffect(() => {
    initSunlightMode();
  }, []);

  const toggle = (val: boolean) => {
    setActive(val);
    setSunlightMode(val);
  };

  return [active, toggle];
}
