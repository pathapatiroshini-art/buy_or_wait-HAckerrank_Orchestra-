import re


def extract_amount(text: str):
    """
    Extract the first money amount found in a text.
    """

    patterns = [
        r"₹\s?([0-9,]+(?:\.[0-9]+)?)",
        r"rs\.?\s?([0-9,]+(?:\.[0-9]+)?)",
        r"([0-9,]+(?:\.[0-9]+)?)\s?(?:rupees|INR)"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            amount = match.group(1)

            amount = amount.replace(",", "")

            return float(amount)

    return None


def extract_purchase_item(text: str):
    """
    Try to identify the item mentioned in a purchase request.
    """

    keywords = [
        "laptop",
        "phone",
        "mobile",
        "tablet",
        "headphones",
        "watch",
        "camera",
        "monitor"
    ]

    text_lower = text.lower()

    for keyword in keywords:

        if keyword in text_lower:
            return keyword

    return None


def extract_purchase_information(text: str):
    """
    Extract basic purchase information from user text.
    """

    amount = extract_amount(text)
    item = extract_purchase_item(text)

    return {
        "item_name": item,
        "amount": amount,
        "original_text": text
    }