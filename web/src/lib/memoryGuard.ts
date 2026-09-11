/**
 * Memory Pressure Guard
 * Kabadiwala Connect — SIH 2026 (PS SIH26229)
 *
 * Detects low-memory devices (≤1 GB) and adjusts behaviour:
 * - Disables on-device ML (use server or manual)
 * - Reduces image pipeline resolution to 960px
 * - Disables non-essential animations
 * - Limits list virtualization windows
 *
 * Also handles cleanup on visibility change / app pause.
 */

export interface MemoryProfile {
  deviceMemoryGB: number;
  isLowMemory: boolean;
  maxImageWidth: number;
  enableML: boolean;
  enableAnimations: boolean;
  listWindowSize: number;
}

/**
 * Detect device memory and return an appropriate profile.
 */
export function getMemoryProfile(): MemoryProfile {
  // navigator.deviceMemory is available in Chrome/WebView
  const deviceMemoryGB = (navigator as any).deviceMemory || 4;
  const isLowMemory = deviceMemoryGB <= 1;

  // Check system "Reduce motion" setting
  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;

  return {
    deviceMemoryGB,
    isLowMemory,
    maxImageWidth: isLowMemory ? 960 : 1280,
    enableML: !isLowMemory,
    enableAnimations: !isLowMemory && !prefersReducedMotion,
    listWindowSize: isLowMemory ? 10 : 20,
  };
}

/**
 * Release decoded images and cancel non-essential operations.
 * Call on visibility change (app going to background) or pause.
 */
export function releaseMemory(): void {
  // Cancel any pending speech
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }

  // Hint to GC (no-op in most engines but doesn't hurt)
  if (typeof window !== 'undefined' && (window as any).gc) {
    try { (window as any).gc(); } catch { /* ignore */ }
  }
}

/**
 * Set up visibility change handler to release memory on background.
 */
export function initMemoryGuard(): void {
  if (typeof document === 'undefined') return;

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      releaseMemory();
    }
  });
}

/**
 * Check if we should prefer reduced motion.
 */
export function shouldReduceMotion(): boolean {
  if (typeof window === 'undefined') return false;
  return window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches || false;
}
