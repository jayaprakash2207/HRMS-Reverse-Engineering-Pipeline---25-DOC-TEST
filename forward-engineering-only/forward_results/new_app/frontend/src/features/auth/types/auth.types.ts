export interface LoginRequest {
  email: string;
  password: string;
}

export interface RefreshTokenRequest {
  refreshToken: string;
}

// Access tokens carry email/role/employeeId claims (see backend README);
// the login/refresh response surfaces the same fields so the SPA doesn't
// need to decode the JWT client-side to know who is signed in.
export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
  email: string;
  role: string;
  employeeId: number | null;
}

export interface AuthenticatedUser {
  email: string;
  role: string;
  employeeId: number | null;
}
