import { Settings, Save, AlertCircle } from "lucide-react";
import { useFlags } from "../hooks/useFlags";

export default function FlagsPage() {
  const { flags, loading, error, updateStatus } = useFlags();

  return (
    <div className="h-full flex gap-4">
      
      {/* Visual Rule Builder */}
      <div className="w-1/2 bg-surface flex flex-col rounded-sm overflow-hidden border border-borderline">
        <div className="px-3 py-2 bg-slate-50 border-b border-borderline flex items-center justify-between shrink-0">
          <div className="flex items-center text-sm font-semibold text-primary">
            <Settings className="w-4 h-4 mr-2 text-secondary" />
            Eligibility & Validation Rules
          </div>
          <button className="flex items-center bg-accent-sky hover:bg-sky-600 text-white px-2.5 py-1.5 rounded-sm text-xs font-semibold transition-colors">
            <Save className="w-3.5 h-3.5 mr-1.5" /> Save Changes
          </button>
        </div>
        
        <div className="flex-1 p-4 overflow-auto space-y-6">
          
          {/* PM-KISAN Rules */}
          <div className="border border-borderline rounded-sm overflow-hidden">
            <div className="bg-slate-50 px-3 py-2 border-b border-borderline flex items-center justify-between">
              <h4 className="text-xs font-bold text-primary uppercase tracking-wider">PM-KISAN</h4>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-medium text-accent-emerald">Active</span>
                <div className="w-8 h-4 bg-accent-emerald rounded-full relative shadow-inner">
                  <div className="absolute right-0.5 top-0.5 w-3 h-3 bg-white rounded-full"></div>
                </div>
              </div>
            </div>
            <div className="p-3 space-y-3 bg-white">
              
              <div className="flex items-center space-x-2">
                <span className="text-xs font-semibold text-secondary w-32">Total Land (Ha)</span>
                <select className="border border-borderline rounded-sm text-xs px-2 py-1 bg-slate-50 text-primary outline-none">
                  <option>&lt;= (Less than or equal to)</option>
                  <option>&gt; (Greater than)</option>
                  <option>== (Equal to)</option>
                </select>
                <input type="number" defaultValue={2.0} className="border border-borderline rounded-sm text-xs px-2 py-1 w-20 bg-slate-50 text-primary outline-none" />
                <span className="text-[10px] text-red-500 font-medium ml-2 bg-red-50 px-1.5 py-0.5 rounded border border-red-100">Exceeds marginal threshold</span>
              </div>

              <div className="flex items-center space-x-2">
                <span className="text-xs font-semibold text-secondary w-32">Total Land (Ha)</span>
                <select className="border border-borderline rounded-sm text-xs px-2 py-1 bg-slate-50 text-primary outline-none">
                  <option>&gt; (Greater than)</option>
                  <option>&lt;= (Less than or equal to)</option>
                  <option>== (Equal to)</option>
                </select>
                <input type="number" defaultValue={0} className="border border-borderline rounded-sm text-xs px-2 py-1 w-20 bg-slate-50 text-primary outline-none" />
                <span className="text-[10px] text-red-500 font-medium ml-2 bg-red-50 px-1.5 py-0.5 rounded border border-red-100">Must own land</span>
              </div>

            </div>
          </div>

          {/* PMFBY Rules */}
          <div className="border border-borderline rounded-sm overflow-hidden">
            <div className="bg-slate-50 px-3 py-2 border-b border-borderline flex items-center justify-between">
              <h4 className="text-xs font-bold text-primary uppercase tracking-wider">PMFBY (Crop Insurance)</h4>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-medium text-accent-emerald">Active</span>
                <div className="w-8 h-4 bg-accent-emerald rounded-full relative shadow-inner">
                  <div className="absolute right-0.5 top-0.5 w-3 h-3 bg-white rounded-full"></div>
                </div>
              </div>
            </div>
            <div className="p-3 space-y-3 bg-white">
              
              <div className="flex items-center space-x-2">
                <span className="text-xs font-semibold text-secondary w-32">Crop Type</span>
                <select className="border border-borderline rounded-sm text-xs px-2 py-1 bg-slate-50 text-primary outline-none">
                  <option>is one of</option>
                  <option>is not</option>
                </select>
                <input type="text" defaultValue="wheat, rice, cotton" className="border border-borderline rounded-sm text-xs px-2 py-1 flex-1 bg-slate-50 text-primary outline-none" />
              </div>

            </div>
          </div>

          <button className="w-full py-2 border-2 border-dashed border-borderline text-secondary text-xs font-semibold rounded-sm hover:bg-slate-50 transition-colors">
            + Add New Scheme Policy
          </button>

        </div>
      </div>

      {/* Flags Data Table */}
      <div className="w-1/2 flex flex-col bg-surface border border-borderline rounded-sm">
        <div className="px-3 py-2 border-b border-borderline bg-slate-50 flex justify-between items-center shrink-0">
          <h3 className="text-sm font-semibold text-primary">Active Engine Flags</h3>
          <span className="text-xs text-secondary font-mono">Live Monitoring</span>
        </div>
        <div className="flex-1 overflow-auto p-4 space-y-3">
          {loading && <p className="text-sm text-secondary">Loading flags…</p>}
          {error && <p className="text-sm text-red-600">{error}</p>}
          {flags.map((flag) => {
            const isHigh = flag.severity.toUpperCase() === "HIGH";
            return (
              <div key={flag.id} className="border border-borderline rounded-sm overflow-hidden">
                <div className="bg-slate-50 px-3 py-1.5 border-b border-borderline flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <AlertCircle className={`w-4 h-4 ${isHigh ? 'text-red-600' : 'text-accent-amber'}`} />
                    <span className="text-xs font-mono font-bold text-primary">{flag.type}</span>
                  </div>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-sm font-bold uppercase ${
                    isHigh ? 'bg-red-100 text-red-700 border border-red-200' : 'bg-amber-100 text-amber-700 border border-amber-200'
                  }`}>
                    {flag.severity}
                  </span>
                </div>
                <div className="p-3 bg-surface">
                  <div className="text-xs text-secondary mb-2 flex justify-between">
                    <span>Target: <strong className="text-primary">{flag.farmer_name ?? "Unknown"}</strong></span>
                    <span className="font-mono">ID: {flag.farmer_id}</span>
                  </div>
                  <p className="text-sm text-primary leading-snug">
                    {flag.reason}
                  </p>
                  <div className="mt-3 flex justify-end space-x-2">
                     <button
                       onClick={() => updateStatus(flag.id, 'dismissed')}
                       className="px-2 py-1 border border-borderline text-xs font-semibold text-secondary hover:bg-slate-50 rounded-sm transition-colors"
                     >
                       Dismiss
                     </button>
                     <button
                       onClick={() => updateStatus(flag.id, 'confirmed')}
                       className="px-2 py-1 bg-primary text-white text-xs font-semibold hover:bg-slate-800 rounded-sm transition-colors"
                     >
                       Investigate
                     </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}
