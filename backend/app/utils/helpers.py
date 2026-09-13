from datetime import date, datetime


def round_money(amount: float):
    """
    Round a monetary value to two decimal places.
    """

    return round(amount, 2)


def is_positive_amount(amount: float):
    """
    Check whether an amount is greater than zero.
    """

    return amount > 0


def parse_date(date_text: str):
    """
    Convert a YYYY-MM-DD string into a date object.
    """

    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return None


def days_until(target_date: date):
    """
    Calculate the number of days from today
    until the target date.
    """

    return (target_date - date.today()).days


def calculate_remaining_balance(
    current_balance: float,
    payment: float
):
    """
    Calculate the balance remaining after a payment.
    """

    return round_money(
        current_balance - payment
    )