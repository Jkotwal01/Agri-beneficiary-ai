// API layer for flags — all HTTP calls go through here
import type { FlagItem } from "../types/flag";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "agri_access_token";

function authHeaders(extra?: HeadersInit): HeadersInit {
  const token = localStorage.getItem(TOKEN_KEY);
  return { ...(token ? { Authorization: `Bearer ${token}` } : {}), ...extra };
}

export async function fetchFlags(): Promise<FlagItem[]> {
  const res = await fetch(`${BASE}/flags`, { headers: authHeaders() });
  if (!res.ok) {
    throw new Error("Failed to load flags");
  }
  return res.json();
}

export async function updateFlagStatus(
  id: number,
  status: "dismissed" | "confirmed"
): Promise<FlagItem> {
  const res = await fetch(`${BASE}/flags/${id}`, {
    method: "PATCH",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error("Failed to update flag status");
  return res.json();
}
