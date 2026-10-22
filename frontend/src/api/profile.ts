// API layer for the farmer's own profile — all HTTP calls go through here
import type { FarmerProfile, ProfileInput, RecommendedScheme } from "../types/profile";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "agri_access_token";

function authHeaders(extra?: HeadersInit): HeadersInit {
  const token = localStorage.getItem(TOKEN_KEY);
  return { ...(token ? { Authorization: `Bearer ${token}` } : {}), ...extra };
}

export async function fetchMyProfile(): Promise<FarmerProfile | null> {
  const res = await fetch(`${BASE}/me/profile`, { headers: authHeaders() });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to load profile");
  return res.json();
}

export async function saveMyProfile(payload: ProfileInput): Promise<FarmerProfile> {
  const res = await fetch(`${BASE}/me/profile`, {
    method: "PUT",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to save profile");
  return res.json();
}

export async function fetchRecommendedSchemes(): Promise<RecommendedScheme[]> {
  const res = await fetch(`${BASE}/me/schemes?section=recommended`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Failed to load recommended schemes");
  return res.json();
}
