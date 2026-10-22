export type FarmerSummary = {
  id: number;
  name: string;
  father_name: string | null;
  dob: string | null;
  mobile: string | null;
  village_code: string | null;
  district_code: string | null;
  total_land_ha: number | null;
  category: string | null;
  confidence: number | null;
  status: "Golden" | "Review";
};
