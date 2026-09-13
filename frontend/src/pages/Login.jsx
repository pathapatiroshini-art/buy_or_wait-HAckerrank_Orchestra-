import { useState } from "react";
import {
  Mail,
  Lock,
  User,
  Wallet,
  PiggyBank,
  ShieldCheck,
  TrendingUp,
  Sparkles,
  ArrowRight,
  Info,
} from "lucide-react";
import Navbar from "../components/Navbar";
import { useAuth } from "../context/AuthContext";

const RISK_OPTIONS = [
  { value: "conservative", label: "Conservative" },
  { value: "balanced", label: "Balanced" },
  { value: "flexible", label: "Flexible" },
];

function Login() {
  const { login, register } = useAuth();

  const [mode, setMode] = useState("login"); // "login" | "register"
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    current_balance: "",
    monthly_income: "",
    minimum_balance: "",
    risk_tolerance: "balanced",
    flexible_expense_willingness: 0.5,
  });

  const update = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const switchMode = (next) => {
    setMode(next);
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      if (mode === "login") {
        await login(form.email, form.password);
      } else {
        await register({
          name: form.name,
          email: form.email,
          password: form.password,
          current_balance: parseFloat(form.current_balance) || 0,
          monthly_income: parseFloat(form.monthly_income) || 0,
          minimum_balance: parseFloat(form.minimum_balance) || 0,
          risk_tolerance: form.risk_tolerance,
          flexible_expense_willingness: parseFloat(form.flexible_expense_willingness),
        });
      }
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="app">
      <Navbar />

      <div className="auth-shell">
        {/* Left: pitch panel, hidden on mobile */}
        <section className="auth-pitch">
          <div className="eyebrow">
            <Sparkles size={14} />
            <span>Smart spending starts here</span>
          </div>

          <h2>
            Know before
            <span> you spend</span>
          </h2>

          <p>
            Buy or Wait? looks at your real balance, upcoming commitments,
            income and preferences before telling you whether a purchase
            is safe today, safe with a plan, or better left for later.
          </p>

          <div className="auth-features">
            <div className="auth-feature">
              <div className="icon-box">
                <ShieldCheck size={18} />
              </div>
              <div>
                <strong>Safety-first analysis</strong>
                <span>Every recommendation protects your minimum balance and essential bills.</span>
              </div>
            </div>

            <div className="auth-feature">
              <div className="icon-box">
                <TrendingUp size={18} />
              </div>
              <div>
                <strong>Personalized, not generic</strong>
                <span>Two people with the same balance can get different answers based on their habits.</span>
              </div>
            </div>

            <div className="auth-feature">
              <div className="icon-box">
                <PiggyBank size={18} />
              </div>
              <div>
                <strong>A plan, not just a verdict</strong>
                <span>Get a payment timeline and flexible-spending suggestions when you need them.</span>
              </div>
            </div>
          </div>
        </section>

        {/* Right: auth card */}
        <section className="auth-card">
          <div className="auth-tabs">
            <button
              type="button"
              className={`auth-tab ${mode === "login" ? "active" : ""}`}
              onClick={() => switchMode("login")}
            >
              Log in
            </button>
            <button
              type="button"
              className={`auth-tab ${mode === "register" ? "active" : ""}`}
              onClick={() => switchMode("register")}
            >
              Create account
            </button>
          </div>

          <h3>{mode === "login" ? "Welcome back" : "Let's set up your profile"}</h3>
          <p className="auth-subtitle">
            {mode === "login"
              ? "Log in to see whether your next purchase can wait."
              : "A few numbers help us personalize every recommendation."}
          </p>

          <form className="auth-form" onSubmit={handleSubmit}>
            {mode === "register" && (
              <div className="auth-field">
                <User size={16} />
                <input
                  type="text"
                  placeholder="Full name"
                  value={form.name}
                  onChange={update("name")}
                  required
                />
              </div>
            )}

            <div className="auth-field">
              <Mail size={16} />
              <input
                type="email"
                placeholder="Email"
                value={form.email}
                onChange={update("email")}
                required
              />
            </div>

            <div className="auth-field">
              <Lock size={16} />
              <input
                type="password"
                placeholder="Password"
                value={form.password}
                onChange={update("password")}
                minLength={6}
                required
              />
            </div>

            {mode === "register" && (
              <>
                <div className="auth-section-label">Your finances</div>

                <div className="auth-field">
                  <Wallet size={16} />
                  <input
                    type="number"
                    placeholder="Current balance"
                    value={form.current_balance}
                    onChange={update("current_balance")}
                  />
                </div>

                <div className="auth-row">
                  <div className="auth-field">
                    <TrendingUp size={16} />
                    <input
                      type="number"
                      placeholder="Monthly income"
                      value={form.monthly_income}
                      onChange={update("monthly_income")}
                    />
                  </div>

                  <div className="auth-field">
                    <ShieldCheck size={16} />
                    <input
                      type="number"
                      placeholder="Min. balance to keep"
                      value={form.minimum_balance}
                      onChange={update("minimum_balance")}
                    />
                  </div>
                </div>

                <div className="auth-field">
                  <PiggyBank size={16} />
                  <select value={form.risk_tolerance} onChange={update("risk_tolerance")}>
                    {RISK_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </>
            )}

            {error && <div className="auth-error">{error}</div>}

            <button type="submit" className="auth-submit" disabled={submitting}>
              {submitting ? (
                "Please wait…"
              ) : (
                <>
                  {mode === "login" ? "Log in" : "Create account"}
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          <div className="auth-switch">
            {mode === "login" ? (
              <>
                No account?{" "}
                <button type="button" onClick={() => switchMode("register")}>
                  Create one
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button type="button" onClick={() => switchMode("login")}>
                  Log in
                </button>
              </>
            )}
          </div>

          {mode === "login" && (
            <div className="auth-demo">
              <Info size={14} />
              <span>
                Demo accounts: <code>asha@buyorwait.com</code>,{" "}
                <code>rohan@buyorwait.com</code>,{" "}
                <code>priya@buyorwait.com</code> — password{" "}
                <code>password123</code>
              </span>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default Login;
