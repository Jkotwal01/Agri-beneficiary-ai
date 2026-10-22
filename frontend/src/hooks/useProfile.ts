import { useEffect, useState } from "react";
import { fetchMyProfile, saveMyProfile } from "../api/profile";
import type { FarmerProfile, ProfileInput } from "../types/profile";

export function useProfile() {
  const [profile, setProfile] = useState<FarmerProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchMyProfile()
      .then((data) => {
        if (!cancelled) setProfile(data);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load profile");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function save(payload: ProfileInput) {
    setSaving(true);
    setError(null);
    try {
      const updated = await saveMyProfile(payload);
      setProfile(updated);
      return updated;
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to save profile");
      throw e;
    } finally {
      setSaving(false);
    }
  }

  return { profile, loading, error, saving, save };
}
