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
 * Never keeps a watcher running.
 */
export async function getSingleGeoFix(): Promise<GeoFix> {
  const approximate: GeoFix = {
    lat: 0, lng: 0, accuracy: 9999, isApproximate: true,
    timestamp: Date.now(),
  };

  try {
    const pos: Position = await Geolocation.getCurrentPosition({
      enableHighAccuracy: true,
      timeout: 8000,
      maximumAge: 60000,
    });

    return {
      lat: pos.coords.latitude,
      lng: pos.coords.longitude,
      accuracy: pos.coords.accuracy ?? 9999,
      isApproximate: false,
      timestamp: pos.timestamp,
    };
  } catch {
    // Try last known location
    try {
      const last = await Geolocation.getCurrentPosition({
        enableHighAccuracy: false,
        timeout: 3000,
        maximumAge: 300000, // 5 min old is okay as "approximate"
      });
      return {
        lat: last.coords.latitude,
        lng: last.coords.longitude,
        accuracy: last.coords.accuracy ?? 9999,
        isApproximate: true,
        timestamp: last.timestamp,
      };
    } catch {
      return approximate;
    }
  }
}

// ─── Network ──────────────────────────────────────────────────────
export interface NetworkStatus {
  connected: boolean;
  connectionType: string;
}

export async function getNetworkStatus(): Promise<NetworkStatus> {
  try {
    const status = await Network.getStatus();
    return {
      connected: status.connected,
      connectionType: status.connectionType,
    };
  } catch {
    return {
      connected: navigator.onLine,
      connectionType: 'unknown',
    };
  }
}

/**
 * Listen for network status changes.
 * Returns an unsubscribe function.
 */
export function onNetworkChange(
  callback: (status: NetworkStatus) => void,
): () => void {
  const handler = Network.addListener('networkStatusChange', (status) => {
    callback({
      connected: status.connected,
      connectionType: status.connectionType,
    });
  });

  return () => {
    handler.then(h => h.remove());
  };
}

// ─── Secure Storage (Preferences for now, Keystore-backed TODO) ──
export async function secureSet(key: string, value: string): Promise<void> {
  await Preferences.set({ key, value });
}

export async function secureGet(key: string): Promise<string | null> {
  const { value } = await Preferences.get({ key });
  return value;
}

export async function secureRemove(key: string): Promise<void> {
  await Preferences.remove({ key });
}

// ─── App Lifecycle ────────────────────────────────────────────────
/**
 * Register back button handler.
 * Returns unsubscribe function.
 */
export function onBackButton(
  callback: () => void,
): () => void {
  const handler = CapApp.addListener('backButton', () => {
    callback();
  });
  return () => {
    handler.then(h => h.remove());
  };
}

/**
 * Register app state change (foreground/background).
 */
export function onAppStateChange(
  callback: (isActive: boolean) => void,
): () => void {
  const handler = CapApp.addListener('appStateChange', (state) => {
    callback(state.isActive);
  });
  return () => {
    handler.then(h => h.remove());
  };
}

/**
 * Exit the app (Android only)
 */
export async function exitApp(): Promise<void> {
  if (isAndroid) {
    await CapApp.exitApp();
  }
}

// ─── Haptics ──────────────────────────────────────────────────────
export async function hapticLight(): Promise<void> {
  try {
    await Haptics.impact({ style: ImpactStyle.Light });
  } catch { /* ignore on web */ }
}

export async function hapticMedium(): Promise<void> {
  try {
    await Haptics.impact({ style: ImpactStyle.Medium });
  } catch { /* ignore on web */ }
}

// ─── Status Bar ───────────────────────────────────────────────────
export async function setStatusBarDark(): Promise<void> {
  if (!isNative) return;
  try {
    await StatusBar.setStyle({ style: StatusBarStyle.Dark });
    await StatusBar.setBackgroundColor({ color: '#0B3D2E' });
  } catch { /* ignore */ }
}

// ─── Share ────────────────────────────────────────────────────────
export async function shareText(
  title: string,
  text: string,
  url?: string,
): Promise<void> {
  try {
    await Share.share({ title, text, url, dialogTitle: title });
  } catch { /* user cancelled */ }
}

export async function shareFile(
  title: string,
  filePath: string,
): Promise<void> {
  try {
    await Share.share({
      title,
      url: filePath,
      dialogTitle: title,
    });
  } catch { /* user cancelled */ }
}

// ─── Filesystem (for receipt downloads) ───────────────────────────
export async function writeAppFile(
  path: string,
  data: string,
  encoding: 'utf8' | 'base64' = 'utf8',
): Promise<string> {
  const result = await Filesystem.writeFile({
    path,
    data,
    directory: Directory.Documents,
    encoding: encoding === 'utf8' ? Encoding.UTF8 : undefined,
    recursive: true,
  });
  return result.uri;
}

// ─── Local Notifications ──────────────────────────────────────────
/**
 * Schedule a local notification with quiet hours (9PM-7AM).
 */
export async function scheduleNotification(
  title: string,
  body: string,
  id?: number,
): Promise<void> {
  const now = new Date();
  const hour = now.getHours();

  // Quiet hours: 9 PM to 7 AM — delay to 7 AM
  if (hour >= 21 || hour < 7) {
    const next7am = new Date();
    if (hour >= 21) next7am.setDate(next7am.getDate() + 1);
    next7am.setHours(7, 0, 0, 0);

    await LocalNotifications.schedule({
      notifications: [{
        title,
        body,
        id: id ?? Math.floor(Math.random() * 100000),
        schedule: { at: next7am },
        smallIcon: 'ic_notification',
      }],
    });
    return;
  }

  await LocalNotifications.schedule({
    notifications: [{
      title,
      body,
      id: id ?? Math.floor(Math.random() * 100000),
      smallIcon: 'ic_notification',
    }],
  });
}

// ─── Keyboard ─────────────────────────────────────────────────────
export function onKeyboardShow(callback: (height: number) => void): () => void {
  if (!isNative) return () => {};
  const handler = Keyboard.addListener('keyboardWillShow', (info) => {
    callback(info.keyboardHeight);
  });
  return () => { handler.then(h => h.remove()); };
}

export function onKeyboardHide(callback: () => void): () => void {
  if (!isNative) return () => {};
  const handler = Keyboard.addListener('keyboardWillHide', () => {
    callback();
  });
  return () => { handler.then(h => h.remove()); };
}
