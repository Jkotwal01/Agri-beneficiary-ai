import { useEffect, useState } from "react";
import { decideApplication, fetchAllApplications, fetchMyApplications } from "../api/applications";
import type { Application } from "../types/application";

export function useMyApplications() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchMyApplications()
      .then((data) => {
        if (!cancelled) setApplications(data);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load applications");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { applications, loading, error };
}

export function useOfficerApplications(params?: {
  status_filter?: string;
  farmer_id?: number;
  search?: string;
}) {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const statusFilter = params?.status_filter;
  const farmerId = params?.farmer_id;
  const search = params?.search;

  useEffect(() => {
    let cancelled = false;
    fetchAllApplications({
      status_filter: statusFilter,
      farmer_id: farmerId,
      search,
    })
      .then((data) => {
        if (!cancelled) setApplications(data);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load applications");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [statusFilter, farmerId, search]);

  async function decide(id: number, decision: "approved" | "rejected", note?: string) {
    const updated = await decideApplication(id, decision, note);
    setApplications((prev) =>
      prev.map((a) =>
        a.id === id ? { ...a, ...updated, status: decision, officer_note: note ?? null } : a
      )
    );
    return updated;
  }

  return { applications, loading, error, decide };
}
