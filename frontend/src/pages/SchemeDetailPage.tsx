import { Link, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useAllSchemes } from "../hooks/useSchemes";

export default function SchemeDetailPage() {
  const { code } = useParams<{ code: string }>();
  const { schemes, loading, error } = useAllSchemes();

  if (loading) return <div className="p-4 text-sm text-secondary">Loading…</div>;
  if (error) return <div className="p-4 text-sm text-red-600">{error}</div>;

  const scheme = schemes.find((s) => s.code === code);

  if (!scheme) {
    return <div className="p-4 text-sm text-secondary">Scheme not found.</div>;
  }

  return (
    <div className="max-w-2xl mx-auto py-4 space-y-4">
      <Link to="/me" className="inline-flex items-center text-xs text-secondary hover:text-primary">
        <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Back to schemes
      </Link>

      <div className="bg-surface border border-borderline rounded-sm p-6">
        <p className="text-xs font-mono text-secondary uppercase tracking-wider">{scheme.code}</p>
        <h1 className="text-lg font-semibold text-primary mt-1">{scheme.name}</h1>
        {scheme.domain && (
          <span className="inline-block mt-2 text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-sm bg-accent-sky/10 text-accent-sky border border-accent-sky/20">
            {scheme.domain}
          </span>
        )}
        <p className="text-sm text-secondary mt-4">
          {scheme.description || "No description available for this scheme."}
        </p>

        <Link
          to={`/me/schemes/${scheme.code}/apply`}
          className="inline-block mt-6 px-4 py-2 bg-accent-emerald text-white text-xs font-semibold rounded-sm hover:bg-emerald-700 transition-colors"
        >
          Apply Now
        </Link>
      </div>
    </div>
  );
}
