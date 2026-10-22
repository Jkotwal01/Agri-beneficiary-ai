// routes.tsx — protected route wiring with role-based access control
import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuthContext } from "./context/AuthContext";
import type { Role } from "./types/auth";

const LoginPage = React.lazy(() => import("./pages/LoginPage"));
const RegisterPage = React.lazy(() => import("./pages/RegisterPage"));

const OfficerLayout = React.lazy(() => import("./layouts/OfficerLayout"));
const DashboardPage = React.lazy(() => import("./pages/DashboardPage"));
const ReviewQueuePage = React.lazy(() => import("./pages/ReviewQueuePage"));
const FlagsPage = React.lazy(() => import("./pages/FlagsPage"));
const OfficerApplicationsPage = React.lazy(() => import("./pages/OfficerApplicationsPage"));
const EvaluationPage = React.lazy(() => import("./pages/EvaluationPage"));

const FarmerLayout = React.lazy(() => import("./layouts/FarmerLayout"));
const FarmerDashboardPage = React.lazy(() => import("./pages/FarmerDashboardPage"));
const ProfileWizardPage = React.lazy(() => import("./pages/ProfileWizardPage"));
const SchemeDetailPage = React.lazy(() => import("./pages/SchemeDetailPage"));
const ApplyPage = React.lazy(() => import("./pages/ApplyPage"));
const MyApplicationsPage = React.lazy(() => import("./pages/MyApplicationsPage"));
const SettingsPage = React.lazy(() => import("./pages/SettingsPage"));

/** Guard: redirect to /login if unauthenticated or wrong role */
function ProtectedRoute({
  children,
  roles,
}: {
  children: React.ReactNode;
  roles?: Role[];
}) {
  const { token, role } = useAuthContext();
  if (!token) return <Navigate to="/login" replace />;
  if (roles && role && !roles.includes(role)) {
    return <Navigate to={role === "farmer" ? "/me" : "/dashboard"} replace />;
  }
  return <>{children}</>;
}

/** Guard: redirect to dashboard if ALREADY authenticated */
function PublicOnlyRoute({ children }: { children: React.ReactNode }) {
  const { token, role } = useAuthContext();
  if (token) {
    return <Navigate to={role === "farmer" ? "/me" : "/dashboard"} replace />;
  }
  return <>{children}</>;
}

export function AppRoutes() {
  return (
    <React.Suspense fallback={<div className="h-screen w-screen flex items-center justify-center text-sm font-mono text-secondary bg-background">Loading...</div>}>
      <Routes>
        {/* Public (Guest only) */}
        <Route path="/login" element={<PublicOnlyRoute><LoginPage /></PublicOnlyRoute>} />
        <Route path="/register" element={<PublicOnlyRoute><RegisterPage /></PublicOnlyRoute>} />

        {/* Farmer-only */}
        <Route
          path="/me"
          element={
            <ProtectedRoute roles={["farmer"]}>
              <FarmerLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<FarmerDashboardPage />} />
          <Route path="profile" element={<ProfileWizardPage />} />
          <Route path="schemes/:code" element={<SchemeDetailPage />} />
          <Route path="schemes/:code/apply" element={<ApplyPage />} />
          <Route path="applications" element={<MyApplicationsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        {/* Officer + Admin */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute roles={["officer", "admin"]}>
              <OfficerLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="review" element={<ReviewQueuePage />} />
          <Route path="flags" element={<FlagsPage />} />
          <Route path="applications" element={<OfficerApplicationsPage />} />
          <Route path="evaluation" element={<EvaluationPage />} />
        </Route>

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </React.Suspense>
  );
}
