from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.purchase import Purchase
from app.schema.purchase import PurchaseCreate
from app.schema.recommendation import RecommendationResponse
from app.services.ai_service import run_affordability_agent
from app.utils.helpers import parse_date

router = APIRouter(prefix="/purchase", tags=["Purchase"])


@router.post("/analyze", response_model=RecommendationResponse)
def analyze_purchase(
    purchase: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Runs the agentic AI decision engine for the logged-in user's purchase
    request and persists both the request and the full decision.
    """

    purchase_input = purchase.model_dump()

    decision = run_affordability_agent(db, current_user, purchase_input)

    deadline_date = parse_date(purchase.deadline) if purchase.deadline else None

    record = Purchase(
        user_id=current_user.id,
        item_name=decision.get("item_name") or purchase.item_name or "Unnamed request",
        amount=purchase.amount or decision.get("amount_safe_to_pay") or 0,
       currency=decision.get("currency") or current_user.currency or "INR",
        deadline=deadline_date,
        payment_preference=purchase.payment_preference,
        raw_request_text=purchase.raw_text,
        status="analyzed",
        agent_decision=decision,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    decision["purchase_id"] = record.id
    decision["requested_amount"] = purchase.amount or record.amount
    decision["currency"] = decision.get("currency") or current_user.currency or "INR"

    return decision


@router.get("/history")
def purchase_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = (
        db.query(Purchase)
        .filter(Purchase.user_id == current_user.id)
        .order_by(Purchase.created_at.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "item_name": r.item_name,
            "amount": r.amount,
            "currency": r.currency,
            "status": r.status,
            "decision": r.agent_decision,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]
