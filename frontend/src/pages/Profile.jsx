import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { User, Mail, Shield, Calendar, LogOut, CheckCircle } from "lucide-react";
import { getCurrentUser, logoutUser } from "../services/api";
import "./Profile.css";

function Profile() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getCurrentUser()
      .then((data) => setUser(data.user))
      .catch((err) => {
        console.error(err);
        setError("Unable to load profile information.");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  function handleLogout() {
    logoutUser();
    navigate("/login");
  }

  if (loading) {
    return (
      <div className="profile-page">
        <div className="page-header">
          <h1>My Profile</h1>
          <p>Loading your profile data...</p>
        </div>
        <div className="profile-loading">
          <div className="skeleton-card small" style={{ maxWidth: '600px', margin: '0 auto', height: '240px' }} />
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="page-header">
        <h1>My Profile</h1>
        <p>Manage your account details and security settings.</p>
      </div>

      {error ? (
        <div className="identify-error-banner card">
          <span>{error}</span>
        </div>
      ) : (
        <div className="profile-content">
          <div className="profile-card card">
            <div className="profile-avatar-section">
              <div className="profile-avatar-large">
                {user?.name ? user.name.charAt(0).toUpperCase() : "U"}
              </div>
              <h2>{user?.name || "System User"}</h2>
              <div className="profile-role">
                <CheckCircle size={14} />
                <span>{user?.role === "admin" ? "Administrator" : "Registered User"}</span>
              </div>
            </div>

            <div className="profile-details-section">
              <h3>Account Information</h3>
              <div className="profile-detail-grid">
                <div className="profile-detail-item">
                  <div className="detail-icon">
                    <User size={18} />
                  </div>
                  <div>
                    <label>Full Name</label>
                    <p>{user?.name || "Not specified"}</p>
                  </div>
                </div>

                <div className="profile-detail-item">
                  <div className="detail-icon">
                    <Mail size={18} />
                  </div>
                  <div>
                    <label>Email Address</label>
                    <p>{user?.email || "Not specified"}</p>
                  </div>
                </div>

                <div className="profile-detail-item">
                  <div className="detail-icon">
                    <Shield size={18} />
                  </div>
                  <div>
                    <label>User ID</label>
                    <p style={{ fontFamily: "monospace", fontSize: "13px" }}>{user?.user_id || "-"}</p>
                  </div>
                </div>

                <div className="profile-detail-item">
                  <div className="detail-icon">
                    <Calendar size={18} />
                  </div>
                  <div>
                    <label>Member Since</label>
                    <p>{user?.created_at ? new Date(user.created_at).toLocaleDateString() : "Active"}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="profile-actions">
              <button className="logout-action-button" onClick={handleLogout}>
                <LogOut size={16} style={{ display: "inline-block", verticalAlign: "middle", marginRight: "8px" }} />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Profile;
