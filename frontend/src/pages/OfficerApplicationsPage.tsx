import { useState } from "react";
import { Check, X } from "lucide-react";
import { useOfficerApplications } from "../hooks/useApplications";
import { useAllSchemes } from "../hooks/useSchemes";

export default function OfficerApplicationsPage() {
  const { applications, loading, error, decide } = useOfficerApplications();
  const { schemes } = useAllSchemes();
  const [busyId, setBusyId] = useState<number | null>(null);

  // Rejection modal state (DEF-04)
  const [rejectTarget, setRejectTarget] = useState<number | null>(null);
  const [rejectNote, setRejectNote] = useState("");

  const schemeName = (schemeId: number) =>
    schemes.find((s) => s.id === schemeId)?.name ?? `Scheme #${schemeId}`;

  async function handleDecision(id: number, decision: "approved" | "rejected", note?: string) {
    setBusyId(id);
    try {
      await decide(id, decision, note);
    } finally {
      setBusyId(null);
    }
  }

  function openRejectModal(id: number) {
    setRejectTarget(id);
    setRejectNote("");
  }

  async function confirmReject() {
    if (rejectTarget === null) return;
    await handleDecision(rejectTarget, "rejected", rejectNote.trim() || undefined);
    setRejectTarget(null);
    setRejectNote("");
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
                        onClick={() => openRejectModal(app.id)}
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

      {/* Rejection Note Modal — DEF-04 */}
      {rejectTarget !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-surface border border-borderline rounded-sm shadow-xl w-full max-w-md p-5 space-y-4">
            <h2 className="text-sm font-semibold text-primary">Rejection Reason</h2>
            <p className="text-xs text-secondary">
              Provide an explanatory note for the farmer explaining why the application was rejected.
            </p>
            <textarea
              id="reject-note-input"
              value={rejectNote}
              onChange={(e) => setRejectNote(e.target.value)}
              placeholder="e.g. Total land holding exceeds maximum ceiling for marginal farmer subsidy."
              rows={4}
              className="w-full px-2.5 py-1.5 text-sm bg-slate-50 border border-borderline rounded-sm text-primary focus:outline-none focus:ring-1 focus:ring-red-400 focus:border-red-400 resize-none"
            />
            <div className="flex justify-end gap-2">
              <button
                id="reject-cancel-btn"
                onClick={() => setRejectTarget(null)}
                className="px-3 py-1.5 border border-borderline text-xs font-semibold text-secondary hover:bg-slate-50 rounded-sm transition-colors"
              >
                Cancel
              </button>
              <button
                id="reject-confirm-btn"
                disabled={busyId === rejectTarget}
                onClick={confirmReject}
                className="px-3 py-1.5 bg-red-600 text-white text-xs font-semibold rounded-sm hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {busyId === rejectTarget ? "Rejecting…" : "Confirm Rejection"}
              </button>
            </div>
          </div>
        </div>
      )}
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
