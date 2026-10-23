// API layer for evaluation metrics — all HTTP calls go through here
import type { EvaluationMetrics } from "../types/evaluation";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "agri_access_token";

function authHeaders(): HeadersInit {
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchEvaluationMetrics(): Promise<EvaluationMetrics> {
  const res = await fetch(`${BASE}/evaluation/metrics`, { headers: authHeaders() });
  if (res.status === 403) {
    throw new Error("Access denied");
  }
  if (!res.ok) throw new Error("Failed to load evaluation metrics");
  return res.json();
}
