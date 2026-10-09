import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuthContext } from "../context/AuthContext";
import { LayoutDashboard, GitMerge, Flag, LogOut } from "lucide-react";

export default function OfficerLayout() {
  const { logout } = useAuthContext();
  const navigate = useNavigate();

  const navItems = [
    { name: "Dashboard", to: "/dashboard", icon: LayoutDashboard },
    { name: "Review Queue", to: "/dashboard/review", icon: GitMerge },
    { name: "Rule Engine", to: "/dashboard/flags", icon: Flag },
  ];

  return (
    <div className="flex h-screen bg-background overflow-hidden font-sans">
      {/* Sidebar */}
      <div className="w-56 bg-surface border-r border-borderline flex flex-col justify-between shrink-0">
        <div>
          <div className="h-12 border-b border-borderline flex items-center px-4">
            <h1 className="text-sm font-semibold tracking-tight text-primary">Agri Beneficiary AI</h1>
          </div>
          <nav className="flex flex-col p-2 space-y-0.5">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.to}
                end={item.to === "/dashboard"}
                className={({ isActive }) =>
                  `flex items-center px-2 py-1.5 text-sm rounded-sm font-medium transition-colors ${
                    isActive
                      ? "bg-slate-100 text-primary"
                      : "text-secondary hover:bg-slate-50 hover:text-primary"
                  }`
                }
              >
                <item.icon className="w-4 h-4 mr-2 opacity-75" />
                {item.name}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="p-2 border-t border-borderline">
          <button
            onClick={() => {
              logout();
              navigate("/login");
            }}
            className="flex items-center w-full px-2 py-1.5 text-sm text-secondary hover:bg-slate-50 hover:text-primary rounded-sm transition-colors"
          >
            <LogOut className="w-4 h-4 mr-2 opacity-75" />
            Logout
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <div className="h-12 border-b border-borderline flex items-center px-4 bg-surface shrink-0">
          <h2 className="text-sm font-semibold text-secondary uppercase tracking-wider">
            Officer Portal
          </h2>
        </div>
        <div className="flex-1 overflow-auto p-4 bg-background">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
