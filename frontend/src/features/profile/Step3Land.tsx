import type { ProfileInput } from "../../types/profile";
import { Field } from "./Step1Personal";

type Props = {
  draft: ProfileInput;
  onChange: <K extends keyof ProfileInput>(key: K, value: ProfileInput[K]) => void;
};

export default function Step3Land({ draft, onChange }: Props) {
  return (
    <div className="space-y-4">
      <Field label="Total Land (Ha)" required>
        <input
          type="number"
          step="0.01"
          className="input"
          value={draft.total_land_ha ?? ""}
          onChange={(e) => onChange("total_land_ha", e.target.value === "" ? null : Number(e.target.value))}
        />
      </Field>
      <Field label="Ownership Type">
        <select
          className="input"
          value={draft.ownership_type ?? ""}
          onChange={(e) => onChange("ownership_type", e.target.value)}
        >
          <option value="">Select</option>
          <option value="owned">Owned</option>
          <option value="leased">Leased</option>
          <option value="shared">Shared</option>
        </select>
      </Field>
      <Field label="Main Crops (comma separated)">
        <input
          className="input"
          value={(draft.main_crops ?? []).join(", ")}
          onChange={(e) =>
            onChange(
              "main_crops",
              e.target.value
                .split(",")
                .map((c) => c.trim().toLowerCase())
                .filter(Boolean)
            )
          }
        />
      </Field>
      <Field label="Irrigation Type">
        <select
          className="input"
          value={draft.irrigation_type ?? ""}
          onChange={(e) => onChange("irrigation_type", e.target.value)}
        >
          <option value="">Select</option>
          <option value="rainfed">Rainfed</option>
          <option value="canal">Canal</option>
          <option value="borewell">Borewell</option>
          <option value="drip">Drip</option>
        </select>
      </Field>
    </div>
  );
}
