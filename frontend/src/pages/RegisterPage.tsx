import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import type { Role } from "../types/auth";

export default function RegisterPage() {
  const { register, loading, error } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("farmer");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      const res = await register({ email, password, role });
      navigate(res.role === "farmer" ? "/me" : "/dashboard");
    } catch {
      // error is stored in hook state
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm bg-surface border border-borderline rounded-sm p-6 shadow-sm">
        <div className="flex flex-col items-center mb-6">
          <div className="w-10 h-10 bg-slate-100 border border-slate-200 rounded-sm flex items-center justify-center text-xl mb-3">🌾</div>
          <h1 className="text-base font-semibold text-primary tracking-tight text-center">Create Account</h1>
          <p className="text-xs text-secondary mt-1">Join the Agri Beneficiary platform</p>
        </div>

        <form onSubmit={handleSubmit} id="register-form" className="space-y-4">
          <div className="space-y-1.5">
            <label htmlFor="reg-email" className="block text-xs font-semibold text-secondary uppercase tracking-wider">Email address</label>
            <input
              id="reg-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              autoComplete="email"
              className="w-full px-2.5 py-1.5 text-sm bg-slate-50 border border-borderline rounded-sm text-primary focus:outline-none focus:ring-1 focus:ring-accent-sky focus:border-accent-sky"
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="reg-password" className="block text-xs font-semibold text-secondary uppercase tracking-wider">Password</label>
            <input
              id="reg-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={8}
              autoComplete="new-password"
              className="w-full px-2.5 py-1.5 text-sm bg-slate-50 border border-borderline rounded-sm text-primary focus:outline-none focus:ring-1 focus:ring-accent-sky focus:border-accent-sky"
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="reg-role" className="block text-xs font-semibold text-secondary uppercase tracking-wider">Role</label>
            <select
              id="reg-role"
              value={role}
              onChange={(e) => setRole(e.target.value as Role)}
              className="w-full px-2.5 py-1.5 text-sm bg-slate-50 border border-borderline rounded-sm text-primary focus:outline-none focus:ring-1 focus:ring-accent-sky focus:border-accent-sky"
            >
              <option value="farmer">Farmer</option>
              <option value="officer">Officer</option>
            </select>
          </div>

          {error && (
            <div className="px-2.5 py-1.5 bg-red-50 border border-red-200 text-red-600 text-xs rounded-sm font-medium" role="alert" id="register-error">
              {error}
            </div>
          )}

          <button
            id="register-submit"
            type="submit"
            disabled={loading}
            className="w-full bg-primary hover:bg-slate-800 text-white font-semibold text-xs py-2 rounded-sm transition-colors disabled:opacity-50"
          >
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="mt-5 text-center text-xs text-secondary">
          Already have an account?{" "}
          <a href="/login" onClick={(e) => { e.preventDefault(); navigate("/login"); }} className="font-semibold text-accent-sky hover:underline">
            Sign in
          </a>
        </p>
      </div>
    </div>
  );
}
