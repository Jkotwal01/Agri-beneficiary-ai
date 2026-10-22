import type { ProfileInput } from "../../types/profile";

type Props = {
  draft: ProfileInput;
  onChange: <K extends keyof ProfileInput>(key: K, value: ProfileInput[K]) => void;
};

const DOMAINS = ["AGRICULTURE", "CREDIT", "INSURANCE"];

export default function Step4Interests({ draft, onChange }: Props) {
  const interests = draft.interests ?? [];

  function toggle(domain: string) {
    if (interests.includes(domain)) {
      onChange("interests", interests.filter((d) => d !== domain));
    } else {
      onChange("interests", [...interests, domain]);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-xs font-semibold text-secondary uppercase tracking-wider mb-2">
          Scheme Domains You're Interested In
        </label>
        <div className="flex flex-wrap gap-2">
          {DOMAINS.map((domain) => (
            <button
              key={domain}
              type="button"
              onClick={() => toggle(domain)}
              className={`px-3 py-1.5 rounded-sm text-xs font-semibold border transition-colors ${
                interests.includes(domain)
                  ? "bg-accent-emerald text-white border-accent-emerald"
                  : "bg-surface text-secondary border-borderline hover:bg-slate-50"
              }`}
            >
              {domain}
            </button>
          ))}
        </div>
      </div>
      <label className="flex items-center gap-2 text-sm text-primary">
        <input
          type="checkbox"
          checked={draft.email_opt_in ?? false}
          onChange={(e) => onChange("email_opt_in", e.target.checked)}
        />
        Email me a weekly digest of new scheme matches
      </label>
    </div>
  );
}
