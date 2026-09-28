import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  PlusCircle,
  Upload,
  Camera,
  AlertCircle,
  CheckCircle2,
  LoaderCircle,
} from "lucide-react";
import { registerCow } from "../services/api";
import "./RegisterCow.css";

function RegisterCow() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [form, setForm] = useState({
    cow_id: "",
    cow_name: "",
    owner_name: "",
    owner_phone: "",
    owner_address: "",
  });

  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleFileUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setSelectedFile(file);
    setImagePreview(URL.createObjectURL(file));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess(false);

    if (!form.cow_id || !form.cow_name || !form.owner_name || !selectedFile) {
      setError("Cow ID, Name, Owner Name, and a Biometric Image are required.");
      return;
    }

    try {
      setLoading(true);
      await registerCow({
        ...form,
        file: selectedFile,
      });
      setSuccess(true);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to register cow.");
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setForm({ cow_id: "", cow_name: "", owner_name: "", owner_phone: "", owner_address: "" });
    setSelectedFile(null);
    setImagePreview(null);
    setSuccess(false);
    setError("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  const RegisterProcessSVG = () => (
    <svg viewBox="0 0 200 200" className="register-anim-svg">
      <defs>
        <linearGradient id="regProcGlow" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="var(--primary-light)" />
          <stop offset="100%" stopColor="var(--primary)" />
        </linearGradient>
      </defs>
      
      <circle cx="100" cy="100" r="75" fill="none" stroke="rgba(15, 139, 118, 0.1)" strokeWidth="2" strokeDasharray="10 10" className="slow-spin" />
      <circle cx="100" cy="100" r="60" fill="none" stroke="rgba(15, 139, 118, 0.2)" strokeWidth="1" />
      
      {/* Document Base */}
      <path d="M70,50 L130,50 Q140,50 140,60 L140,140 Q140,150 130,150 L70,150 Q60,150 60,140 L60,60 Q60,50 70,50 Z" fill="rgba(15, 139, 118, 0.05)" stroke="url(#regProcGlow)" strokeWidth="2" />
      
      {/* Cow Muzzle Silhouette on Document */}
      <path d="M85,95 C85,75 115,75 115,95 C120,110 110,120 100,120 C90,120 80,110 85,95 Z" fill="none" stroke="var(--primary)" strokeWidth="2" />
      
      {/* Upload Arrow */}
      <path d="M100,125 L100,135 M95,130 L100,125 L105,130" fill="none" stroke="var(--secondary)" strokeWidth="2" className="bounce-arrow" />
      
      {/* Plus Symbol */}
      <circle cx="140" cy="140" r="16" fill="var(--card)" stroke="var(--primary)" strokeWidth="2" className="pulse-plus" />
      <path d="M134,140 L146,140 M140,134 L140,146" stroke="var(--primary)" strokeWidth="2" />
    </svg>
  );

  if (success) {
    return (
      <div className="register-cow-page">
        <div className="page-header">
          <h1>Register Cow</h1>
          <p>Create a new biometric profile.</p>
        </div>
        <div className="card success-panel text-center" style={{ padding: '64px 32px' }}>
          <div className="success-icon-wrapper" style={{ margin: '0 auto 24px', width: '80px', height: '80px', background: 'var(--success-light)', color: 'var(--success)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <CheckCircle2 size={40} />
          </div>
          <h2 style={{ fontSize: '28px', color: 'var(--text-main)', marginBottom: '16px' }}>Cow Registered Successfully</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: '32px' }}>
            <strong>{form.cow_name}</strong> (ID: {form.cow_id}) has been added to your biometric database.
          </p>
          <div className="action-buttons" style={{ justifyContent: 'center' }}>
            <button className="btn-primary" onClick={() => navigate("/cows")}>View My Cows</button>
            <button className="btn-outline" onClick={handleReset}>Register Another Cow</button>
            <button className="btn-outline" onClick={() => navigate("/dashboard")}>Back to Dashboard</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="register-cow-page">
      <div className="page-header">
        <h1>Register Cow</h1>
        <p>Create a new biometric profile and add a cow to your registered cattle database.</p>
      </div>

      {error && (
        <div className="identify-error-banner card">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="register-grid">
        <form onSubmit={handleSubmit} className="register-form-area card">
          <div className="card-heading">
            <h2>Cow Information</h2>
            <p>Basic identification details.</p>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label>Cow ID (Tag Number) *</label>
              <input type="text" name="cow_id" value={form.cow_id} onChange={handleChange} placeholder="e.g. MOO-2023-001" required />
            </div>
            <div className="form-group">
              <label>Cow Name *</label>
              <input type="text" name="cow_name" value={form.cow_name} onChange={handleChange} placeholder="e.g. Daisy" required />
            </div>
          </div>

          <div className="card-heading mt-4">
            <h2>Owner Information</h2>
            <p>Contact details for the owner.</p>
          </div>

          <div className="form-group">
            <label>Owner Name *</label>
            <input type="text" name="owner_name" value={form.owner_name} onChange={handleChange} placeholder="Full Name" required />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Phone Number</label>
              <input type="tel" name="owner_phone" value={form.owner_phone} onChange={handleChange} placeholder="Phone Number" />
            </div>
            <div className="form-group">
              <label>Address</label>
              <input type="text" name="owner_address" value={form.owner_address} onChange={handleChange} placeholder="Farm Address" />
            </div>
          </div>

          <div className="card-heading mt-4">
            <h2>Biometric Image *</h2>
            <p>Upload a clear image of the cow's muzzle.</p>
          </div>

          <div className="biometric-upload-area" onClick={() => fileInputRef.current?.click()}>
            {imagePreview ? (
              <img src={imagePreview} alt="Preview" className="upload-preview" />
            ) : (
              <div className="upload-placeholder">
                <Upload size={40} style={{ color: 'var(--primary)', marginBottom: '16px' }} />
                <h3>Click to upload muzzle image</h3>
                <p>PNG, JPG or JPEG (Max 10MB)</p>
              </div>
            )}
            <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileUpload} hidden />
          </div>

          {imagePreview && (
            <button type="button" className="btn-outline mt-3" onClick={(e) => { e.stopPropagation(); setImagePreview(null); setSelectedFile(null); if (fileInputRef.current) fileInputRef.current.value = ""; }}>
              Remove Image
            </button>
          )}

          <div className="form-submit mt-4" style={{ marginTop: '40px' }}>
            <button type="submit" className="btn-identify" style={{ width: '100%', padding: '16px' }} disabled={loading}>
              {loading ? (
                <><LoaderCircle size={20} className="spin" /> Registering biometric profile...</>
              ) : (
                <><PlusCircle size={20} /> Register Cow</>
              )}
            </button>
          </div>
        </form>

        <div className="register-info-area">
          <div className="card sticky-info">
            <div className="animation-container" style={{ width: '100%', maxWidth: '240px', margin: '0 auto 32px' }}>
              <RegisterProcessSVG />
            </div>
            <h3 style={{ fontSize: '20px', color: 'var(--text-main)', marginBottom: '16px' }}>Registration Process</h3>
            <ol className="process-list">
              <li>
                <div className="step-num">1</div>
                <div>
                  <h4>Upload Image</h4>
                  <p>Provide a high-quality close-up of the cow's muzzle.</p>
                </div>
              </li>
              <li>
                <div className="step-num">2</div>
                <div>
                  <h4>Detect Muzzle</h4>
                  <p>Our YOLO model automatically detects and crops the muzzle area.</p>
                </div>
              </li>
              <li>
                <div className="step-num">3</div>
                <div>
                  <h4>Extract Features</h4>
                  <p>ResNet50 extracts unique biometric embeddings from the pattern.</p>
                </div>
              </li>
              <li>
                <div className="step-num">4</div>
                <div>
                  <h4>Register Profile</h4>
                  <p>The embeddings are securely stored in the FAISS database.</p>
                </div>
              </li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RegisterCow;