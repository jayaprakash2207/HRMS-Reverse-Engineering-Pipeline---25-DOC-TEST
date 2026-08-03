import React from 'react';
import { useAuth } from '../../features/auth/hooks/useAuth';

// Placeholder landing page: no other module's screens exist yet this sprint
// (Security/Identity only). Gives logged-in users somewhere to land and a way
// to sign out; future sprints will replace this with real module navigation.
export function DashboardPage(): JSX.Element {
  const { user, logout } = useAuth();

  return (
    <main>
      <h1>HRMS</h1>
      {user && (
        <p>
          Signed in as <strong>{user.email}</strong> ({user.role})
        </p>
      )}
      <button type="button" onClick={() => void logout()}>
        Sign out
      </button>
    </main>
  );
}
