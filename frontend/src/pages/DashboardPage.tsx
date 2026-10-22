import { useEffect, useState } from "react";
import { CheckCircle2, AlertTriangle, Users, FileText } from "lucide-react";

type Summary = {
  total_ingested: number;
  golden_records: number;
  active_flags: number;
  pending_reviews: number;
};

type Farmer = {
  id: number;
  name: string;
  district_code: string;
  village_code: string;
  mobile: string;
  agristack_id: string | null;
  pmkisan_id: string | null;
  pmfby_id: string | null;
  kcc_id: string | null;
  status: string;
};

export default function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [farmers, setFarmers] = useState<Farmer[]>([]);

  useEffect(() => {
    fetch("/api/reports/summary")
      .then((res) => res.json())
      .then(setSummary);
    
    fetch("/api/farmers")
      .then((res) => res.json())
      .then((data) => setFarmers(data.items));
  }, []);

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Top Counters Row */}
      <div className="grid grid-cols-4 gap-4 shrink-0">
        <StatCard title="Total Ingested" value={summary?.total_ingested} icon={FileText} />
        <StatCard title="Golden Records" value={summary?.golden_records} icon={CheckCircle2} color="text-accent-emerald" />
        <StatCard title="Active Flags" value={summary?.active_flags} icon={AlertTriangle} color="text-accent-amber" />
        <StatCard title="Pending Reviews" value={summary?.pending_reviews} icon={Users} color="text-accent-sky" />
      </div>

      {/* Dense Datagrid */}
      <div className="flex-1 bg-surface border border-borderline rounded-sm flex flex-col min-h-0">
        <div className="px-3 py-2 border-b border-borderline bg-slate-50 flex items-center justify-between shrink-0">
          <h3 className="text-sm font-semibold text-primary">Master Beneficiary Mapping</h3>
          <span className="text-xs text-secondary font-mono">Showing {farmers.length} records</span>
        </div>
        <div className="flex-1 overflow-auto">
          <table className="w-full text-left border-collapse">
            <thead className="sticky top-0 bg-slate-50 border-b border-borderline z-10">
              <tr>
                <Th>ID</Th>
                <Th>Name</Th>
                <Th>Mobile</Th>
                <Th>District / Village</Th>
                <Th>AgriStack</Th>
                <Th>PM-KISAN</Th>
                <Th>PMFBY</Th>
                <Th>KCC</Th>
                <Th>Status</Th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-borderline">
              {farmers.map((f) => (
                <tr key={f.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-3 py-1.5 whitespace-nowrap font-mono text-xs text-secondary">{f.id}</td>
                  <td className="px-3 py-1.5 whitespace-nowrap font-medium text-primary">{f.name}</td>
                  <td className="px-3 py-1.5 whitespace-nowrap font-mono text-xs text-secondary">{f.mobile}</td>
                  <td className="px-3 py-1.5 whitespace-nowrap text-xs text-secondary">
                    {f.district_code} <span className="text-slate-400">/</span> {f.village_code}
                  </td>
                  <td className="px-3 py-1.5 whitespace-nowrap font-mono text-xs"><TrackId val={f.agristack_id} /></td>
                  <td className="px-3 py-1.5 whitespace-nowrap font-mono text-xs"><TrackId val={f.pmkisan_id} /></td>
                  <td className="px-3 py-1.5 whitespace-nowrap font-mono text-xs"><TrackId val={f.pmfby_id} /></td>
                  <td className="px-3 py-1.5 whitespace-nowrap font-mono text-xs"><TrackId val={f.kcc_id} /></td>
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
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, color = "text-secondary" }: { title: string; value?: number; icon: any; color?: string }) {
  return (
    <div className="bg-surface border border-borderline rounded-sm p-3 flex items-center space-x-3">
      <div className={`p-2 rounded-sm bg-slate-50 border border-borderline ${color}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-xs font-medium text-secondary uppercase tracking-wider">{title}</p>
        <p className="text-xl font-bold text-primary mt-0.5">{value === undefined ? "—" : value.toLocaleString()}</p>
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

function TrackId({ val }: { val: string | null }) {
  if (!val) return <span className="text-slate-300">-</span>;
  return <span className="text-primary bg-slate-100 px-1 py-0.5 rounded-sm border border-slate-200">{val}</span>;
}
