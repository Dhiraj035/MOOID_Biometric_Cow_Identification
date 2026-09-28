import { useRef, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  Camera,
  Upload,
  RotateCcw,
  ScanFace,
  CheckCircle2,
  AlertCircle,
  LoaderCircle,
  ScanLine,
  ArrowRight,
  ShieldCheck,
  PlusCircle
} from "lucide-react";
import { identifyCow } from "../services/api";
import "./IdentifyCow.css";

function IdentifyCow() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  const [image, setImage] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [stream, setStream] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const startCamera = async () => {
    try {
      setError(null);
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
        audio: false,
      });
      setStream(mediaStream);
      setCameraActive(true);
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      }, 100);
    } catch (err) {
      console.error(err);
      setError("Unable to access the camera. Please verify camera permissions in your browser.");
    }
  };

  const stopCamera = () => {
    if (stream) stream.getTracks().forEach((track) => track.stop());
    setStream(null);
    setCameraActive(false);
  };

  const captureImage = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], "camera-capture.jpg", { type: "image/jpeg" });
        setSelectedFile(file);
        setImage(URL.createObjectURL(blob));
        stopCamera();
      }
    }, "image/jpeg");
  };

  const handleFileUpload = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setError("Please select a valid image file (JPG, PNG, WEBP).");
      return;
    }

    setSelectedFile(file);
    setImage(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  };

  const handleIdentify = async () => {
    if (!selectedFile) {
      setError("Please capture or select an image first.");
      return;
    }
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      const response = await identifyCow(selectedFile);
      setResult(response);
    } catch (err) {
      console.error(err);
      setError(err.message || "Cow identification failed.");
    } finally {
      setLoading(false);
    }
  };

  const resetImage = () => {
    stopCamera();
    setImage(null);
    setSelectedFile(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const BiometricScannerSVG = () => (
    <svg viewBox="0 0 200 200" className="identify-anim-svg" aria-hidden="true">
      <defs>
        <linearGradient id="scanGlow" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="var(--primary)" />
          <stop offset="100%" stopColor="var(--secondary)" />
        </linearGradient>
      </defs>

      {/* Target Reticle */}
      <circle cx="100" cy="100" r="90" fill="none" stroke="rgba(20, 184, 166, 0.1)" strokeWidth="1" />
      <circle cx="100" cy="100" r="60" fill="none" stroke="rgba(20, 184, 166, 0.2)" strokeWidth="1" strokeDasharray="5 5" className="target-ring" />

      {/* Central Muzzle Icon */}
      <path
        d="M60,110 C60,70 140,70 140,110 C150,140 130,160 100,160 C70,160 50,140 60,110 Z"
        fill="rgba(15, 139, 118, 0.05)"
        stroke="url(#scanGlow)"
        strokeWidth="2"
      />
      <circle cx="80" cy="120" r="8" fill="none" stroke="var(--primary)" strokeWidth="2" />
      <circle cx="120" cy="120" r="8" fill="none" stroke="var(--primary)" strokeWidth="2" />

      {/* Scanning Line & Light */}
      <line x1="20" y1="100" x2="180" y2="100" stroke="var(--secondary)" strokeWidth="3" className="scanner-line" />
      <polygon points="100,190 90,180 110,180" fill="var(--secondary)" className="scanner-arrow" />
    </svg>
  );

  const similarityScore = result
    ? result.similarity_percentage ?? Math.round((result.similarity || 0) * 100)
    : 0;

  const yoloScore = result
    ? result.yolo_confidence_percentage ?? (result.yolo_confidence ? Math.round(result.yolo_confidence * 100) : null)
    : null;

  return (
    <>
      <div className="page-header">
        <h1>Identify Cow</h1>
        <p>Capture or upload a muzzle image for instant biometric identification.</p>
      </div>

      {error && (
        <div className="identify-error-banner card">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="identify-grid">
        {/* =================================================
            CAPTURE AREA
        ================================================= */}
        <div className="capture-area card">
          <div className="card-heading">
            <h2>Capture Image</h2>
            <p>Position the cow's muzzle clearly inside the frame.</p>
          </div>

          <div className="camera-viewport">
            {cameraActive ? (
              <>
                <video ref={videoRef} autoPlay playsInline muted className="camera-video" />
                <div className="camera-overlay">
                  <div className="corner tl" />
                  <div className="corner tr" />
                  <div className="corner bl" />
                  <div className="corner br" />
                </div>
              </>
            ) : image ? (
              <img src={image} alt="Selected cow preview" className="preview-image" />
            ) : (
              <div className="empty-viewport">
                <div className="empty-icon">
                  <Camera size={44} />
                </div>
                <h3>No image selected</h3>
                <p>Use your device camera or upload a photo</p>
              </div>
            )}
          </div>

          <div className="action-buttons">
            {!cameraActive && !image && (
              <>
                <button className="btn-primary" onClick={startCamera}>
                  <Camera size={18} /> Use Camera
                </button>
                <button className="btn-secondary" onClick={() => fileInputRef.current?.click()}>
                  <Upload size={18} /> Upload Image
                </button>
                <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileUpload} hidden />
              </>
            )}

            {cameraActive && (
              <>
                <button className="btn-primary" onClick={captureImage}>
                  <Camera size={18} /> Capture
                </button>
                <button className="btn-danger" onClick={stopCamera}>
                  Cancel
                </button>
              </>
            )}

            {image && !cameraActive && (
              <div className="selected-actions">
                <button className="btn-identify" onClick={handleIdentify} disabled={loading}>
                  {loading ? (
                    <><LoaderCircle size={18} className="spin" /> Analyzing Biometrics...</>
                  ) : (
                    <><ScanFace size={18} /> Identify Cow</>
                  )}
                </button>
                <button className="btn-outline" onClick={resetImage} disabled={loading}>
                  <RotateCcw size={18} /> Reset
                </button>
              </div>
            )}
          </div>
        </div>

        {/* =================================================
            RESULT AREA
        ================================================= */}
        <div className="result-area card">
          <div className="card-heading">
            <h2>Identification Result</h2>
            <p>Biometric matching output and confidence scores.</p>
          </div>

          {!result && !loading && (
            <div className="result-placeholder">
              <div className="scanner-animation-wrapper">
                <BiometricScannerSVG />
              </div>
              <h3>Ready to Scan</h3>
              <p>Upload a muzzle photo and click <strong>Identify Cow</strong> to run AI recognition.</p>
            </div>
          )}

          {loading && (
            <div className="result-placeholder">
              <LoaderCircle size={48} className="spin text-primary" style={{ color: 'var(--primary)', marginBottom: '16px' }} />
              <h3>Analyzing Biometric Patterns...</h3>
              <p>Running YOLO muzzle detection and ResNet50 biometric feature extraction.</p>
            </div>
          )}

          {result && !loading && (
            <div className="result-data">
              {result.result === "KNOWN" ? (
                <div className="status-banner success">
                  <CheckCircle2 size={24} />
                  <span>Cow Identified Successfully</span>
                </div>
              ) : (
                <div className="status-banner warning">
                  <AlertCircle size={24} />
                  <span>Unknown Cow (No match found above threshold)</span>
                </div>
              )}

              <div className="identified-cow-info">
                <div className="result-avatar">🐄</div>
                <div className="result-text">
                  <span>{result.result === "KNOWN" ? "Registered Cattle" : "Identification Status"}</span>
                  <h2>{result.cow_id || "Unregistered Cow"}</h2>
                  {result.cow_name && (
                    <p style={{ margin: "4px 0 0", fontSize: "16px", color: "var(--primary)", fontWeight: "600" }}>
                      {result.cow_name}
                    </p>
                  )}
                </div>
              </div>

              {/* Similarity Metric */}
              <div className="metric-box">
                <div className="metric-header">
                  <span>Biometric Similarity</span>
                  <strong>{similarityScore}%</strong>
                </div>
                <div className="progress-bg">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${Math.min(100, similarityScore)}%`,
                      background: result.result === "KNOWN"
                        ? "linear-gradient(to right, var(--secondary), var(--primary))"
                        : "linear-gradient(to right, #f59e0b, #ef4444)"
                    }}
                  />
                </div>
                {result.unknown_threshold && (
                  <div style={{ marginTop: "8px", fontSize: "12px", color: "var(--text-muted)", display: "flex", justifyContent: "space-between" }}>
                    <span>Threshold: {(result.unknown_threshold * 100).toFixed(1)}%</span>
                    <span>Result: <strong>{result.result}</strong></span>
                  </div>
                )}
              </div>

              {/* YOLO Detection Confidence */}
              {yoloScore !== null && (
                <div className="small-status" style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "6px", marginBottom: "16px" }}>
                  <ShieldCheck size={16} style={{ color: "var(--primary)" }} />
                  <span>Muzzle Detection Confidence: <strong>{yoloScore}%</strong></span>
                </div>
              )}

              {/* Top Matches if available */}
              {Array.isArray(result.top_matches) && result.top_matches.length > 0 && (
                <div className="top-matches-wrapper" style={{ marginTop: "16px" }}>
                  <h4 style={{ margin: "0 0 10px", fontSize: "13px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                    Candidate Matches
                  </h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    {result.top_matches.slice(0, 3).map((match, idx) => (
                      <div
                        key={match.cow_id || idx}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          padding: "8px 12px",
                          background: idx === 0 && result.result === "KNOWN" ? "var(--primary-subtle)" : "var(--background)",
                          borderRadius: "var(--radius-sm)",
                          fontSize: "13px",
                          border: "1px solid var(--border)"
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <span style={{ fontWeight: "700", color: "var(--text-muted)" }}>#{match.rank || idx + 1}</span>
                          <span style={{ fontWeight: "600", color: "var(--text-main)" }}>{match.cow_name || match.cow_id}</span>
                          {match.cow_name && <span style={{ color: "var(--text-muted)", fontSize: "11px" }}>({match.cow_id})</span>}
                        </div>
                        <span style={{ fontWeight: "600", color: "var(--primary)" }}>
                          {match.similarity_percentage ?? (match.similarity ? (match.similarity * 100).toFixed(1) : 0)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Follow-up actions */}
              <div style={{ marginTop: "24px", display: "flex", gap: "12px", flexWrap: "wrap" }}>
                {result.result === "UNKNOWN" ? (
                  <button
                    className="btn-primary"
                    onClick={() => navigate("/register-cow")}
                    style={{ flex: 1, justifyContent: "center" }}
                  >
                    <PlusCircle size={16} /> Register this Cow
                  </button>
                ) : (
                  <button
                    className="btn-secondary"
                    onClick={() => navigate("/cows")}
                    style={{ flex: 1, justifyContent: "center" }}
                  >
                    View in My Cows <ArrowRight size={16} />
                  </button>
                )}
                <button
                  className="btn-outline"
                  onClick={resetImage}
                  style={{ justifyContent: "center" }}
                >
                  <RotateCcw size={16} /> Scan Another
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default IdentifyCow;