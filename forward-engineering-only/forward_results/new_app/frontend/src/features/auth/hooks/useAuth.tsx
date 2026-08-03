import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import * as authApi from '../api/authApi';
import { clearRefreshToken, readRefreshToken, storeRefreshToken } from '../api/authStorage';
import { onUnauthorized, setAccessToken } from '../../../shared/api/httpClient';
import { AuthResponse, AuthenticatedUser } from '../types/auth.types';

interface AuthContextValue {
  user: AuthenticatedUser | null;
  isBootstrapping: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }): JSX.Element {
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  const applySession = useCallback((session: AuthResponse) => {
    setAccessToken(session.accessToken);
    storeRefreshToken(session.refreshToken);
    setUser({ email: session.email, role: session.role, employeeId: session.employeeId });
  }, []);

  const clearSession = useCallback(() => {
    setAccessToken(null);
    clearRefreshToken();
    setUser(null);
  }, []);

  useEffect(() => {
    // Stateless JWT: an account locked mid-token-life stays valid until the
    // access token expires (see backend README). The only client-side signal
    // that a session has gone bad is a 401 from a subsequent request.
    onUnauthorized(() => {
      clearSession();
    });
  }, [clearSession]);

  useEffect(() => {
    const existingRefreshToken = readRefreshToken();
    if (!existingRefreshToken) {
      setIsBootstrapping(false);
      return;
    }
    authApi
      .refresh({ refreshToken: existingRefreshToken })
      .then((session) => applySession(session))
      .catch(() => clearSession())
      .finally(() => setIsBootstrapping(false));
    // Runs once on mount to restore a session from a persisted refresh token.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const session = await authApi.login({ email, password });
      applySession(session);
    },
    [applySession]
  );

  const logout = useCallback(async () => {
    const existingRefreshToken = readRefreshToken();
    try {
      if (existingRefreshToken) {
        await authApi.logout({ refreshToken: existingRefreshToken });
      }
    } finally {
      clearSession();
    }
  }, [clearSession]);

  const value = useMemo<AuthContextValue>(
    () => ({ user, isBootstrapping, login, logout }),
    [user, isBootstrapping, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
