"""
Run the agentic AI decision engine over the provided `requests.csv`
dataset and write out the recommendation for each row.

This is the quickest way to see the LLM agent reasoning over the exact
data you supplied (amount, deadline, whether partial payment is
allowed, and the free-form request text) instead of the old static
buttons. Since the dataset doesn't include a financial profile per
`user_id`, each row is evaluated against one of the three seeded demo
users (round-robin) so you can see how the very same request gets a
different recommendation depending on who is asking - the
personalization requirement in practice.

Usage (from the `backend` directory, after running seed_data.py and
setting GROQ_API_KEY in .env):

    python scripts/evaluate_dataset.py /path/to/requests.csv results.csv
"""
import csv
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal
from app.models.user import User
from app.services.ai_service import run_affordability_agent

DEMO_EMAILS = ["asha@buyorwait.com", "rohan@buyorwait.com", "priya@buyorwait.com"]


def payment_preference_from_flag(flag: str) -> str:
    return "partial" if str(flag).strip().lower() in ("true", "1", "yes") else "full"


def main(input_path: str, output_path: str):
    db = SessionLocal()
    demo_users = [
        db.query(User).filter(User.email == e).first() for e in DEMO_EMAILS
    ]
    demo_users = [u for u in demo_users if u is not None]

    if not demo_users:
        print("No demo users found - run `python scripts/seed_data.py` first.")
        return

    with open(input_path, newline="", encoding="utf-8") as f_in, \
         open(output_path, "w", newline="", encoding="utf-8") as f_out:

        reader = csv.DictReader(f_in)
        writer = csv.writer(f_out)
        writer.writerow([
            "request_id", "evaluated_as_user", "amount_safe_to_pay",
            "affordability_status", "recommended_payment_method",
            "earliest_date_for_full_payment", "decision_explanation",
        ])

        for i, row in enumerate(reader):
            user = demo_users[i % len(demo_users)]

            purchase_input = {
                "item_name": row.get("request_type"),
                "amount": float(row["requested_amount"]) if row.get("requested_amount") else None,
                "deadline": row.get("desired_completion_date") or None,
                "payment_preference": payment_preference_from_flag(row.get("allows_partial_payment", "")),
                "raw_text": row.get("request_text"),
            }

            decision = run_affordability_agent(db, user, purchase_input)

            writer.writerow([
                row.get("request_id"),
                user.email,
                decision.get("amount_safe_to_pay"),
                decision.get("affordability_status"),
                decision.get("recommended_payment_method"),
                decision.get("earliest_date_for_full_payment"),
                decision.get("decision_explanation"),
            ])

            print(f"[{row.get('request_id')}] as {user.email} -> "
                  f"{decision.get('affordability_status')} / "
                  f"{decision.get('recommended_payment_method')}")

    db.close()
    print(f"\nWrote results to {output_path}")


if __name__ == "__main__":
    input_csv = sys.argv[1] if len(sys.argv) > 1 else "requests.csv"
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "requests_evaluated.csv"
    main(input_csv, output_csv)
