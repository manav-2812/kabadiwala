import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAuthStore } from '../features/auth/authStore';

describe('AuthStore Zustand Store (§3.2)', () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({
      user: null,
      token: null,
      isLoading: false,
      _otpChannel: null,
      _pendingSignup: null,
    });
  });

  it('initializes with null user when localStorage is empty', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
  });

  it('logout clears both store state and localStorage token', () => {
    // Simulate logged in state
    localStorage.setItem('kc_token', 'mock-jwt-token-12345');
    useAuthStore.setState({
      token: 'mock-jwt-token-12345',
      user: {
        id: 'usr-1',
        phone: '9876543210',
        name: 'Ram Lal',
        role: 'collector',
        language: 'hi',
      },
    });

    expect(useAuthStore.getState().token).toBe('mock-jwt-token-12345');
    expect(localStorage.getItem('kc_token')).toBe('mock-jwt-token-12345');

    // Perform logout
    useAuthStore.getState().logout();

    expect(useAuthStore.getState().token).toBeNull();
    expect(useAuthStore.getState().user).toBeNull();
    expect(localStorage.getItem('kc_token')).toBeNull();
  });

  it('setLanguage updates store and localStorage', () => {
    useAuthStore.setState({
      user: {
        id: 'usr-1',
        phone: '9876543210',
        name: 'Ram Lal',
        role: 'collector',
        language: 'hi',
      },
    });

    useAuthStore.getState().setLanguage('pa');

    expect(localStorage.getItem('kc_language')).toBe('pa');
    expect(useAuthStore.getState().user?.language).toBe('pa');
  });
});
