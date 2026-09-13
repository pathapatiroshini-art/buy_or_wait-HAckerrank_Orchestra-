import {
  ArrowDownRight,
  Lightbulb,
  PiggyBank
} from "lucide-react";


function SavingsSuggestions({
  suggestions = [],
  target = 10000
}) {

  const defaultSuggestions = [
    {
      category: "Dining out",
      currentAmount: 6000,
      suggestedReduction: 1200,
      newAmount: 4800
    },
    {
      category: "Entertainment",
      currentAmount: 4000,
      suggestedReduction: 800,
      newAmount: 3200
    },
    {
      category: "Shopping",
      currentAmount: 5000,
      suggestedReduction: 1000,
      newAmount: 4000
    }
  ];

  const data =
    suggestions.length > 0
      ? suggestions
      : defaultSuggestions;


  const totalSavings = data.reduce(
    (total, item) =>
      total + item.suggestedReduction,
    0
  );


  return (
    <section className="savings-section">

      <div className="section-heading">

        <div>
          <span className="section-label">
            SAVINGS COACH
          </span>

          <h3>
            Small changes, more spending room
          </h3>
        </div>

        <div className="savings-total">

          <PiggyBank size={18} />

          <span>
            ₹{totalSavings.toLocaleString("en-IN")}
          </span>

        </div>

      </div>


      <div className="savings-card">

        <div className="savings-intro">

          <div className="savings-icon">
            <Lightbulb size={21} />
          </div>

          <div>
            <strong>
              Potential monthly savings
            </strong>

            <p>
              These are flexible expenses you could
              reduce if you want to reach your goal sooner.
            </p>
          </div>

        </div>


        <div className="savings-list">

          {data.map((item, index) => (

            <div
              className="saving-item"
              key={`${item.category}-${index}`}
            >

              <div className="saving-item-info">

                <strong>
                  {item.category}
                </strong>

                <span>
                  Current: ₹
                  {item.currentAmount.toLocaleString("en-IN")}
                </span>

              </div>


              <div className="saving-reduction">

                <ArrowDownRight size={16} />

                <span>
                  Save ₹
                  {item.suggestedReduction.toLocaleString(
                    "en-IN"
                  )}
                </span>

              </div>


              <div className="saving-new-amount">

                <span>
                  New
                </span>

                <strong>
                  ₹{item.newAmount.toLocaleString("en-IN")}
                </strong>

              </div>

            </div>

          ))}

        </div>


        <div className="savings-target">

          <span>
            Goal
          </span>

          <strong>
            ₹{target.toLocaleString("en-IN")}
          </strong>

          <span>
            / month
          </span>

        </div>

      </div>

    </section>
  );
}


export default SavingsSuggestions;