import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { loginUser } from "../services/api";
import { Eye, EyeOff } from "lucide-react";
import "./Login.css";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");

    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    try {
      setLoading(true);
      await loginUser(email, password);
      // Login successful
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Invalid email or password.");
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
          <h2>AI-powered biometric cow identification</h2>
          <p>Identify and manage cattle using unique muzzle patterns.</p>
        </div>
      </div>

      <div className="auth-right-panel">
        <div className="auth-card-modern">
          <div className="auth-header">
            <h2>Welcome Back</h2>
            <p>Sign in to your Moo-ID account</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label>Email Address</label>
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <div className="password-input-wrapper">
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete="current-password"
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
            </div>

            {error && <div className="auth-error-modern">{error}</div>}

            <button
              type="submit"
              className="auth-button-modern"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className="auth-footer-modern">
            <p>
              Don't have an account?{" "}
              <Link to="/register">Create an account</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;