/**
 * Capacitor Native Bridge
 * Kabadiwala Connect — SIH 2026 (PS SIH26229)
 *
 * Thin abstraction over Capacitor plugins so the rest of the app
 * can call `nativeBridge.takePicture()` etc. without importing
 * Capacitor directly. Falls back gracefully when running in a browser.
 */

import { Capacitor } from '@capacitor/core';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { Geolocation, type Position } from '@capacitor/geolocation';
import { Network } from '@capacitor/network';
import { Share } from '@capacitor/share';
import { Preferences } from '@capacitor/preferences';
import { App as CapApp } from '@capacitor/app';
import { Haptics, ImpactStyle } from '@capacitor/haptics';
import { Keyboard } from '@capacitor/keyboard';
import { StatusBar, Style as StatusBarStyle } from '@capacitor/status-bar';
import { LocalNotifications } from '@capacitor/local-notifications';
import { Filesystem, Directory, Encoding } from '@capacitor/filesystem';

// ─── Platform Detection ───────────────────────────────────────────
export const isNative = Capacitor.isNativePlatform();
export const isAndroid = Capacitor.getPlatform() === 'android';
export const isWeb = Capacitor.getPlatform() === 'web';

// ─── Camera ───────────────────────────────────────────────────────
export interface PhotoResult {
  dataUrl: string;      // base64 data URL
  webPath?: string;     // web-accessible path
  format: string;
}

/**
 * Take a photo using the native camera or file picker.
 * Returns base64 data URL for immediate display + storage.
 * Target: 1280px width, 70% quality → typically ≤150 KB.
 */
export async function takePicture(): Promise<PhotoResult | null> {
  try {
    const photo = await Camera.getPhoto({
      resultType: CameraResultType.DataUrl,
      source: CameraSource.Camera,
      quality: 70,
      width: 1280,
      allowEditing: false,
      correctOrientation: true,
      saveToGallery: false,
    });

    return {
      dataUrl: photo.dataUrl || '',
      webPath: photo.webPath,
      format: photo.format || 'jpeg',
    };
  } catch (err: any) {
    // User cancelled or permission denied — not an error for us
    if (err?.message?.includes('cancelled') || err?.message?.includes('denied')) {
      console.info('Camera: user cancelled or denied');
      return null;
    }
    console.warn('Camera error:', err);
    return null;
  }
}

/**
 * Pick from gallery instead of camera
 */
