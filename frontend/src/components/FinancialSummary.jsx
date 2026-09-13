import {
  CircleDollarSign,
  ShieldCheck,
  WalletCards
} from "lucide-react";


function FinancialSummary({
  balance = 112500,
  safeToSpend = 42000,
  upcomingPayments = 18500
}) {
  return (
    <section className="overview-grid">

      {/* Available Balance */}
      <div className="money-card">

        <div className="card-top">
          <span>Available balance</span>

          <div className="icon-box">
            <WalletCards size={19} />
          </div>
        </div>

        <h3>
          ₹{balance.toLocaleString("en-IN")}
        </h3>

        <div className="card-footer">
          <span>Current balance</span>

          <span className="positive">
            Healthy
          </span>
        </div>

      </div>


      {/* Safe To Spend */}
      <div className="money-card">

        <div className="card-top">
          <span>Safe to spend</span>

          <div className="icon-box">
            <ShieldCheck size={19} />
          </div>
        </div>

        <h3>
          ₹{safeToSpend.toLocaleString("en-IN")}
        </h3>

        <div className="card-footer">
          <span>After commitments</span>

          <span className="positive">
            Protected
          </span>
        </div>

      </div>


      {/* Upcoming Payments */}
      <div className="money-card">

        <div className="card-top">
          <span>Upcoming payments</span>

          <div className="icon-box">
            <CircleDollarSign size={19} />
          </div>
        </div>

        <h3>
          ₹{upcomingPayments.toLocaleString("en-IN")}
        </h3>

        <div className="card-footer">
          <span>Next 30 days</span>

          <span>
            5 payments
          </span>
        </div>

      </div>

    </section>
  );
}


export default FinancialSummary;