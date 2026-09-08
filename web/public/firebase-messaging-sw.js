/**
 * Firebase Cloud Messaging Service Worker
 * File: public/firebase-messaging-sw.js
 *
 * Handles background push notifications when the app tab is closed/hidden.
 * Must live at the root URL so it has the broadest possible scope.
 */

importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey:            "AIzaSyD_c3yDMb0SfidHUAdILAsF8PA59d3AcR8",
  authDomain:        "kabadiwala-d9179.firebaseapp.com",
  projectId:         "kabadiwala-d9179",
  storageBucket:     "kabadiwala-d9179.firebasestorage.app",
  messagingSenderId: "648613915182",
  appId:             "1:648613915182:web:4ddd69b18434f126ca0dbf",
});

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
