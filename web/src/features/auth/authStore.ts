/**
 * Auth Store — Kabadiwala Connect
 *
 * Primary Auth Engine: Firebase Phone Authentication
 * - Delivers real SMS OTP directly to user's phone via carrier gateways
 * - 10,000 free OTPs/month with zero DLT paperwork
 * - Exchanged with backend /api/auth/verify-firebase for Kabadiwala JWT
 */
import { create } from 'zustand';
import { apiRequest } from '../../lib/api';
import {
  isFirebaseConfigured,
  sendFirebaseOtp,
  verifyFirebaseOtp,
} from '../../lib/firebasePhoneAuth';

export interface UserProfile {
  id: string;
  phone: string;
  name: string;
  display_name_local?: string | null;
  role: 'collector' | 'aggregator' | 'recycler' | 'admin';
  language: string;
  profile?: any;
}

export interface PendingSignupData {
  phone?: string;
  email?: string;
  name: string;
  role: string;
  language: string;
  city?: string;
  company_name?: string;
  cpcb_license_no?: string;
}

interface AuthState {
  user: UserProfile | null;
  token: string | null;
  isLoading: boolean;
  _otpChannel: 'firebase' | 'backend' | null;
  _pendingSignup: PendingSignupData | null;

  requestOtp: (identifier: string, isEmail?: boolean) => Promise<{
    status: string;
    message: string;
    delivered?: boolean;
    provider?: string;
    dev_otp?: string;
    warning?: string;
  }>;
  signup: (data: PendingSignupData) => Promise<{
    status: string;
    message: string;
    delivered?: boolean;
    provider?: string;
    dev_otp?: string;
    warning?: string;
  }>;
  login: (identifier: string, otp: string, isEmail?: boolean) => Promise<void>;
  logout: () => void;
  setLanguage: (lang: string) => void;
  checkSession: () => Promise<void>;

  /** Register FCM device token with backend so it can push notifications */
  registerFcmToken: (token: string) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('kc_token'),
  isLoading: false,
  _otpChannel: null,
  _pendingSignup: null,

  requestOtp: async (identifier: string, isEmail?: boolean) => {
    // 1. Email OTP Flow directly through backend/SMTP
    if (isEmail) {
      const res = await apiRequest('/api/auth/request-otp', {
        method: 'POST',
        body: JSON.stringify({ email: identifier }),
      });
      set({ _otpChannel: 'backend', _pendingSignup: null });
      return res;
    }

    // 2. Try Firebase Phone Auth first if configured
    if (isFirebaseConfigured()) {
      try {
        await sendFirebaseOtp(identifier);
        set({ _otpChannel: 'firebase', _pendingSignup: null });
        return {
          status: 'success',
          message: `Real verification SMS dispatched to +91 ${identifier}`,
          delivered: true,
          provider: 'Firebase SMS',
        };
      } catch (fbErr: any) {
        console.warn('[AuthStore] Firebase Phone Auth unavailable or failed, attempting backend fallback:', fbErr);
        // Automatic graceful fallback to backend OTP so the user is never blocked
        try {
          const res = await apiRequest('/api/auth/request-otp', {
            method: 'POST',
            body: JSON.stringify({ phone: identifier }),
          });
          set({ _otpChannel: 'backend', _pendingSignup: null });
          return {
            ...res,
            warning: fbErr?.message || 'Firebase Phone Auth is disabled in Firebase Console. Switched to backend OTP.',
          };
        } catch (backendErr) {
          throw fbErr;
        }
      }
    }

    // 3. Direct backend OTP fallback if Firebase is not configured
    const res = await apiRequest('/api/auth/request-otp', {
      method: 'POST',
      body: JSON.stringify({ phone: identifier }),
    });
    set({ _otpChannel: 'backend', _pendingSignup: null });
    return res;
  },

  signup: async (data: PendingSignupData) => {
    // 1. Email signup flow
    if (data.email) {
      const res = await apiRequest('/api/auth/signup', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      set({ _otpChannel: 'backend', _pendingSignup: data });
      return res;
    }

    // 2. Try Firebase Phone Auth first if configured
    if (isFirebaseConfigured() && data.phone) {
      try {
        await sendFirebaseOtp(data.phone);
        set({ _otpChannel: 'firebase', _pendingSignup: data });
        return {
          status: 'success',
          message: `Real verification SMS dispatched to +91 ${data.phone}`,
          delivered: true,
          provider: 'Firebase SMS',
        };
      } catch (fbErr: any) {
        console.warn('[AuthStore] Firebase Phone Auth signup failed, attempting backend fallback:', fbErr);
        try {
          const res = await apiRequest('/api/auth/signup', {
            method: 'POST',
            body: JSON.stringify(data),
          });
          set({ _otpChannel: 'backend', _pendingSignup: data });
          return {
            ...res,
            warning: fbErr?.message || 'Firebase Phone Auth is disabled in Firebase Console. Switched to backend OTP.',
          };
        } catch (backendErr) {
          throw fbErr;
        }
      }
    }

    // 3. Direct backend signup fallback
    const res = await apiRequest('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    set({ _otpChannel: 'backend', _pendingSignup: data });
    return res;
  },

  login: async (identifier: string, otp: string, isEmail?: boolean) => {
    set({ isLoading: true });
    try {
      const channel = get()._otpChannel ?? (isFirebaseConfigured() && !isEmail ? 'firebase' : 'backend');
      const pendingSignup = get()._pendingSignup;

      let res: any;
      if (channel === 'firebase' && !isEmail) {
        // Verify code with Firebase client-side SDK
        const firebaseIdToken = await verifyFirebaseOtp(otp);

        // Exchange verified Firebase token with backend for Kabadiwala JWT + profile creation
        res = await apiRequest('/api/auth/verify-firebase', {
          method: 'POST',
          body: JSON.stringify({
            phone: identifier,
            firebase_id_token: firebaseIdToken,
            ...(pendingSignup || {}),
          }),
        });
      } else {
        // Standard backend OTP verify (Phone or Email)
        const body = isEmail ? { email: identifier, otp } : { phone: identifier, otp };
        res = await apiRequest('/api/auth/verify-otp', {
          method: 'POST',
          body: JSON.stringify(body),
        });
      }

      localStorage.setItem('kc_token', res.access_token);
      set({
        user: res.user,
        token: res.access_token,
        isLoading: false,
        _otpChannel: null,
        _pendingSignup: null,
      });
    } catch (err) {
      set({ isLoading: false });
      throw err;
    }
  },

  logout: () => {
    localStorage.removeItem('kc_token');
    set({ user: null, token: null, _otpChannel: null, _pendingSignup: null });
  },

  setLanguage: (lang: string) => {
    localStorage.setItem('kc_language', lang);
    const user = get().user;
    if (user) {
      set({ user: { ...user, language: lang } });
      apiRequest('/api/auth/me', {
        method: 'PATCH',
        body: JSON.stringify({ language: lang }),
      }).catch(() => {});
    }
  },

  checkSession: async () => {
    try {
      const user = await apiRequest('/api/auth/me');
      set({ user });
    } catch {
      set({ user: null, token: null });
      localStorage.removeItem('kc_token');
    }
  },

  registerFcmToken: async (fcmToken: string) => {
    const token = get().token;
    if (!token) return;
    await apiRequest('/api/notifications/fcm-token', {
      method: 'POST',
      body: JSON.stringify({ fcm_token: fcmToken }),
    }).catch(() => {});
  },
}));
