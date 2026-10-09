import { useEffect, useState } from "react";
import { Settings, Save, AlertCircle } from "lucide-react";

type FlagItem = {
  id: number;
  farmer_id: number;
  farmer_name: string;
  type: string;
  severity: string;
  status: string;
  details: string;
};

export default function FlagsPage() {
  const [flags, setFlags] = useState<FlagItem[]>([]);

  useEffect(() => {
    fetch("/api/flags")
      .then((res) => res.json())
      .then((data) => setFlags(data.items));
  }, []);

  const yamlConfig = `# schemes.yaml - Eligibility & Duplicate Rules
PM_KISAN:
  domain: AGRICULTURE
  active: true
  rules:
    - field: total_land_ha
      operator: "<="
      value: 2.0
      error: "Exceeds marginal farmer threshold"
    - field: total_land_ha
      operator: ">"
      value: 0
      error: "Must own > 0 land"

PMFBY:
  domain: AGRICULTURE
  active: true
  rules:
    - field: crop
      operator: "in"
      value: ["wheat", "rice", "cotton"]
      error: "Uninsured crop type"
`;

  return (
    <div className="h-full flex gap-4">
      
      {/* YAML Configurator */}
      <div className="w-1/2 bg-primary flex flex-col rounded-sm overflow-hidden border border-primary shadow-xl">
        <div className="px-3 py-2 bg-slate-800 border-b border-slate-700 flex items-center justify-between">
          <div className="flex items-center text-xs font-mono text-slate-300">
            <Settings className="w-3.5 h-3.5 mr-2" />
            schemes.yaml (Active Engine Config)
          </div>
          <button className="flex items-center bg-accent-sky hover:bg-sky-500 text-white px-2 py-1 rounded-sm text-[11px] font-semibold transition-colors">
            <Save className="w-3 h-3 mr-1" /> Deploy Rules
          </button>
        </div>
        <div className="flex-1 p-4 overflow-auto">
          <pre className="text-[12px] font-mono leading-relaxed text-slate-300">
            <code>
{yamlConfig.split('\n').map((line, i) => (
  <div key={i} className="flex">
    <span className="w-8 shrink-0 text-slate-600 select-none border-r border-slate-700 mr-4 text-right pr-2">
      {i + 1}
    </span>
    <span>
      {line.includes('PM_KISAN:') || line.includes('PMFBY:') ? (
        <span className="text-accent-emerald font-bold">{line}</span>
      ) : line.includes('rules:') ? (
        <span className="text-purple-400">{line}</span>
      ) : line.includes('value:') ? (
        <span className="text-accent-amber">{line}</span>
      ) : line.includes('#') ? (
        <span className="text-slate-500 italic">{line}</span>
      ) : (
        <span>{line}</span>
      )}
    </span>
  </div>
))}
            </code>
          </pre>
        </div>
      </div>

      {/* Flags Data Table */}
      <div className="w-1/2 flex flex-col bg-surface border border-borderline rounded-sm">
        <div className="px-3 py-2 border-b border-borderline bg-slate-50 flex justify-between items-center shrink-0">
          <h3 className="text-sm font-semibold text-primary">Active Engine Flags</h3>
          <span className="text-xs text-secondary font-mono">Live Monitoring</span>
        </div>
        <div className="flex-1 overflow-auto p-4 space-y-3">
          {flags.map((flag) => (
            <div key={flag.id} className="border border-borderline rounded-sm overflow-hidden">
              <div className="bg-slate-50 px-3 py-1.5 border-b border-borderline flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  <AlertCircle className={`w-4 h-4 ${flag.severity === 'HIGH' ? 'text-red-600' : 'text-accent-amber'}`} />
                  <span className="text-xs font-mono font-bold text-primary">{flag.type}</span>
                </div>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-sm font-bold uppercase ${
                  flag.severity === 'HIGH' ? 'bg-red-100 text-red-700 border border-red-200' : 'bg-amber-100 text-amber-700 border border-amber-200'
                }`}>
                  {flag.severity}
                </span>
              </div>
              <div className="p-3 bg-surface">
                <div className="text-xs text-secondary mb-2 flex justify-between">
                  <span>Target: <strong className="text-primary">{flag.farmer_name}</strong></span>
                  <span className="font-mono">ID: {flag.farmer_id}</span>
                </div>
                <p className="text-sm text-primary leading-snug">
                  {flag.details}
                </p>
                <div className="mt-3 flex justify-end space-x-2">
                   <button className="px-2 py-1 border border-borderline text-xs font-semibold text-secondary hover:bg-slate-50 rounded-sm transition-colors">Dismiss</button>
                   <button className="px-2 py-1 bg-primary text-white text-xs font-semibold hover:bg-slate-800 rounded-sm transition-colors">Investigate</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
