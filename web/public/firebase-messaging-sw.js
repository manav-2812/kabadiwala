/**
 * Firebase Cloud Messaging Service Worker
 * File: public/firebase-messaging-sw.js
 *
 * Handles background push notifications when the app tab is closed/hidden.
 * Must live at the root URL so it has the broadest possible scope.
 */

importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');

const firebaseConfig = {
  apiKey:            self.__FIREBASE_API_KEY__ || '',
  authDomain:        self.__FIREBASE_AUTH_DOMAIN__ || '',
  projectId:         self.__FIREBASE_PROJECT_ID__ || '',
  storageBucket:     self.__FIREBASE_STORAGE_BUCKET__ || '',
  messagingSenderId: self.__FIREBASE_MESSAGING_SENDER_ID__ || '',
  appId:             self.__FIREBASE_APP_ID__ || '',
};

if (firebaseConfig.apiKey) {
  try {
    firebase.initializeApp(firebaseConfig);
    const messaging = firebase.messaging();

    /**
     * Background message handler — fires when the app is in the background or closed.
     */
    messaging.onBackgroundMessage((payload) => {
      const title = payload.notification?.title ?? 'Kabadiwala Connect';
      const options = {
        body:    payload.notification?.body ?? '',
        icon:    payload.notification?.icon ?? '/favicon.svg',
        badge:   '/favicon.svg',
        data:    payload.data,
        actions: [{ action: 'open', title: 'Open App' }],
      };
      self.registration.showNotification(title, options);
    });
  } catch (err) {
    console.warn('[FCM SW] Failed to initialize Firebase Messaging:', err);
  }
}

/** On notification click — open the app or a specific URL */
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = event.notification?.data?.url ?? '/';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      for (const client of windowClients) {
        if (client.url === url && 'focus' in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow(url);
    })
  );
});
