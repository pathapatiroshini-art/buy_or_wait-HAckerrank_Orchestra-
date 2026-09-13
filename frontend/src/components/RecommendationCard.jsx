import {
  CheckCircle2,
  Clock3,
  ShieldAlert,
  WalletCards
} from "lucide-react";


const statusConfig = {
  affordable_now: {
    label: "SAFE TO BUY",
    icon: CheckCircle2,
    className: "safe",
    message: "You can afford this purchase without putting your financial safety at risk."
  },

  affordable_with_plan: {
    label: "SAFE WITH A PLAN",
    icon: WalletCards,
    className: "plan",
    message: "This purchase can fit your finances, but paying the full amount today isn't ideal."
  },

  affordable_later: {
    label: "BETTER TO WAIT",
    icon: Clock3,
    className: "wait",
    message: "Waiting for upcoming income will make this purchase safer."
  },

  not_affordable: {
    label: "NOT AFFORDABLE",
    icon: ShieldAlert,
    className: "danger",
    message: "This purchase would put your financial safety at risk right now."
  }
};


function RecommendationCard({
  status = "affordable_with_plan",
  safeAmount = 42000,
  purchaseAmount = 75000,
  explanation
}) {

  const config =
    statusConfig[status] ||
    statusConfig.affordable_with_plan;

  const StatusIcon = config.icon;

  return (
    <section className="recommendation-section">

      <div className="section-heading">

        <div>
          <span className="section-label">
            AI DECISION
          </span>

          <h3>
            Your financial recommendation
          </h3>
        </div>

      </div>


      <div
        className={`recommendation-card ${config.className}`}
      >

        {/* Decision */}
        <div className="recommendation-status">

          <div className="status-dot">
            <StatusIcon size={18} />
          </div>

          <div>

            <span>
              {config.label}
            </span>

            <p>
              {explanation || config.message}
            </p>

          </div>

        </div>


        {/* Amount */}
        <div className="recommendation-number">

          <span>
            Safe amount today
          </span>

          <strong>
            ₹{safeAmount.toLocaleString("en-IN")}
          </strong>

          <small>
            Purchase price: ₹
            {purchaseAmount.toLocaleString("en-IN")}
          </small>

        </div>

      </div>

    </section>
  );
}


export default RecommendationCard;