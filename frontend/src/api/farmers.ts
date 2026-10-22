// API layer for farmers — all HTTP calls go through here
import type { FarmerSummary } from "../types/farmer";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "agri_access_token";

function authHeaders(): HeadersInit {
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchFarmers(q?: string): Promise<FarmerSummary[]> {
  const url = new URL(`${BASE}/farmers`);
  if (q) url.searchParams.set("q", q);
  const res = await fetch(url, { headers: authHeaders() });
  if (!res.ok) {
    throw new Error("Failed to load farmers");
  }
  return res.json();
}
