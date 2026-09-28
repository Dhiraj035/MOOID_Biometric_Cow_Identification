import { useState, useEffect } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import {
  LayoutDashboard,
  ScanFace,
  PlusCircle,
  History,
  User,
  Settings,
  LogOut,
  Menu,
  X
} from "lucide-react";
import { logoutUser, checkBackendHealth, getCurrentUser } from "../services/api";
import "./Layout.css";

function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState("checking");
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Health check
    checkBackendHealth()
      .then(() => setBackendStatus("online"))
      .catch(() => setBackendStatus("offline"));

    // User details for avatar
    getCurrentUser()
      .then((data) => setUser(data?.user || null))
      .catch(() => setUser(null));
  }, []);

  // Close sidebar automatically on route change
  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  const primaryMenuItems = [
    { name: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },
    { name: "Identify Cow", icon: ScanFace, path: "/identify" },
    { name: "Register Cow", icon: PlusCircle, path: "/register-cow" },
    { name: "My Cows", icon: "cow", path: "/cows" },
    { name: "Recognition History", icon: History, path: "/history" },
  ];

  const secondaryMenuItems = [
    { name: "Profile", icon: User, path: "/profile" },
    { name: "Settings", icon: Settings, path: "/settings" },
  ];

  function handleLogout() {
    logoutUser();
    navigate("/login");
  }

  function handleNavigation(path) {
    navigate(path);
    setSidebarOpen(false);
  }

  const userInitial = user?.name ? user.name.charAt(0).toUpperCase() : "U";

  return (
    <div className="app-container">
      {/* Mobile Top Header (Sticky on <= 900px) */}
      <header className="mobile-header">
        <div className="mobile-header-left">
          <button
            className="mobile-icon-btn mobile-menu-toggle"
            onClick={() => setSidebarOpen((prev) => !prev)}
            aria-label="Toggle navigation drawer"
            aria-expanded={sidebarOpen}
          >
            {sidebarOpen ? <X size={22} /> : <Menu size={22} />}
          </button>

          <div
            className="mobile-header-brand"
            onClick={() => handleNavigation("/dashboard")}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") handleNavigation("/dashboard"); }}
          >
            <div className="sidebar-logo mobile-logo">
              <ScanFace size={18} strokeWidth={2.4} />
            </div>
            <span className="mobile-brand-title">Moo-ID</span>
            <span
              className={`mobile-status-dot ${backendStatus}`}
              title={`Biometric System ${backendStatus === "online" ? "Online" : "Offline"}`}
            />
          </div>
        </div>

        <div className="mobile-header-right">
          <button
            className={`mobile-avatar-btn ${location.pathname === "/profile" ? "active" : ""}`}
            onClick={() => handleNavigation("/profile")}
            aria-label="View user profile"
            title="My Profile"
          >
            {user?.name ? (
              <span className="mobile-avatar-text">{userInitial}</span>
            ) : (
              <User size={18} />
            )}
          </button>
        </div>
      </header>

      {/* Sidebar (Desktop permanent / Mobile drawer) */}
      <aside className={`app-sidebar ${sidebarOpen ? "open" : ""}`} aria-label="Sidebar navigation">
        <div className="sidebar-header">
          <div
            className="sidebar-brand-wrapper"
            onClick={() => handleNavigation("/dashboard")}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") handleNavigation("/dashboard"); }}
          >
            <div className="sidebar-logo">
              <ScanFace size={22} strokeWidth={2.4} />
            </div>
            <div className="sidebar-brand-text">
              <h2>Moo-ID</h2>
              <span className="brand-tagline">AI Biometrics</span>
            </div>
          </div>
          <button
            className="sidebar-close-btn"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section-label">MAIN NAVIGATION</div>
          {primaryMenuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <button
                key={item.path}
                className={`nav-link ${isActive ? "active" : ""}`}
                onClick={() => handleNavigation(item.path)}
              >
                {item.icon === "cow" ? (
                  <span className="nav-emoji">🐄</span>
                ) : (
                  <Icon size={19} />
                )}
                <span>{item.name}</span>
              </button>
            );
          })}

          <div className="nav-separator">
            <div className="nav-divider" />
          </div>

          <div className="nav-section-label">ACCOUNT</div>
          {secondaryMenuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.path}
                className={`nav-link ${isActive ? "active" : ""}`}
                onClick={() => handleNavigation(item.path)}
              >
                <Icon size={19} />
                <span>{item.name}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="system-status-indicator">
            <div className={`status-dot ${backendStatus}`}></div>
            <span className="system-status-text">
              Biometric AI {backendStatus === "online" ? "Online" : backendStatus === "checking" ? "Connecting" : "Offline"}
            </span>
          </div>

          <button className="nav-link logout-link" onClick={handleLogout}>
            <LogOut size={19} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Mobile Drawer Backdrop */}
      {sidebarOpen && (
        <div
          className="sidebar-backdrop"
          onClick={() => setSidebarOpen(false)}
          role="button"
          tabIndex={0}
          aria-label="Close navigation overlay"
        />
      )}

      {/* Main Content Area */}
      <main className="app-main" id="main-content">
        {children}
      </main>
    </div>
  );
}

export default Layout;
