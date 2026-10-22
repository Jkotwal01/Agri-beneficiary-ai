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

export function useOfficerApplications() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchAllApplications()
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

  async function decide(id: number, decision: "approved" | "rejected") {
    await decideApplication(id, decision);
    setApplications((prev) => prev.map((a) => (a.id === id ? { ...a, status: decision } : a)));
  }

  return { applications, loading, error, decide };
}
