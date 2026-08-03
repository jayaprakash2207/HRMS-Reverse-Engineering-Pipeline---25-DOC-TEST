import { httpClient } from '../../../shared/api/httpClient';
import { AuthResponse, LoginRequest, RefreshTokenRequest } from '../types/auth.types';

const AUTH_BASE_PATH = '/api/v1/auth';

export async function login(request: LoginRequest): Promise<AuthResponse> {
  const { data } = await httpClient.post<AuthResponse>(`${AUTH_BASE_PATH}/login`, request);
  return data;
}

export async function refresh(request: RefreshTokenRequest): Promise<AuthResponse> {
  const { data } = await httpClient.post<AuthResponse>(`${AUTH_BASE_PATH}/refresh`, request);
  return data;
}

export async function logout(request: RefreshTokenRequest): Promise<void> {
  await httpClient.post(`${AUTH_BASE_PATH}/logout`, request);
}
