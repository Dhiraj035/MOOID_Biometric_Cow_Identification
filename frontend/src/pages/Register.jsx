import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { registerUser } from "../services/api";
import { Eye, EyeOff } from "lucide-react";
import "./Login.css"; // Reuse split-screen styles

function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  function getPasswordStrength(pwd) {
    if (pwd.length === 0) return { label: "", color: "transparent" };
    if (pwd.length < 6) return { label: "Weak", color: "#b0524b" };
    if (pwd.length < 10) return { label: "Medium", color: "#e8a03a" };
    return { label: "Strong", color: "#0f8b76" };
  }

  const strength = getPasswordStrength(form.password);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!form.name || !form.email || !form.password) {
      setError("Name, email and password are required.");
      return;
    }

    if (form.password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);
      await registerUser({
        name: form.name,
        email: form.email,
        phone: form.phone,
        password: form.password,
      });

      setSuccess("Account created successfully. Redirecting to login...");
      setTimeout(() => {
        navigate("/login");
      }, 1500);
    } catch (err) {
      setError(err.message || "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-split-page">
      <div className="auth-left-panel">
        <div className="auth-brand-info">
          <div className="auth-logo-large">
            <span style={{ fontSize: "40px" }}>🐄</span>
          </div>
          <h1>Moo-ID</h1>
          <h2>Join the biometric cattle revolution</h2>
          <p>Register now to manage your livestock with advanced AI recognition technology.</p>
        </div>
      </div>

      <div className="auth-right-panel" style={{ padding: "20px" }}>
        <div className="auth-card-modern" style={{ maxWidth: "450px" }}>
          <div className="auth-header">
            <h2>Create Account</h2>
            <p>Get started with Moo-ID</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                name="name"
                placeholder="Enter your name"
                value={form.name}
                onChange={handleChange}
                autoComplete="name"
                required
              />
            </div>

            <div className="form-group">
              <label>Email Address</label>
              <input
                type="email"
                name="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange}
                autoComplete="email"
                required
              />
            </div>

            <div className="form-group">
              <label>Phone Number (Optional)</label>
              <input
                type="tel"
                name="phone"
                placeholder="Enter your phone number"
                value={form.phone}
                onChange={handleChange}
                autoComplete="tel"
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <div className="password-input-wrapper">
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  placeholder="Create a password"
                  value={form.password}
                  onChange={handleChange}
                  autoComplete="new-password"
                  required
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {form.password && (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '4px' }}>
                  <div style={{ flex: 1, height: '4px', background: '#dce5e1', borderRadius: '2px', overflow: 'hidden' }}>
                    <div style={{ width: strength.label === 'Weak' ? '33%' : strength.label === 'Medium' ? '66%' : '100%', height: '100%', background: strength.color, transition: 'all 0.3s' }}></div>
                  </div>
                  <span style={{ fontSize: '11px', color: strength.color, marginLeft: '10px', fontWeight: '600' }}>{strength.label}</span>
                </div>
              )}
            </div>

            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type={showPassword ? "text" : "password"}
                name="confirmPassword"
                placeholder="Confirm your password"
                value={form.confirmPassword}
                onChange={handleChange}
                autoComplete="new-password"
                required
              />
            </div>

            {error && <div className="auth-error-modern">{error}</div>}
            
            {success && (
              <div style={{ background: '#eff9f5', color: '#08785f', border: '1px solid #c2e5de', padding: '12px 16px', borderRadius: '8px', fontSize: '13px', fontWeight: '500' }}>
                {success}
              </div>
            )}

            <button
              type="submit"
              className="auth-button-modern"
              disabled={loading || !!success}
            >
              {loading ? "Creating account..." : "Create Account"}
            </button>
          </form>

          <div className="auth-footer-modern">
            <p>
              Already have an account?{" "}
              <Link to="/login">Sign In</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;