from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, JSON, DateTime, Text
from sqlalchemy.sql import func

from app.core.database import Base


class Purchase(Base):
    """
    A purchase / spending request analyzed by the LLM agent.

    `raw_request_text` preserves whatever free-form message the user typed
    ("Can I afford a MacBook for 75,000?", an image-extracted caption,
    etc.) and `agent_decision` stores the full structured recommendation
    the agent produced, so the analysis is auditable and personalized
    history can be reused in future requests for the same user.
    """

    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    item_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")

    deadline = Column(Date, nullable=True)
    payment_preference = Column(String, nullable=True)

    raw_request_text = Column(Text, nullable=True)

    status = Column(String, default="pending")  # pending | approved | completed | cancelled

    # Full structured output produced by the agent (amount_safe_to_pay,
    # affordability_status, recommended_payment_method, payment_plan,
    # earliest_date_for_full_payment, spending_changes_needed,
    # decision_explanation) - stored verbatim for transparency/history.
    agent_decision = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
