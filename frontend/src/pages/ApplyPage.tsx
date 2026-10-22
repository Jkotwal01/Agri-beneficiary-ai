import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { prefillApplication, submitApplication } from "../api/applications";
import AutofillBanner from "../features/apply/AutofillBanner";
import DynamicFormField from "../features/apply/DynamicFormField";
import type { SchemeFormField } from "../types/application";

export default function ApplyPage() {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();

  const [fields, setFields] = useState<SchemeFormField[]>([]);
  const [autofilledKeys, setAutofilledKeys] = useState<string[]>([]);
  const [values, setValues] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!code) return;
    let cancelled = false;
    prefillApplication(code)
      .then((result) => {
        if (cancelled) return;
        setFields(result.fields);
        setAutofilledKeys(result.autofilled_keys);
        setValues(result.values);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load form");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [code]);

  const requiredFilled = fields
    .filter((f) => f.required)
    .every((f) => values[f.key] !== null && values[f.key] !== undefined && values[f.key] !== "");

  async function handleSubmit() {
    if (!code) return;
    setSubmitting(true);
    setError(null);
    try {
      await submitApplication(code, values);
      navigate("/me/applications");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to submit application");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <div className="p-4 text-sm text-secondary">Loading application form…</div>;

  return (
    <div className="max-w-xl mx-auto py-4 space-y-4">
      <Link to={`/me/schemes/${code}`} className="inline-flex items-center text-xs text-secondary hover:text-primary">
        <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Back to scheme
      </Link>

      <div className="bg-surface border border-borderline rounded-sm p-6 space-y-4">
        <div>
          <h1 className="text-lg font-semibold text-primary">Apply for {code}</h1>
          <p className="text-sm text-secondary mt-0.5">Review the autofilled fields and complete the rest.</p>
        </div>

        <AutofillBanner count={autofilledKeys.length} />

        {fields.map((field) => (
          <DynamicFormField
            key={field.key}
            field={field}
            value={values[field.key]}
            wasAutofilled={autofilledKeys.includes(field.key)}
            onChange={(v) => setValues((prev) => ({ ...prev, [field.key]: v }))}
          />
        ))}

        {error && <p className="text-xs text-red-600">{error}</p>}

        <button
          type="button"
          disabled={!requiredFilled || submitting}
          onClick={handleSubmit}
          className="w-full px-4 py-2 bg-accent-emerald text-white text-xs font-semibold rounded-sm hover:bg-emerald-700 transition-colors disabled:opacity-40"
        >
          {submitting ? "Submitting…" : "Submit Application"}
        </button>
      </div>
    </div>
  );
}
