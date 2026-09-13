def validate_payment_plan(
    current_balance: float,
    minimum_balance: float,
    upcoming_expenses: float,
    amount_today: float
):
    """
    Check whether a payment is financially safe.
    """

    remaining_balance = current_balance - amount_today

    # Check minimum balance
    if remaining_balance < minimum_balance:
        return {
            "safe": False,
            "reason": "Payment would reduce the balance below the minimum balance.",
            "remaining_balance": remaining_balance
        }

    # Check upcoming expenses
    balance_after_expenses = (
        remaining_balance - upcoming_expenses
    )

    if balance_after_expenses < minimum_balance:
        return {
            "safe": False,
            "reason": "Payment would leave insufficient money for upcoming expenses.",
            "remaining_balance": remaining_balance
        }

    return {
        "safe": True,
        "reason": "Payment satisfies the current safety conditions.",
        "remaining_balance": remaining_balance
    }