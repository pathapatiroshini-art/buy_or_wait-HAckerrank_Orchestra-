from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)

    current_balance: float = 0.0
    monthly_income: float = 0.0
    minimum_balance: float = 0.0
    currency: str = "INR"

    # Personalization signals collected at signup
    risk_tolerance: str = "balanced"  # conservative | balanced | flexible
    preferred_payment_method: Optional[str] = None
    flexible_expense_willingness: float = 0.5


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    current_balance: float
    monthly_income: float
    minimum_balance: float
    currency: str
    risk_tolerance: str
    preferred_payment_method: Optional[str] = None
    flexible_expense_willingness: float

    class Config:
        from_attributes = True
