// AuthContext — stores token + decoded user in memory; persists to localStorage
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { AuthUser, Role } from "../types/auth";

const TOKEN_KEY = "agri_access_token";

interface AuthState {
  token: string | null;
  user: AuthUser | null;
  role: Role | null;
}

interface AuthContextValue extends AuthState {
  setAuth: (token: string, role: Role) => void;
  logout: () => void;
}

function decodePayload(token: string): { sub: string; role: Role; email: string } | null {
  try {
    const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(base64));
  } catch {
    return null;
  }
}

export const AuthContext = createContext<AuthContextValue>({
  token: null,
  user: null,
  role: null,
  setAuth: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (!stored) return { token: null, user: null, role: null };
    const payload = decodePayload(stored);
    if (!payload) return { token: null, user: null, role: null };
    return {
      token: stored,
      role: payload.role,
      user: { id: parseInt(payload.sub, 10), email: payload.email, role: payload.role },
    };
  });

  const setAuth = useCallback((token: string, role: Role) => {
    localStorage.setItem(TOKEN_KEY, token);
    const payload = decodePayload(token);
    setState({
      token,
      role,
      user: payload
        ? { id: parseInt(payload.sub, 10), email: payload.email, role }
        : null,
    });
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setState({ token: null, user: null, role: null });
  }, []);

  const value = useMemo(() => ({ ...state, setAuth, logout }), [state, setAuth, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  return useContext(AuthContext);
}
