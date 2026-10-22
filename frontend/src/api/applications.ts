// API layer for scheme applications — all HTTP calls go through here
import type { Application, PrefillResult } from "../types/application";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "agri_access_token";

function authHeaders(extra?: HeadersInit): HeadersInit {
  const token = localStorage.getItem(TOKEN_KEY);
  return { ...(token ? { Authorization: `Bearer ${token}` } : {}), ...extra };
}

export async function prefillApplication(schemeCode: string): Promise<PrefillResult> {
  const res = await fetch(`${BASE}/applications/prefill`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ scheme_code: schemeCode }),
  });
  if (!res.ok) throw new Error("Failed to prefill application");
  return res.json();
}

export async function submitApplication(
  schemeCode: string,
  formData: Record<string, unknown>
): Promise<Application> {
  const res = await fetch(`${BASE}/applications`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ scheme_code: schemeCode, form_data: formData }),
  });
  if (res.status === 409) {
    throw new Error("You already have an active application for this scheme");
  }
  if (!res.ok) throw new Error("Failed to submit application");
  return res.json();
}

export async function fetchMyApplications(): Promise<Application[]> {
  const res = await fetch(`${BASE}/applications`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Failed to load applications");
  return res.json();
}

export async function fetchAllApplications(): Promise<Application[]> {
  const res = await fetch(`${BASE}/applications`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Failed to load applications");
  return res.json();
}

export async function decideApplication(
  id: number,
  decision: "approved" | "rejected",
  note?: string
): Promise<Application> {
  const res = await fetch(`${BASE}/applications/${id}/decision`, {
    method: "PATCH",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ status: decision, note }),
  });
  if (!res.ok) throw new Error("Failed to save decision");
  return res.json();
}
