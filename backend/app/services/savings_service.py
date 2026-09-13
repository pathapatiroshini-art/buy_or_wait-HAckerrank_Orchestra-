def calculate_savings_suggestions(
    expenses: list,
    monthly_savings_target: float,
    trim_ratio: float = 0.20,
):
    """
    Find flexible expenses that can potentially be reduced.

    `trim_ratio` is personalized per user (derived from their
    `flexible_expense_willingness`) instead of a fixed 20% for everyone.
    """

    suggestions = []
    total_possible_savings = 0

    for expense in expenses:

        category = expense["category"]
        amount = expense["amount"]
        flexibility = expense["flexibility"]

        if flexibility == "flexible":

            suggested_reduction = round(amount * trim_ratio, 2)

            suggestions.append({
                "category": category,
                "current_amount": amount,
                "suggested_reduction": suggested_reduction,
                "new_amount": round(amount - suggested_reduction, 2),
            })

            total_possible_savings += suggested_reduction

    total_possible_savings = round(total_possible_savings, 2)

    target_reached = total_possible_savings >= monthly_savings_target

    return {
        "monthly_savings_target": monthly_savings_target,
        "possible_monthly_savings": total_possible_savings,
        "target_reached": target_reached,
        "trim_ratio_used": trim_ratio,
        "suggestions": suggestions,
    }
