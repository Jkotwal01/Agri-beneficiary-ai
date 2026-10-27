import { useEffect, useState } from "react";
import { fetchFlags, updateFlagStatus } from "../api/flags";
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

  async function updateStatus(id: number, status: "dismissed" | "confirmed") {
    const updated = await updateFlagStatus(id, status);
    setFlags((prev) => prev.map((f) => (f.id === id ? updated : f)));
  }

  return { flags, error, loading, updateStatus };
}
