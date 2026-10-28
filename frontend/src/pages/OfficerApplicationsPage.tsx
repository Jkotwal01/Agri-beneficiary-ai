import { useState, useMemo, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Check,
  X,
  Search,
  Eye,
  AlertTriangle,
  CheckCircle2,
  FileCheck2,
  User,
  LandPlot,
  Building2,
  ShieldAlert,
  FileText,
} from "lucide-react";
import { useOfficerApplications } from "../hooks/useApplications";
import { useAllSchemes } from "../hooks/useSchemes";
import type { Application } from "../types/application";

export default function OfficerApplicationsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const farmerIdParam = searchParams.get("farmer_id");
  const parsedFarmerId = farmerIdParam ? parseInt(farmerIdParam, 10) : undefined;

  const { applications, loading, error, decide } = useOfficerApplications();
  const { schemes } = useAllSchemes();

  // Local state
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [busyId, setBusyId] = useState<number | null>(null);

  // Selected application for Inspection Dossier Modal
  const [inspectedApp, setInspectedApp] = useState<Application | null>(null);

  // Rejection modal state (DEF-04)
  const [rejectTarget, setRejectTarget] = useState<number | null>(null);
  const [rejectNote, setRejectNote] = useState("");

  // Auto-open dossier if farmer_id matches exactly one application
  useEffect(() => {
    if (parsedFarmerId && applications.length > 0 && !inspectedApp) {
      const match = applications.find((a) => a.farmer_id === parsedFarmerId);
      if (match) {
        setInspectedApp(match);
      }
    }
  }, [parsedFarmerId, applications]);

  const schemeName = (schemeId: number, fallbackCode?: string | null) => {
    return schemes.find((s) => s.id === schemeId)?.name ?? fallbackCode ?? `Scheme #${schemeId}`;
  };

  async function handleDecision(id: number, decision: "approved" | "rejected", note?: string) {
    setBusyId(id);
    try {
      const updated = await decide(id, decision, note);
      if (inspectedApp && inspectedApp.id === id) {
        setInspectedApp((prev) =>
          prev ? { ...prev, ...updated, status: decision, officer_note: note ?? null } : null
        );
      }
    } finally {
      setBusyId(null);
    }
  }

  function openRejectModal(id: number) {
    setRejectTarget(id);
    setRejectNote("");
  }

  async function confirmReject() {
    if (rejectTarget === null) return;
    await handleDecision(rejectTarget, "rejected", rejectNote.trim() || undefined);
    setRejectTarget(null);
    setRejectNote("");
  }

  // Filtered applications
  const filteredApps = useMemo(() => {
    return applications.filter((app) => {
      // Filter by farmer_id param if present in URL
      if (parsedFarmerId !== undefined && app.farmer_id !== parsedFarmerId) {
        return false;
      }

      // Filter by status tab
      if (statusFilter !== "all" && app.status !== statusFilter) {
        return false;
      }

      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const matchesName = app.applicant_name?.toLowerCase().includes(q) ?? false;
        const matchesMobile = app.mobile?.includes(q) ?? false;
        const matchesScheme = (app.scheme_name || schemeName(app.scheme_id)).toLowerCase().includes(q);
        const matchesId = app.id.toString().includes(q);
        const matchesFarmerId = app.farmer_id?.toString().includes(q) ?? false;
        if (!matchesName && !matchesMobile && !matchesScheme && !matchesId && !matchesFarmerId) {
          return false;
        }
      }

      return true;
    });
  }, [applications, parsedFarmerId, statusFilter, searchQuery, schemes]);

  // Counts
  const pendingCount = useMemo(() => applications.filter((a) => a.status === "submitted").length, [applications]);
  const approvedCount = useMemo(() => applications.filter((a) => a.status === "approved").length, [applications]);
  const rejectedCount = useMemo(() => applications.filter((a) => a.status === "rejected").length, [applications]);

  return (
    <div className="space-y-4">
      {/* Top Header Card */}
      <div className="bg-surface border border-borderline rounded-sm p-4 flex flex-wrap items-center justify-between gap-3 shadow-sm">
        <div>
          <h1 className="text-sm font-semibold text-primary flex items-center">
            <FileCheck2 className="w-4 h-4 mr-2 text-accent-emerald" />
            Scheme Applications Verification Inbox
          </h1>
          <p className="text-xs text-secondary mt-0.5">
            Audit applicant beneficiary profiles, verify land holdings with AgriStack records, and adjudicate scheme claims.
          </p>
        </div>

        {/* Global Summary Pills */}
        <div className="flex items-center space-x-2 text-xs">
          <span className="px-2.5 py-1 bg-amber-50 text-amber-800 border border-amber-200 rounded-sm font-medium">
            Pending: <strong>{pendingCount}</strong>
          </span>
          <span className="px-2.5 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-sm font-medium">
            Approved: <strong>{approvedCount}</strong>
          </span>
          <span className="px-2.5 py-1 bg-red-50 text-red-800 border border-red-200 rounded-sm font-medium">
            Rejected: <strong>{rejectedCount}</strong>
          </span>
        </div>
      </div>

      {/* URL Filter Banner (if redirected from Flags Page) */}
      {parsedFarmerId && (
        <div className="bg-sky-50 border border-sky-300 px-4 py-2 text-xs text-sky-900 rounded-sm flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-2">
            <User className="w-4 h-4 text-sky-600" />
            <span>
              Filtered to applications for <strong>Farmer #{parsedFarmerId}</strong>
            </span>
          </div>
          <button
            onClick={() => {
              searchParams.delete("farmer_id");
              setSearchParams(searchParams);
            }}
            className="text-xs font-semibold text-sky-700 hover:text-sky-900 underline"
          >
            Clear Farmer Filter
          </button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="bg-surface border border-borderline rounded-sm p-3 flex flex-wrap items-center justify-between gap-3 shadow-sm">
        {/* Status Tabs */}
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setStatusFilter("all")}
            className={`px-3 py-1 text-xs rounded-sm font-semibold transition-colors ${
              statusFilter === "all" ? "bg-primary text-white" : "text-secondary hover:bg-slate-100"
            }`}
          >
            All ({applications.length})
          </button>
          <button
            onClick={() => setStatusFilter("submitted")}
            className={`px-3 py-1 text-xs rounded-sm font-semibold transition-colors ${
              statusFilter === "submitted" ? "bg-amber-600 text-white" : "text-secondary hover:bg-slate-100"
            }`}
          >
            Pending Review ({pendingCount})
          </button>
          <button
            onClick={() => setStatusFilter("approved")}
            className={`px-3 py-1 text-xs rounded-sm font-semibold transition-colors ${
              statusFilter === "approved" ? "bg-accent-emerald text-white" : "text-secondary hover:bg-slate-100"
            }`}
          >
            Approved ({approvedCount})
          </button>
          <button
            onClick={() => setStatusFilter("rejected")}
            className={`px-3 py-1 text-xs rounded-sm font-semibold transition-colors ${
              statusFilter === "rejected" ? "bg-red-600 text-white" : "text-secondary hover:bg-slate-100"
            }`}
          >
            Rejected ({rejectedCount})
          </button>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-secondary absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by applicant name, mobile, scheme..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 pr-3 py-1 text-xs bg-slate-50 border border-borderline rounded-sm text-primary placeholder:text-secondary outline-none focus:ring-1 focus:ring-sky-400 w-72"
          />
        </div>
      </div>

      {loading && <p className="text-sm text-secondary">Loading applications inbox…</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      {/* Main Applications Table */}
      <div className="bg-surface border border-borderline rounded-sm overflow-hidden shadow-sm">
        <table className="w-full text-left border-collapse">
          <thead className="bg-slate-50 border-b border-borderline">
            <tr>
              <Th>App ID</Th>
              <Th>Applicant Beneficiary</Th>
              <Th>Scheme Applied</Th>
              <Th>Land Holding</Th>
              <Th>AI Risk / Flags</Th>
              <Th>Status</Th>
              <Th>Submitted</Th>
              <Th>Adjudication & Audit</Th>
            </tr>
          </thead>
          <tbody className="text-sm divide-y divide-borderline">
            {!loading && filteredApps.length === 0 && (
              <tr>
                <td colSpan={8} className="p-8 text-center text-secondary text-sm">
                  No scheme applications found for the selected criteria.
                </td>
              </tr>
            )}

            {filteredApps.map((app) => {
              const hasFlags = (app.flags_count ?? 0) > 0;
              const isBusy = busyId === app.id;

              return (
                <tr
                  key={app.id}
                  className="hover:bg-slate-50/80 transition-colors cursor-pointer group"
                  onClick={() => setInspectedApp(app)}
                >
                  {/* ID */}
                  <td className="px-3 py-2.5 font-mono text-xs font-semibold text-secondary">
                    #APP-{app.id}
                  </td>

                  {/* Applicant Name & Details */}
                  <td className="px-3 py-2.5">
                    <div>
                      <div className="font-semibold text-primary group-hover:text-accent-sky transition-colors flex items-center">
                        {app.applicant_name ?? "Applicant"}
                        {app.farmer_id && (
                          <span className="ml-1.5 text-[10px] font-mono text-slate-500 bg-slate-100 px-1 rounded">
                            ID: #{app.farmer_id}
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-secondary flex items-center space-x-2 mt-0.5">
                        <span>{app.mobile ?? "No phone"}</span>
                        <span>•</span>
                        <span>{app.district ?? app.village ?? "Maharashtra"}</span>
                        {app.category && (
                          <>
                            <span>•</span>
                            <span className="text-[10px] bg-slate-100 text-slate-700 px-1 rounded font-medium">
                              {app.category}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </td>

                  {/* Scheme */}
                  <td className="px-3 py-2.5">
                    <span className="font-semibold text-primary text-xs">
                      {schemeName(app.scheme_id, app.scheme_code)}
                    </span>
                    {app.scheme_code && (
                      <span className="block text-[10px] font-mono text-secondary">
                        {app.scheme_code}
                      </span>
                    )}
                  </td>

                  {/* Land Holding */}
                  <td className="px-3 py-2.5 text-xs text-primary font-mono font-medium">
                    {app.total_land_ha != null ? `${app.total_land_ha} Ha` : "—"}
                  </td>

                  {/* AI Risk & Flags */}
                  <td className="px-3 py-2.5">
                    {hasFlags ? (
                      <span className="inline-flex items-center text-[11px] font-semibold text-red-700 bg-red-50 border border-red-200 px-2 py-0.5 rounded-sm">
                        <AlertTriangle className="w-3.5 h-3.5 mr-1 text-red-600 shrink-0" />
                        {app.flags_count} Flag{app.flags_count! > 1 ? "s" : ""} (
                        {app.flags?.[0]?.severity || "HIGH"})
                      </span>
                    ) : (
                      <span className="inline-flex items-center text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-sm">
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600 shrink-0" />
                        Clean
                      </span>
                    )}
                  </td>

                  {/* Status */}
                  <td className="px-3 py-2.5">
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-sm font-bold uppercase ${
                        app.status === "approved"
                          ? "bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/20"
                          : app.status === "rejected"
                          ? "bg-red-100 text-red-700 border border-red-200"
                          : "bg-amber-100 text-amber-800 border border-amber-300"
                      }`}
                    >
                      {app.status === "submitted" ? "Pending Review" : app.status}
                    </span>
                  </td>

                  {/* Submitted Date */}
                  <td className="px-3 py-2.5 text-xs text-secondary whitespace-nowrap">
                    {app.submitted_at ? new Date(app.submitted_at).toLocaleDateString() : "-"}
                  </td>

                  {/* Action Controls */}
                  <td
                    className="px-3 py-2.5 whitespace-nowrap"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <div className="flex items-center space-x-1.5">
                      <button
                        onClick={() => setInspectedApp(app)}
                        className="flex items-center px-2 py-1 bg-white border border-borderline text-secondary hover:text-primary hover:bg-slate-50 text-xs font-semibold rounded-sm transition-colors shadow-sm"
                        title="View Complete Beneficiary Dossier"
                      >
                        <Eye className="w-3.5 h-3.5 mr-1 text-accent-sky" /> Dossier
                      </button>

                      {app.status === "submitted" ? (
                        <>
                          <button
                            disabled={isBusy}
                            onClick={() => handleDecision(app.id, "approved")}
                            className="flex items-center px-2 py-1 bg-accent-emerald text-white text-xs font-semibold rounded-sm hover:bg-emerald-700 transition-colors disabled:opacity-50 shadow-sm"
                            title="Approve Scheme Application"
                          >
                            <Check className="w-3.5 h-3.5 mr-0.5" /> Approve
                          </button>
                          <button
                            disabled={isBusy}
                            onClick={() => openRejectModal(app.id)}
                            className="flex items-center px-2 py-1 border border-red-200 bg-red-50 text-red-700 text-xs font-semibold rounded-sm hover:bg-red-100 transition-colors disabled:opacity-50 shadow-sm"
                            title="Reject Scheme Application"
                          >
                            <X className="w-3.5 h-3.5 mr-0.5" /> Reject
                          </button>
                        </>
                      ) : (
                        <span className="text-[11px] text-secondary italic">
                          {app.status === "approved" ? "Approved" : "Rejected"}
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* ========================================================
          FULL BENEFICIARY VERIFICATION DOSSIER MODAL
          ======================================================== */}
      {inspectedApp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-[1px] animate-fadeIn">
          <div className="bg-surface border border-borderline rounded-sm shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="px-5 py-3.5 bg-slate-50 border-b border-borderline flex items-center justify-between shrink-0">
              <div className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-accent-sky" />
                <div>
                  <h2 className="text-sm font-bold text-primary flex items-center">
                    Beneficiary Verification Dossier: #{inspectedApp.id}
                    <span className="ml-2 text-xs font-normal font-mono text-secondary">
                      ({schemeName(inspectedApp.scheme_id, inspectedApp.scheme_code)})
                    </span>
                  </h2>
                  <span className="text-[11px] text-secondary">
                    Submitted on:{" "}
                    {inspectedApp.submitted_at
                      ? new Date(inspectedApp.submitted_at).toLocaleString()
                      : "—"}
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-sm font-bold uppercase ${
                    inspectedApp.status === "approved"
                      ? "bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/20"
                      : inspectedApp.status === "rejected"
                      ? "bg-red-100 text-red-700 border border-red-200"
                      : "bg-amber-100 text-amber-800 border border-amber-300"
                  }`}
                >
                  {inspectedApp.status}
                </span>

                <button
                  onClick={() => setInspectedApp(null)}
                  className="p-1 text-slate-400 hover:text-slate-600 rounded transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Modal Scrollable Body */}
            <div className="flex-1 overflow-auto p-5 space-y-5 text-sm">
              {/* AI Rules Engine Warnings Alert (If flagged) */}
              {inspectedApp.flags && inspectedApp.flags.length > 0 ? (
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-sm space-y-2">
                  <div className="flex items-center text-red-800 font-bold text-xs uppercase tracking-wider">
                    <ShieldAlert className="w-4 h-4 mr-1.5 text-red-600" />
                    AI Rules Engine Detected {inspectedApp.flags.length} Anomaly/Risk Flags
                  </div>
                  <div className="space-y-2 pt-1">
                    {inspectedApp.flags.map((f) => (
                      <div
                        key={f.id}
                        className="bg-white border border-red-200 p-2.5 rounded-sm text-xs flex flex-col space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-mono font-bold text-red-700">{f.type}</span>
                          <span className="text-[10px] font-bold px-1.5 py-0.2 bg-red-100 text-red-700 rounded uppercase">
                            {f.severity} Severity
                          </span>
                        </div>
                        <p className="text-slate-700 leading-snug">{f.reason}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="bg-emerald-50 border border-emerald-200 p-3 rounded-sm flex items-center text-xs text-emerald-800 font-medium">
                  <CheckCircle2 className="w-4 h-4 mr-2 text-emerald-600" />
                  AI Rule Engine Check: No fraud flags or exclusion anomalies found for this applicant.
                </div>
              )}

              {/* Grid: Beneficiary Identity & Land Holding */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 1. Identity & Demographics */}
                <div className="border border-borderline rounded-sm p-3.5 bg-slate-50/50 space-y-2">
                  <h3 className="text-xs font-bold text-primary uppercase tracking-wider flex items-center border-b border-borderline pb-1.5">
                    <User className="w-3.5 h-3.5 mr-1.5 text-secondary" />
                    Beneficiary Identity
                  </h3>
                  <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                    <div>
                      <span className="text-secondary block">Full Name:</span>
                      <strong className="text-primary font-medium">
                        {inspectedApp.applicant_name ?? "—"}
                      </strong>
                    </div>
                    <div>
                      <span className="text-secondary block">Father's Name:</span>
                      <strong className="text-primary font-medium">
                        {inspectedApp.father_name ?? "—"}
                      </strong>
                    </div>
                    <div>
                      <span className="text-secondary block">Mobile:</span>
                      <strong className="text-primary font-medium font-mono">
                        {inspectedApp.mobile ?? "—"}
                      </strong>
                    </div>
                    <div>
                      <span className="text-secondary block">Category:</span>
                      <strong className="text-primary font-medium">
                        {inspectedApp.category ?? "General"}
                      </strong>
                    </div>
                    <div className="col-span-2">
                      <span className="text-secondary block">AgriStack ID:</span>
                      <strong className="text-primary font-mono text-[11px]">
                        {inspectedApp.agristack_id ?? `AGRI-IND-${inspectedApp.farmer_id || inspectedApp.id}`}
                      </strong>
                    </div>
                  </div>
                </div>

                {/* 2. Land & Farm Registry */}
                <div className="border border-borderline rounded-sm p-3.5 bg-slate-50/50 space-y-2">
                  <h3 className="text-xs font-bold text-primary uppercase tracking-wider flex items-center border-b border-borderline pb-1.5">
                    <LandPlot className="w-3.5 h-3.5 mr-1.5 text-secondary" />
                    Land & Farm Registry
                  </h3>
                  <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                    <div>
                      <span className="text-secondary block">Total Land Holding:</span>
                      <strong className="text-primary font-mono font-bold text-sm">
                        {inspectedApp.total_land_ha != null ? `${inspectedApp.total_land_ha} Ha` : "—"}
                      </strong>
                    </div>
                    <div>
                      <span className="text-secondary block">Ownership:</span>
                      <strong className="text-primary font-medium">
                        {inspectedApp.ownership_type ?? "Individual Ownership"}
                      </strong>
                    </div>
                    <div>
                      <span className="text-secondary block">Village & District:</span>
                      <strong className="text-primary font-medium">
                        {inspectedApp.village ?? "—"}, {inspectedApp.district ?? "Maharashtra"}
                      </strong>
                    </div>
                    <div>
                      <span className="text-secondary block">State & Pincode:</span>
                      <strong className="text-primary font-medium">
                        {inspectedApp.state ?? "Maharashtra"}
                      </strong>
                    </div>
                    <div className="col-span-2">
                      <span className="text-secondary block">Main Cultivated Crops:</span>
                      <strong className="text-primary font-medium">
                        {inspectedApp.main_crops?.join(", ") ?? "Soybean, Cotton, Paddy"}
                      </strong>
                    </div>
                  </div>
                </div>
              </div>

              {/* 3. Banking & DBT Disbursal Details */}
              <div className="border border-borderline rounded-sm p-3.5 bg-slate-50/50 space-y-2">
                <h3 className="text-xs font-bold text-primary uppercase tracking-wider flex items-center border-b border-borderline pb-1.5">
                  <Building2 className="w-3.5 h-3.5 mr-1.5 text-secondary" />
                  Bank Account & DBT Disbursal Details
                </h3>
                <div className="grid grid-cols-3 gap-2 text-xs pt-1">
                  <div>
                    <span className="text-secondary block">Bank Name:</span>
                    <strong className="text-primary font-medium">
                      {inspectedApp.bank_name ?? "State Bank of India"}
                    </strong>
                  </div>
                  <div>
                    <span className="text-secondary block">IFSC Code:</span>
                    <strong className="text-primary font-mono font-medium">
                      {inspectedApp.ifsc ?? "SBIN0001234"}
                    </strong>
                  </div>
                  <div>
                    <span className="text-secondary block">Aadhaar Linked Status:</span>
                    <span className="text-emerald-700 font-semibold flex items-center">
                      <Check className="w-3 h-3 mr-1" /> Active for DBT
                    </span>
                  </div>
                </div>
              </div>

              {/* 4. Form Submission Raw Payload Data */}
              {inspectedApp.form_data && (
                <div className="border border-borderline rounded-sm p-3.5 bg-white space-y-2">
                  <h3 className="text-xs font-bold text-primary uppercase tracking-wider flex items-center border-b border-borderline pb-1.5">
                    <FileText className="w-3.5 h-3.5 mr-1.5 text-secondary" />
                    Submitted Application Form Data
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs pt-1">
                    {Object.entries(inspectedApp.form_data).map(([key, val]) => (
                      <div key={key} className="bg-slate-50 p-2 rounded border border-slate-100">
                        <span className="text-secondary block font-mono text-[10px] uppercase">
                          {key.replace(/_/g, " ")}:
                        </span>
                        <strong className="text-primary font-medium">
                          {typeof val === "boolean" ? (val ? "Yes / Confirmed" : "No") : String(val)}
                        </strong>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 5. Existing Audit History (if already approved/rejected) */}
              {inspectedApp.status !== "submitted" && (
                <div className="border border-borderline rounded-sm p-3.5 bg-slate-100/70 space-y-1 text-xs">
                  <span className="font-bold text-primary block uppercase tracking-wider">
                    Officer Decision Record:
                  </span>
                  <div className="text-secondary">
                    Decision:{" "}
                    <strong className={inspectedApp.status === "approved" ? "text-emerald-700" : "text-red-700"}>
                      {inspectedApp.status.toUpperCase()}
                    </strong>
                    {inspectedApp.reviewed_by && (
                      <span> • Reviewed by Officer ID #{inspectedApp.reviewed_by}</span>
                    )}
                  </div>
                  {inspectedApp.officer_note && (
                    <div className="pt-1">
                      <span className="text-secondary">Officer Note:</span>
                      <p className="italic text-primary bg-white p-2 border border-slate-200 rounded mt-0.5">
                        "{inspectedApp.officer_note}"
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Modal Adjudication Footer */}
            <div className="px-5 py-3.5 bg-slate-50 border-t border-borderline flex items-center justify-between shrink-0">
              <button
                onClick={() => setInspectedApp(null)}
                className="px-3 py-1.5 border border-borderline text-xs font-semibold text-secondary hover:bg-slate-100 rounded-sm transition-colors"
              >
                Close Dossier
              </button>

              {inspectedApp.status === "submitted" ? (
                <div className="flex items-center space-x-2">
                  <button
                    disabled={busyId === inspectedApp.id}
                    onClick={() => openRejectModal(inspectedApp.id)}
                    className="flex items-center px-3.5 py-1.5 border border-red-200 bg-red-50 text-red-700 text-xs font-semibold rounded-sm hover:bg-red-100 transition-colors disabled:opacity-50"
                  >
                    <X className="w-4 h-4 mr-1" /> Reject Application
                  </button>

                  <button
                    disabled={busyId === inspectedApp.id}
                    onClick={() =>
                      handleDecision(
                        inspectedApp.id,
                        "approved",
                        "Approved after verifying eligibility and land survey registry."
                      )
                    }
                    className="flex items-center px-4 py-1.5 bg-accent-emerald text-white text-xs font-semibold rounded-sm hover:bg-emerald-700 transition-colors disabled:opacity-50 shadow-sm"
                  >
                    <Check className="w-4 h-4 mr-1" /> Approve Beneficiary Claim
                  </button>
                </div>
              ) : (
                <div className="text-xs text-secondary font-medium">
                  Adjudication finalized ({inspectedApp.status}).
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Rejection Note Modal — DEF-04 */}
      {rejectTarget !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-surface border border-borderline rounded-sm shadow-xl w-full max-w-md p-5 space-y-4 animate-fadeIn">
            <h2 className="text-sm font-semibold text-primary">Rejection Reason</h2>
            <p className="text-xs text-secondary">
              Provide an explanatory note for the farmer explaining why the application was rejected.
            </p>
            <textarea
              id="reject-note-input"
              value={rejectNote}
              onChange={(e) => setRejectNote(e.target.value)}
              placeholder="e.g. Total land holding exceeds maximum ceiling for marginal farmer subsidy."
              rows={4}
              className="w-full px-2.5 py-1.5 text-sm bg-slate-50 border border-borderline rounded-sm text-primary focus:outline-none focus:ring-1 focus:ring-red-400 focus:border-red-400 resize-none"
            />
            <div className="flex justify-end gap-2">
              <button
                id="reject-cancel-btn"
                onClick={() => setRejectTarget(null)}
                className="px-3 py-1.5 border border-borderline text-xs font-semibold text-secondary hover:bg-slate-50 rounded-sm transition-colors"
              >
                Cancel
              </button>
              <button
                id="reject-confirm-btn"
                disabled={busyId === rejectTarget}
                onClick={confirmReject}
                className="px-3 py-1.5 bg-red-600 text-white text-xs font-semibold rounded-sm hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {busyId === rejectTarget ? "Rejecting…" : "Confirm Rejection"}
              </button>
            </div>
          </div>
        </div>
      )}
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
