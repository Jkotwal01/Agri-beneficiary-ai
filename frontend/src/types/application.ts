export type SchemeFormField = {
  key: string;
  label: string;
  type: "text" | "number" | "date" | "checkbox";
  required: boolean;
  autofill_from?: string;
};

export type Scheme = {
  id: number;
  code: string;
  name: string;
  description: string | null;
  domain: string | null;
  status: string | null;
  start_date: string | null;
  end_date: string | null;
};

export type PrefillResult = {
  values: Record<string, unknown>;
  autofilled_keys: string[];
  fields: SchemeFormField[];
};

export type Application = {
  id: number;
  farmer_profile_id: number;
  scheme_id: number;
  status: "submitted" | "approved" | "rejected" | string;
  form_data: Record<string, unknown> | null;
  autofilled_keys: string[] | null;
  submitted_at: string | null;
  reviewed_by: number | null;
  officer_note: string | null;
};
