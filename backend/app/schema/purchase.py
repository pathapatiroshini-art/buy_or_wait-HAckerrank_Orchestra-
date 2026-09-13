from pydantic import BaseModel
from typing import Optional


class PurchaseCreate(BaseModel):
    """
    Structured purchase request. Every field except `item_name`/`amount`
    is optional because the agent can also work purely off `raw_text`
    (a free-form message, possibly extracted from an uploaded image or
    chat message) using its extraction tool.
    """
    item_name: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    deadline: Optional[str] = None
    payment_preference: Optional[str] = None
    raw_text: Optional[str] = None


class PurchaseResponse(BaseModel):
    id: int
    item_name: str
    amount: float
    currency: str
    deadline: Optional[str] = None
    payment_preference: Optional[str] = None
    status: str
