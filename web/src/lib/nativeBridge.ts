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
export async function pickFromGallery(): Promise<PhotoResult | null> {
  try {
    const photo = await Camera.getPhoto({
      resultType: CameraResultType.DataUrl,
      source: CameraSource.Photos,
      quality: 70,
      width: 1280,
      allowEditing: false,
      correctOrientation: true,
    });

    return {
      dataUrl: photo.dataUrl || '',
      webPath: photo.webPath,
      format: photo.format || 'jpeg',
    };
  } catch {
    return null;
  }
}

// ─── EXIF Stripping ───────────────────────────────────────────────
/**
 * Strip EXIF data from a base64 JPEG image.
 * Creates a new canvas, draws the image, and exports clean JPEG.
 * Also enforces ≤150 KB by re-encoding at lower quality if needed.
 */
export async function stripExifAndCompress(
  dataUrl: string,
  maxBytes: number = 150 * 1024,
  maxWidth: number = 1280,
): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      // Scale down if needed
      let w = img.width;
      let h = img.height;
      if (w > maxWidth) {
        h = Math.round((h * maxWidth) / w);
        w = maxWidth;
      }

      const canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(img, 0, 0, w, h);

      // Try progressively lower quality until under maxBytes
      let quality = 0.7;
      let result = canvas.toDataURL('image/jpeg', quality);

      while (result.length * 0.75 > maxBytes && quality > 0.2) {
        quality -= 0.1;
        result = canvas.toDataURL('image/jpeg', quality);
      }

      resolve(result);
    };
    img.onerror = () => resolve(dataUrl); // fallback to original
    img.src = dataUrl;
  });
}

/**
 * Generate a ≤15 KB thumbnail from a data URL
 */
export async function createThumbnail(
  dataUrl: string,
  maxDim: number = 120,
): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      let w = img.width;
      let h = img.height;
      if (w > h) {
        h = Math.round((h * maxDim) / w);
        w = maxDim;
      } else {
        w = Math.round((w * maxDim) / h);
        h = maxDim;
      }

      const canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(img, 0, 0, w, h);

      resolve(canvas.toDataURL('image/jpeg', 0.5));
    };
    img.onerror = () => resolve('');
    img.src = dataUrl;
  });
}

// ─── Geolocation ──────────────────────────────────────────────────
export interface GeoFix {
  lat: number;
  lng: number;
  accuracy: number;
  isApproximate: boolean;
  timestamp: number;
}

/**
 * Get a single high-accuracy GPS fix with 8s timeout.
 * Falls back to last known position labeled "approximate".
