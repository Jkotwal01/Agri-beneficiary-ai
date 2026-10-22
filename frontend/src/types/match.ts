export type CleanRecord = {
  id: number;
  source_name: string | null;
  name_norm: string | null;
  mobile10: string | null;
  district_code: string | null;
  village_code: string | null;
  survey_no: string | null;
  dob: string | null;
};

export type ShapFeature = {
  feature: string;
  value: string;
  shap_value: number;
};

export type MatchItem = {
  id: number;
  score: number;
  decision: string;
  record_a: CleanRecord | null;
  record_b: CleanRecord | null;
  features: Record<string, number>;
  shap: ShapFeature[];
};
