import type { ProfileInput } from "../../types/profile";

type Props = {
  draft: ProfileInput;
  onChange: <K extends keyof ProfileInput>(key: K, value: ProfileInput[K]) => void;
};

export default function Step1Personal({ draft, onChange }: Props) {
  return (
    <div className="space-y-4">
      <Field label="Full Name" required>
        <input
          className="input"
          value={draft.full_name ?? ""}
          onChange={(e) => onChange("full_name", e.target.value)}
        />
      </Field>
      <Field label="Father's Name">
        <input
          className="input"
          value={draft.father_name ?? ""}
          onChange={(e) => onChange("father_name", e.target.value)}
        />
      </Field>
      <Field label="Date of Birth">
        <input
          type="date"
          className="input"
          value={draft.dob ?? ""}
          onChange={(e) => onChange("dob", e.target.value)}
        />
      </Field>
      <Field label="Gender">
        <select
          className="input"
          value={draft.gender ?? ""}
          onChange={(e) => onChange("gender", e.target.value)}
        >
          <option value="">Select</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>
      </Field>
      <Field label="Mobile Number" required>
        <input
          className="input"
          value={draft.mobile ?? ""}
          onChange={(e) => onChange("mobile", e.target.value)}
        />
      </Field>
    </div>
  );
}

export function Field({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-xs font-semibold text-secondary uppercase tracking-wider mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {children}
    </div>
  );
}
