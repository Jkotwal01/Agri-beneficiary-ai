import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuthContext } from "../context/AuthContext";
import { LayoutDashboard, FileText, Settings, LogOut, Sprout, User } from "lucide-react";

export default function FarmerLayout() {
  const { logout } = useAuthContext();
  const navigate = useNavigate();

  const navItems = [
    { name: "Schemes", to: "/me", icon: LayoutDashboard },
    { name: "My Profile", to: "/me/profile", icon: User },
    { name: "My Applications", to: "/me/applications", icon: FileText },
    { name: "Settings", to: "/me/settings", icon: Settings },
  ];

  return (
    <div className="flex h-screen bg-background overflow-hidden font-sans">
      <div className="w-56 bg-surface border-r border-borderline flex flex-col justify-between shrink-0">
        <div>
          <div className="h-12 border-b border-borderline flex items-center px-4">
            <Sprout className="w-4 h-4 text-accent-emerald mr-2" />
            <h1 className="text-sm font-semibold tracking-tight text-primary">Farmer Portal</h1>
          </div>
          <nav className="flex flex-col p-2 space-y-0.5">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.to}
                end={item.to === "/me"}
                className={({ isActive }) =>
                  `flex items-center px-2 py-2 text-sm rounded-sm font-medium transition-colors ${
                    isActive
                      ? "bg-slate-100 text-primary"
                      : "text-secondary hover:bg-slate-50 hover:text-primary"
                  }`
                }
              >
                <item.icon className="w-4 h-4 shrink-0 opacity-75" />
                <span className="ml-2">{item.name}</span>
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
            className="flex items-center w-full px-2 py-2 text-sm text-secondary hover:bg-slate-50 hover:text-primary rounded-sm transition-colors"
          >
            <LogOut className="w-4 h-4 shrink-0 opacity-75 text-red-500" />
            <span className="ml-2">Logout</span>
          </button>
        </div>
      </div>

      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <div className="flex-1 overflow-auto p-4 bg-background">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
