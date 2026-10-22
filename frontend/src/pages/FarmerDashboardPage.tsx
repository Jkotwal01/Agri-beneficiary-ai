import { Link } from "react-router-dom";
import { useProfile } from "../hooks/useProfile";
import { useRecommendedSchemes } from "../hooks/useSchemes";
import CompletenessMeter from "../features/profile/CompletenessMeter";
import SchemeFeedCard from "../features/schemes/SchemeFeedCard";

export default function FarmerDashboardPage() {
  const { profile, loading: profileLoading } = useProfile();
  const { schemes, loading, error } = useRecommendedSchemes();

  const showProfilePrompt = !profileLoading && (!profile || profile.completeness < 100);

  return (
    <div className="max-w-3xl mx-auto space-y-6 py-4">
      <div>
        <h1 className="text-lg font-semibold text-primary">
          Welcome{profile?.full_name ? `, ${profile.full_name}` : ""}
        </h1>
        <p className="text-sm text-secondary mt-0.5">Schemes matched to your profile.</p>
      </div>

      {showProfilePrompt && (
        <div className="bg-surface border border-accent-amber/30 bg-accent-amber/5 rounded-sm p-4 space-y-3">
          <CompletenessMeter value={profile?.completeness ?? 0} />
          <Link
            to="/me/profile"
            className="inline-block text-xs font-semibold text-accent-emerald hover:underline"
          >
            {profile ? "Complete your profile" : "Build your profile"} to unlock scheme recommendations →
          </Link>
        </div>
      )}

      {loading && <p className="text-sm text-secondary">Loading your scheme feed…</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      {!loading && !error && schemes.length === 0 && (
        <p className="text-sm text-secondary">
          No matched schemes yet — finish your profile so we can check your eligibility.
        </p>
      )}

      <div className="space-y-3">
        {schemes.map((s) => (
          <SchemeFeedCard key={s.scheme_id} scheme={s} />
        ))}
      </div>
    </div>
  );
}
