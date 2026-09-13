import React, { useEffect, useState } from "react";
import { LogOut } from "lucide-react";

import Navbar from "./components/Navbar";
import PurchaseInput from "./components/PurchaseInput";
import FinancialSummary from "./components/FinancialSummary";
import RecommendationCard from "./components/RecommendationCard";
import PaymentOptions from "./components/PaymentOptions";
import CashFlowChart from "./components/CashFlowChart";
import SavingsSuggestions from "./components/SavingsSuggestions";
import PaymentTimeline from "./components/PaymentTimeline";
import Login from "./pages/Login";

import { useAuth } from "./context/AuthContext";
import {
  analyzePurchase,
  getFinancialSummary,
  getCashFlowForecast,
  getSavingsSuggestions,
} from "./services/api";

function formatChartDate(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  } catch (_) {
    return iso;
  }
}

function App() {
  const { user, loading, logout } = useAuth();

  const [purchase, setPurchase] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");

  const [summary, setSummary] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [savings, setSavings] = useState(null);
  const [decision, setDecision] = useState(null);
  const [selectedPayment, setSelectedPayment] = useState(null);

  useEffect(() => {
    if (!user) return;

    getFinancialSummary().then(setSummary).catch(() => {});
    getCashFlowForecast(60)
      .then((data) =>
        setForecast(
          (data.forecast || []).map((p) => ({
            date: formatChartDate(p.date),
            balance: p.balance,
          }))
        )
      )
      .catch(() => {});
    getSavingsSuggestions(10000).then(setSavings).catch(() => {});
  }, [user]);

  if (loading) {
    return <div className="app" />;
  }

  if (!user) {
    return <Login />;
  }

  const handleAnalyze = async () => {
    if (!purchase.trim()) {
      alert("Please tell us what you want to buy or pay for.");
      return;
    }

    setAnalyzing(true);
    setError("");

    try {
      const result = await analyzePurchase({ raw_text: purchase });
      setDecision(result);
      setSelectedPayment(
        result.recommended_payment_method === "do_not_proceed"
          ? "wait"
          : result.recommended_payment_method
      );

      // Refresh financials since a new purchase record was created.
      getFinancialSummary().then(setSummary).catch(() => {});
    } catch (err) {
      setError(err.message || "Something went wrong analyzing your request.");
    } finally {
      setAnalyzing(false);
    }
  };

  const paymentPlan = (decision?.payment_plan || []).map((p, i) => ({
    date: formatChartDate(p.date),
    amount: p.amount,
    label: i === 0 ? "Initial payment" : `Payment ${i + 1}`,
    status: i === 0 ? "completed" : "upcoming",
  }));

  const spendingChanges = (decision?.spending_changes_needed || []).map((s) => ({
    category: s.category,
    currentAmount: s.reduction,
    suggestedReduction: s.reduction,
    newAmount: 0,
  }));

  return (
    <div className="app">
      <div style={{ display: "flex", justifyContent: "flex-end", padding: "8px 24px" }}>
        <span style={{ marginRight: 12, opacity: 0.7 }}>
          {user.name} ({user.risk_tolerance})
        </span>
        <button onClick={logout} style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <LogOut size={16} /> Log out
        </button>
      </div>

      <Navbar />

      <main className="dashboard">
        <section className="hero">
          <div className="hero-content">
            <div className="eyebrow">
              ✨<span>Smart spending starts here</span>
            </div>

            <h2>
              Should you
              <span> buy it </span>
              or wait?
            </h2>

            <p>
              Tell our AI agent what you want to buy or pay for. It will look
              up your real balance, upcoming commitments, income and
              preferences before making a personalized recommendation.
            </p>
          </div>

          <PurchaseInput
            purchase={purchase}
            setPurchase={setPurchase}
            onAnalyze={handleAnalyze}
          />

          {analyzing && <p style={{ marginTop: 12 }}>The AI agent is reviewing your finances…</p>}
          {error && <p style={{ marginTop: 12, color: "#ff6b6b" }}>{error}</p>}
        </section>

        {summary && (
          <FinancialSummary
            balance={summary.current_balance}
            safeToSpend={summary.safe_to_spend}
            upcomingPayments={summary.upcoming_payments_total}
          />
        )}

        {decision && (
          <>
            <RecommendationCard
              status={decision.affordability_status}
              safeAmount={decision.amount_safe_to_pay}
              purchaseAmount={decision.requested_amount ?? decision.amount_safe_to_pay ?? 0}
              explanation={decision.decision_explanation}
            />

            <PaymentOptions
              recommended={decision.recommended_payment_method}
              selected={selectedPayment}
              onSelect={setSelectedPayment}
            />

            {paymentPlan.length > 0 && <PaymentTimeline payments={paymentPlan} />}
          </>
        )}

        {forecast.length > 0 && summary && (
          <CashFlowChart forecast={forecast} minimumBalance={summary.minimum_balance} />
        )}

        {savings && (
          <SavingsSuggestions
            suggestions={
              spendingChanges.length > 0
                ? spendingChanges
                : (savings.suggestions || []).map((s) => ({
                    category: s.category,
                    currentAmount: s.current_amount,
                    suggestedReduction: s.suggested_reduction,
                    newAmount: s.new_amount,
                  }))
            }
            target={savings.monthly_savings_target}
          />
        )}
      </main>
    </div>
  );
}

export default App;
