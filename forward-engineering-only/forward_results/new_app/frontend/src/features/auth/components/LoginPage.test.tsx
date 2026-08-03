import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { LoginPage } from './LoginPage';
import { useAuth } from '../hooks/useAuth';

jest.mock('../hooks/useAuth');

const mockedUseAuth = useAuth as jest.Mock;

function renderLoginPage() {
  return render(
    <MemoryRouter initialEntries={['/login']}>
      <LoginPage />
    </MemoryRouter>
  );
}

describe('LoginPage', () => {
  const login = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockedUseAuth.mockReturnValue({ user: null, isBootstrapping: false, login, logout: jest.fn() });
  });

  it('renders email and password fields and a submit control', () => {
    renderLoginPage();

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('submits the entered email and password to login()', async () => {
    login.mockResolvedValue(undefined);
    renderLoginPage();

    await userEvent.type(screen.getByLabelText(/email/i), 'jane.doe@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'correct-horse-battery-staple');
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() =>
      expect(login).toHaveBeenCalledWith('jane.doe@example.com', 'correct-horse-battery-staple')
    );
  });

  it('displays an error message when login fails and does not clear the form silently', async () => {
    login.mockRejectedValue(new Error('Invalid credentials'));
    renderLoginPage();

    await userEvent.type(screen.getByLabelText(/email/i), 'jane.doe@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'wrong-password');
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByRole('alert')).toBeInTheDocument();
  });

  it('disables the submit control while a login request is in flight to prevent double submission', async () => {
    let resolveLogin: () => void = () => {};
    login.mockReturnValue(new Promise<void>((resolve) => { resolveLogin = resolve; }));
    renderLoginPage();

    await userEvent.type(screen.getByLabelText(/email/i), 'jane.doe@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'correct-horse-battery-staple');
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    await userEvent.click(submitButton);

    expect(submitButton).toBeDisabled();

    resolveLogin();
    await waitFor(() => expect(submitButton).not.toBeDisabled());
  });

  it('does not call login() when required fields are left empty', async () => {
    renderLoginPage();

    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(login).not.toHaveBeenCalled();
  });

  it('redirects away from the login form when a user is already authenticated', () => {
    mockedUseAuth.mockReturnValue({
      user: { email: 'jane.doe@example.com', role: 'EMPLOYEE', employeeId: 42 },
      isBootstrapping: false,
      login,
      logout: jest.fn(),
    });

    renderLoginPage();

    expect(screen.queryByLabelText(/email/i)).not.toBeInTheDocument();
  });
});
