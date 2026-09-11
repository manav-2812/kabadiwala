/**
 * Firebase Phone Auth Service
 * Kabadiwala Connect
 *
 * Provides real carrier SMS OTP request + verification via Firebase Authentication.
 * 10,000 free SMS / month with zero DLT paperwork.
 */
import {
  RecaptchaVerifier,
  signInWithPhoneNumber,
  type ConfirmationResult,
  type ApplicationVerifier,
} from 'firebase/auth';
import { firebaseAuth } from './firebase';

let confirmationResult: ConfirmationResult | null = null;
let recaptchaVerifier: RecaptchaVerifier | null = null;

/** Returns true if Firebase Phone Auth is configured */
export function isFirebaseConfigured(): boolean {
  const apiKey = import.meta.env.VITE_FIREBASE_API_KEY;
  return typeof apiKey === 'string' && apiKey.length > 0;
}

/** Formats Firebase Auth errors into friendly, actionable human messages */
export function formatFirebaseError(err: any): string {
  const code = err?.code || '';
  const msg = err?.message || String(err);

  if (code === 'auth/operation-not-allowed') {
    if (msg.toLowerCase().includes('region')) {
      return 'Firebase SMS Region Policy: SMS delivery to India (+91) is restricted by default in your Firebase project. Go to Firebase Console > Authentication > Settings > SMS Region Policy and allow India (+91), or add your number under "Phone numbers for testing".';
    }
    return 'Phone authentication is not enabled in Firebase Console. Go to Firebase Console > Authentication > Sign-in method > Phone > Enable.';
  }
  if (code === 'auth/invalid-phone-number') {
    return 'Invalid phone number format. Please enter a valid 10-digit Indian mobile number.';
  }
  if (code === 'auth/quota-exceeded' || code === 'auth/too-many-requests') {
    return 'Firebase SMS quota exceeded or too many attempts. Please try again after a few minutes.';
  }
  if (code === 'auth/captcha-check-failed') {
    return 'reCAPTCHA verification failed. Please refresh the page and try again.';
  }
  if (code === 'auth/invalid-verification-code') {
    return 'Invalid 6-digit verification code. Please check the SMS and re-enter.';
  }
  if (code === 'auth/code-expired') {
    return 'Verification code expired. Please click Resend Code to get a fresh OTP.';
  }
  if (code === 'auth/unauthorized-domain') {
    return 'Current domain (localhost) is not authorized in Firebase Console. Add "localhost" under Firebase Console > Authentication > Settings > Authorized domains.';
  }
  if (code === 'auth/network-request-failed') {
    return 'Network connection error while contacting Firebase. Please check your internet connection.';
  }
  return msg.replace('Firebase: ', '') || 'Authentication error. Please try again.';
}

/**
 * Creates (or reuses) an invisible reCAPTCHA verifier attached to #recaptcha-container.
 */
export function ensureRecaptcha(): ApplicationVerifier {
  let container = document.getElementById('recaptcha-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'recaptcha-container';
    document.body.appendChild(container);
  }

  if (!recaptchaVerifier) {
    recaptchaVerifier = new RecaptchaVerifier(firebaseAuth, 'recaptcha-container', {
      size: 'invisible',
      callback: () => {
        // reCAPTCHA solved silently
      },
      'expired-callback': () => {
        resetRecaptcha();
      },
    });
  }
  return recaptchaVerifier;
}

/**
 * Format any phone number into E.164 (+91XXXXXXXXXX)
 */
export function formatToE164(phone: string): string {
  const digits = phone.replace(/\D/g, '');
  if (digits.length === 12 && digits.startsWith('91')) {
    return `+${digits}`;
  }
  if (digits.length >= 10) {
    return `+91${digits.slice(-10)}`;
  }
  return `+91${digits}`;
}

/**
 * Send real carrier SMS OTP using Firebase Phone Auth.
 */
export async function sendFirebaseOtp(phone: string): Promise<void> {
  const e164 = formatToE164(phone);
  const verifier = ensureRecaptcha();

  try {
    confirmationResult = await signInWithPhoneNumber(firebaseAuth, e164, verifier);
  } catch (err: any) {
    console.error('[Firebase Phone Auth] Send error:', err);
    resetRecaptcha();
    throw new Error(formatFirebaseError(err));
  }
}

/**
 * Verify the 6-digit code the user entered.
 * On success returns the Firebase ID token for the verified phone.
 */
export async function verifyFirebaseOtp(code: string): Promise<string> {
  if (!confirmationResult) {
    throw new Error('No pending OTP request. Please enter your phone and request OTP first.');
  }
  try {
    const credential = await confirmationResult.confirm(code);
    const idToken = await credential.user.getIdToken();
    confirmationResult = null;
    return idToken;
  } catch (err: any) {
    console.error('[Firebase Phone Auth] Verify error:', err);
    throw new Error(formatFirebaseError(err));
  }
}

/** Reset verifier (e.g. after errors or retries) */
export function resetRecaptcha(): void {
  try {
    if (recaptchaVerifier) {
      recaptchaVerifier.clear();
    }
  } catch {
    // Ignore clear errors
  }
  recaptchaVerifier = null;
  confirmationResult = null;

  // Cleanly replace container element in DOM so grecaptcha does not conflict on retry
  if (typeof document !== 'undefined') {
    const existing = document.getElementById('recaptcha-container');
    if (existing && existing.parentNode) {
      const replacement = document.createElement('div');
      replacement.id = 'recaptcha-container';
      existing.parentNode.replaceChild(replacement, existing);
    }
  }
}
