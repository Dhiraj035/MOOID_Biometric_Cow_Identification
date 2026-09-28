import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { History, CheckCircle2, AlertCircle, PlusCircle, RotateCcw, ScanFace } from "lucide-react";
import { getDashboardStats } from "../services/api";
import "./RecognitionHistory.css";

function RecognitionHistory() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadHistory() {
    try {
      setLoading(true);
      setError("");
      const data = await getDashboardStats();
      setHistory(Array.isArray(data?.recent_activity) ? data.recent_activity : []);
    } catch (err) {
      console.error(err);
      setError("Failed to load recognition history.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  function formatDate(timestamp) {
    if (!timestamp) return "Unknown time";
    try {
      return new Date(timestamp).toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    } catch {
      return "Unknown time";
    }
  }

  return (
    <div className="history-container">
      <div className="history-header-row">
        <div className="page-header">
          <h1>Recognition History</h1>
          <p>Complete historical logs of biometric scans, identifications, and registrations.</p>
        </div>
        <button className="btn-secondary" onClick={loadHistory} disabled={loading}>
          <RotateCcw size={15} className={loading ? "spin" : ""} /> Refresh
        </button>
      </div>

      {error && (
        <div className="identify-error-banner card">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="history-card card">
        {loading ? (
          <div className="history-loading-box">
            {[1, 2, 3, 4].map((n) => (
              <div key={n} className="skeleton-card" style={{ height: "54px", marginBottom: "10px" }} />
            ))}
          </div>
        ) : history.length === 0 ? (
          <div className="history-empty-state">
            <div className="empty-history-icon">
              <History size={36} />
            </div>
            <h3>No recognition logs recorded</h3>
            <p>Once you scan or identify cows using muzzle images, records will be logged automatically.</p>
            <button className="btn-primary" onClick={() => navigate("/identify")} style={{ marginTop: "12px" }}>
              <ScanFace size={16} /> Scan Cow Now
            </button>
          </div>
        ) : (
          <>
            {/* Desktop Table */}
            <div className="history-table-container">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Action</th>
                    <th>Cow ID</th>
                    <th>Match Result</th>
                    <th className="align-right">Date & Time</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((activity, index) => {
                    const isKnown = activity.result === "KNOWN";
                    const isUnknown = activity.result === "UNKNOWN";

                    return (
                      <tr key={activity._id || index} className="history-row">
                        <td className="status-cell">
                          {isKnown ? (
                            <span className="status-indicator-badge known" title="Positively Identified">
                              <CheckCircle2 size={16} />
                            </span>
                          ) : isUnknown ? (
                            <span className="status-indicator-badge unknown" title="Unrecognized Cow">
                              <AlertCircle size={16} />
                            </span>
                          ) : (
                            <span className="status-indicator-badge neutral">
                              <PlusCircle size={16} />
                            </span>
                          )}
                        </td>

                        <td className="action-cell">
                          <span className="action-label">
                            {activity.action === "IDENTIFICATION" ? "Muzzle Biometric Scan" : activity.action || "Log"}
                          </span>
                        </td>

                        <td className="cow-id-cell">
                          {activity.cow_id ? (
                            <span className="cow-id-tag">{activity.cow_id}</span>
                          ) : (
                            <span className="cow-id-placeholder">—</span>
                          )}
                        </td>

                        <td className="result-cell">
                          <span className={`status-badge ${isKnown ? "known" : isUnknown ? "unknown" : "neutral"}`}>
                            {activity.result || "Logged"}
                          </span>
                        </td>

                        <td className="align-right time-cell">
                          {formatDate(activity.timestamp)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Mobile Stacked History Cards */}
            <div className="history-mobile-list">
              {history.map((activity, index) => {
                const isKnown = activity.result === "KNOWN";
                const isUnknown = activity.result === "UNKNOWN";

                return (
                  <div key={activity._id || index} className="history-mobile-item">
                    <div className="mobile-item-top">
                      <div className="mobile-item-meta">
                        {isKnown ? (
                          <CheckCircle2 size={16} className="text-success" />
                        ) : isUnknown ? (
                          <AlertCircle size={16} className="text-warning" />
                        ) : (
                          <PlusCircle size={16} className="text-muted" />
                        )}
                        <span className="mobile-item-action">
                          {activity.action === "IDENTIFICATION" ? "Muzzle Biometric Scan" : activity.action || "Log"}
                        </span>
                      </div>
                      <span className={`status-badge ${isKnown ? "known" : isUnknown ? "unknown" : "neutral"}`}>
                        {activity.result || "Logged"}
                      </span>
                    </div>

                    <div className="mobile-item-bottom">
                      <div className="mobile-item-id">
                        Cow ID: <strong>{activity.cow_id || "Unregistered"}</strong>
                      </div>
                      <div className="mobile-item-date">
                        {formatDate(activity.timestamp)}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default RecognitionHistory;
