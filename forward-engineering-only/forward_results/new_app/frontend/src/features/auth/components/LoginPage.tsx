import React, { useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { extractApiError, getHttpStatus } from '../../../shared/api/apiError';
import './LoginPage.css';

interface LocationState {
  from?: string;
}

export function LoginPage(): JSX.Element {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Already-authenticated visitors (e.g. session restored from a persisted
  // refresh token) should never see the login form - send them where they
  // were headed instead.
  if (user) {
    const state = location.state as LocationState | null;
    return <Navigate to={state?.from ?? '/'} replace />;
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      // Requires both an email AND a password - there is no "email only"
      // shortcut here, deliberately, per UI/UX Specification §4 (the source
      // system's unconditional-session-issuance defect must not resurface).
      await login(email, password);
      const state = location.state as LocationState | null;
      navigate(state?.from ?? '/', { replace: true });
    } catch (error) {
      const status = getHttpStatus(error);
      const apiError = extractApiError(error);

      if (status === 403 || apiError?.errorCode === 'ACCOUNT_LOCKED') {
        setErrorMessage(
          'This account has been locked after repeated failed sign-in attempts. Contact your administrator to unlock it.'
        );
      } else if (status === 401) {
        setErrorMessage('Incorrect email or password.');
      } else {
        setErrorMessage(apiError?.message ?? 'Something went wrong while signing in. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <form className="login-page__form" onSubmit={(event) => void handleSubmit(event)} noValidate>
        <h1>Sign in</h1>

        <label htmlFor="login-email">Email</label>
        <input
          id="login-email"
          name="email"
          type="email"
          autoComplete="username"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />

        <label htmlFor="login-password">Password</label>
        <input
          id="login-password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />

        {errorMessage && (
          <p role="alert" className="login-page__error">
            {errorMessage}
          </p>
        )}

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </main>
  );
}
