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
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-logo">🌾</div>
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-subtitle">Join the Agri Beneficiary platform</p>

        <form onSubmit={handleSubmit} className="auth-form" id="register-form">
          <div className="form-group">
            <label htmlFor="reg-email">Email address</label>
            <input
              id="reg-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="reg-password">Password</label>
            <input
              id="reg-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={8}
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="reg-role">Role</label>
            <select
              id="reg-role"
              value={role}
              onChange={(e) => setRole(e.target.value as Role)}
            >
              <option value="farmer">Farmer</option>
              <option value="officer">Officer</option>
            </select>
          </div>

          {error && (
            <div className="auth-error" role="alert" id="register-error">
              {error}
            </div>
          )}

          <button
            id="register-submit"
            type="submit"
            className="auth-btn"
            disabled={loading}
          >
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account?{" "}
          <a href="/login" onClick={(e) => { e.preventDefault(); navigate("/login"); }}>
            Sign in
          </a>
        </p>
      </div>
    </div>
  );
}
