import { useEffect, useState } from "react";
import { fetchRecommendedSchemes } from "../api/profile";
import { fetchSchemes } from "../api/schemes";
import type { RecommendedScheme } from "../types/profile";
import type { Scheme } from "../types/application";

export function useRecommendedSchemes() {
  const [schemes, setSchemes] = useState<RecommendedScheme[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchRecommendedSchemes()
      .then((data) => {
        if (!cancelled) setSchemes(data);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load schemes");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { schemes, loading, error };
}

export function useAllSchemes() {
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchSchemes()
      .then((data) => {
        if (!cancelled) setSchemes(data);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load schemes");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { schemes, loading, error };
}
