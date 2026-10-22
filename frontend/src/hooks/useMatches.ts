import { useEffect, useState } from "react";
import { decideMatch, fetchReviewMatches } from "../api/matches";
import type { MatchItem } from "../types/match";

export function useMatches() {
  const [matches, setMatches] = useState<MatchItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetchReviewMatches()
      .then((data) => {
        if (!cancelled) setMatches(data);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load matches");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function decide(id: number, decision: "confirm" | "reject") {
    await decideMatch(id, decision);
    setMatches((prev) => prev.filter((m) => m.id !== id));
  }

  return { matches, error, loading, decide };
}
