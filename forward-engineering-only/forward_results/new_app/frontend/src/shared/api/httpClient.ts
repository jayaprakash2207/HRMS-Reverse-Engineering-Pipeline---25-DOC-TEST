import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

let currentAccessToken: string | null = null;
let unauthorizedHandler: (() => void) | null = null;

export function setAccessToken(token: string | null): void {
  currentAccessToken = token;
}

export function getAccessToken(): string | null {
  return currentAccessToken;
}

// Registered by the auth feature's AuthProvider so this shared module never
// has to import feature code to react to a session becoming invalid.
export function onUnauthorized(handler: () => void): void {
  unauthorizedHandler = handler;
}

export const httpClient = axios.create({
  baseURL: __API_BASE_URL__,
  headers: {
    'Content-Type': 'application/json',
  },
});

httpClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (currentAccessToken) {
    config.headers.set('Authorization', `Bearer ${currentAccessToken}`);
  }
  return config;
});

httpClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      currentAccessToken = null;
      unauthorizedHandler?.();
    }
    return Promise.reject(error);
  }
);
