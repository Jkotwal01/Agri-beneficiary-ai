import { useState } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuthContext } from "../context/AuthContext";
import { LayoutDashboard, GitMerge, Flag, FileCheck, LogOut, PanelLeftClose, PanelLeftOpen } from "lucide-react";

export default function OfficerLayout() {
  const { logout } = useAuthContext();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(true);

  const navItems = [
    { name: "Dashboard", to: "/dashboard", icon: LayoutDashboard },
    { name: "Review Queue", to: "/dashboard/review", icon: GitMerge },
    { name: "Rule Engine", to: "/dashboard/flags", icon: Flag },
    { name: "Applications", to: "/dashboard/applications", icon: FileCheck },
  ];

  return (
    <div className="flex h-screen bg-background overflow-hidden font-sans">
      {/* Sidebar */}
      <div className={`${isOpen ? 'w-56' : 'w-14'} transition-all duration-300 ease-in-out bg-surface border-r border-borderline flex flex-col justify-between shrink-0`}>
        <div>
          <div className="h-12 border-b border-borderline flex items-center px-4 overflow-hidden whitespace-nowrap">
            {isOpen ? (
              <h1 className="text-sm font-semibold tracking-tight text-primary">Agri Beneficiary AI</h1>
            ) : (
              <div className="w-6 h-6 bg-slate-100 border border-slate-200 rounded-sm flex items-center justify-center text-xs">🌾</div>
            )}
          </div>
          <nav className="flex flex-col p-2 space-y-0.5">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.to}
                end={item.to === "/dashboard"}
                title={item.name}
                className={({ isActive }) =>
                  `flex items-center px-2 py-2 text-sm rounded-sm font-medium transition-colors overflow-hidden ${
                    isActive
                      ? "bg-slate-100 text-primary"
                      : "text-secondary hover:bg-slate-50 hover:text-primary"
                  }`
                }
              >
                <item.icon className="w-4 h-4 shrink-0 opacity-75" />
                <span className={`ml-2 whitespace-nowrap transition-opacity duration-200 ${isOpen ? 'opacity-100' : 'opacity-0 w-0'}`}>
                  {item.name}
                </span>
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="p-2 border-t border-borderline space-y-1">
          <button
            onClick={() => setIsOpen(!isOpen)}
            title="Toggle Sidebar"
            className="flex items-center w-full px-2 py-2 text-sm text-secondary hover:bg-slate-50 hover:text-primary rounded-sm transition-colors overflow-hidden"
          >
            {isOpen ? <PanelLeftClose className="w-4 h-4 shrink-0 opacity-75" /> : <PanelLeftOpen className="w-4 h-4 shrink-0 opacity-75" />}
            <span className={`ml-2 whitespace-nowrap transition-opacity duration-200 ${isOpen ? 'opacity-100' : 'opacity-0 w-0'}`}>
              Collapse
            </span>
          </button>
          <button
            onClick={() => {
              logout();
              navigate("/login");
            }}
            title="Logout"
            className="flex items-center w-full px-2 py-2 text-sm text-secondary hover:bg-slate-50 hover:text-primary rounded-sm transition-colors overflow-hidden"
          >
            <LogOut className="w-4 h-4 shrink-0 opacity-75 text-red-500" />
            <span className={`ml-2 whitespace-nowrap transition-opacity duration-200 ${isOpen ? 'opacity-100' : 'opacity-0 w-0'}`}>
              Logout
            </span>
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
