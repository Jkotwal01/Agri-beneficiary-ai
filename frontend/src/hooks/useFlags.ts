import { useEffect, useState } from "react";
import { fetchFlags } from "../api/flags";
import type { FlagItem } from "../types/flag";

export function useFlags() {
  const [flags, setFlags] = useState<FlagItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetchFlags()
      .then((data) => {
        if (!cancelled) setFlags(data);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load flags");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { flags, error, loading };
}
