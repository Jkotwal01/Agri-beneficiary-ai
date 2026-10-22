import type { SchemeFormField } from "../../types/application";

type Props = {
  field: SchemeFormField;
  value: unknown;
  wasAutofilled: boolean;
  onChange: (value: unknown) => void;
};

export default function DynamicFormField({ field, value, wasAutofilled, onChange }: Props) {
  const baseClass = `input ${wasAutofilled ? "border-accent-emerald bg-accent-emerald/5" : ""}`;

  return (
    <div>
      <label className="block text-xs font-semibold text-secondary uppercase tracking-wider mb-1">
        {field.label} {field.required && <span className="text-red-500">*</span>}
        {wasAutofilled && <span className="ml-1 text-accent-emerald normal-case">· autofilled</span>}
      </label>

      {field.type === "checkbox" ? (
        <input
          type="checkbox"
          checked={Boolean(value)}
          onChange={(e) => onChange(e.target.checked)}
        />
      ) : (
        <input
          type={field.type === "number" ? "number" : field.type === "date" ? "date" : "text"}
          className={baseClass}
          value={(value as string | number | undefined) ?? ""}
          onChange={(e) =>
            onChange(field.type === "number" ? Number(e.target.value) : e.target.value)
          }
        />
      )}
    </div>
  );
}
