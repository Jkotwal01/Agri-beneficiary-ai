import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import type { RecommendedScheme } from "../../types/profile";

export default function SchemeFeedCard({ scheme }: { scheme: RecommendedScheme }) {
  return (
    <div className="bg-surface border border-borderline rounded-sm p-4 flex items-center justify-between hover:border-accent-emerald transition-colors">
      <div>
        <p className="text-xs font-mono text-secondary uppercase tracking-wider">{scheme.scheme_code}</p>
        <h3 className="text-sm font-semibold text-primary mt-0.5">{scheme.scheme_name}</h3>
      </div>
      <Link
        to={`/me/schemes/${scheme.scheme_code}`}
        className="flex items-center text-xs font-semibold text-accent-emerald hover:underline"
      >
        View & Apply <ArrowRight className="w-3.5 h-3.5 ml-1" />
      </Link>
    </div>
  );
}
