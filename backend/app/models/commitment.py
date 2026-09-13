from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from app.core.database import Base


class Commitment(Base):
    """A confirmed upcoming payment: rent, EMI, subscriptions, bills..."""

    __tablename__ = "commitments"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(Date, nullable=False)

    category = Column(String, nullable=False)
    is_essential = Column(Boolean, default=True)

    status = Column(String, default="pending")  # pending | paid | cancelled
