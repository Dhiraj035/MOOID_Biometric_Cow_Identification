import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  ScanFace,
  History,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  PlusCircle,
  Database,
  ScanLine,
  RefreshCw
} from "lucide-react";
import { getDashboardStats, getCurrentUser } from "../services/api";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [user, setUser] = useState(null);

  const [stats, setStats] = useState({
    total_cows: 0,
    total_identifications: 0,
  });

  const [recentActivity, setRecentActivity] = useState([]);

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      const [statsData, userData] = await Promise.allSettled([
        getDashboardStats(),
        getCurrentUser()
      ]);

      if (statsData.status === "fulfilled" && statsData.value) {
        setStats({
          total_cows: statsData.value?.stats?.total_cows || 0,
          total_identifications: statsData.value?.stats?.total_identifications || 0,
        });
        setRecentActivity(
          Array.isArray(statsData.value?.recent_activity)
            ? statsData.value.recent_activity
            : []
        );
      } else if (statsData.status === "rejected") {
        throw statsData.reason;
      }

      if (userData.status === "fulfilled" && userData.value?.user) {
        setUser(userData.value.user);
      }
    } catch (err) {
      console.error("Dashboard error:", err);
      setError(err?.message || "Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  function formatDate(timestamp) {
    if (!timestamp) return "Just now";
    try {
      const date = new Date(timestamp);
      return date.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    } catch {
      return "Unknown time";
    }
  }

  /* =====================================================
     CUSTOM BIOMETRIC INLINE SVGs
  ===================================================== */
  const IdentifyCowSVG = () => (
    <svg viewBox="0 0 160 160" className="action-card-svg identify-svg" aria-hidden="true">
      <defs>
        <linearGradient id="scanGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#0F8B76" />
          <stop offset="50%" stopColor="#14B8A6" />
          <stop offset="100%" stopColor="#06B6D4" />
        </linearGradient>
        <linearGradient id="beamGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="rgba(6, 182, 212, 0.4)" />
          <stop offset="100%" stopColor="rgba(20, 184, 166, 0.05)" />
        </linearGradient>
      </defs>

      {/* Target Reticle & Scan Rings */}
      <circle cx="80" cy="80" r="62" fill="none" stroke="rgba(20, 184, 166, 0.2)" strokeWidth="1.5" strokeDasharray="6 4" className="rotate-ring" />
      <circle cx="80" cy="80" r="50" fill="none" stroke="rgba(6, 182, 212, 0.25)" strokeWidth="1" />

      {/* Muzzle Contour */}
      <path
        d="M56,92 C56,68 104,68 104,92 C108,108 100,120 80,120 C60,120 52,108 56,92 Z"
        fill="rgba(15, 139, 118, 0.06)"
        stroke="url(#scanGrad)"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      {/* Nostril Patterns */}
      <ellipse cx="68" cy="100" rx="5" ry="7" fill="none" stroke="url(#scanGrad)" strokeWidth="2" />
      <ellipse cx="92" cy="100" rx="5" ry="7" fill="none" stroke="url(#scanGrad)" strokeWidth="2" />

      {/* Biometric Feature Points */}
      <circle cx="64" cy="84" r="2.5" fill="#06B6D4" />
      <circle cx="96" cy="84" r="2.5" fill="#06B6D4" />
      <circle cx="80" cy="88" r="2.5" fill="#14B8A6" />
      <circle cx="73" cy="112" r="2.5" fill="#0F8B76" />
      <circle cx="87" cy="112" r="2.5" fill="#0F8B76" />
      <line x1="64" y1="84" x2="80" y2="88" stroke="rgba(6, 182, 212, 0.4)" strokeWidth="1" strokeDasharray="2 2" />
      <line x1="96" y1="84" x2="80" y2="88" stroke="rgba(6, 182, 212, 0.4)" strokeWidth="1" strokeDasharray="2 2" />

      {/* Viewfinder Corners */}
      <path d="M40,54 L40,42 L52,42" fill="none" stroke="var(--teal)" strokeWidth="2" strokeLinecap="round" />
      <path d="M120,54 L120,42 L108,42" fill="none" stroke="var(--teal)" strokeWidth="2" strokeLinecap="round" />
      <path d="M40,106 L40,118 L52,118" fill="none" stroke="var(--teal)" strokeWidth="2" strokeLinecap="round" />
      <path d="M120,106 L120,118 L108,118" fill="none" stroke="var(--teal)" strokeWidth="2" strokeLinecap="round" />

      {/* Scanning Beam */}
      <line x1="36" y1="80" x2="124" y2="80" stroke="#06B6D4" strokeWidth="2" className="scan-beam-line" />
    </svg>
  );

  const RegisterCowSVG = () => (
    <svg viewBox="0 0 160 160" className="action-card-svg register-svg" aria-hidden="true">
      <defs>
        <linearGradient id="regGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#08705F" />
          <stop offset="50%" stopColor="#0F8B76" />
          <stop offset="100%" stopColor="#14B8A6" />
        </linearGradient>
      </defs>

      {/* Concentric Biometric Rings */}
      <circle cx="80" cy="80" r="62" fill="none" stroke="rgba(15, 139, 118, 0.15)" strokeWidth="1" className="pulse-ring-outer" />
      <circle cx="80" cy="80" r="48" fill="none" stroke="rgba(20, 184, 166, 0.25)" strokeWidth="1.5" />

      {/* Muzzle Profile Contour */}
      <path
        d="M68,60 L60,44 L76,56 Q80,52 84,56 L100,44 L92,60 Q104,76 100,100 L88,116 Q80,120 72,116 L60,100 Q56,76 68,60 Z"
        fill="rgba(20, 184, 166, 0.06)"
        stroke="url(#regGrad)"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />

      {/* Biometric Ridge Lines */}
      <path d="M72,76 Q80,68 88,76" fill="none" stroke="url(#regGrad)" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M68,88 Q80,80 92,88" fill="none" stroke="url(#regGrad)" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M72,100 Q80,92 88,100" fill="none" stroke="url(#regGrad)" strokeWidth="1.5" strokeLinecap="round" />

      {/* Plus Badge */}
      <g transform="translate(108, 108)">
        <circle cx="0" cy="0" r="15" fill="var(--surface)" stroke="var(--primary)" strokeWidth="2.5" />
        <line x1="-6" y1="0" x2="6" y2="0" stroke="var(--primary)" strokeWidth="2.5" strokeLinecap="round" />
        <line x1="0" y1="-6" x2="0" y2="6" stroke="var(--primary)" strokeWidth="2.5" strokeLinecap="round" />
      </g>
    </svg>
  );

  return (
    <div className="dashboard-container">
      {/* =================================================
          1. HEADER & WELCOME
      ================================================= */}
      <header className="dashboard-header">
        <div className="welcome-text-group">
          <h1>Welcome back{user?.name ? `, ${user.name}` : ""}</h1>
          <p>AI-powered biometric cow identification using muzzle patterns.</p>
        </div>

        <div className="dashboard-status-chip">
          <span className="live-status-dot" />
          <span>Biometric System Online</span>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="dashboard-error-card card">
          <AlertCircle size={22} className="error-icon" />
          <div className="error-body">
            <strong>Unable to load live dashboard stats</strong>
            <p>{error}</p>
          </div>
          <button onClick={loadDashboard} className="btn-secondary retry-btn">
            <RefreshCw size={15} /> Retry
          </button>
        </div>
      )}

      {/* Loading Skeleton */}
      {loading ? (
        <div className="dashboard-skeleton-grid">
          <div className="skeleton-stats-row">
            <div className="skeleton-card stat" />
            <div className="skeleton-card stat" />
          </div>
          <div className="skeleton-actions-row">
            <div className="skeleton-card action" />
            <div className="skeleton-card action" />
          </div>
          <div className="skeleton-card activity" />
        </div>
      ) : (
        <>
          {/* =================================================
              2. COMPACT STATISTICS (ONLY TOTAL COWS & SCANS)
          ================================================= */}
          <section className="dashboard-stats-row" aria-label="System Statistics">
            <div className="stat-card card">
              <div className="stat-card-inner">
                <div className="stat-icon-badge cow-badge">
                  <span className="stat-emoji" role="img" aria-label="cow">🐄</span>
                </div>
                <div className="stat-text">
                  <span className="stat-number">{stats.total_cows}</span>
                  <span className="stat-label">Registered Cows</span>
                </div>
              </div>
            </div>

            <div className="stat-card card">
              <div className="stat-card-inner">
                <div className="stat-icon-badge scan-badge">
                  <ScanLine size={20} strokeWidth={2.4} />
                </div>
                <div className="stat-text">
                  <span className="stat-number">{stats.total_identifications}</span>
                  <span className="stat-label">Total Scans</span>
                </div>
              </div>
            </div>
          </section>

          {/* =================================================
              3. PRIMARY ACTION CARDS (SIDE-BY-SIDE ON ALL SCREENS)
          ================================================= */}
          <section className="dashboard-actions-section" aria-label="Quick Actions">
            <div className="dashboard-actions-grid">
              {/* IDENTIFY COW CARD */}
              <div
                className="action-card identify-card"
                onClick={() => navigate("/identify")}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    navigate("/identify");
                  }
                }}
                aria-label="Identify Cow by muzzle image"
              >
                <div className="action-card-graphic">
                  <IdentifyCowSVG />
                </div>

                <div className="action-card-body">
                  <div className="action-card-title-row">
                    <h2>Identify Cow</h2>
                    <ArrowRight size={18} className="action-arrow" />
                  </div>
                  <p className="action-card-desc">
                    Biometric muzzle recognition & FAISS database match.
                  </p>
                </div>
              </div>

              {/* REGISTER COW CARD */}
              <div
                className="action-card register-card"
                onClick={() => navigate("/register-cow")}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    navigate("/register-cow");
                  }
                }}
                aria-label="Register new Cow biometric profile"
              >
                <div className="action-card-graphic">
                  <RegisterCowSVG />
                </div>

                <div className="action-card-body">
                  <div className="action-card-title-row">
                    <h2>Register Cow</h2>
                    <ArrowRight size={18} className="action-arrow" />
                  </div>
                  <p className="action-card-desc">
                    Extract muzzle embedding & register cattle profile.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* =================================================
              4. RECENT ACTIVITY
          ================================================= */}
          <section className="dashboard-activity-section card" aria-label="Recent Identification Activity">
            <div className="activity-section-header">
              <div className="activity-title-group">
                <History size={18} className="activity-icon" />
                <h3>Recent Activity</h3>
              </div>
              <Link to="/history" className="view-all-link">
                View all logs <ArrowRight size={14} />
              </Link>
            </div>

            {recentActivity.length === 0 ? (
              <div className="activity-empty-state">
                <div className="empty-state-icon">
                  <History size={32} />
                </div>
                <h4>No recent activity yet</h4>
                <p>Scan a cow muzzle or register a new cow to view activity logs.</p>
                <button
                  className="btn-primary empty-action-btn"
                  onClick={() => navigate("/identify")}
                >
                  <ScanFace size={16} /> Identify Cow
                </button>
              </div>
            ) : (
              <>
                {/* Desktop Table View */}
                <div className="activity-table-wrapper">
                  <table className="activity-table">
                    <thead>
                      <tr>
                        <th>Status</th>
                        <th>Action</th>
                        <th>Cow ID</th>
                        <th>Timestamp</th>
                        <th className="align-right">Result</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentActivity.slice(0, 6).map((activity, index) => {
                        const isKnown = activity.result === "KNOWN";
                        const isUnknown = activity.result === "UNKNOWN";

                        return (
                          <tr key={activity._id || index} className="activity-row">
                            <td className="status-col">
                              {isKnown ? (
                                <span className="status-indicator-badge known" title="Positively Identified">
                                  <CheckCircle2 size={15} />
                                </span>
                              ) : isUnknown ? (
                                <span className="status-indicator-badge unknown" title="Unrecognized / Unknown Cow">
                                  <AlertCircle size={15} />
                                </span>
                              ) : (
                                <span className="status-indicator-badge neutral">
                                  <PlusCircle size={15} />
                                </span>
                              )}
                            </td>

                            <td className="action-name-col">
                              <span className="primary-activity-name">
                                {activity.action === "IDENTIFICATION"
                                  ? "Muzzle Scan"
                                  : activity.action || "Biometric Scan"}
                              </span>
                            </td>

                            <td className="cow-id-col">
                              {activity.cow_id ? (
                                <span className="cow-id-code">{activity.cow_id}</span>
                              ) : (
                                <span className="cow-id-none">—</span>
                              )}
                            </td>

                            <td className="time-col">
                              {formatDate(activity.timestamp)}
                            </td>

                            <td className="align-right result-col">
                              <span
                                className={`status-badge ${
                                  isKnown ? "known" : isUnknown ? "unknown" : "neutral"
                                }`}
                              >
                                {activity.result || "Logged"}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {/* Mobile Responsive Stacked Cards */}
                <div className="activity-cards-mobile">
                  {recentActivity.slice(0, 5).map((activity, index) => {
                    const isKnown = activity.result === "KNOWN";
                    const isUnknown = activity.result === "UNKNOWN";

                    return (
                      <div key={activity._id || index} className="activity-mobile-card">
                        <div className="mobile-card-top">
                          <div className="mobile-card-title-group">
                            {isKnown ? (
                              <CheckCircle2 size={16} className="text-success" />
                            ) : isUnknown ? (
                              <AlertCircle size={16} className="text-warning" />
                            ) : (
                              <PlusCircle size={16} className="text-muted" />
                            )}
                            <span className="mobile-activity-type">
                              {activity.action === "IDENTIFICATION" ? "Muzzle Scan" : "Biometric Scan"}
                            </span>
                          </div>
                          <span
                            className={`status-badge ${
                              isKnown ? "known" : isUnknown ? "unknown" : "neutral"
                            }`}
                          >
                            {activity.result || "Logged"}
                          </span>
                        </div>

                        <div className="mobile-card-bottom">
                          <span className="mobile-cow-id">
                            ID: <strong>{activity.cow_id || "Unregistered"}</strong>
                          </span>
                          <span className="mobile-timestamp">
                            {formatDate(activity.timestamp)}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </>
            )}
          </section>
        </>
      )}
    </div>
  );
}

export default Dashboard;