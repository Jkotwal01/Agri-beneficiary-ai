import { useState } from "react";
import { useProfile } from "../hooks/useProfile";

export default function SettingsPage() {
  const { profile, loading, saving, save } = useProfile();
  const [saved, setSaved] = useState(false);

  async function toggleOptIn() {
    if (!profile) return;
    setSaved(false);
    await save({ email_opt_in: !profile.email_opt_in });
    setSaved(true);
  }

  if (loading) return <div className="p-4 text-sm text-secondary">Loading…</div>;

  return (
    <div className="max-w-xl mx-auto py-4 space-y-4">
      <h1 className="text-lg font-semibold text-primary">Settings</h1>

      <div className="bg-surface border border-borderline rounded-sm p-6 space-y-4">
        <label className="flex items-center justify-between">
          <span className="text-sm text-primary">Weekly scheme digest email</span>
          <input
            type="checkbox"
            checked={profile?.email_opt_in ?? false}
            onChange={toggleOptIn}
            disabled={saving || !profile}
          />
        </label>
        {saved && <p className="text-xs text-accent-emerald">Preference saved.</p>}
        {!profile && (
          <p className="text-xs text-secondary">Build your profile first to manage preferences.</p>
        )}
      </div>
    </div>
  );
}
