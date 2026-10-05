/**
 * LoginPage Vitest tests — Phase 05 frontend spec.
 *
 * 1. Renders email + password inputs and submit button.
 * 2. Valid mock credentials → useAuth called with token.
 * 3. Bad credentials → error message displayed.
 * 4. After login, redirects to /dashboard (officer) or /me (farmer).
 */
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

// Mock the useAuth hook before importing the component
vi.mock("../hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

import { useAuth } from "../hooks/useAuth";
import LoginPage from "../pages/LoginPage";

const mockUseAuth = useAuth as ReturnType<typeof vi.fn>;

function renderLogin(initialPath = "/login") {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<div>Dashboard</div>} />
        <Route path="/me" element={<div>MyProfile</div>} />
      </Routes>
    </MemoryRouter>
  );
}

afterEach(() => vi.clearAllMocks());

// ---------------------------------------------------------------------------
// 1. Renders inputs and submit button
// ---------------------------------------------------------------------------
describe("LoginPage rendering", () => {
  it("renders email input, password input, and submit button", () => {
    mockUseAuth.mockReturnValue({ login: vi.fn(), loading: false, error: null });
    renderLogin();

    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// 2. Valid credentials → redirects to /dashboard (officer)
// ---------------------------------------------------------------------------
describe("LoginPage — successful officer login", () => {
  it("redirects to /dashboard after officer login", async () => {
    const mockLogin = vi.fn().mockResolvedValue({ access_token: "tok", role: "officer" });
    mockUseAuth.mockReturnValue({ login: mockLogin, loading: false, error: null });

    renderLogin();

    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: "officer@test.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "secret123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => expect(screen.getByText("Dashboard")).toBeInTheDocument());
    expect(mockLogin).toHaveBeenCalledWith({
      email: "officer@test.com",
      password: "secret123",
    });
  });
});

// ---------------------------------------------------------------------------
// 3. Bad credentials → error message displayed
// ---------------------------------------------------------------------------
describe("LoginPage — failed login", () => {
  it("shows error message on bad credentials", async () => {
    const mockLogin = vi.fn().mockRejectedValue(new Error("Incorrect email or password"));
    mockUseAuth.mockReturnValue({
      login: mockLogin,
      loading: false,
      error: "Incorrect email or password",
    });

    renderLogin();

    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: "bad@test.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "wrong" },
    });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent("Incorrect email or password")
    );
  });
});

// ---------------------------------------------------------------------------
// 4. Farmer login → redirects to /me
// ---------------------------------------------------------------------------
describe("LoginPage — farmer redirect", () => {
  it("redirects to /me after farmer login", async () => {
    const mockLogin = vi.fn().mockResolvedValue({ access_token: "tok", role: "farmer" });
    mockUseAuth.mockReturnValue({ login: mockLogin, loading: false, error: null });

    renderLogin();

    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: "farmer@test.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "farmerpass" },
    });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => expect(screen.getByText("MyProfile")).toBeInTheDocument());
  });
});
