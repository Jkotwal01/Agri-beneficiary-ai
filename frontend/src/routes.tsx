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

// Placeholder pages — replaced by their actual implementation in later phases
function FarmerProfile() {
  return <div style={{ padding: 32 }}><h1>My Farmer Profile</h1></div>;
}

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

export function AppRoutes() {
  return (
    <React.Suspense fallback={<div className="h-screen w-screen flex items-center justify-center text-sm font-mono text-secondary bg-background">Loading...</div>}>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Farmer-only */}
        <Route
          path="/me"
          element={
            <ProtectedRoute roles={["farmer"]}>
              <FarmerProfile />
            </ProtectedRoute>
          }
        />

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
        </Route>

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </React.Suspense>
  );
}
