import type { ProfileInput } from "../../types/profile";
import { Field } from "./Step1Personal";

type Props = {
  draft: ProfileInput;
  onChange: <K extends keyof ProfileInput>(key: K, value: ProfileInput[K]) => void;
};

export default function Step2Address({ draft, onChange }: Props) {
  return (
    <div className="space-y-4">
      <Field label="Village" required>
        <input className="input" value={draft.village ?? ""} onChange={(e) => onChange("village", e.target.value)} />
      </Field>
      <Field label="Taluka">
        <input className="input" value={draft.taluka ?? ""} onChange={(e) => onChange("taluka", e.target.value)} />
      </Field>
      <Field label="District" required>
        <input className="input" value={draft.district ?? ""} onChange={(e) => onChange("district", e.target.value)} />
      </Field>
      <Field label="State">
        <input className="input" value={draft.state ?? ""} onChange={(e) => onChange("state", e.target.value)} />
      </Field>
      <Field label="Pincode">
        <input className="input" value={draft.pincode ?? ""} onChange={(e) => onChange("pincode", e.target.value)} />
      </Field>
    </div>
  );
}
