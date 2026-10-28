import { useState, useMemo } from "react";
import { Link } from "react-router-dom";
import {
  AlertCircle,
  Check,
  Loader2,
  ArrowUpRight,
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  ShieldAlert,
  RotateCcw,
} from "lucide-react";
import { useFlags } from "../hooks/useFlags";

export default function FlagsPage() {
  const { flags, loading, error, updateStatus, updatingId } = useFlags();

  // Filters & Search
  const [statusFilter, setStatusFilter] = useState<"all" | "open" | "confirmed" | "dismissed">("all");
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Pagination (Change 1: sets of 50 or 100)
  const [pageSize, setPageSize] = useState<number>(50);
  const [currentPage, setCurrentPage] = useState<number>(1);

  // Toast feedback
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Status counts (calculated on all flags)
  const openCount = useMemo(() => flags.filter((f) => f.status === "open").length, [flags]);
  const confirmedCount = useMemo(() => flags.filter((f) => f.status === "confirmed").length, [flags]);
  const dismissedCount = useMemo(() => flags.filter((f) => f.status === "dismissed").length, [flags]);

  // Unique flag types for filter dropdown
  const flagTypes = useMemo(() => {
    const types = new Set(flags.map((f) => f.type));
    return Array.from(types).sort();
  }, [flags]);

  // Filtered dataset
  const filteredFlags = useMemo(() => {
    return flags.filter((flag) => {
      // Status
      if (statusFilter !== "all" && flag.status !== statusFilter) return false;
      // Severity
      if (severityFilter !== "all" && flag.severity.toUpperCase() !== severityFilter.toUpperCase()) return false;
      // Type
      if (typeFilter !== "all" && flag.type !== typeFilter) return false;
      // Search
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const matchesName = flag.farmer_name?.toLowerCase().includes(q) ?? false;
        const matchesId = flag.farmer_id.toString().includes(q);
        const matchesType = flag.type.toLowerCase().includes(q);
        const matchesReason = flag.reason.toLowerCase().includes(q);
        if (!matchesName && !matchesId && !matchesType && !matchesReason) return false;
      }
      return true;
    });
  }, [flags, statusFilter, severityFilter, typeFilter, searchQuery]);

  // Pagination calculations
  const totalItems = filteredFlags.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const safePage = Math.min(currentPage, totalPages);

  const paginatedFlags = useMemo(() => {
    const startIndex = (safePage - 1) * pageSize;
    return filteredFlags.slice(startIndex, startIndex + pageSize);
  }, [filteredFlags, safePage, pageSize]);

  // Reset to page 1 whenever any filter or search changes
  const handleFilterChange = (setter: (val: any) => void, val: any) => {
    setter(val);
    setCurrentPage(1);
  };

  const handleUpdate = async (id: number, status: "dismissed" | "confirmed", farmerName?: string | null) => {
    try {
      await updateStatus(id, status);
      const actionLabel = status === "confirmed" ? "Under Investigation" : "Dismissed";
      setToastMessage(`Flag #${id} (${farmerName || "Farmer"}) marked as ${actionLabel}`);
      setTimeout(() => setToastMessage(null), 3500);
    } catch {
      setToastMessage(`Failed to update status for flag #${id}`);
      setTimeout(() => setToastMessage(null), 3500);
    }
  };

  // Generate page numbers to show in pagination controls
  const visiblePages = useMemo(() => {
    const delta = 2;
    const range: number[] = [];
    for (
      let i = Math.max(2, safePage - delta);
      i <= Math.min(totalPages - 1, safePage + delta);
      i++
    ) {
      range.push(i);
    }

    if (safePage - delta > 2) {
      range.unshift(-1); // ellipsis
    }
    if (safePage + delta < totalPages - 1) {
      range.push(-2); // ellipsis
    }

    range.unshift(1);
    if (totalPages > 1) {
      range.push(totalPages);
    }
    return range;
  }, [safePage, totalPages]);

  return (
    <div className="h-full flex flex-col space-y-3">
      {/* Top Header Card */}
      <div className="bg-surface border border-borderline rounded-sm px-4 py-3 flex flex-wrap items-center justify-between gap-3 shrink-0 shadow-sm">
        <div>
          <h2 className="text-sm font-semibold text-primary flex items-center">
            <ShieldAlert className="w-4 h-4 mr-2 text-red-600" />
            Engine Flags & Fraud Monitoring
          </h2>
          <p className="text-xs text-secondary mt-0.5">
            Automated intelligence audit feed. Review cross-scheme anomalies, parcel overclaims, and exclusion violations.
          </p>
        </div>

        {/* Global Status Badges */}
        <div className="flex items-center space-x-2 text-xs">
          <span className="px-2 py-1 bg-amber-50 text-amber-800 border border-amber-200 rounded-sm font-medium">
            Open: <strong>{openCount.toLocaleString()}</strong>
          </span>
          <span className="px-2 py-1 bg-sky-50 text-sky-800 border border-sky-200 rounded-sm font-medium">
            Investigating: <strong>{confirmedCount.toLocaleString()}</strong>
          </span>
          <span className="px-2 py-1 bg-slate-100 text-slate-700 border border-slate-200 rounded-sm font-medium">
            Dismissed: <strong>{dismissedCount.toLocaleString()}</strong>
          </span>
        </div>
      </div>

      {/* Action Toast Alert */}
      {toastMessage && (
        <div className="bg-emerald-50 border border-emerald-300 px-4 py-2 text-xs text-emerald-800 rounded-sm flex items-center justify-between shadow-sm animate-fadeIn">
          <span className="flex items-center font-medium">
            <Check className="w-4 h-4 mr-2 text-emerald-600" />
            {toastMessage}
          </span>
          <button
            onClick={() => setToastMessage(null)}
            className="text-emerald-700 hover:text-emerald-900 font-bold ml-4"
          >
            ✕
          </button>
        </div>
      )}

      {/* Filter & Search Bar */}
      <div className="bg-surface border border-borderline rounded-sm p-3 flex flex-wrap items-center justify-between gap-3 shrink-0 shadow-sm">
        {/* Left: Status Filter Tabs */}
        <div className="flex items-center space-x-1">
          <button
            onClick={() => handleFilterChange(setStatusFilter, "all")}
            className={`px-2.5 py-1 text-xs rounded-sm font-semibold transition-colors ${
              statusFilter === "all" ? "bg-primary text-white" : "text-secondary hover:bg-slate-100"
            }`}
          >
            All ({flags.length.toLocaleString()})
          </button>
          <button
            onClick={() => handleFilterChange(setStatusFilter, "open")}
            className={`px-2.5 py-1 text-xs rounded-sm font-semibold transition-colors ${
              statusFilter === "open" ? "bg-amber-600 text-white" : "text-secondary hover:bg-slate-100"
            }`}
          >
            Open ({openCount.toLocaleString()})
          </button>
          <button
            onClick={() => handleFilterChange(setStatusFilter, "confirmed")}
            className={`px-2.5 py-1 text-xs rounded-sm font-semibold transition-colors ${
              statusFilter === "confirmed" ? "bg-accent-sky text-white" : "text-secondary hover:bg-slate-100"
            }`}
          >
            Investigating ({confirmedCount.toLocaleString()})
          </button>
          <button
            onClick={() => handleFilterChange(setStatusFilter, "dismissed")}
            className={`px-2.5 py-1 text-xs rounded-sm font-semibold transition-colors ${
              statusFilter === "dismissed" ? "bg-slate-600 text-white" : "text-secondary hover:bg-slate-100"
            }`}
          >
            Dismissed ({dismissedCount.toLocaleString()})
          </button>
        </div>

        {/* Right: Search + Dropdown Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-secondary absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search farmer, ID, reason..."
              value={searchQuery}
              onChange={(e) => handleFilterChange(setSearchQuery, e.target.value)}
              className="pl-8 pr-3 py-1 text-xs bg-slate-50 border border-borderline rounded-sm text-primary placeholder:text-secondary outline-none focus:ring-1 focus:ring-sky-400 w-56"
            />
          </div>

          {/* Severity Dropdown */}
          <select
            value={severityFilter}
            onChange={(e) => handleFilterChange(setSeverityFilter, e.target.value)}
            className="text-xs bg-slate-50 border border-borderline rounded-sm px-2 py-1 text-primary outline-none focus:ring-1 focus:ring-sky-400"
          >
            <option value="all">All Severities</option>
            <option value="high">High Severity</option>
            <option value="medium">Medium Severity</option>
            <option value="low">Low Severity</option>
          </select>

          {/* Flag Type Dropdown */}
          <select
            value={typeFilter}
            onChange={(e) => handleFilterChange(setTypeFilter, e.target.value)}
            className="text-xs bg-slate-50 border border-borderline rounded-sm px-2 py-1 text-primary outline-none focus:ring-1 focus:ring-sky-400 max-w-[170px]"
          >
            <option value="all">All Anomaly Types</option>
            {flagTypes.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>

          {/* Reset Filters Button */}
          {(statusFilter !== "all" || severityFilter !== "all" || typeFilter !== "all" || searchQuery) && (
            <button
              onClick={() => {
                setStatusFilter("all");
                setSeverityFilter("all");
                setTypeFilter("all");
                setSearchQuery("");
                setCurrentPage(1);
              }}
              title="Reset Filters"
              className="p-1 text-secondary hover:text-primary rounded"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Main Flags List */}
      <div className="flex-1 bg-surface border border-borderline rounded-sm flex flex-col overflow-hidden shadow-sm">
        {/* List Sub-header with Results Count & Page Size Selector */}
        <div className="bg-slate-50 px-4 py-2 border-b border-borderline flex items-center justify-between shrink-0">
          <span className="text-xs text-secondary font-mono">
            {totalItems === 0
              ? "0 records found"
              : `Showing ${(safePage - 1) * pageSize + 1}–${Math.min(
                  safePage * pageSize,
                  totalItems
                )} of ${totalItems.toLocaleString()} flags`}
          </span>

          <div className="flex items-center space-x-2">
            <span className="text-xs text-secondary">Per page:</span>
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="text-xs bg-white border border-borderline rounded-sm px-2 py-0.5 text-primary outline-none"
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>

        {/* Cards Feed */}
        <div className="flex-1 overflow-auto p-4 space-y-3">
          {loading && (
            <div className="flex items-center justify-center p-12 text-sm text-secondary">
              <Loader2 className="w-5 h-5 mr-2 animate-spin text-accent-sky" />
              Loading flag anomalies…
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 text-red-700 text-sm rounded-sm">
              {error}
            </div>
          )}

          {!loading && paginatedFlags.length === 0 && (
            <div className="p-12 text-center text-secondary text-sm">
              <Filter className="w-8 h-8 mx-auto mb-2 opacity-30" />
              No flags match your selected filters. Try broadening your criteria.
            </div>
          )}

          {!loading &&
            paginatedFlags.map((flag) => {
              const isHigh = flag.severity.toUpperCase() === "HIGH";
              const isBusy = updatingId === flag.id;

              return (
                <div
                  key={flag.id}
                  className="border border-borderline rounded-sm overflow-hidden bg-white shadow-sm hover:border-slate-300 transition-colors"
                >
                  {/* Card Header Bar */}
                  <div className="bg-slate-50 px-4 py-1.5 border-b border-borderline flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <AlertCircle
                        className={`w-4 h-4 ${
                          isHigh ? "text-red-600" : "text-accent-amber"
                        }`}
                      />
                      <span className="text-xs font-mono font-bold text-primary">
                        {flag.type}
                      </span>
                      <span className="text-[11px] text-secondary font-mono">
                        #FL-{flag.id}
                      </span>
                    </div>

                    <div className="flex items-center space-x-1.5">
                      {/* Severity Badge */}
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded-sm font-bold uppercase ${
                          isHigh
                            ? "bg-red-100 text-red-700 border border-red-200"
                            : "bg-amber-100 text-amber-700 border border-amber-200"
                        }`}
                      >
                        {flag.severity}
                      </span>

                      {/* Status Badge */}
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded-sm font-bold uppercase ${
                          flag.status === "confirmed"
                            ? "bg-sky-100 text-sky-800 border border-sky-300"
                            : flag.status === "dismissed"
                            ? "bg-slate-200 text-slate-700 border border-slate-300"
                            : "bg-amber-100 text-amber-800 border border-amber-300"
                        }`}
                      >
                        {flag.status === "confirmed"
                          ? "Under Investigation"
                          : flag.status}
                      </span>
                    </div>
                  </div>

                  {/* Card Body */}
                  <div className="p-3 bg-surface">
                    <div className="text-xs text-secondary mb-2 flex flex-wrap justify-between items-center gap-2">
                      <span>
                        Target Beneficiary:{" "}
                        <strong className="text-primary text-sm capitalize">
                          {flag.farmer_name ?? "Unknown"}
                        </strong>
                      </span>
                      <span className="font-mono text-xs bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
                        Farmer ID: #{flag.farmer_id}
                      </span>
                    </div>

                    <p className="text-sm text-primary leading-snug">
                      {flag.reason}
                    </p>

                    {/* Card Footer: View Applications & Actions */}
                    <div className="mt-3 pt-2 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
                      <Link
                        to={`/dashboard/applications?farmer_id=${flag.farmer_id}`}
                        className="text-xs text-accent-sky hover:text-sky-700 font-semibold flex items-center transition-colors"
                      >
                        View Applications & Dossier{" "}
                        <ArrowUpRight className="w-3.5 h-3.5 ml-0.5" />
                      </Link>

                      <div className="flex items-center space-x-2">
                        {flag.status === "confirmed" ? (
                          <>
                            <span className="text-xs text-sky-700 font-semibold px-2 py-1 bg-sky-50 rounded border border-sky-200 flex items-center">
                              <Check className="w-3.5 h-3.5 mr-1 text-sky-600" />{" "}
                              Under Investigation
                            </span>
                            <button
                              onClick={() =>
                                handleUpdate(
                                  flag.id,
                                  "dismissed",
                                  flag.farmer_name
                                )
                              }
                              disabled={isBusy}
                              className="px-2.5 py-1 border border-borderline text-xs font-semibold text-secondary hover:bg-slate-50 rounded-sm transition-colors disabled:opacity-50"
                            >
                              Dismiss
                            </button>
                          </>
                        ) : flag.status === "dismissed" ? (
                          <>
                            <span className="text-xs text-slate-500 font-semibold px-2 py-1 bg-slate-100 rounded border border-slate-200">
                              Dismissed
                            </span>
                            <button
                              onClick={() =>
                                handleUpdate(
                                  flag.id,
                                  "confirmed",
                                  flag.farmer_name
                                )
                              }
                              disabled={isBusy}
                              className="px-2.5 py-1 bg-primary text-white text-xs font-semibold hover:bg-slate-800 rounded-sm transition-colors flex items-center disabled:opacity-50"
                            >
                              {isBusy ? (
                                <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
                              ) : null}
                              Reopen & Investigate
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              onClick={() =>
                                handleUpdate(
                                  flag.id,
                                  "dismissed",
                                  flag.farmer_name
                                )
                              }
                              disabled={isBusy}
                              className="px-2.5 py-1 border border-borderline text-xs font-semibold text-secondary hover:bg-slate-50 rounded-sm transition-colors disabled:opacity-50"
                            >
                              Dismiss
                            </button>
                            <button
                              onClick={() =>
                                handleUpdate(
                                  flag.id,
                                  "confirmed",
                                  flag.farmer_name
                                )
                              }
                              disabled={isBusy}
                              className="px-3 py-1 bg-primary text-white text-xs font-semibold hover:bg-slate-800 rounded-sm transition-colors flex items-center disabled:opacity-50 shadow-sm"
                            >
                              {isBusy ? (
                                <>
                                  <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
                                  Updating...
                                </>
                              ) : (
                                "Investigate"
                              )}
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
        </div>

        {/* Pagination Footer Controls (Change 1) */}
        {!loading && totalPages > 1 && (
          <div className="bg-slate-50 border-t border-borderline px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 shrink-0">
            <div className="text-xs text-secondary font-mono">
              Page <strong>{safePage}</strong> of <strong>{totalPages}</strong> ({totalItems.toLocaleString()} total items)
            </div>

            <div className="flex items-center space-x-1">
              {/* First Page */}
              <button
                onClick={() => setCurrentPage(1)}
                disabled={safePage === 1}
                title="First Page"
                className="p-1.5 rounded border border-borderline bg-white text-secondary hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronsLeft className="w-3.5 h-3.5" />
              </button>

              {/* Prev Page */}
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={safePage === 1}
                title="Previous Page"
                className="p-1.5 rounded border border-borderline bg-white text-secondary hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>

              {/* Numbered Page Buttons */}
              <div className="flex items-center space-x-1 px-1">
                {visiblePages.map((pageNum, idx) => {
                  if (pageNum < 0) {
                    return (
                      <span key={`ellipsis_${idx}`} className="px-1.5 text-xs text-secondary font-mono">
                        …
                      </span>
                    );
                  }
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`min-w-[28px] h-7 px-1.5 text-xs rounded font-mono font-medium transition-colors ${
                        safePage === pageNum
                          ? "bg-primary text-white"
                          : "bg-white border border-borderline text-secondary hover:bg-slate-50"
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>

              {/* Next Page */}
              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={safePage === totalPages}
                title="Next Page"
                className="p-1.5 rounded border border-borderline bg-white text-secondary hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>

              {/* Last Page */}
              <button
                onClick={() => setCurrentPage(totalPages)}
                disabled={safePage === totalPages}
                title="Last Page"
                className="p-1.5 rounded border border-borderline bg-white text-secondary hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronsRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
