// API layer for the review queue — all HTTP calls go through here
import type { MatchItem } from "../types/match";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "agri_access_token";

function authHeaders(extra?: HeadersInit): HeadersInit {
  const token = localStorage.getItem(TOKEN_KEY);
  return { ...(token ? { Authorization: `Bearer ${token}` } : {}), ...extra };
}

export async function fetchReviewMatches(): Promise<MatchItem[]> {
  const res = await fetch(`${BASE}/matches?decision=review`, { headers: authHeaders() });
  if (!res.ok) {
    throw new Error("Failed to load review queue");
  }
  return res.json();
}

export async function decideMatch(id: number, decision: "confirm" | "reject"): Promise<MatchItem> {
  const res = await fetch(`${BASE}/matches/${id}/decision`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ decision }),
  });
  if (!res.ok) {
    throw new Error("Failed to save decision");
  }
  return res.json();
}
