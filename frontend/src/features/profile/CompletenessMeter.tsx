export default function CompletenessMeter({ value }: { value: number }) {
  return (
    <div className="w-full">
      <div className="flex justify-between text-xs text-secondary mb-1">
        <span>Profile Completeness</span>
        <span className="font-mono font-semibold text-primary">{value}%</span>
      </div>
      <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-accent-emerald transition-all duration-500"
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}
