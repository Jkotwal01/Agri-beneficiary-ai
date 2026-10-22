import { CheckCircle2, Circle, XCircle } from "lucide-react";
import type { Application } from "../../types/application";

const STEPS = ["submitted", "approved"];

export default function StatusTimeline({ application }: { application: Application }) {
  const isRejected = application.status === "rejected";

  return (
    <div className="flex items-center gap-2">
      {STEPS.map((step, i) => {
        const reached = isRejected ? i === 0 : STEPS.indexOf(application.status) >= i;
        return (
          <div key={step} className="flex items-center gap-2">
            {reached ? (
              <CheckCircle2 className="w-4 h-4 text-accent-emerald" />
            ) : (
              <Circle className="w-4 h-4 text-slate-300" />
            )}
            <span className={`text-xs capitalize ${reached ? "text-primary font-medium" : "text-secondary"}`}>
              {step}
            </span>
            {i < STEPS.length - 1 && <div className="w-6 h-px bg-borderline" />}
          </div>
        );
      })}
      {isRejected && (
        <div className="flex items-center gap-2 ml-2">
          <XCircle className="w-4 h-4 text-red-500" />
          <span className="text-xs text-red-600 font-medium">Rejected</span>
        </div>
      )}
    </div>
  );
}
