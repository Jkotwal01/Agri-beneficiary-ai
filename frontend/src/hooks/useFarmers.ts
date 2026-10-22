import { useEffect, useState } from "react";
import { fetchFarmers } from "../api/farmers";
import type { FarmerSummary } from "../types/farmer";

export function useFarmers(q?: string) {
  const [farmers, setFarmers] = useState<FarmerSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetchFarmers(q)
      .then((data) => {
        if (!cancelled) setFarmers(data);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load farmers");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [q]);

  return { farmers, error, loading };
}
