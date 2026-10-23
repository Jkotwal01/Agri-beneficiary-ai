import { useEffect, useState } from "react";
import { BarChart3 } from "lucide-react";
import { fetchEvaluationMetrics } from "../api/evaluation";
import MetricsTable from "../features/evaluation/MetricsTable";
import PrecisionRecallChart from "../features/evaluation/PrecisionRecallChart";
import type { EvaluationMetrics } from "../types/evaluation";

export default function EvaluationPage() {
  const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchEvaluationMetrics()
      .then((data) => {
        if (!cancelled) setMetrics(data);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load metrics");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error === "Access denied") {
    return (
      <div className="h-full flex items-center justify-center text-sm text-red-600">
        Access denied — evaluation metrics are restricted to admins.
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-4 py-4">
      <div className="flex items-center gap-2">
        <BarChart3 className="w-4 h-4 text-accent-sky" />
        <h1 className="text-lg font-semibold text-primary">Resolution Evaluation</h1>
      </div>

      {loading && <p className="text-sm text-secondary">Loading metrics…</p>}
      {error && error !== "Access denied" && <p className="text-sm text-red-600">{error}</p>}

      {metrics && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-surface border border-borderline rounded-sm p-4">
            <h2 className="text-xs font-semibold text-secondary uppercase tracking-wider mb-2">
              Metrics
            </h2>
            <MetricsTable metrics={metrics} />
          </div>
          <div className="bg-surface border border-borderline rounded-sm p-4">
            <h2 className="text-xs font-semibold text-secondary uppercase tracking-wider mb-2">
              Precision / Recall / F1
            </h2>
            <PrecisionRecallChart metrics={metrics} />
          </div>
        </div>
      )}
    </div>
  );
}
