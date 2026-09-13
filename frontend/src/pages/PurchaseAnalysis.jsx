import {
  ArrowLeft,
  Brain,
  CheckCircle2
} from "lucide-react";

import RecommendationCard from "../components/RecommendationCard";
import PaymentOptions from "../components/PaymentOptions";
import CashFlowChart from "../components/CashFlowChart";
import PaymentTimeline from "../components/PaymentTimeline";
import SavingsSuggestions from "../components/SavingsSuggestions";


function PurchaseAnalysis({
  purchase = "MacBook for ₹75,000",
  onBack
}) {

  return (
    <div className="app">

      {/* Analysis Header */}
      <header className="analysis-header">

        <button
          className="back-button"
          onClick={onBack}
        >
          <ArrowLeft size={18} />

          <span>
            Back to dashboard
          </span>
        </button>


        <div className="analysis-brand">

          <div className="brand-icon">
            <Brain size={20} />
          </div>

          <div>
            <strong>
              Purchase Analysis
            </strong>

            <span>
              AI financial assessment
            </span>
          </div>

        </div>


        <div className="analysis-status">

          <CheckCircle2 size={17} />

          <span>
            Analysis complete
          </span>

        </div>

      </header>


      <main className="analysis-page">

        {/* Purchase Summary */}
        <section className="purchase-summary">

          <div>
            <span className="section-label">
              PURCHASE REQUEST
            </span>

            <h1>
              {purchase}
            </h1>

            <p>
              We analyzed your current balance,
              commitments, projected cash flow and
              available payment strategies.
            </p>
          </div>


          <div className="analysis-summary-card">

            <span>
              Requested amount
            </span>

            <strong>
              ₹75,000
            </strong>

            <small>
              Financial safety check completed
            </small>

          </div>

        </section>


        {/* Recommendation */}
        <RecommendationCard
          status="affordable_with_plan"
          safeAmount={42000}
          purchaseAmount={75000}
          explanation="The purchase is possible, but paying the full amount today would reduce your available financial buffer too much."
        />


        {/* Payment Strategies */}
        <PaymentOptions
          recommended="partial_payment"
        />


        {/* Forecast */}
        <CashFlowChart
          minimumBalance={30000}
        />


        {/* Timeline */}
        <PaymentTimeline />


        {/* Savings */}
        <SavingsSuggestions
          target={10000}
        />

      </main>

    </div>
  );
}


export default PurchaseAnalysis;