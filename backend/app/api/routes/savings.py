from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.financial_context import get_recent_transactions
from app.services.savings_service import calculate_savings_suggestions

router = APIRouter(prefix="/savings", tags=["Savings"])


@router.get("/suggest")
def suggest_savings(
    target: float = 10000,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Personalized savings suggestions: pulls the user's own flexible
    expenses from their transaction history rather than a fixed 20%
    rule applied identically to everyone. The trim percentage scales
    with the user's own `flexible_expense_willingness`.
    """
    txns = get_recent_transactions(db, current_user, days=30)

    expenses = [
        {
            "category": t["category"],
            "amount": t["amount"],
            "flexibility": t["flexibility"],
        }
        for t in txns["transactions"]
        if t["transaction_type"] == "expense"
    ]

    return calculate_savings_suggestions(
        expenses,
        target,
        trim_ratio=max(0.05, min(0.5, current_user.flexible_expense_willingness)),
    )
