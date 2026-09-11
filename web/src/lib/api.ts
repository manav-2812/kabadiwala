import { queueAction } from '../offline/outbox';
import { handleMockRequest, isStandaloneDemo } from '../offline/mockApi';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

// Request timeout for 2G/3G networks (connect 10s, read 25s)
const REQUEST_TIMEOUT_MS = 25000;

export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // ─── Standalone Demo Mode: intercept with mock API ───
  if (isStandaloneDemo()) {
    const method = options.method?.toUpperCase() || 'GET';
    const body = options.body ? JSON.parse(options.body as string) : undefined;
    const result = await handleMockRequest(endpoint, method, body);
    if (result !== null) return result as T;
  }

  const isSimulatedOffline = localStorage.getItem('kc_simulate_offline') === 'true';
  const isReallyOffline = typeof navigator !== 'undefined' && !navigator.onLine;

  if (isSimulatedOffline || isReallyOffline) {
    // If it's a mutation (POST, PATCH, DELETE), queue in outbox!
    const method = options.method?.toUpperCase() || 'GET';
    if (method !== 'GET') {
      const payload = options.body ? JSON.parse(options.body as string) : {};
      const uuid = await queueAction(endpoint, payload);
      // Return simulated optimistic success
      return {
        status: 'queued_offline',
        client_uuid: uuid,
        message: 'Action saved offline in IndexedDB queue. Will sync automatically.'
      } as any;
    }
  }

  const token = localStorage.getItem('kc_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>)
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;

  // AbortController for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorDetail: any = { code: 'HTTP_ERROR', message_key: 'unknown_error' };
      try {
        errorDetail = await response.json();
      } catch {}
      throw errorDetail;
    }

    return response.json();
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err?.name === 'AbortError') {
      throw { code: 'TIMEOUT', message_key: 'request_timeout' };
    }
    throw err;
  }
}

