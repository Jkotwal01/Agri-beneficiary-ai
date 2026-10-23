import type { EvaluationMetrics } from "../../types/evaluation";

const ROWS: { key: keyof EvaluationMetrics; label: string }[] = [
  { key: "f1", label: "F1 Score" },
  { key: "precision", label: "Precision" },
  { key: "recall", label: "Recall" },
  { key: "auto_link_rate", label: "Auto-Link Rate" },
  { key: "review_rate", label: "Review Rate" },
];

export default function MetricsTable({ metrics }: { metrics: EvaluationMetrics }) {
  return (
    <table className="w-full text-left border-collapse">
      <tbody className="divide-y divide-borderline">
        {ROWS.map(({ key, label }) => (
          <tr key={key}>
            <td className="px-3 py-2 text-sm text-secondary">{label}</td>
            <td className="px-3 py-2 text-sm font-mono font-semibold text-primary text-right">
              {(metrics[key] * 100).toFixed(1)}%
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
