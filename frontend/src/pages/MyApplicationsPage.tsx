import { useMyApplications } from "../hooks/useApplications";
import { useAllSchemes } from "../hooks/useSchemes";
import StatusTimeline from "../features/applications/StatusTimeline";

export default function MyApplicationsPage() {
  const { applications, loading, error } = useMyApplications();
  const { schemes } = useAllSchemes();

  const schemeName = (schemeId: number) =>
    schemes.find((s) => s.id === schemeId)?.name ?? `Scheme #${schemeId}`;

  return (
    <div className="max-w-2xl mx-auto py-4 space-y-4">
      <h1 className="text-lg font-semibold text-primary">My Applications</h1>

      {loading && <p className="text-sm text-secondary">Loading…</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {!loading && !error && applications.length === 0 && (
        <p className="text-sm text-secondary">You haven't applied to any schemes yet.</p>
      )}

      <div className="space-y-3">
        {applications.map((app) => (
          <div key={app.id} className="bg-surface border border-borderline rounded-sm p-4 space-y-3">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-sm font-semibold text-primary">{schemeName(app.scheme_id)}</h3>
                <p className="text-xs text-secondary mt-0.5">
                  {app.submitted_at ? new Date(app.submitted_at).toLocaleDateString() : ""}
                </p>
              </div>
            </div>
            <StatusTimeline application={app} />
            {app.officer_note && (
              <p className="text-xs text-secondary bg-slate-50 border border-borderline rounded-sm px-2 py-1.5">
                Officer note: {app.officer_note}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
