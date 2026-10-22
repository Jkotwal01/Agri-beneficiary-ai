import { useState } from "react";
import { Check, X } from "lucide-react";
import { useOfficerApplications } from "../hooks/useApplications";
import { useAllSchemes } from "../hooks/useSchemes";

export default function OfficerApplicationsPage() {
  const { applications, loading, error, decide } = useOfficerApplications();
  const { schemes } = useAllSchemes();
  const [busyId, setBusyId] = useState<number | null>(null);

  const schemeName = (schemeId: number) =>
    schemes.find((s) => s.id === schemeId)?.name ?? `Scheme #${schemeId}`;

  async function handleDecision(id: number, decision: "approved" | "rejected") {
    setBusyId(id);
    try {
      await decide(id, decision);
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-sm font-semibold text-primary">Scheme Applications Inbox</h1>

      {loading && <p className="text-sm text-secondary">Loading…</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="bg-surface border border-borderline rounded-sm overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead className="bg-slate-50 border-b border-borderline">
            <tr>
              <Th>ID</Th>
              <Th>Scheme</Th>
              <Th>Status</Th>
              <Th>Submitted</Th>
              <Th>Actions</Th>
            </tr>
          </thead>
          <tbody className="text-sm divide-y divide-borderline">
            {applications.map((app) => (
              <tr key={app.id}>
                <td className="px-3 py-2 font-mono text-xs text-secondary">{app.id}</td>
                <td className="px-3 py-2 text-primary font-medium">{schemeName(app.scheme_id)}</td>
                <td className="px-3 py-2">
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded-sm font-bold uppercase ${
                      app.status === "approved"
                        ? "bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/20"
                        : app.status === "rejected"
                        ? "bg-red-100 text-red-700 border border-red-200"
                        : "bg-accent-amber/10 text-accent-amber border border-accent-amber/20"
                    }`}
                  >
                    {app.status}
                  </span>
                </td>
                <td className="px-3 py-2 text-xs text-secondary">
                  {app.submitted_at ? new Date(app.submitted_at).toLocaleDateString() : "-"}
                </td>
                <td className="px-3 py-2">
                  {app.status === "submitted" ? (
                    <div className="flex gap-2">
                      <button
                        disabled={busyId === app.id}
                        onClick={() => handleDecision(app.id, "approved")}
                        className="flex items-center px-2 py-1 bg-accent-emerald text-white text-xs font-semibold rounded-sm hover:bg-emerald-700 transition-colors disabled:opacity-50"
                      >
                        <Check className="w-3.5 h-3.5 mr-1" /> Approve
                      </button>
                      <button
                        disabled={busyId === app.id}
                        onClick={() => handleDecision(app.id, "rejected")}
                        className="flex items-center px-2 py-1 border border-red-200 bg-red-50 text-red-700 text-xs font-semibold rounded-sm hover:bg-red-100 transition-colors disabled:opacity-50"
                      >
                        <X className="w-3.5 h-3.5 mr-1" /> Reject
                      </button>
                    </div>
                  ) : (
                    <span className="text-xs text-secondary">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="px-3 py-2 text-xs font-semibold text-secondary uppercase tracking-wider whitespace-nowrap">
      {children}
    </th>
  );
}
