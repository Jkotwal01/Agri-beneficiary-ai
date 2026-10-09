import { useEffect, useState } from "react";
import { Check, X, Activity, GitMerge } from "lucide-react";

type MatchItem = {
  id: number;
  score: number;
  record_a: Record<string, string | null>;
  record_b: Record<string, string | null>;
  features: Record<string, number>;
  shap: { feature: string; value: string; shap_value: number }[];
};

export default function ReviewQueuePage() {
  const [matches, setMatches] = useState<MatchItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    fetch("/api/matches?decision=review")
      .then((res) => res.json())
      .then((data) => setMatches(data.items));
  }, []);

  if (matches.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-secondary text-sm">
        No matches pending review.
      </div>
    );
  }

  const match = matches[currentIndex];

  const handleDecision = () => {
    // Mock API call to save decision
    if (currentIndex < matches.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      setMatches([]);
    }
  };

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Header */}
      <div className="bg-surface border border-borderline rounded-sm px-4 py-3 flex items-center justify-between shrink-0">
        <div>
          <h3 className="text-sm font-semibold text-primary flex items-center">
            <GitMerge className="w-4 h-4 mr-2 text-accent-amber" />
            Fuzzy Matching Resolution Tool
          </h3>
          <p className="text-xs text-secondary mt-0.5">
            Manual override required. AI confidence falls in the uncertainty band [0.50 - 0.80].
          </p>
        </div>
        <div className="text-xs font-mono bg-slate-100 text-secondary px-2 py-1 rounded-sm border border-slate-200">
          Queue: {currentIndex + 1} / {matches.length}
        </div>
      </div>

      {/* Split Pane View */}
      <div className="flex-1 flex gap-4 min-h-0">
        
        {/* Record A */}
        <div className="flex-1 bg-surface border border-borderline rounded-sm flex flex-col overflow-hidden">
          <div className="bg-slate-50 px-3 py-2 border-b border-borderline text-xs font-semibold text-secondary uppercase tracking-wider flex justify-between">
            <span>Record A</span>
            <span className="text-accent-sky font-mono bg-accent-sky/10 px-1.5 rounded-sm border border-accent-sky/20">
              {match.record_a.source}
            </span>
          </div>
          <div className="p-4 flex-1 overflow-auto">
            <RecordDetails record={match.record_a} />
          </div>
        </div>

        {/* Center Control / XGBoost Gauge */}
        <div className="w-72 shrink-0 flex flex-col space-y-4">
          
          <div className="bg-surface border border-borderline rounded-sm p-4 flex flex-col items-center justify-center text-center">
            <div className="text-xs font-semibold text-secondary uppercase tracking-wider mb-2">
              XGBoost Confidence
            </div>
            {/* Gauge representation */}
            <div className="relative w-32 h-16 overflow-hidden flex items-end justify-center mb-2">
              <div className="absolute top-0 w-32 h-32 rounded-full border-[12px] border-slate-100" />
              <div 
                className="absolute top-0 w-32 h-32 rounded-full border-[12px] border-accent-amber transition-transform duration-1000 ease-out" 
                style={{ clipPath: 'polygon(0 50%, 100% 50%, 100% 100%, 0 100%)', transform: `rotate(${(match.score * 180) - 180}deg)` }}
              />
              <span className="text-2xl font-bold text-primary font-mono mb-[-4px]">
                {(match.score * 100).toFixed(1)}%
              </span>
            </div>
            
            <div className="w-full mt-4 flex gap-2">
              <button 
                onClick={() => handleDecision()}
                className="flex-1 flex items-center justify-center px-3 py-1.5 border border-red-200 bg-red-50 text-red-700 text-xs font-semibold rounded-sm hover:bg-red-100 transition-colors"
              >
                <X className="w-3.5 h-3.5 mr-1" />
                Reject
              </button>
              <button 
                onClick={() => handleDecision()}
                className="flex-1 flex items-center justify-center px-3 py-1.5 bg-accent-emerald text-white text-xs font-semibold rounded-sm hover:bg-emerald-700 transition-colors shadow-sm"
              >
                <Check className="w-3.5 h-3.5 mr-1" />
                Merge
              </button>
            </div>
          </div>

          <div className="bg-surface border border-borderline rounded-sm flex-1 flex flex-col overflow-hidden">
            <div className="bg-slate-50 px-3 py-2 border-b border-borderline text-xs font-semibold text-secondary uppercase tracking-wider flex items-center">
              <Activity className="w-3.5 h-3.5 mr-1.5" />
              SHAP Explainability
            </div>
            <div className="p-3 flex-1 overflow-auto space-y-3">
              {match.shap.map((s, i) => (
                <div key={i} className="text-xs">
                  <div className="flex justify-between mb-1">
                    <span className="font-mono text-secondary">{s.feature}</span>
                    <span className={`font-mono font-medium ${s.shap_value > 0 ? 'text-accent-emerald' : 'text-red-600'}`}>
                      {s.shap_value > 0 ? '+' : ''}{s.shap_value.toFixed(2)}
                    </span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden flex">
                    {/* Fake bar visualization */}
                    <div className="w-1/2 flex justify-end">
                       {s.shap_value < 0 && <div className="h-full bg-red-500" style={{ width: `${Math.min(Math.abs(s.shap_value) * 50, 100)}%` }} />}
                    </div>
                    <div className="w-1/2 flex justify-start">
                       {s.shap_value > 0 && <div className="h-full bg-accent-emerald" style={{ width: `${Math.min(s.shap_value * 50, 100)}%` }} />}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
        </div>

        {/* Record B */}
        <div className="flex-1 bg-surface border border-borderline rounded-sm flex flex-col overflow-hidden">
          <div className="bg-slate-50 px-3 py-2 border-b border-borderline text-xs font-semibold text-secondary uppercase tracking-wider flex justify-between">
            <span>Record B</span>
            <span className="text-accent-sky font-mono bg-accent-sky/10 px-1.5 rounded-sm border border-accent-sky/20">
              {match.record_b.source}
            </span>
          </div>
          <div className="p-4 flex-1 overflow-auto">
             <RecordDetails record={match.record_b} />
          </div>
        </div>

      </div>
    </div>
  );
}

function RecordDetails({ record }: { record: Record<string, string | null> }) {
  const fields = [
    { label: "Normalized Name", key: "name_norm" },
    { label: "Mobile (10 digit)", key: "mobile10" },
    { label: "District Code", key: "district_code" },
    { label: "Survey Number", key: "survey_no" },
    { label: "Date of Birth", key: "dob" },
  ];

  return (
    <div className="space-y-4">
      {fields.map((f) => (
        <div key={f.key}>
          <div className="text-[11px] font-semibold text-secondary uppercase tracking-wider mb-1">
            {f.label}
          </div>
          <div className="text-sm font-mono text-primary bg-slate-50 border border-slate-200 px-2 py-1.5 rounded-sm">
            {record[f.key] || <span className="text-slate-400 italic">null</span>}
          </div>
        </div>
      ))}
    </div>
  );
}
