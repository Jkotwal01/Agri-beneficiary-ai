// routes.tsx — protected route wiring with role-based access control
import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuthContext } from "./context/AuthContext";
import type { Role } from "./types/auth";

const LoginPage = React.lazy(() => import("./pages/LoginPage"));
const RegisterPage = React.lazy(() => import("./pages/RegisterPage"));

// Placeholder pages — replaced by their actual implementation in later phases
function Dashboard() {
  return <div style={{ padding: 32 }}><h1>Officer / Admin Dashboard</h1></div>;
}
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
    <React.Suspense fallback={<div>Loading…</div>}>
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
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </React.Suspense>
  );
}
