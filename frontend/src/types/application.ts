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

export type ApplicationFlag = {
  id: number;
  type: string;
  severity: string;
  reason: string;
  status: string;
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

  // Enriched applicant & scheme details for real-world officer audits
  applicant_name?: string | null;
  father_name?: string | null;
  farmer_id?: number | null;
  mobile?: string | null;
  email?: string | null;
  village?: string | null;
  taluka?: string | null;
  district?: string | null;
  state?: string | null;
  category?: string | null;
  total_land_ha?: number | null;
  ownership_type?: string | null;
  main_crops?: string[] | null;
  bank_name?: string | null;
  ifsc?: string | null;
  agristack_id?: string | null;
  scheme_name?: string | null;
  scheme_code?: string | null;
  flags_count?: number;
  flags?: ApplicationFlag[];
};
