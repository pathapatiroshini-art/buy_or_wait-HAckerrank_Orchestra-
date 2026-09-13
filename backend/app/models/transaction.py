from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.sql import func

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    category = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)  # income | expense

    # Whether this recurring expense is essential (rent, groceries, loan
    # EMI) or flexible (dining out, entertainment, shopping). The agent
    # uses this to decide which "spending_changes_needed" it can safely
    # suggest cutting.
    flexibility = Column(String, default="essential")  # essential | flexible

    transaction_date = Column(Date, server_default=func.current_date())
