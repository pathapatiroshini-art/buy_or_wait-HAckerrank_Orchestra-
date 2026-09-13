from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class PaymentPlanItem(BaseModel):
    date: str
    amount: float
    note: Optional[str] = None


class SpendingChange(BaseModel):
    category: str
    reduction: float
    reason: Optional[str] = None


AffordabilityStatus = Literal[
    "affordable_now",
    "affordable_with_plan",
    "affordable_later",
    "not_affordable",
]

PaymentMethod = Literal[
    "full_payment",
    "partial_payment",
    "installments",
    "wait",
    "do_not_proceed",
]


class RecommendationResponse(BaseModel):
    """
    The structured decision the LLM agent must produce for every
    purchase / spending request. This is the contract the agent's
    final `submit_decision` tool call is validated against.
    """

    purchase_id: Optional[int] = None
    item_name: Optional[str] = None
    requested_amount: Optional[float] = None
    currency: str = "INR"

    amount_safe_to_pay: float

    affordability_status: AffordabilityStatus

    recommended_payment_method: PaymentMethod

    payment_plan: List[PaymentPlanItem] = Field(default_factory=list)

    earliest_date_for_full_payment: Optional[str] = None

    spending_changes_needed: List[SpendingChange] = Field(default_factory=list)

    decision_explanation: str
