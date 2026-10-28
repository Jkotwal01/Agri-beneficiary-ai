import { useState } from "react";
import { Settings, Save, Plus, ShieldCheck, AlertCircle, Trash2, CheckCircle2 } from "lucide-react";

interface PolicyRule {
  id: string;
  field: string;
  operator: string;
  value: string | number;
  alertText: string;
}

interface SchemePolicy {
  id: string;
  code: string;
  name: string;
  active: boolean;
  rules: PolicyRule[];
}

export default function RulesPage() {
  const [policies, setPolicies] = useState<SchemePolicy[]>([
    {
      id: "pmkisan",
      code: "PM_KISAN",
      name: "PM-KISAN (Income Support Scheme)",
      active: true,
      rules: [
        {
          id: "r1",
          field: "Total Land (Ha)",
          operator: "<=",
          value: 2.0,
          alertText: "Exceeds marginal/small farmer ceiling threshold (2.0 Ha)",
        },
        {
          id: "r2",
          field: "Total Land (Ha)",
          operator: ">",
          value: 0,
          alertText: "Land holding must be greater than 0 Ha (must own cultivable land)",
        },
        {
          id: "r3",
          field: "Institutional Landholder",
          operator: "==",
          value: "No",
          alertText: "Institutional landholders are legally excluded from PM-KISAN",
        },
      ],
    },
    {
      id: "pmfby",
      code: "PMFBY",
      name: "PMFBY (Pradhan Mantri Fasal Bima Yojana)",
      active: true,
      rules: [
        {
          id: "r4",
          field: "Notified Crop",
          operator: "is one of",
          value: "wheat, rice, cotton, soybean, mustard",
          alertText: "Crop must be notified for the village/district under insurance season",
        },
        {
          id: "r5",
          field: "Claimed Parcel Area (Ha)",
          operator: "<=",
          value: "Survey Parcel Size",
          alertText: "Parcel overclaim violation: insured area exceeds geo-registry survey size",
        },
      ],
    },
    {
      id: "nfsm",
      code: "NFSM",
      name: "NFSM (National Food Security Mission)",
      active: true,
      rules: [
        {
          id: "r6",
          field: "Subsidized Machinery Claims",
          operator: "<=",
          value: 1,
          alertText: "Maximum 1 subsidized farm equipment per beneficiary per financial year",
        },
      ],
    },
    {
      id: "kcc",
      code: "KCC",
      name: "KCC (Kisan Credit Card Scheme)",
      active: false,
      rules: [
        {
          id: "r7",
          field: "Credit Limit (INR)",
          operator: "<=",
          value: 300000,
          alertText: "Exceeds interest subvention ceiling of ₹3 Lakhs",
        },
      ],
    },
  ]);

  const [savedSuccess, setSavedSuccess] = useState(false);

  const togglePolicyActive = (id: string) => {
    setPolicies((prev) =>
      prev.map((p) => (p.id === id ? { ...p, active: !p.active } : p))
    );
  };

  const handleRuleValueChange = (policyId: string, ruleId: string, newValue: string | number) => {
    setPolicies((prev) =>
      prev.map((p) => {
        if (p.id !== policyId) return p;
        return {
          ...p,
          rules: p.rules.map((r) => (r.id === ruleId ? { ...r, value: newValue } : r)),
        };
      })
    );
  };

  const handleRuleOperatorChange = (policyId: string, ruleId: string, newOp: string) => {
    setPolicies((prev) =>
      prev.map((p) => {
        if (p.id !== policyId) return p;
        return {
          ...p,
          rules: p.rules.map((r) => (r.id === ruleId ? { ...r, operator: newOp } : r)),
        };
      })
    );
  };

  const handleDeleteRule = (policyId: string, ruleId: string) => {
    setPolicies((prev) =>
      prev.map((p) => {
        if (p.id !== policyId) return p;
        return {
          ...p,
          rules: p.rules.filter((r) => r.id !== ruleId),
        };
      })
    );
  };

  const handleAddRule = (policyId: string) => {
    const newRule: PolicyRule = {
      id: `r_${Date.now()}`,
      field: "Total Land (Ha)",
      operator: "<=",
      value: 5.0,
      alertText: "Threshold exceeded for eligible quota",
    };

    setPolicies((prev) =>
      prev.map((p) => {
        if (p.id !== policyId) return p;
        return { ...p, rules: [...p.rules, newRule] };
      })
    );
  };

  const handleSave = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Header */}
      <div className="bg-surface border border-borderline rounded-sm px-4 py-3 flex items-center justify-between shrink-0">
        <div>
          <h2 className="text-sm font-semibold text-primary flex items-center">
            <Settings className="w-4 h-4 mr-2 text-secondary" />
            Eligibility & Validation Rules Engine
          </h2>
          <p className="text-xs text-secondary mt-0.5">
            Configure automated policy constraints, exclusion criteria, and threshold parameters for real-time validation.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {savedSuccess && (
            <span className="flex items-center text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-1 rounded border border-emerald-200 animate-fadeIn">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />
              Policy rules saved successfully
            </span>
          )}
          <button
            onClick={handleSave}
            className="flex items-center bg-accent-sky hover:bg-sky-600 text-white px-3 py-1.5 rounded-sm text-xs font-semibold transition-colors shadow-sm"
          >
            <Save className="w-3.5 h-3.5 mr-1.5" /> Save Changes
          </button>
        </div>
      </div>

      {/* Policies List */}
      <div className="flex-1 overflow-auto space-y-4 pr-1">
        {policies.map((policy) => (
          <div key={policy.id} className="bg-surface border border-borderline rounded-sm overflow-hidden shadow-sm">
            {/* Policy Title Bar */}
            <div className="bg-slate-50 px-4 py-2.5 border-b border-borderline flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <ShieldCheck className={`w-4 h-4 ${policy.active ? "text-accent-emerald" : "text-secondary"}`} />
                <h3 className="text-xs font-bold text-primary uppercase tracking-wider">{policy.name}</h3>
                <span className="text-[10px] font-mono px-1.5 py-0.2 bg-slate-200 text-slate-700 rounded">
                  {policy.code}
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`text-xs font-medium ${policy.active ? "text-accent-emerald" : "text-secondary"}`}>
                  {policy.active ? "Active" : "Disabled"}
                </span>
                <button
                  type="button"
                  onClick={() => togglePolicyActive(policy.id)}
                  className={`w-9 h-5 rounded-full relative transition-colors ${
                    policy.active ? "bg-accent-emerald" : "bg-slate-300"
                  }`}
                >
                  <div
                    className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-all shadow-sm ${
                      policy.active ? "right-0.5" : "left-0.5"
                    }`}
                  />
                </button>
              </div>
            </div>

            {/* Rules Container */}
            <div className="p-4 space-y-3 bg-white">
              {policy.rules.length === 0 ? (
                <p className="text-xs text-secondary italic">No rules defined for this policy.</p>
              ) : (
                policy.rules.map((rule) => (
                  <div
                    key={rule.id}
                    className="flex flex-wrap items-center gap-2 p-2.5 bg-slate-50/70 border border-slate-200 rounded-sm"
                  >
                    <span className="text-xs font-semibold text-secondary min-w-[130px]">{rule.field}</span>
                    <select
                      value={rule.operator}
                      onChange={(e) => handleRuleOperatorChange(policy.id, rule.id, e.target.value)}
                      className="border border-borderline rounded-sm text-xs px-2 py-1 bg-white text-primary outline-none focus:ring-1 focus:ring-sky-400"
                    >
                      <option value="<=">&lt;= (Less than or equal to)</option>
                      <option value=">">&gt; (Greater than)</option>
                      <option value="==">== (Equal to)</option>
                      <option value="!=">!= (Not equal to)</option>
                      <option value="is one of">is one of</option>
                      <option value="is not">is not</option>
                    </select>

                    <input
                      type={typeof rule.value === "number" ? "number" : "text"}
                      value={rule.value}
                      onChange={(e) =>
                        handleRuleValueChange(
                          policy.id,
                          rule.id,
                          typeof rule.value === "number" ? parseFloat(e.target.value) || 0 : e.target.value
                        )
                      }
                      className="border border-borderline rounded-sm text-xs px-2 py-1 bg-white text-primary outline-none focus:ring-1 focus:ring-sky-400 min-w-[100px] flex-1"
                    />

                    <span className="text-[11px] text-red-600 font-medium bg-red-50 px-2 py-1 rounded border border-red-100 flex items-center">
                      <AlertCircle className="w-3 h-3 mr-1 shrink-0" />
                      {rule.alertText}
                    </span>

                    <button
                      onClick={() => handleDeleteRule(policy.id, rule.id)}
                      title="Remove rule"
                      className="p-1 text-slate-400 hover:text-red-500 rounded transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))
              )}

              <div className="pt-2">
                <button
                  onClick={() => handleAddRule(policy.id)}
                  className="flex items-center text-xs font-semibold text-accent-sky hover:text-sky-700 transition-colors"
                >
                  <Plus className="w-3.5 h-3.5 mr-1" /> Add Custom Rule Condition
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
