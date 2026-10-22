import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useProfile } from "../hooks/useProfile";
import CompletenessMeter from "../features/profile/CompletenessMeter";
import Step1Personal from "../features/profile/Step1Personal";
import Step2Address from "../features/profile/Step2Address";
import Step3Land from "../features/profile/Step3Land";
import Step4Interests from "../features/profile/Step4Interests";
import type { FarmerProfile, ProfileInput } from "../types/profile";

const STEPS = ["Personal", "Address", "Land", "Interests"];

function draftFromProfile(profile: FarmerProfile | null): ProfileInput {
  if (!profile) return {};
  return {
    full_name: profile.full_name,
    father_name: profile.father_name,
    dob: profile.dob,
    gender: profile.gender,
    mobile: profile.mobile,
    village: profile.village,
    taluka: profile.taluka,
    district: profile.district,
    state: profile.state,
    pincode: profile.pincode,
    total_land_ha: profile.total_land_ha,
    ownership_type: profile.ownership_type,
    main_crops: profile.main_crops,
    irrigation_type: profile.irrigation_type,
    interests: profile.interests,
    email_opt_in: profile.email_opt_in,
  };
}

export default function ProfileWizardPage() {
  const { profile, loading, saving, error, save } = useProfile();

  if (loading) {
    return <div className="p-8 text-sm text-secondary">Loading profile…</div>;
  }

  return <WizardBody profile={profile} saving={saving} error={error} save={save} />;
}

function WizardBody({
  profile,
  saving,
  error,
  save,
}: {
  profile: FarmerProfile | null;
  saving: boolean;
  error: string | null;
  save: (payload: ProfileInput) => Promise<FarmerProfile>;
}) {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [draft, setDraft] = useState<ProfileInput>(() => draftFromProfile(profile));

  function onChange<K extends keyof ProfileInput>(key: K, value: ProfileInput[K]) {
    setDraft((prev) => ({ ...prev, [key]: value }));
  }

  async function handleNext() {
    await save(draft);
    if (step < STEPS.length - 1) {
      setStep((s) => s + 1);
    } else {
      navigate("/me");
    }
  }

  return (
    <div className="max-w-xl mx-auto py-8 space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-primary mb-1">Build Your Profile</h1>
        <p className="text-sm text-secondary">
          A complete profile helps us match you to the right schemes and autofill applications.
        </p>
      </div>

      <CompletenessMeter value={profile?.completeness ?? 0} />

      <div className="bg-surface border border-borderline rounded-sm p-6">
        <div className="flex items-center gap-2 mb-6">
          {STEPS.map((label, i) => (
            <div key={label} className="flex items-center gap-2">
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                  i === step
                    ? "bg-accent-sky text-white"
                    : i < step
                    ? "bg-accent-emerald text-white"
                    : "bg-slate-100 text-secondary"
                }`}
              >
                {i + 1}
              </div>
              <span className={`text-xs ${i === step ? "text-primary font-semibold" : "text-secondary"}`}>
                {label}
              </span>
              {i < STEPS.length - 1 && <div className="w-6 h-px bg-borderline" />}
            </div>
          ))}
        </div>

        {step === 0 && <Step1Personal draft={draft} onChange={onChange} />}
        {step === 1 && <Step2Address draft={draft} onChange={onChange} />}
        {step === 2 && <Step3Land draft={draft} onChange={onChange} />}
        {step === 3 && <Step4Interests draft={draft} onChange={onChange} />}

        {error && <p className="text-xs text-red-600 mt-4">{error}</p>}

        <div className="flex justify-between mt-6">
          <button
            type="button"
            disabled={step === 0}
            onClick={() => setStep((s) => s - 1)}
            className="px-3 py-1.5 text-xs font-semibold text-secondary border border-borderline rounded-sm disabled:opacity-40 hover:bg-slate-50 transition-colors"
          >
            Back
          </button>
          <button
            type="button"
            disabled={saving}
            onClick={handleNext}
            className="px-4 py-1.5 text-xs font-semibold text-white bg-accent-emerald rounded-sm hover:bg-emerald-700 transition-colors disabled:opacity-60"
          >
            {saving ? "Saving…" : step === STEPS.length - 1 ? "Save" : "Next"}
          </button>
        </div>
      </div>
    </div>
  );
}
