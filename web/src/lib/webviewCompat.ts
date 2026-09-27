// [SIH-2026-PS-SIH26229] Iteration 102 polish
/**
 * WebView Compatibility Check
 * Kabadiwala Connect — SIH 2026 (PS SIH26229)
 *
 * Entry-level Android 8-10 devices may run an older Android System WebView.
 * This module feature-detects required APIs and shows a friendly update
 * prompt if the WebView is too old, while allowing basic use where possible.
 */

import { isNative, isAndroid } from './nativeBridge';

interface CompatReport {
  ok: boolean;
  missing: string[];
  webViewVersion: string | null;
}

/**
 * Check if the WebView supports all required features.
 */
export function checkWebViewCompat(): CompatReport {
  const missing: string[] = [];

  // Feature detections
  if (typeof WebAssembly === 'undefined') {
    missing.push('WebAssembly');
  }

  if (typeof IntersectionObserver === 'undefined') {
    missing.push('IntersectionObserver');
  }

  if (typeof CSS !== 'undefined' && CSS.supports) {
    if (!CSS.supports('padding-top', 'env(safe-area-inset-top, 0px)')) {
      // Not critical — will use fallback values
    }
  }

  if (typeof BigInt === 'undefined') {
    missing.push('BigInt');
  }

  if (typeof AbortController === 'undefined') {
    missing.push('AbortController');
  }

  // Try to detect WebView version from user agent
  let webViewVersion: string | null = null;
  const ua = navigator.userAgent;
  const chromeMatch = ua.match(/Chrome\/(\d+)/);
  if (chromeMatch) {
    webViewVersion = chromeMatch[1];
    const majorVersion = parseInt(webViewVersion, 10);
    // Chrome < 69 is too old for our features
    if (majorVersion < 69) {
      missing.push(`Chrome ${webViewVersion} (need 69+)`);
    }
  }

  return {
    ok: missing.length === 0,
    missing,
    webViewVersion,
  };
}

/**
 * Show a native-styled update prompt if WebView is too old.
 * Uses plain DOM (no React) since React itself might not load on very old WebViews.
 */
export function showWebViewUpdatePrompt(missing: string[]): void {
  // Only show on native Android
  if (!isAndroid) return;

  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position: fixed; inset: 0; z-index: 99999;
    background: #F7F5EF; display: flex; flex-direction: column;
    align-items: center; justify-content: center; padding: 32px;
    font-family: sans-serif; text-align: center;
  `;

  overlay.innerHTML = `
    <div style="font-size: 64px; margin-bottom: 16px;">🔄</div>
    <h2 style="font-size: 22px; color: #14201A; margin-bottom: 12px;">
      कृपया Android System WebView अपडेट करें
    </h2>
    <p style="font-size: 16px; color: #5B6B62; margin-bottom: 8px;">
      Please update Android System WebView
    </p>
    <p style="font-size: 14px; color: #8B9B92; margin-bottom: 24px;">
      ਕਿਰਪਾ ਕਰਕੇ Android System WebView ਅੱਪਡੇਟ ਕਰੋ
    </p>
    <p style="font-size: 13px; color: #8B9B92; margin-bottom: 24px;">
      Missing: ${missing.join(', ')}
    </p>
    <button id="kc-update-webview" style="
      background: #0B3D2E; color: white; border: none; border-radius: 12px;
      padding: 16px 32px; font-size: 18px; cursor: pointer;
      min-width: 200px; min-height: 56px;
    ">
      Update WebView ▶
    </button>
    <button id="kc-skip-update" style="
      background: transparent; color: #5B6B62; border: 1px solid #D4D9D6;
      border-radius: 12px; padding: 12px 24px; font-size: 14px;
      cursor: pointer; margin-top: 12px;
    ">
      Continue anyway
    </button>
  `;

  document.body.appendChild(overlay);

  // Open Play Store for WebView update
  document.getElementById('kc-update-webview')?.addEventListener('click', () => {
    window.open(
      'https://play.google.com/store/apps/details?id=com.google.android.webview',
      '_system'
    );
  });

  // Allow continuing with degraded experience
  document.getElementById('kc-skip-update')?.addEventListener('click', () => {
    overlay.remove();
  });
}

/**
 * Run compatibility check on startup.
 * Shows update prompt if critical features are missing.
 */
export function initWebViewCheck(): void {
  if (!isNative) return;

  const report = checkWebViewCompat();
  if (!report.ok) {
    console.warn('WebView compatibility issues:', report.missing);
    // Show prompt for critical missing features (WebAssembly, BigInt)
    const critical = report.missing.filter(m =>
      m.includes('WebAssembly') || m.includes('Chrome')
    );
    if (critical.length > 0) {
      showWebViewUpdatePrompt(report.missing);
    }
  }
}
