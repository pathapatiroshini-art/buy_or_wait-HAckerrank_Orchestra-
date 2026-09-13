"""
Seed demo accounts (with real, hashed login credentials) so the app can
be tried immediately. Deliberately creates two users with the SAME
current balance but different risk tolerance / flexible-expense
willingness / minimum balance, to demonstrate that the agent gives
different, personalized recommendations for the same purchase.

Run from the `backend` directory:
    python scripts/seed_data.py
"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import Base, engine, SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.transaction import Transaction
from app.models.commitment import Commitment

Base.metadata.create_all(bind=engine)

DEMO_PASSWORD = "password123"

USERS = [
    dict(
        name="Asha (Conservative saver)",
        email="asha@buyorwait.com",
        current_balance=112500.0,
        monthly_income=65000.0,
        minimum_balance=45000.0,
        currency="INR",
        risk_tolerance="conservative",
        preferred_payment_method="full",
        flexible_expense_willingness=0.2,
    ),
    dict(
        name="Rohan (Balanced, same balance as Asha)",
        email="rohan@buyorwait.com",
        current_balance=112500.0,
        monthly_income=65000.0,
        minimum_balance=15000.0,
        currency="INR",
        risk_tolerance="flexible",
        preferred_payment_method="partial",
        flexible_expense_willingness=0.8,
    ),
    dict(
        name="Priya (Tight budget)",
        email="priya@buyorwait.com",
        current_balance=38000.0,
        monthly_income=42000.0,
        minimum_balance=10000.0,
        currency="INR",
        risk_tolerance="balanced",
        preferred_payment_method=None,
        flexible_expense_willingness=0.5,
    ),
]

FLEXIBLE_EXPENSES = [
    ("Dining out", 6000, "flexible"),
    ("Entertainment", 4000, "flexible"),
    ("Shopping", 5000, "flexible"),
]

ESSENTIAL_EXPENSES = [
    ("Groceries", 9000, "essential"),
    ("Utilities", 4500, "essential"),
]

COMMITMENTS = [
    ("Rent", 25000, 7, "housing", True),
    ("Credit card EMI", 6500, 15, "loan", True),
    ("Phone/internet subscription", 1500, 20, "subscription", False),
]


def seed():
    db = SessionLocal()
    try:
        for u in USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if existing:
                print(f"Skipping existing user {u['email']}")
                continue

            user = User(
                name=u["name"],
                email=u["email"],
                hashed_password=hash_password(DEMO_PASSWORD),
                current_balance=u["current_balance"],
                monthly_income=u["monthly_income"],
                minimum_balance=u["minimum_balance"],
                currency=u["currency"],
                risk_tolerance=u["risk_tolerance"],
                preferred_payment_method=u["preferred_payment_method"],
                flexible_expense_willingness=u["flexible_expense_willingness"],
            )
            db.add(user)
            db.flush()  # get user.id

            for name, amount, days_out, category, is_essential in COMMITMENTS:
                db.add(
                    Commitment(
                        user_id=user.id,
                        name=name,
                        amount=amount,
                        due_date=date.today() + timedelta(days=days_out),
                        category=category,
                        is_essential=is_essential,
                    )
                )

            for desc, amount, flexibility in FLEXIBLE_EXPENSES + ESSENTIAL_EXPENSES:
                db.add(
                    Transaction(
                        user_id=user.id,
                        description=desc,
                        amount=amount,
                        category=desc,
                        transaction_type="expense",
                        flexibility=flexibility,
                        transaction_date=date.today() - timedelta(days=5),
                    )
                )

            db.add(
                Transaction(
                    user_id=user.id,
                    description="Monthly salary",
                    amount=u["monthly_income"],
                    category="salary",
                    transaction_type="income",
                    flexibility="essential",
                    transaction_date=date.today() - timedelta(days=10),
                )
            )

            print(f"Created demo user: {u['email']} / password: {DEMO_PASSWORD}")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("\nDone. Log in at POST /auth/login with any of the emails above and "
          f"password '{DEMO_PASSWORD}'.")
