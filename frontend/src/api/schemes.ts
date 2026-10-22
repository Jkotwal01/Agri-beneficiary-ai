// API layer for schemes — all HTTP calls go through here
import type { Scheme } from "../types/application";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "agri_access_token";

function authHeaders(): HeadersInit {
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchSchemes(): Promise<Scheme[]> {
  const res = await fetch(`${BASE}/schemes`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Failed to load schemes");
  return res.json();
}
