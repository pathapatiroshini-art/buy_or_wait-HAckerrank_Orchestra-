import {
  Check,
  CreditCard,
  HandCoins,
  PauseCircle,
  Wallet
} from "lucide-react";


const paymentOptions = [
  {
    id: "full_payment",
    title: "Pay in full",
    description: "Pay the entire amount today.",
    icon: Wallet
  },
  {
    id: "partial_payment",
    title: "Pay partially",
    description: "Pay what is safe today and the rest later.",
    icon: HandCoins
  },
  {
    id: "installments",
    title: "Use installments",
    description: "Spread the cost across multiple payments.",
    icon: CreditCard
  },
  {
    id: "wait",
    title: "Wait",
    description: "Delay the purchase until your finances improve.",
    icon: PauseCircle
  }
];


function PaymentOptions({
  recommended = "partial_payment",
  selected,
  onSelect
}) {
  const activeOption = selected || recommended;

  return (
    <section className="payment-options-section">

      <div className="section-heading">
        <div>
          <span className="section-label">
            PAYMENT STRATEGY
          </span>

          <h3>
            Choose the safest way to proceed
          </h3>
        </div>
      </div>


      <div className="payment-options-grid">

        {paymentOptions.map((option) => {

          const Icon = option.icon;

          const isRecommended =
            option.id === recommended;

          const isSelected =
            option.id === activeOption;

          return (
            <button
              key={option.id}
              className={`payment-option ${
                isSelected ? "selected" : ""
              }`}
              onClick={() => onSelect?.(option.id)}
            >

              <div className="payment-option-icon">
                <Icon size={21} />
              </div>


              <div className="payment-option-content">

                <div className="payment-option-title">

                  <strong>
                    {option.title}
                  </strong>

                  {isRecommended && (
                    <span className="recommended-badge">
                      Recommended
                    </span>
                  )}

                </div>

                <p>
                  {option.description}
                </p>

              </div>


              <div className="payment-option-check">
                {isSelected && (
                  <Check size={17} />
                )}
              </div>

            </button>
          );
        })}

      </div>

    </section>
  );
}


export default PaymentOptions;