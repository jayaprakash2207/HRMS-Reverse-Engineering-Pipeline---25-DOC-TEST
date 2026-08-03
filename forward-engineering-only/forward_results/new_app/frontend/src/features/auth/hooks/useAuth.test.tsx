import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from './useAuth';
import * as authApi from '../api/authApi';
import * as authStorage from '../api/authStorage';
import * as httpClient from '../../../shared/api/httpClient';

jest.mock('../api/authApi');
jest.mock('../api/authStorage');
jest.mock('../../../shared/api/httpClient');

const mockedAuthApi = authApi as jest.Mocked<typeof authApi>;
const mockedAuthStorage = authStorage as jest.Mocked<typeof authStorage>;
const mockedHttpClient = httpClient as jest.Mocked<typeof httpClient>;

const SESSION = {
  accessToken: 'access-token-value',
  refreshToken: 'refresh-token-value',
  tokenType: 'Bearer',
  expiresIn: 900,
  email: 'jane.doe@example.com',
  role: 'EMPLOYEE',
  employeeId: 42,
};

function TestConsumer(): JSX.Element {
  const { user, isBootstrapping, login, logout } = useAuth();
  return (
    <div>
      <p data-testid="bootstrapping">{String(isBootstrapping)}</p>
      <p data-testid="user">{user ? `${user.email}:${user.role}` : 'none'}</p>
      <button onClick={() => void login('jane.doe@example.com', 'correct-horse-battery-staple')}>login</button>
      <button onClick={() => void logout()}>logout</button>
    </div>
  );
}

function renderWithProvider() {
  return render(
    <AuthProvider>
      <TestConsumer />
    </AuthProvider>
  );
}

describe('useAuth / AuthProvider', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockedAuthStorage.readRefreshToken.mockReturnValue(null);
  });

  it('throws when used outside of an AuthProvider', () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
    expect(() => render(<TestConsumer />)).toThrow('useAuth must be used within an AuthProvider');
    consoleError.mockRestore();
  });

  it('finishes bootstrapping with no user when no refresh token is stored', async () => {
    renderWithProvider();

    await waitFor(() => expect(screen.getByTestId('bootstrapping')).toHaveTextContent('false'));
    expect(screen.getByTestId('user')).toHaveTextContent('none');
    expect(mockedAuthApi.refresh).not.toHaveBeenCalled();
  });

  it('restores a session from a stored refresh token on mount', async () => {
    mockedAuthStorage.readRefreshToken.mockReturnValue('stored-refresh-token');
    mockedAuthApi.refresh.mockResolvedValue(SESSION);

    renderWithProvider();

    await waitFor(() => expect(screen.getByTestId('bootstrapping')).toHaveTextContent('false'));
    expect(mockedAuthApi.refresh).toHaveBeenCalledWith({ refreshToken: 'stored-refresh-token' });
    expect(screen.getByTestId('user')).toHaveTextContent('jane.doe@example.com:EMPLOYEE');
    expect(mockedHttpClient.setAccessToken).toHaveBeenCalledWith('access-token-value');
    expect(mockedAuthStorage.storeRefreshToken).toHaveBeenCalledWith('refresh-token-value');
  });

  it('clears the session when the stored refresh token is no longer valid', async () => {
    mockedAuthStorage.readRefreshToken.mockReturnValue('stale-refresh-token');
    mockedAuthApi.refresh.mockRejectedValue(new Error('expired'));

    renderWithProvider();

    await waitFor(() => expect(screen.getByTestId('bootstrapping')).toHaveTextContent('false'));
    expect(screen.getByTestId('user')).toHaveTextContent('none');
    expect(mockedAuthStorage.clearRefreshToken).toHaveBeenCalled();
    expect(mockedHttpClient.setAccessToken).toHaveBeenCalledWith(null);
  });

  it('login() calls the API and populates the user on success', async () => {
    mockedAuthApi.login.mockResolvedValue(SESSION);
    renderWithProvider();
    await waitFor(() => expect(screen.getByTestId('bootstrapping')).toHaveTextContent('false'));

    await userEvent.click(screen.getByText('login'));

    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('jane.doe@example.com:EMPLOYEE'));
    expect(mockedAuthApi.login).toHaveBeenCalledWith({
      email: 'jane.doe@example.com',
      password: 'correct-horse-battery-staple',
    });
    expect(mockedAuthStorage.storeRefreshToken).toHaveBeenCalledWith('refresh-token-value');
  });

  it('logout() calls the API with the stored refresh token and always clears the session', async () => {
    mockedAuthStorage.readRefreshToken.mockReturnValueOnce(null).mockReturnValue('refresh-token-value');
    mockedAuthApi.login.mockResolvedValue(SESSION);
    mockedAuthApi.logout.mockResolvedValue(undefined);
    renderWithProvider();
    await waitFor(() => expect(screen.getByTestId('bootstrapping')).toHaveTextContent('false'));
    await userEvent.click(screen.getByText('login'));
    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('jane.doe@example.com:EMPLOYEE'));

    await userEvent.click(screen.getByText('logout'));

    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('none'));
    expect(mockedAuthApi.logout).toHaveBeenCalledWith({ refreshToken: 'refresh-token-value' });
    expect(mockedHttpClient.setAccessToken).toHaveBeenLastCalledWith(null);
  });

  it('logout() clears the session even when the API call fails', async () => {
    mockedAuthStorage.readRefreshToken.mockReturnValueOnce(null).mockReturnValue('refresh-token-value');
    mockedAuthApi.login.mockResolvedValue(SESSION);
    mockedAuthApi.logout.mockRejectedValue(new Error('network error'));
    renderWithProvider();
    await waitFor(() => expect(screen.getByTestId('bootstrapping')).toHaveTextContent('false'));
    await userEvent.click(screen.getByText('login'));
    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('jane.doe@example.com:EMPLOYEE'));

    await userEvent.click(screen.getByText('logout'));

    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('none'));
  });

  it('logout() clears local session state without calling the API when no refresh token is stored', async () => {
    mockedAuthStorage.readRefreshToken.mockReturnValue(null);
    renderWithProvider();
    await waitFor(() => expect(screen.getByTestId('bootstrapping')).toHaveTextContent('false'));

    await userEvent.click(screen.getByText('logout'));

    expect(mockedAuthApi.logout).not.toHaveBeenCalled();
    expect(mockedHttpClient.setAccessToken).toHaveBeenCalledWith(null);
  });

  it('registers an unauthorized handler that clears the session when a 401 is observed', async () => {
    let capturedHandler: (() => void) | undefined;
    mockedHttpClient.onUnauthorized.mockImplementation((handler) => {
      capturedHandler = handler;
    });
    mockedAuthApi.login.mockResolvedValue(SESSION);
    renderWithProvider();
    await waitFor(() => expect(screen.getByTestId('bootstrapping')).toHaveTextContent('false'));
    await userEvent.click(screen.getByText('login'));
    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('jane.doe@example.com:EMPLOYEE'));

    expect(capturedHandler).toBeDefined();
    capturedHandler!();

    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('none'));
  });
});
