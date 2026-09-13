"""
Data-access functions used as *tools* by the LLM agent
(app/services/ai_agent.py). Each function pulls real data for one user
out of the database and returns plain JSON-serializable dicts - the
agent decides which of these it needs and in what order to call them.
"""
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.transaction import Transaction
from app.models.commitment import Commitment
from app.models.purchase import Purchase
from app.services.forecast_service import forecast_balance


def get_financial_snapshot(db: Session, user: User) -> dict:
    return {
        "current_balance": user.current_balance,
        "monthly_income": user.monthly_income,
        "minimum_balance": user.minimum_balance,
        "currency": user.currency,
        "risk_tolerance": user.risk_tolerance,
        "preferred_payment_method": user.preferred_payment_method,
        "flexible_expense_willingness": user.flexible_expense_willingness,
    }


def get_upcoming_commitments(db: Session, user: User, days: int = 60) -> dict:
    horizon = date.today() + timedelta(days=days)

    commitments = (
        db.query(Commitment)
        .filter(
            Commitment.user_id == user.id,
            Commitment.status == "pending",
            Commitment.due_date <= horizon,
        )
        .order_by(Commitment.due_date.asc())
        .all()
    )

    items = [
        {
            "name": c.name,
            "amount": c.amount,
            "due_date": c.due_date.isoformat(),
            "category": c.category,
            "is_essential": c.is_essential,
        }
        for c in commitments
    ]

    return {
        "horizon_days": days,
        "total_upcoming": round(sum(c["amount"] for c in items), 2),
        "commitments": items,
    }


def get_recent_transactions(db: Session, user: User, days: int = 90) -> dict:
    since = date.today() - timedelta(days=days)

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user.id,
            Transaction.transaction_date >= since,
        )
        .order_by(Transaction.transaction_date.desc())
        .all()
    )

    items = [
        {
            "description": t.description,
            "amount": t.amount,
            "category": t.category,
            "transaction_type": t.transaction_type,
            "flexibility": t.flexibility,
            "date": t.transaction_date.isoformat() if t.transaction_date else None,
        }
        for t in transactions
    ]

    flexible_monthly_total = round(
        sum(
            t["amount"]
            for t in items
            if t["transaction_type"] == "expense" and t["flexibility"] == "flexible"
        ),
        2,
    )

    essential_monthly_total = round(
        sum(
            t["amount"]
            for t in items
            if t["transaction_type"] == "expense" and t["flexibility"] == "essential"
        ),
        2,
    )

    return {
        "window_days": days,
        "transactions": items,
        "flexible_expense_total": flexible_monthly_total,
        "essential_expense_total": essential_monthly_total,
    }


def get_purchase_history(db: Session, user: User, limit: int = 10) -> dict:
    purchases = (
        db.query(Purchase)
        .filter(Purchase.user_id == user.id)
        .order_by(Purchase.created_at.desc())
        .limit(limit)
        .all()
    )

    items = [
        {
            "item_name": p.item_name,
            "amount": p.amount,
            "currency": p.currency,
            "status": p.status,
            "decision": p.agent_decision,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in purchases
    ]

    return {"past_requests": items}


def get_cash_flow_forecast(db: Session, user: User, days: int = 60) -> dict:
    txn_data = get_recent_transactions(db, user, days=30)
    monthly_essential_expenses = txn_data["essential_expense_total"]

    forecast = forecast_balance(
        current_balance=user.current_balance,
        monthly_income=user.monthly_income,
        monthly_expenses=monthly_essential_expenses,
        days=days,
    )

    return {"days": days, "forecast": forecast}
