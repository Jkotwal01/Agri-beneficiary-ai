// useAuth — thin hook over AuthContext + API calls
import { useState } from "react";
import { apiLogin, apiRegister } from "../api/auth";
import { useAuthContext } from "../context/AuthContext";
import type { LoginRequest, RegisterRequest } from "../types/auth";

export function useAuth() {
  const { token, user, role, setAuth, logout } = useAuthContext();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function login(payload: LoginRequest) {
    setLoading(true);
    setError(null);
    try {
      const res = await apiLogin(payload);
      setAuth(res.access_token, res.role);
      return res;
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Login failed";
      setError(msg);
      throw e;
    } finally {
      setLoading(false);
    }
  }

  async function register(payload: RegisterRequest) {
    setLoading(true);
    setError(null);
    try {
      const res = await apiRegister(payload);
      setAuth(res.access_token, res.role);
      return res;
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Registration failed";
      setError(msg);
      throw e;
    } finally {
      setLoading(false);
    }
  }

  return { token, user, role, loading, error, login, register, logout };
}
