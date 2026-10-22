import type { EvaluationMetrics } from "../../types/evaluation";

const BARS: { key: keyof EvaluationMetrics; label: string; color: string }[] = [
  { key: "precision", label: "Precision", color: "var(--color-accent-sky)" },
  { key: "recall", label: "Recall", color: "var(--color-accent-emerald)" },
  { key: "f1", label: "F1", color: "var(--color-accent-amber)" },
];

export default function PrecisionRecallChart({ metrics }: { metrics: EvaluationMetrics }) {
  return (
    <div className="space-y-3">
      {BARS.map(({ key, label, color }) => {
        const value = metrics[key];
        return (
          <div key={key}>
            <div className="flex justify-between text-xs text-secondary mb-1">
              <span>{label}</span>
              <span className="font-mono font-semibold text-primary">{(value * 100).toFixed(1)}%</span>
            </div>
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full transition-all duration-500"
                style={{ width: `${value * 100}%`, backgroundColor: color }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
