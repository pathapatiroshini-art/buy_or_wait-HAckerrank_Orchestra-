from pydantic import BaseModel
from typing import List


class TransactionCreate(BaseModel):
    description: str
    amount: float
    category: str
    transaction_type: str


class FinancialDataCreate(BaseModel):
    current_balance: float
    monthly_income: float
    minimum_balance: float
    transactions: List[TransactionCreate] = []


class FinancialSummary(BaseModel):
    current_balance: float
    monthly_income: float
    minimum_balance: float
    total_expenses: float
    remaining_balance: float