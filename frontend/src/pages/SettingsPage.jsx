import { useState, useEffect } from "react";
import {
  Sun,
  Moon,
  Monitor,
  Database,
  Cpu,
  ShieldCheck,
  CheckCircle2,
  Sparkles
} from "lucide-react";
import { getInitialTheme, applyTheme } from "../services/theme";
import { checkBackendHealth } from "../services/api";
import "./SettingsPage.css";

function SettingsPage() {
  const [currentTheme, setCurrentTheme] = useState("light");
  const [backendHealth, setBackendHealth] = useState({ status: "checking", device: "Detecting..." });

  useEffect(() => {
    setCurrentTheme(getInitialTheme());

    const handleThemeChange = (e) => {
      setCurrentTheme(e.detail);
    };

    window.addEventListener("moo_id_theme_change", handleThemeChange);

    checkBackendHealth()
      .then((data) => {
        setBackendHealth({
          status: "healthy",
          device: data?.device || "CPU / PyTorch",
        });
      })
      .catch(() => {
        setBackendHealth({
          status: "offline",
          device: "Disconnected",
        });
      });

    return () => {
      window.removeEventListener("moo_id_theme_change", handleThemeChange);
    };
  }, []);

  function handleSelectTheme(theme) {
    setCurrentTheme(theme);
    applyTheme(theme);
  }

  return (
    <div className="settings-container">
      <div className="page-header">
        <h1>Settings</h1>
        <p>Configure interface appearance, biometric preferences, and system parameters.</p>
      </div>

      <div className="settings-grid">
        {/* =================================================
            1. APPEARANCE (THEME SWITCHER)
        ================================================= */}
        <div className="settings-card card">
          <div className="settings-card-header">
            <div className="settings-card-icon">
              <Monitor size={20} />
            </div>
            <div>
              <h2>Appearance</h2>
              <p>Choose your preferred interface theme for Moo-ID</p>
            </div>
          </div>

          <div className="theme-selector-group" role="radiogroup" aria-label="Theme selection">
            {/* LIGHT MODE OPTION */}
            <div
              className={`theme-option-card ${currentTheme === "light" ? "active" : ""}`}
              onClick={() => handleSelectTheme("light")}
              role="radio"
              aria-checked={currentTheme === "light"}
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  handleSelectTheme("light");
                }
              }}
            >
              <div className="theme-option-preview light-preview">
                <div className="preview-top-bar" />
                <div className="preview-content-box">
                  <div className="preview-accent-chip" />
                  <div className="preview-line" />
                </div>
              </div>

              <div className="theme-option-label">
                <Sun size={18} className="theme-label-icon sun-icon" />
                <span>Light Mode</span>
                {currentTheme === "light" && <CheckCircle2 size={16} className="check-icon" />}
              </div>
            </div>

            {/* DARK MODE OPTION */}
            <div
              className={`theme-option-card ${currentTheme === "dark" ? "active" : ""}`}
              onClick={() => handleSelectTheme("dark")}
              role="radio"
              aria-checked={currentTheme === "dark"}
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  handleSelectTheme("dark");
                }
              }}
            >
              <div className="theme-option-preview dark-preview">
                <div className="preview-top-bar" />
                <div className="preview-content-box">
                  <div className="preview-accent-chip" />
                  <div className="preview-line" />
                </div>
              </div>

              <div className="theme-option-label">
                <Moon size={18} className="theme-label-icon moon-icon" />
                <span>Dark Mode</span>
                {currentTheme === "dark" && <CheckCircle2 size={16} className="check-icon" />}
              </div>
            </div>
          </div>
        </div>

        {/* =================================================
            2. AI BIOMETRIC PIPELINE CONFIGURATION
        ================================================= */}
        <div className="settings-card card">
          <div className="settings-card-header">
            <div className="settings-card-icon">
              <Cpu size={20} />
            </div>
            <div>
              <h2>Biometric Engine Configuration</h2>
              <p>Active machine learning parameters and inference thresholds</p>
            </div>
          </div>

          <div className="settings-fields-list">
            <div className="settings-field-row">
              <div className="field-meta">
                <span className="field-name">Muzzle Detection Model</span>
                <span className="field-desc">Ultralytics YOLOv8 inference model</span>
              </div>
              <span className="status-badge known">YOLOv8 Active</span>
            </div>

            <div className="settings-field-row">
              <div className="field-meta">
                <span className="field-name">Feature Extraction Model</span>
                <span className="field-desc">ResNet-50 biometric embedding layer</span>
              </div>
              <span className="field-value-chip">512 Dimensions</span>
            </div>

            <div className="settings-field-row">
              <div className="field-meta">
                <span className="field-name">Similarity Search Engine</span>
                <span className="field-desc">Facebook AI Similarity Search (FAISS FlatIP)</span>
              </div>
              <span className="field-value-chip">Cosine Similarity</span>
            </div>

            <div className="settings-field-row">
              <div className="field-meta">
                <span className="field-name">Recognition Threshold</span>
                <span className="field-desc">Minimum similarity for a positive "KNOWN" match</span>
              </div>
              <span className="field-value-chip">0.5813 (58.1%)</span>
            </div>
          </div>
        </div>

        {/* =================================================
            3. BACKEND API CONNECTION
        ================================================= */}
        <div className="settings-card card">
          <div className="settings-card-header">
            <div className="settings-card-icon">
              <Database size={20} />
            </div>
            <div>
              <h2>Backend & Services</h2>
              <p>Active FastAPI backend service and connection endpoint</p>
            </div>
          </div>

          <div className="settings-fields-list">
            <div className="settings-field-row">
              <div className="field-meta">
                <span className="field-name">FastAPI Endpoint</span>
                <span className="field-desc">Target server for biometric recognition APIs</span>
              </div>
              <input
                type="text"
                value="http://127.0.0.1:8000"
                disabled
                className="endpoint-input"
              />
            </div>

            <div className="settings-field-row">
              <div className="field-meta">
                <span className="field-name">Connection Status</span>
                <span className="field-desc">Real-time health status with backend service</span>
              </div>
              <span className={`status-badge ${backendHealth.status === "healthy" ? "known" : "unknown"}`}>
                <ShieldCheck size={14} />
                {backendHealth.status === "healthy" ? "Connected & Healthy" : "Offline"}
              </span>
            </div>

            <div className="settings-field-row">
              <div className="field-meta">
                <span className="field-name">Execution Hardware</span>
                <span className="field-desc">PyTorch compute device reported by backend</span>
              </div>
              <span className="field-value-chip">{backendHealth.device}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
