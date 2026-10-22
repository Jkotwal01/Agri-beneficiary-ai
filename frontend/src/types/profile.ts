export type FarmerProfile = {
  id: number;
  user_id: number;
  farmer_id: number | null;
  full_name: string | null;
  father_name: string | null;
  dob: string | null;
  gender: string | null;
  mobile: string | null;
  email: string | null;
  category: string | null;
  village: string | null;
  taluka: string | null;
  district: string | null;
  state: string | null;
  pincode: string | null;
  total_land_ha: number | null;
  ownership_type: string | null;
  main_crops: string[] | null;
  irrigation_type: string | null;
  interests: string[] | null;
  agristack_id: string | null;
  bank_name: string | null;
  ifsc: string | null;
  email_opt_in: boolean | null;
  verified: boolean;
  completeness: number;
};

export type ProfileInput = Partial<Omit<FarmerProfile, "id" | "user_id" | "farmer_id" | "verified" | "completeness">>;

export type RecommendedScheme = {
  scheme_id: number;
  scheme_code: string;
  scheme_name: string;
};
