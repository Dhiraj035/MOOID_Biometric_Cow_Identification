import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  ScanFace,
  Scan,
  Camera,
  Cpu,
  Layers,
  Database,
  ShieldCheck,
  ChevronRight,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  Zap,
  Activity,
  Menu,
  X,
  Fingerprint,
  Award,
  Compass,
} from "lucide-react";
import Cow3D from "../components/Cow3D";
import { getToken } from "../services/api";
import "./LandingPage.css";

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [isAuthenticated] = useState(() => Boolean(getToken()));

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 40) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Smooth scroll handler for anchor links
  const scrollToSection = (id) => {
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  const techCards = [
    {
      title: "YOLOv8",
      subtitle: "Muzzle Detection",
      badge: "Vision AI",
      icon: Scan,
      color: "emerald",
      description:
        "High-performance computer vision model trained to autonomously detect and localize the bovine muzzle region of interest (ROI) with sub-pixel bounding box precision in varied outdoor conditions.",
      specs: ["Sub-50ms Detection", "Bounding Box Normalization", "Multi-Angle Robustness"],
    },
    {
      title: "ResNet50",
      subtitle: "Deep Feature Extraction",
      badge: "Deep Learning",
      icon: Cpu,
      color: "teal",
      description:
        "Deep 50-layer residual convolutional architecture that isolates fine dermatoglyphic ridge patterns, groove contours, and bead textures unique to each cattle muzzle.",
      specs: ["Residual Skip Connections", "Hierarchical Texture Maps", "ImageNet & Cattle Pretrained"],
    },
    {
      title: "ArcFace",
      subtitle: "Biometric Embedding",
      badge: "Metric Learning",
      icon: ShieldCheck,
      color: "cyan",
      description:
        "Additive Angular Margin Loss optimizing deep feature hyperspheres to enforce high inter-class divergence and tight intra-class compactness between distinct cattle identities.",
      specs: ["Additive Angular Margin", "Hypersphere Projection", "High Margin Separation"],
    },
    {
      title: "512-D",
      subtitle: "Feature Representation",
      badge: "Biometric Vector",
      icon: Layers,
      color: "indigo",
      description:
        "Compact 512-dimensional normalized numerical fingerprint mathematically encoding the permanent muzzle biometrics of individual cattle for tamper-proof identification.",
      specs: ["L2 Normalized Vector", "Compact Memory Footprint", "Collision-Proof Signature"],
    },
    {
      title: "FAISS",
      subtitle: "Similarity Search & Matching",
      badge: "Vector Search",
      icon: Database,
      color: "green",
      description:
        "Hardware-accelerated vector indexing engine computing cosine similarity and nearest-neighbor distances across thousands of registered cattle profiles in sub-milliseconds.",
      specs: ["Cosine Similarity Index", "Sub-millisecond Querying", "Scalable to Large Herds"],
    },
  ];

  const steps = [
    {
      num: "01",
      title: "Capture Cow Image",
      desc: "Take a frontal photo of the cow's face or muzzle using any smartphone, farm camera, or tablet device.",
      icon: Camera,
    },
    {
      num: "02",
      title: "Detect Muzzle",
      desc: "YOLOv8 automatically locates, segments, and standardizes the muzzle region, filtering out surrounding background.",
      icon: Scan,
    },
    {
      num: "03",
      title: "Extract Biometric Features",
      desc: "ResNet50 and ArcFace compute a unique 512-dimensional mathematical embedding of the dermatoglyphic ridge pattern.",
      icon: Cpu,
    },
    {
      num: "04",
      title: "Identify Registered Cow",
      desc: "FAISS vector search matches the embedding against the database, instantly returning cow identity, records, and ownership.",
      icon: ShieldCheck,
    },
  ];

  const comparisons = [
    {
      feature: "Tamper & Fraud Resistance",
      mooId: "100% Unalterable Biometric",
      earTags: "Vulnerable to Loss & Theft",
      rfid: "Can Be Cloned or Removed",
    },
    {
      feature: "Animal Welfare",
      mooId: "Completely Non-Invasive",
      earTags: "Causes Pain & Infection",
      rfid: "Invasive Surgical Injection",
    },
    {
      feature: "Durability & Permanence",
      mooId: "Permanent Throughout Life",
      earTags: "Frequently Torn / Replaced",
      rfid: "Electronic Degradation",
    },
    {
      feature: "Hardware Requirement",
      mooId: "Standard Smartphone / Camera",
      earTags: "Special Applicator Pincers",
      rfid: "Expensive RFID Scanners",
    },
  ];

  return (
    <div className="landing-page-root">
      {/* Background Ambient Glows */}
      <div className="ambient-glow glow-top-center" />
      <div className="ambient-glow glow-hero-right" />
      <div className="ambient-glow glow-bottom" />

      {/* =========================================================
          LANDING NAVBAR
      ========================================================= */}
      <header className={`landing-navbar ${isScrolled ? "scrolled" : ""}`}>
        <div className="landing-nav-container">
          {/* Brand Logo */}
          <div
            className="landing-brand"
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            role="button"
            tabIndex={0}
          >
            <div className="brand-logo-glow">
              <ScanFace size={22} strokeWidth={2.4} />
            </div>
            <div className="brand-title-wrap">
              <span className="brand-name">Moo-ID</span>
              <span className="brand-tag">AI BIOMETRICS</span>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="desktop-nav-links">
            <button className="nav-text-btn" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
              Home
            </button>
            <button className="nav-text-btn" onClick={() => scrollToSection("technology")}>
              Technology
            </button>
            <button className="nav-text-btn" onClick={() => scrollToSection("how-it-works")}>
              How It Works
            </button>
            <button className="nav-text-btn" onClick={() => scrollToSection("biometrics")}>
              Biometrics
            </button>
            <button className="nav-text-btn" onClick={() => scrollToSection("features")}>
              Features
            </button>
          </nav>

          {/* Auth Action Buttons */}
          <div className="landing-nav-actions">
            {isAuthenticated ? (
              <Link to="/dashboard" className="btn-primary-gradient">
                <span>Go to Dashboard</span>
                <ArrowRight size={16} />
              </Link>
            ) : (
              <>
                <Link to="/login" className="btn-ghost">
                  Sign In
                </Link>
                <Link to="/register" className="btn-primary-gradient">
                  <span>Get Started</span>
                  <ChevronRight size={16} />
                </Link>
              </>
            )}

            {/* Mobile Hamburger Toggle */}
            <button
              className="mobile-menu-btn"
              onClick={() => setMobileMenuOpen((prev) => !prev)}
              aria-label="Toggle navigation menu"
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Drawer */}
        {mobileMenuOpen && (
          <div className="mobile-nav-drawer">
            <button
              className="mobile-nav-link"
              onClick={() => {
                setMobileMenuOpen(false);
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
            >
              Home
            </button>
            <button className="mobile-nav-link" onClick={() => scrollToSection("technology")}>
              Technology
            </button>
            <button className="mobile-nav-link" onClick={() => scrollToSection("how-it-works")}>
              How It Works
            </button>
            <button className="mobile-nav-link" onClick={() => scrollToSection("biometrics")}>
              Biometrics
            </button>
            <button className="mobile-nav-link" onClick={() => scrollToSection("features")}>
              Features
            </button>

            <div className="mobile-drawer-divider" />

            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="btn-primary-gradient mobile-action-btn"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span>Go to Dashboard</span>
                <ArrowRight size={16} />
              </Link>
            ) : (
              <div className="mobile-drawer-actions">
                <Link
                  to="/login"
                  className="btn-ghost mobile-action-btn"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="btn-primary-gradient mobile-action-btn"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <span>Get Started</span>
                  <ChevronRight size={16} />
                </Link>
              </div>
            )}
          </div>
        )}
      </header>

      {/* =========================================================
          HERO SECTION
      ========================================================= */}
      <section className="landing-hero-section">
        <div className="landing-container hero-grid">
          {/* Left Column: Hero Content */}
          <div className="hero-text-col">
            {/* Small Badge */}
            <div className="hero-badge">
              <span className="badge-pulse-indicator" />
              <Sparkles size={14} className="hero-badge-icon" />
              <span>AI-POWERED BIOMETRIC IDENTIFICATION</span>
            </div>

            {/* Main Heading */}
            <h1 className="hero-heading">
              Identify Every Cow. <br />
              <span className="hero-heading-gradient">By Its Muzzle.</span>
            </h1>

            {/* Supporting Paragraph */}
            <p className="hero-description">
              Advanced biometric identification for cattle using AI-powered
              muzzle pattern recognition. Engineered with YOLOv8 muzzle
              detection, deep ResNet50 feature extraction, and 512-D ArcFace
              biometric embeddings for non-invasive, fraud-proof livestock
              management.
            </p>

            {/* Action Buttons */}
            <div className="hero-btn-row">
              <Link
                to={isAuthenticated ? "/dashboard" : "/register"}
                className="btn-hero-primary"
              >
                <span>Get Started</span>
                <ArrowRight size={18} />
              </Link>

              <button
                className="btn-hero-secondary"
                onClick={() => scrollToSection("technology")}
              >
                <Compass size={18} />
                <span>Explore Technology</span>
              </button>
            </div>

            {/* Live Metrics Row */}
            <div className="hero-stats-row">
              <div className="hero-stat-card">
                <span className="stat-number">99.2%</span>
                <span className="stat-label">Match Accuracy</span>
              </div>
              <div className="stat-divider" />
              <div className="hero-stat-card">
                <span className="stat-number">&lt; 350ms</span>
                <span className="stat-label">Inference Time</span>
              </div>
              <div className="stat-divider" />
              <div className="hero-stat-card">
                <span className="stat-number">512-D</span>
                <span className="stat-label">Deep Vector</span>
              </div>
              <div className="stat-divider" />
              <div className="hero-stat-card">
                <span className="stat-number">100%</span>
                <span className="stat-label">Non-Invasive</span>
              </div>
            </div>
          </div>

          {/* Right Column: 3D Cow Showcase */}
          <div className="hero-model-col">
            <Cow3D />
          </div>
        </div>
      </section>

      {/* =========================================================
          TECHNOLOGY SECTION
      ========================================================= */}
      <section id="technology" className="landing-section tech-section">
        <div className="landing-container">
          <div className="section-header text-center">
            <div className="section-pill">
              <Cpu size={14} />
              <span>CORE ARCHITECTURE</span>
            </div>
            <h2 className="section-title">
              Next-Gen Deep Learning <br />
              <span className="text-gradient">Bovine Biometrics Pipeline</span>
            </h2>
            <p className="section-desc">
              Every stage of the Moo-ID framework is optimized for bovine
              dermatoglyphic discrimination, transforming skin ridge textures
              into immutable biometric signatures.
            </p>
          </div>

          <div className="tech-cards-grid">
            {techCards.map((tech) => {
              const Icon = tech.icon;
              return (
                <div key={tech.title} className={`tech-card ${tech.color}`}>
                  <div className="tech-card-header">
                    <div className="tech-icon-wrap">
                      <Icon size={24} />
                    </div>
                    <span className="tech-badge">{tech.badge}</span>
                  </div>

                  <h3 className="tech-card-title">{tech.title}</h3>
                  <h4 className="tech-card-subtitle">{tech.subtitle}</h4>
                  <p className="tech-card-description">{tech.description}</p>

                  <div className="tech-specs-list">
                    {tech.specs.map((spec) => (
                      <div key={spec} className="tech-spec-item">
                        <CheckCircle2 size={13} className="spec-check" />
                        <span>{spec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* =========================================================
          HOW IT WORKS (4 STEPS)
      ========================================================= */}
      <section id="how-it-works" className="landing-section steps-section">
        <div className="landing-container">
          <div className="section-header text-center">
            <div className="section-pill">
              <Zap size={14} />
              <span>SEAMLESS WORKFLOW</span>
            </div>
            <h2 className="section-title">
              How Moo-ID Identifies <br />
              <span className="text-gradient">Cattle in 4 Simple Steps</span>
            </h2>
            <p className="section-desc">
              From snapping a quick farm photo to instant identity retrieval in
              under half a second.
            </p>
          </div>

          <div className="steps-grid">
            {steps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div key={step.num} className="step-card">
                  <div className="step-num-pill">{step.num}</div>
                  <div className="step-icon-wrap">
                    <Icon size={24} />
                  </div>
                  <h3 className="step-title">{step.title}</h3>
                  <p className="step-desc">{step.desc}</p>
                  {idx < steps.length - 1 && <div className="step-connector" />}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* =========================================================
          BIOMETRICS SCIENCE SECTION
      ========================================================= */}
      <section id="biometrics" className="landing-section biometrics-section">
        <div className="landing-container">
          <div className="bio-split-layout">
            <div className="bio-info-col">
              <div className="section-pill">
                <Fingerprint size={14} />
                <span>BIOMETRIC SCIENCE</span>
              </div>
              <h2 className="section-title">
                Why Bovine Muzzle Prints <br />
                <span className="text-gradient">Surpass Traditional Tags</span>
              </h2>
              <p className="section-desc">
                Just like human fingerprints, the dermatoglyphic ridge and groove
                patterns on a cow's muzzle (nasolabial disc) are biologically
                unique to each animal and remain completely unchanged across its
                entire lifespan.
              </p>

              <div className="bio-key-points">
                <div className="bio-point">
                  <div className="bio-point-icon">
                    <ShieldCheck size={20} />
                  </div>
                  <div>
                    <h4>100% Tamper & Fraud Proof</h4>
                    <p>
                      Ear tags can be torn, swapped, or lost. Muzzle prints are
                      inseparable from the living animal.
                    </p>
                  </div>
                </div>

                <div className="bio-point">
                  <div className="bio-point-icon">
                    <Award size={20} />
                  </div>
                  <div>
                    <h4>Non-Invasive & Stress-Free</h4>
                    <p>
                      No ear punching, no branding pain, and no electronic
                      implants. Simply take a photo from a safe distance.
                    </p>
                  </div>
                </div>

                <div className="bio-point">
                  <div className="bio-point-icon">
                    <Activity size={20} />
                  </div>
                  <div>
                    <h4>Permanent Lifetime Biometric</h4>
                    <p>
                      Muzzle ridge topologies grow proportionally without
                      losing geometric uniqueness as the calf matures.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Comparison Table */}
            <div className="bio-table-col">
              <div className="comparison-card">
                <h3 className="comparison-card-title">
                  Livestock Identification Comparison
                </h3>
                <div className="table-responsive">
                  <table className="comparison-table">
                    <thead>
                      <tr>
                        <th>Metric</th>
                        <th className="highlight-col">Moo-ID AI</th>
                        <th>Ear Tags</th>
                        <th>RFID Tags</th>
                      </tr>
                    </thead>
                    <tbody>
                      {comparisons.map((row) => (
                        <tr key={row.feature}>
                          <td className="table-feature-name">{row.feature}</td>
                          <td className="table-cell-highlight">{row.mooId}</td>
                          <td className="table-cell-dim">{row.earTags}</td>
                          <td className="table-cell-dim">{row.rfid}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================
          KEY FEATURES SECTION
      ========================================================= */}
      <section id="features" className="landing-section features-section">
        <div className="landing-container">
          <div className="section-header text-center">
            <div className="section-pill">
              <Sparkles size={14} />
              <span>CAPABILITIES</span>
            </div>
            <h2 className="section-title">
              Complete Cattle Intelligence <br />
              <span className="text-gradient">For Farms & Herd Managers</span>
            </h2>
            <p className="section-desc">
              Everything required to register, monitor, verify, and trace livestock
              in one streamlined platform.
            </p>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-card-icon">
                <Camera size={24} />
              </div>
              <h3>Instant Camera Identification</h3>
              <p>
                Capture real-time muzzle photos directly through the web camera
                or upload high-resolution images for sub-second recognition.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-card-icon">
                <ScanFace size={24} />
              </div>
              <h3>Seamless Herd Registration</h3>
              <p>
                Enroll new calves and adult cattle in seconds with automated
                YOLOv8 muzzle cropping and feature vector caching.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-card-icon">
                <Database size={24} />
              </div>
              <h3>Comprehensive Health Records</h3>
              <p>
                Store breed details, birth dates, vaccination histories, and
                veterinary notes tied permanently to each cow's biometric ID.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-card-icon">
                <Activity size={24} />
              </div>
              <h3>Audit Trails & Recognition History</h3>
              <p>
                Review historical scans, match confidence percentages, top
                candidate rankings, and verification timestamps.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================
          CALL TO ACTION (CTA)
      ========================================================= */}
      <section className="landing-section cta-section">
        <div className="landing-container">
          <div className="cta-banner">
            <div className="cta-banner-content">
              <h2 className="cta-title">
                Ready to Experience Biometric Cattle Identification?
              </h2>
              <p className="cta-desc">
                Elevate livestock traceability, eliminate identity fraud, and
                safeguard your herd with AI-powered muzzle recognition.
              </p>
              <div className="cta-btn-group">
                <Link
                  to={isAuthenticated ? "/dashboard" : "/register"}
                  className="btn-hero-primary"
                >
                  <span>{isAuthenticated ? "Launch Dashboard" : "Get Started Now"}</span>
                  <ArrowRight size={18} />
                </Link>
                {!isAuthenticated && (
                  <Link to="/login" className="btn-hero-secondary">
                    <span>Sign In to Account</span>
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================
          LANDING FOOTER
      ========================================================= */}
      <footer className="landing-footer">
        <div className="landing-container footer-content">
          <div className="footer-brand-col">
            <div className="landing-brand">
              <div className="brand-logo-glow">
                <ScanFace size={20} strokeWidth={2.4} />
              </div>
              <span className="brand-name">Moo-ID</span>
            </div>
            <p className="footer-tagline">
              AI-Powered Biometric Livestock Identification & Traceability System.
            </p>
            <div className="footer-tech-stack">
              <span>YOLOv8</span>
              <span>•</span>
              <span>ResNet50</span>
              <span>•</span>
              <span>ArcFace</span>
              <span>•</span>
              <span>FAISS</span>
              <span>•</span>
              <span>Three.js</span>
            </div>
          </div>

          <div className="footer-links-col">
            <h4>Quick Navigation</h4>
            <ul>
              <li>
                <button className="footer-link-btn" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
                  Home
                </button>
              </li>
              <li>
                <button className="footer-link-btn" onClick={() => scrollToSection("technology")}>
                  Technology
                </button>
              </li>
              <li>
                <button className="footer-link-btn" onClick={() => scrollToSection("how-it-works")}>
                  How It Works
                </button>
              </li>
              <li>
                <button className="footer-link-btn" onClick={() => scrollToSection("biometrics")}>
                  Biometrics
                </button>
              </li>
            </ul>
          </div>

          <div className="footer-links-col">
            <h4>Application</h4>
            <ul>
              <li>
                <Link to="/login" className="footer-link">
                  Sign In
                </Link>
              </li>
              <li>
                <Link to="/register" className="footer-link">
                  Register Account
                </Link>
              </li>
              <li>
                <Link to="/dashboard" className="footer-link">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link to="/identify" className="footer-link">
                  Identify Cow
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="landing-container footer-bottom-bar">
          <p>© {new Date().getFullYear()} Moo-ID Biometrics. All rights reserved.</p>
          <p className="footer-note">Built for ethical, non-invasive livestock identification.</p>
        </div>
      </footer>
    </div>
  );
}
