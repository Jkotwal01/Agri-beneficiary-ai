// API layer for reports — all HTTP calls go through here
import type { ReportSummary } from "../types/report";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "agri_access_token";

function authHeaders(): HeadersInit {
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchSummary(): Promise<ReportSummary> {
  const res = await fetch(`${BASE}/reports/summary`, { headers: authHeaders() });
  if (!res.ok) {
    throw new Error("Failed to load report summary");
  }
  return res.json();
}
