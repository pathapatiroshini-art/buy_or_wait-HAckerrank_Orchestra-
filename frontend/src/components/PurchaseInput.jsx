import {
  ArrowRight,
  CircleDollarSign
} from "lucide-react";


function PurchaseInput({
  purchase,
  setPurchase,
  onAnalyze
}) {
  return (
    <div className="purchase-box">

      <div className="input-header">
        <CircleDollarSign size={20} />

        <span>
          What are you planning to buy?
        </span>
      </div>


      <div className="purchase-input">

        <input
          type="text"
          value={purchase}
          onChange={(event) =>
            setPurchase(event.target.value)
          }
          placeholder="e.g. MacBook for ₹75,000"
        />


        <button onClick={onAnalyze}>
          Analyze

          <ArrowRight size={18} />
        </button>

      </div>


      <div className="input-hint">
        You can type naturally — our AI will understand it.
      </div>

    </div>
  );
}


export default PurchaseInput;