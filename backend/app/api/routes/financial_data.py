from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.financial_context import (
    get_financial_snapshot,
    get_recent_transactions,
    get_upcoming_commitments,
    get_cash_flow_forecast,
)

router = APIRouter(prefix="/financial-data", tags=["Financial Data"])


@router.get("/summary")
def financial_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    snapshot = get_financial_snapshot(db, current_user)
    upcoming = get_upcoming_commitments(db, current_user, days=30)
    txns = get_recent_transactions(db, current_user, days=30)

    safe_to_spend = max(
        0.0,
        round(
            current_user.current_balance
            - current_user.minimum_balance
            - upcoming["total_upcoming"],
            2,
        ),
    )

    return {
        **snapshot,
        "safe_to_spend": safe_to_spend,
        "upcoming_payments_total": upcoming["total_upcoming"],
        "upcoming_payments_count": len(upcoming["commitments"]),
        "flexible_expense_total": txns["flexible_expense_total"],
        "essential_expense_total": txns["essential_expense_total"],
    }


@router.get("/forecast")
def cash_flow_forecast(
    days: int = 60,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_cash_flow_forecast(db, current_user, days=days)


@router.get("/commitments")
def upcoming_commitments(
    days: int = 60,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_upcoming_commitments(db, current_user, days=days)
