// Auth-related TypeScript types
export type Role = "admin" | "officer" | "farmer";

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
  role: Role;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  role: Role;
}

export interface AuthUser {
  id: number;
  email: string;
  role: Role;
}
