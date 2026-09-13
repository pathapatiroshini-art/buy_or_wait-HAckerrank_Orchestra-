import { useState } from "react";

import Navbar from "../components/Navbar";
import PurchaseInput from "../components/PurchaseInput";
import FinancialSummary from "../components/FinancialSummary";
import RecommendationCard from "../components/RecommendationCard";
import PaymentOptions from "../components/PaymentOptions";
import CashFlowChart from "../components/CashFlowChart";
import SavingsSuggestions from "../components/SavingsSuggestions";
import PaymentTimeline from "../components/PaymentTimeline";


function Dashboard() {

  const [purchase, setPurchase] = useState("");

  const [selectedPayment, setSelectedPayment] =
    useState("partial_payment");


  const handleAnalyze = () => {

    if (!purchase.trim()) {
      alert("Please enter something you want to buy.");
      return;
    }

    console.log(
      "Purchase request:",
      purchase
    );
  };


  return (
    <div className="app">

      <Navbar />


      <main className="dashboard">

        {/* Hero */}
        <section className="hero">

          <div className="hero-content">

            <div className="eyebrow">
              ✨
              <span>
                Smart spending starts here
              </span>
            </div>


            <h2>
              Should you
              <span> buy it </span>
              or wait?
            </h2>


            <p>
              Tell us what you want to buy. We'll look at
              your balance, upcoming expenses, income and
              financial commitments before making a
              recommendation.
            </p>

          </div>


          <PurchaseInput
            purchase={purchase}
            setPurchase={setPurchase}
            onAnalyze={handleAnalyze}
          />

        </section>


        {/* Financial Overview */}
        <FinancialSummary
          balance={112500}
          safeToSpend={42000}
          upcomingPayments={18500}
        />


        {/* AI Recommendation */}
        <RecommendationCard
          status="affordable_with_plan"
          safeAmount={42000}
          purchaseAmount={75000}
          explanation="This purchase can fit your finances, but paying the full amount today isn't ideal."
        />


        {/* Payment Options */}
        <PaymentOptions
          recommended="partial_payment"
          selected={selectedPayment}
          onSelect={setSelectedPayment}
        />


        {/* Cash Flow */}
        <CashFlowChart
          minimumBalance={30000}
        />


        {/* Payment Timeline */}
        <PaymentTimeline />


        {/* Savings Coach */}
        <SavingsSuggestions
          target={10000}
        />

      </main>

    </div>
  );
}


export default Dashboard;