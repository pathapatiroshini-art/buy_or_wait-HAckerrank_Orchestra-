import {
  TrendingDown,
  TrendingUp
} from "lucide-react";


function CashFlowChart({
  forecast = [],
  minimumBalance = 30000
}) {

  const defaultForecast = [
    { date: "Today", balance: 112500 },
    { date: "Sep 17", balance: 101000 },
    { date: "Sep 22", balance: 94000 },
    { date: "Sep 27", balance: 82000 },
    { date: "Oct 02", balance: 91000 },
    { date: "Oct 07", balance: 78000 }
  ];

  const data =
    forecast.length > 0
      ? forecast
      : defaultForecast;


  const balances = data.map(
    (item) => item.balance
  );

  const highestBalance = Math.max(...balances);
  const lowestBalance = Math.min(...balances);

  const trend =
    balances[balances.length - 1] >= balances[0]
      ? "up"
      : "down";


  return (
    <section className="cash-flow-section">

      <div className="section-heading">

        <div>
          <span className="section-label">
            CASH FLOW
          </span>

          <h3>
            Your financial runway
          </h3>
        </div>


        <div className={`trend-indicator ${trend}`}>

          {trend === "up" ? (
            <TrendingUp size={17} />
          ) : (
            <TrendingDown size={17} />
          )}

          <span>
            {trend === "up"
              ? "Balance increasing"
              : "Balance decreasing"}
          </span>

        </div>

      </div>


      <div className="cash-flow-card">

        <div className="chart-summary">

          <div>
            <span>Projected balance</span>

            <strong>
              ₹{lowestBalance.toLocaleString("en-IN")}
            </strong>

            <small>
              Lowest point in forecast
            </small>
          </div>


          <div>
            <span>Safety floor</span>

            <strong>
              ₹{minimumBalance.toLocaleString("en-IN")}
            </strong>

            <small>
              Preferred minimum balance
            </small>
          </div>

        </div>


        <div className="chart-area">

          <div className="safety-line">
            <span>
              Safety floor ₹
              {minimumBalance.toLocaleString("en-IN")}
            </span>
          </div>


          <div className="chart-bars">

            {data.map((item, index) => {

              const percentage =
                highestBalance > 0
                  ? (item.balance / highestBalance) * 100
                  : 0;

              const isBelowSafety =
                item.balance < minimumBalance;

              return (
                <div
                  className="chart-column"
                  key={`${item.date}-${index}`}
                >

                  <div className="bar-wrapper">

                    <div
                      className={`chart-bar ${
                        isBelowSafety
                          ? "below-safety"
                          : ""
                      }`}
                      style={{
                        height: `${Math.max(
                          percentage,
                          8
                        )}%`
                      }}
                      title={`₹${item.balance.toLocaleString(
                        "en-IN"
                      )}`}
                    />

                  </div>

                  <span>
                    {item.date}
                  </span>

                </div>
              );
            })}

          </div>

        </div>

      </div>

    </section>
  );
}


export default CashFlowChart;