import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, RotateCcw, AlertCircle, PlusCircle, ShieldCheck } from "lucide-react";
import { getMyCows } from "../services/api";
import "./Cows.css";

function Cows() {
  const navigate = useNavigate();
  const [cows, setCows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  async function loadCows() {
    try {
      setLoading(true);
      setError("");
      const data = await getMyCows();
      setCows(Array.isArray(data?.cows) ? data.cows : []);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to load registered cows.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCows();
  }, []);

  const filteredCows = cows.filter(
    (cow) =>
      cow.cow_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cow.cow_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cow.owner_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="cows-container">
      <div className="cows-header-row">
        <div className="page-header">
          <h1>My Cows</h1>
          <p>Registered cattle profiles with biometric muzzle embeddings.</p>
        </div>
        <div className="cows-header-actions">
          <button className="btn-secondary" onClick={loadCows} disabled={loading}>
            <RotateCcw size={15} className={loading ? "spin" : ""} /> Refresh
          </button>
          <button className="btn-primary" onClick={() => navigate("/register-cow")}>
            <PlusCircle size={15} /> Register Cow
          </button>
        </div>
      </div>

      {error && (
        <div className="identify-error-banner card">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Search & Filter Bar */}
      <div className="cows-controls-card card">
        <div className="cows-search-box">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search by Cow ID, Name, or Owner..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="cows-search-input"
          />
        </div>
        <div className="cows-count-badge">
          {filteredCows.length} {filteredCows.length === 1 ? "Cow" : "Cows"}
        </div>
      </div>

      {/* Grid of Registered Cattle */}
      {loading ? (
        <div className="cows-grid">
          {[1, 2, 3, 4].map((n) => (
            <div key={n} className="skeleton-card card" style={{ height: "220px" }} />
          ))}
        </div>
      ) : filteredCows.length === 0 ? (
        <div className="cows-empty-state card">
          <div className="empty-avatar-circle">
            <span role="img" aria-label="cow">🐄</span>
          </div>
          <h3>{searchTerm ? "No matching cattle found" : "No cows registered yet"}</h3>
          <p>
            {searchTerm
              ? `No registered profiles match "${searchTerm}".`
              : "Register your first cow to store biometric muzzle patterns in MongoDB & FAISS."}
          </p>
          {!searchTerm && (
            <button className="btn-primary" onClick={() => navigate("/register-cow")} style={{ marginTop: "8px" }}>
              <PlusCircle size={16} /> Register Cow Now
            </button>
          )}
        </div>
      ) : (
        <div className="cows-grid">
          {filteredCows.map((cow) => (
            <div key={cow.cow_id} className="cow-profile-card card">
              <div className="cow-profile-top">
                <div className="cow-avatar-box">
                  <span>🐄</span>
                </div>
                <div className="cow-primary-meta">
                  <h3>{cow.cow_name || "Unnamed"}</h3>
                  <span className="cow-tag-id">{cow.cow_id}</span>
                </div>
                <span className="live-status-dot active" title="Active Biometric Profile" />
              </div>

              <div className="cow-profile-details">
                <div className="cow-detail-row">
                  <span className="detail-label">Owner</span>
                  <span className="detail-value">{cow.owner_name || "—"}</span>
                </div>

                <div className="cow-detail-row">
                  <span className="detail-label">Registered</span>
                  <span className="detail-value">
                    {cow.created_at ? new Date(cow.created_at).toLocaleDateString() : "Active"}
                  </span>
                </div>

                <div className="cow-detail-row">
                  <span className="detail-label">Biometric Status</span>
                  <span className="status-badge known" style={{ padding: "2px 8px", fontSize: "11px" }}>
                    <ShieldCheck size={12} /> Embedded
                  </span>
                </div>

                {(cow.owner_phone || cow.owner_address) && (
                  <div className="cow-contact-subrow">
                    {cow.owner_phone && <div>📞 {cow.owner_phone}</div>}
                    {cow.owner_address && <div>📍 {cow.owner_address}</div>}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Cows;
