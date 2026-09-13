import {
  CalendarDays,
  CheckCircle2,
  CircleDollarSign
} from "lucide-react";


function PaymentTimeline({
  payments = []
}) {

  const defaultPayments = [
    {
      date: "Today",
      amount: 42000,
      label: "Initial payment",
      status: "completed"
    },
    {
      date: "Oct 07",
      amount: 16500,
      label: "Second payment",
      status: "upcoming"
    },
    {
      date: "Nov 07",
      amount: 16500,
      label: "Final payment",
      status: "upcoming"
    }
  ];


  const data =
    payments.length > 0
      ? payments
      : defaultPayments;


  return (
    <section className="timeline-section">

      <div className="section-heading">

        <div>
          <span className="section-label">
            PAYMENT PLAN
          </span>

          <h3>
            Your payment timeline
          </h3>
        </div>

      </div>


      <div className="timeline-card">

        <div className="timeline-header">

          <div>
            <span>
              Purchase payment schedule
            </span>

            <strong>
              {data.length} payments
            </strong>
          </div>

          <CalendarDays size={22} />

        </div>


        <div className="timeline">

          {data.map((payment, index) => {

            const isCompleted =
              payment.status === "completed";

            const isLast =
              index === data.length - 1;

            return (
              <div
                className="timeline-item"
                key={`${payment.date}-${index}`}
              >

                <div className="timeline-marker">

                  {isCompleted ? (
                    <CheckCircle2 size={19} />
                  ) : (
                    <CircleDollarSign size={19} />
                  )}

                </div>


                <div className="timeline-content">

                  <div className="timeline-date">
                    {payment.date}
                  </div>

                  <strong>
                    {payment.label}
                  </strong>

                  <span>
                    ₹{payment.amount.toLocaleString("en-IN")}
                  </span>

                </div>


                {!isLast && (
                  <div className="timeline-line" />
                )}

              </div>
            );
          })}

        </div>

      </div>

    </section>
  );
}


export default PaymentTimeline;