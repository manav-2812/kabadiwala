import React, { useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from '../features/auth/authStore';
import { useOfflineStore } from '../features/offline/offlineStore';
import { initFcm, onForegroundNotification } from '../lib/fcm';
import '../i18n/i18n';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 30000,
    },
  },
});

export const AppProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { checkSession, registerFcmToken, user } = useAuthStore();
  const { updatePendingCount, syncNow } = useOfflineStore();

  useEffect(() => {
    checkSession();
    updatePendingCount();

    const handleOnline = () => {
      useOfflineStore.setState({ isOnline: true });
      syncNow();
    };
    const handleOffline = () => {
      useOfflineStore.setState({ isOnline: false });
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Initialise FCM once a user is authenticated
  useEffect(() => {
    if (!user) return;

    let cleanupForeground: (() => void) | undefined;

    initFcm().then((token) => {
      if (token) {
        // Register token with backend so we can push server-initiated alerts
        registerFcmToken(token);
      }
    });

    // Show in-app toast for foreground notifications
    cleanupForeground = onForegroundNotification((payload) => {
      // Simple notification — you can swap this for a toast library
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(payload.title, {
          body: payload.body,
          icon: payload.icon ?? '/favicon.svg',
        });
      } else {
        console.info('[FCM] Foreground notification:', payload.title, payload.body);
      }
    });

    return () => {
      cleanupForeground?.();
    };
  }, [user]);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};
