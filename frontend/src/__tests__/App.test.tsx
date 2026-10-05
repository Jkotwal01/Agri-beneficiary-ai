import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import LoginPage from "../pages/LoginPage";

// App.test just verifies the login page renders — detailed login tests are in LoginPage.test.tsx
describe("App default route", () => {
  it("renders the login page by default", () => {
    render(
      <MemoryRouter initialEntries={["/login"]}>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });
});
