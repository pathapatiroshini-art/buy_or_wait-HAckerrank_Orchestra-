from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """
    A user account. Holds both login credentials and the personalization
    signals the agent uses to make different recommendations for two
    people who otherwise have the same balance:

    - risk_tolerance: how conservative the user wants to be
    - flexible_expense_willingness: how open the user is to trimming
      flexible spending (dining out, entertainment, shopping...) to
      speed up a purchase
    - preferred_payment_method: a standing preference the agent should
      respect unless it is unsafe
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)

    # Login credentials
    hashed_password = Column(String, nullable=False)

    # Core financial snapshot
    current_balance = Column(Float, default=0.0)
    monthly_income = Column(Float, default=0.0)
    minimum_balance = Column(Float, default=0.0)
    currency = Column(String, default="INR")

    # Personalization signals
    risk_tolerance = Column(String, default="balanced")  # conservative | balanced | flexible
    preferred_payment_method = Column(String, nullable=True)  # full | partial | installments | wait
    flexible_expense_willingness = Column(Float, default=0.5)  # 0.0 (unwilling) - 1.0 (very willing)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
