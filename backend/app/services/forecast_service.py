from datetime import date, timedelta


def forecast_balance(
    current_balance: float,
    monthly_income: float,
    monthly_expenses: float,
    days: int = 30
):
    """
    Forecast the user's balance for the given number of days.
    """

    daily_income = monthly_income / 30
    daily_expenses = monthly_expenses / 30

    forecast = []

    balance = current_balance

    for day in range(days + 1):

        forecast_date = date.today() + timedelta(days=day)

        if day > 0:
            balance += daily_income
            balance -= daily_expenses

        forecast.append({
            "date": forecast_date.isoformat(),
            "balance": round(balance, 2)
        })

    return forecast