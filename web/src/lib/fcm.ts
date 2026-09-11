/**
 * Firebase Cloud Messaging (FCM) — Web Push Service
 * Kabadiwala Connect
 *
 * Handles:
 *  - Requesting notification permission from the browser
 *  - Registering the FCM service worker
 *  - Getting the device FCM token to send to the backend
 *  - Receiving foreground notifications and showing them in-app
 *
 * Free & unlimited for all notification types.
 */
import { getToken, onMessage } from 'firebase/messaging';
import { firebaseMessaging } from './firebase';

export type FcmNotificationPayload = {
  title: string;
  body: string;
  icon?: string;
  url?: string;
  data?: Record<string, string>;
};

type NotificationCallback = (payload: FcmNotificationPayload) => void;
const subscribers: NotificationCallback[] = [];

/**
 * Request browser notification permission and register service worker.
 * Returns the FCM registration token, or null if permission denied / not supported.
 */
export async function initFcm(): Promise<string | null> {
  if (!firebaseMessaging) return null;

  const permission = await Notification.requestPermission();
  if (permission !== 'granted') {
    console.info('[FCM] Notification permission denied by user.');
    return null;
  }

  try {
    // Register Firebase SW (vite-plugin-pwa already registers sw.js;
    // Firebase needs its own sw or merged logic)
    const swRegistration = await navigator.serviceWorker.register('/firebase-messaging-sw.js', {
      scope: '/',
    });

    const token = await getToken(firebaseMessaging, {
      vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY,
      serviceWorkerRegistration: swRegistration,
    });

    if (token) {
      console.info('[FCM] Device token obtained:', token.slice(0, 20) + '...');
      return token;
    }
    return null;
  } catch (err) {
    console.warn('[FCM] Failed to get token:', err);
    return null;
  }
}

/**
 * Register a callback that fires when a push notification arrives
 * while the app is in the foreground.
 */
export function onForegroundNotification(cb: NotificationCallback): () => void {
  subscribers.push(cb);

  if (!firebaseMessaging) return () => {};

  const unsubscribe = onMessage(firebaseMessaging, (payload) => {
    const notification: FcmNotificationPayload = {
      title: payload.notification?.title ?? 'Kabadiwala Connect',
      body:  payload.notification?.body  ?? '',
      icon:  payload.notification?.icon,
      url:   (payload.data?.url as string) ?? '/',
      data:  payload.data as Record<string, string>,
    };
    subscribers.forEach((fn) => fn(notification));
  });

  // Return cleanup function
  return () => {
    unsubscribe();
    const idx = subscribers.indexOf(cb);
    if (idx !== -1) subscribers.splice(idx, 1);
  };
}
