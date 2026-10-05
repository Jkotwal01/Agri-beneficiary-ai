import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function LoginPage() {
  const { login, loading, error } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      const res = await login({ email, password });
      // Role-based redirect
      if (res.role === "farmer") {
        navigate("/me");
      } else {
        navigate("/dashboard");
      }
    } catch {
      // error is stored in hook state
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-logo">🌾</div>
        <h1 className="auth-title">Agri Beneficiary Intelligence</h1>
        <p className="auth-subtitle">Sign in to your account</p>

        <form onSubmit={handleSubmit} className="auth-form" id="login-form">
          <div className="form-group">
            <label htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="auth-error" role="alert" id="login-error">
              {error}
            </div>
          )}

          <button
            id="login-submit"
            type="submit"
            className="auth-btn"
            disabled={loading}
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="auth-switch">
          Don't have an account?{" "}
          <a href="/register" onClick={(e) => { e.preventDefault(); navigate("/register"); }}>
            Register
          </a>
        </p>
      </div>
    </div>
  );
}
