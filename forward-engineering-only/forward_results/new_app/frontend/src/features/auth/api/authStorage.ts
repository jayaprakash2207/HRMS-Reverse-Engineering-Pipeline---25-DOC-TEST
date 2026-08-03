// Persists only the refresh token across reloads so the SPA can silently
// re-establish a session on load; the access token itself lives in memory
// only (shared/api/httpClient) and is never written to storage.
const REFRESH_TOKEN_KEY = 'hrms.auth.refreshToken';

export function storeRefreshToken(token: string): void {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

export function readRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function clearRefreshToken(): void {
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}
