import { Sparkles } from "lucide-react";

export default function AutofillBanner({ count }: { count: number }) {
  if (count === 0) return null;
  return (
    <div className="flex items-center text-xs text-accent-emerald bg-accent-emerald/5 border border-accent-emerald/20 rounded-sm px-3 py-2">
      <Sparkles className="w-3.5 h-3.5 mr-1.5" />
      {count} field{count === 1 ? "" : "s"} autofilled from your profile.
    </div>
  );
}
