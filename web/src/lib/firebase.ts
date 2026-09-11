/**
 * Firebase App Initialisation
 * Kabadiwala Connect — Single import point for all Firebase services.
 *
 * Services used:
 *  - Firebase Auth  → Phone OTP (10,000 free SMS / month, no DLT)
 *  - Firebase FCM   → Web push notifications (unlimited, free)
 */
import { initializeApp, getApps, type FirebaseApp } from 'firebase/app';
import { getAuth, type Auth } from 'firebase/auth';
import { getMessaging, type Messaging } from 'firebase/messaging';

const firebaseConfig = {
  apiKey:            import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain:        import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId:         import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket:     import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId:             import.meta.env.VITE_FIREBASE_APP_ID,
};

// Guard against double-init during hot module reload
let app: FirebaseApp;
if (getApps().length === 0) {
  app = initializeApp(firebaseConfig);
} else {
  app = getApps()[0];
}

/** Firebase Auth — used for Phone OTP login */
export const firebaseAuth: Auth = getAuth(app);

/** Firebase Cloud Messaging — used for web push notifications */
export let firebaseMessaging: Messaging | null = null;
try {
  // Messaging only works in secure contexts (https / localhost)
  if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
    firebaseMessaging = getMessaging(app);
  }
} catch {
  // Non-browser SSR or unsupported browser — skip silently
}

export default app;
