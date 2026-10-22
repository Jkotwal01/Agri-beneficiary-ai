import { CheckCircle2, AlertTriangle, Users, FileText, type LucideIcon } from "lucide-react";
import { useSummary } from "../hooks/useReports";
import { useFarmers } from "../hooks/useFarmers";

export default function DashboardPage() {
  const { summary, loading: summaryLoading, error: summaryError } = useSummary();
  const { farmers, loading: farmersLoading, error: farmersError } = useFarmers();

  return (
    <div className="flex flex-col h-full space-y-4">
      {summaryError && <ErrorBanner message={summaryError} />}
      {farmersError && <ErrorBanner message={farmersError} />}

      {/* Top Counters Row */}
      <div className="grid grid-cols-4 gap-4 shrink-0">
        <StatCard title="Total Records" value={summary?.total_records} icon={FileText} loading={summaryLoading} />
        <StatCard title="Unique Farmers" value={summary?.unique_farmers} icon={CheckCircle2} color="text-accent-emerald" loading={summaryLoading} />
        <StatCard title="Open Flags" value={summary?.open_flags} icon={AlertTriangle} color="text-accent-amber" loading={summaryLoading} />
        <StatCard title="Exclusions" value={summary?.exclusions} icon={Users} color="text-accent-sky" loading={summaryLoading} />
      </div>

      {/* Dense Datagrid */}
      <div className="flex-1 bg-surface border border-borderline rounded-sm flex flex-col min-h-0">
        <div className="px-3 py-2 border-b border-borderline bg-slate-50 flex items-center justify-between shrink-0">
          <h3 className="text-sm font-semibold text-primary">Master Beneficiary Mapping</h3>
          <span className="text-xs text-secondary font-mono">Showing {farmers.length} records</span>
        </div>
        <div className="flex-1 overflow-auto">
          {farmersLoading ? (
            <div className="p-4 text-sm text-secondary">Loading farmers…</div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead className="sticky top-0 bg-slate-50 border-b border-borderline z-10">
                <tr>
                  <Th>ID</Th>
                  <Th>Name</Th>
                  <Th>Mobile</Th>
                  <Th>District / Village</Th>
                  <Th>Land (Ha)</Th>
                  <Th>Category</Th>
                  <Th>Confidence</Th>
                  <Th>Status</Th>
                </tr>
              </thead>
              <tbody className="text-sm divide-y divide-borderline">
                {farmers.map((f) => (
                  <tr key={f.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-3 py-1.5 whitespace-nowrap font-mono text-xs text-secondary">{f.id}</td>
                    <td className="px-3 py-1.5 whitespace-nowrap font-medium text-primary">{f.name}</td>
                    <td className="px-3 py-1.5 whitespace-nowrap font-mono text-xs text-secondary">{f.mobile ?? "-"}</td>
                    <td className="px-3 py-1.5 whitespace-nowrap text-xs text-secondary">
                      {f.district_code ?? "-"} <span className="text-slate-400">/</span> {f.village_code ?? "-"}
                    </td>
                    <td className="px-3 py-1.5 whitespace-nowrap font-mono text-xs text-secondary">
                      {f.total_land_ha ?? "-"}
                    </td>
                    <td className="px-3 py-1.5 whitespace-nowrap text-xs text-secondary">{f.category ?? "-"}</td>
                    <td className="px-3 py-1.5 whitespace-nowrap font-mono text-xs text-secondary">
                      {f.confidence !== null ? f.confidence.toFixed(2) : "-"}
                    </td>
                    <td className="px-3 py-1.5 whitespace-nowrap">
                      <span className={`inline-flex items-center px-1.5 py-0.5 rounded-sm text-[10px] font-bold uppercase tracking-wider ${
                        f.status === 'Golden' ? 'bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/20' :
                        'bg-accent-amber/10 text-accent-amber border border-accent-amber/20'
                      }`}>
                        {f.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, color = "text-secondary", loading }: { title: string; value?: number; icon: LucideIcon; color?: string; loading?: boolean }) {
  return (
    <div className="bg-surface border border-borderline rounded-sm p-3 flex items-center space-x-3">
      <div className={`p-2 rounded-sm bg-slate-50 border border-borderline ${color}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-xs font-medium text-secondary uppercase tracking-wider">{title}</p>
        <p className="text-xl font-bold text-primary mt-0.5">
          {loading || value === undefined ? "—" : value.toLocaleString()}
        </p>
      </div>
    </div>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="px-3 py-2 text-xs font-semibold text-secondary uppercase tracking-wider whitespace-nowrap">
      {children}
    </th>
  );
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="shrink-0 bg-red-50 border border-red-200 text-red-700 text-xs px-3 py-2 rounded-sm">
      {message}
    </div>
  );
}
