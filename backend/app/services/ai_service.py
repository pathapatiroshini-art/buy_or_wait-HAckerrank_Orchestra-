"""
=====================================================================
Agentic AI decision engine for "Buy or Wait?"
=====================================================================

Groq-powered agentic decision engine.

The LLM first uses financial tools to gather the user's financial
information.

After gathering the required information, a separate final LLM call
produces a structured JSON decision WITHOUT tool calling.

The deterministic safety validator always runs after the LLM decision.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from groq import Groq

from app.core.config import settings
from app.models.user import User
from app.services import financial_context as fc
from app.services.extraction_service import extract_purchase_information
from app.services.safety_validator import validate_payment_plan


# ---------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------

def _tool_definitions() -> List[dict]:
    """
    Financial information tools.

    IMPORTANT:
    submit_decision is intentionally NOT a tool.

    The final decision is generated using Groq JSON mode instead.
    This prevents malformed tool-call JSON from crashing the request.
    """

    return [
        {
            "type": "function",
            "function": {
                "name": "get_financial_snapshot",
                "description": (
                    "Get the user's current balance, monthly income, "
                    "preferred minimum balance, currency, risk tolerance, "
                    "and standing payment preference."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_upcoming_commitments",
                "description": (
                    "List confirmed upcoming payments such as rent, EMIs, "
                    "subscriptions and bills due within a number of days."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": (
                                "Look-ahead window in days. Default is 60."
                            ),
                        }
                    },
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_recent_transactions",
                "description": (
                    "List recent income and expense transactions tagged "
                    "as essential or flexible. Use this to determine "
                    "which flexible expenses could potentially be reduced."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": (
                                "Look-back window in days. Default is 90."
                            ),
                        }
                    },
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_purchase_history",
                "description": (
                    "List the user's previous purchase requests and "
                    "decisions to help maintain consistency."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_cash_flow_forecast",
                "description": (
                    "Get a day-by-day projected balance for the next N days "
                    "based on confirmed income and essential expenses."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": (
                                "Forecast horizon in days. Default is 60."
                            ),
                        }
                    },
                    "additionalProperties": False,
                },
            },
        },
    ]


# ---------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------

def _dispatch_tool(
    db: Session,
    user: User,
    name: str,
    tool_input: dict,
) -> dict:

    if name == "get_financial_snapshot":
        return fc.get_financial_snapshot(db, user)

    if name == "get_upcoming_commitments":
        return fc.get_upcoming_commitments(
            db,
            user,
            days=tool_input.get("days", 60),
        )

    if name == "get_recent_transactions":
        return fc.get_recent_transactions(
            db,
            user,
            days=tool_input.get("days", 90),
        )

    if name == "get_purchase_history":
        return fc.get_purchase_history(db, user)

    if name == "get_cash_flow_forecast":
        return fc.get_cash_flow_forecast(
            db,
            user,
            days=tool_input.get("days", 60),
        )

    return {
        "error": f"Unknown tool '{name}'"
    }


# ---------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------

SYSTEM_PROMPT = """
You are the affordability agent inside "Buy or Wait?", a personal
finance assistant.

A user has asked whether they can afford a purchase or payment.

Your job is to analyze the request using the user's actual financial
information and recommend one of:

- pay in full
- pay partially
- use installments
- wait
- do not proceed

You do not know the user's finances until you use the financial tools.

You MUST gather at least:

1. get_financial_snapshot
2. get_upcoming_commitments

Use these tools when relevant:

- get_recent_transactions
- get_cash_flow_forecast
- get_purchase_history

A recommendation is SAFE only if:

- every payment in the plan can actually be made on its date,
- the full requested amount is completed by the stated deadline,
- essential expenses remain covered,
- confirmed upcoming commitments remain covered,
- the user's balance never falls below their preferred minimum balance.

Personalize the recommendation using:

- risk tolerance
- flexible expense willingness
- preferred payment method
- current balance
- income
- upcoming commitments
- transaction history
- purchase history
- cash flow forecast

Do NOT assume installments are always better.

When comparing payment methods, consider:

- immediate cash impact
- future payment burden
- fees or interest if available
- user's preferences
- upcoming commitments
- minimum balance requirement

A conservative user with a high minimum balance and low willingness
to reduce flexible spending should receive a more cautious
recommendation than a flexible user with the same balance.

IMPORTANT:

Your final response MUST be valid JSON.

Do not use markdown.

Do not use code fences.

Do not add explanations outside the JSON.

Keep decision_explanation to at most 2 short sentences.

Keep payment_plan concise.

Keep spending_changes_needed to at most 3 items.
"""


# ---------------------------------------------------------------------
# User message
# ---------------------------------------------------------------------

def _build_user_message(
    purchase: dict,
    today: date,
) -> str:

    lines = [
        f"Today's date is {today.isoformat()}.",
        "",
        "Purchase / spending request:",
    ]

    if purchase.get("raw_text"):
        lines.append(
            f'- Message from user: "{purchase["raw_text"]}"'
        )

    if purchase.get("item_name"):
        lines.append(
            f"- Item / purpose: {purchase['item_name']}"
        )

    if purchase.get("amount") is not None:
        lines.append(
            f"- Amount: {purchase['amount']} "
            f"{purchase.get('currency') or ''}".strip()
        )

    if purchase.get("deadline"):
        lines.append(
            f"- Needed by: {purchase['deadline']}"
        )

    if purchase.get("payment_preference"):
        lines.append(
            f"- Stated payment preference: "
            f"{purchase['payment_preference']}"
        )

    lines.append(
        "",
    )

    lines.append(
        "Use the financial tools to gather the information needed "
        "for a safe personalized recommendation."
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------
# Final JSON schema instructions
# ---------------------------------------------------------------------

FINAL_DECISION_INSTRUCTIONS = """
Return ONLY a valid JSON object with exactly these fields:

{
  "amount_safe_to_pay": number,
  "affordability_status": "affordable_now" | "affordable_with_plan" | "affordable_later" | "not_affordable",
  "recommended_payment_method": "full_payment" | "partial_payment" | "installments" | "wait" | "do_not_proceed",
  "payment_plan": [
    {
      "date": "YYYY-MM-DD",
      "amount": number,
      "note": "short note"
    }
  ],
  "earliest_date_for_full_payment": "YYYY-MM-DD" or null,
  "spending_changes_needed": [
    {
      "category": "short category",
      "reduction": number,
      "reason": "short reason"
    }
  ],
  "decision_explanation": "maximum 2 short sentences"
}

Rules:

- amount_safe_to_pay means the maximum amount safely payable today.
- Do not claim the purchase is affordable if essential expenses,
  confirmed commitments, or the minimum balance would be violated.
- If the purchase cannot safely be made today but can be made later,
  use affordable_later and wait.
- If a partial payment is genuinely useful and safe, use partial_payment.
- If installments are appropriate, use installments.
- Do not invent fees, interest rates, income, expenses, or dates.
- Keep payment_plan short.
- Keep spending_changes_needed to at most 3 items.
- Keep decision_explanation short.
"""


# ---------------------------------------------------------------------
# Safety guardrails
# ---------------------------------------------------------------------

def _apply_safety_guardrails(
    decision: dict,
    user: User,
    upcoming_total: float,
) -> dict:

    hard_cap = max(
        0.0,
        round(
            user.current_balance
            - user.minimum_balance
            - upcoming_total,
            2,
        ),
    )

    amount_today = (
        decision.get("amount_safe_to_pay", 0) or 0
    )

    try:
        amount_today = float(amount_today)
    except (TypeError, ValueError):
        amount_today = 0.0

    if amount_today < 0:
        amount_today = 0.0

    if amount_today > hard_cap:

        decision["amount_safe_to_pay"] = hard_cap

        explanation = decision.get(
            "decision_explanation",
            "",
        )

        decision["decision_explanation"] = (
            explanation.rstrip()
            + " Adjusted to respect the minimum balance "
            "and confirmed upcoming payments."
        ).strip()

    check = validate_payment_plan(
        current_balance=user.current_balance,
        minimum_balance=user.minimum_balance,
        upcoming_expenses=upcoming_total,
        amount_today=decision.get(
            "amount_safe_to_pay",
            0,
        ) or 0,
    )

    if not check["safe"]:

        decision["amount_safe_to_pay"] = 0.0
        decision["affordability_status"] = "not_affordable"
        decision["recommended_payment_method"] = "wait"

    return decision


# ---------------------------------------------------------------------
# Normalize final decision
# ---------------------------------------------------------------------

def _normalize_decision(
    decision: dict,
    purchase: dict,
    user: User,
) -> dict:

    valid_statuses = {
        "affordable_now",
        "affordable_with_plan",
        "affordable_later",
        "not_affordable",
    }

    valid_methods = {
        "full_payment",
        "partial_payment",
        "installments",
        "wait",
        "do_not_proceed",
    }

    # Amount
    try:
        decision["amount_safe_to_pay"] = max(
            0.0,
            float(
                decision.get(
                    "amount_safe_to_pay",
                    0,
                )
                or 0
            ),
        )
    except (TypeError, ValueError):
        decision["amount_safe_to_pay"] = 0.0

    # Status
    if decision.get("affordability_status") not in valid_statuses:
        decision["affordability_status"] = "not_affordable"

    # Method
    if decision.get("recommended_payment_method") not in valid_methods:
        decision["recommended_payment_method"] = "wait"

    # Payment plan
    if not isinstance(
        decision.get("payment_plan"),
        list,
    ):
        decision["payment_plan"] = []

    normalized_plan = []

    for item in decision["payment_plan"][:10]:

        if not isinstance(item, dict):
            continue

        try:
            amount = float(
                item.get("amount", 0)
                or 0
            )
        except (TypeError, ValueError):
            amount = 0.0

        normalized_plan.append(
            {
                "date": str(
                    item.get(
                        "date",
                        "",
                    )
                ),
                "amount": max(
                    0.0,
                    amount,
                ),
                "note": str(
                    item.get(
                        "note",
                        "",
                    )
                )[:150],
            }
        )

    decision["payment_plan"] = normalized_plan

    # Earliest date
    earliest = decision.get(
        "earliest_date_for_full_payment"
    )

    if earliest in (
        "",
        "null",
        "None",
    ):
        earliest = None

    decision["earliest_date_for_full_payment"] = earliest

    # Spending changes
    changes = decision.get(
        "spending_changes_needed",
        [],
    )

    if not isinstance(changes, list):
        changes = []

    normalized_changes = []

    for item in changes[:3]:

        if not isinstance(item, dict):
            continue

        try:
            reduction = float(
                item.get(
                    "reduction",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            reduction = 0.0

        normalized_changes.append(
            {
                "category": str(
                    item.get(
                        "category",
                        "",
                    )
                )[:100],
                "reduction": max(
                    0.0,
                    reduction,
                ),
                "reason": str(
                    item.get(
                        "reason",
                        "",
                    )
                )[:150],
            }
        )

    decision["spending_changes_needed"] = normalized_changes

    # Explanation
    explanation = str(
        decision.get(
            "decision_explanation",
            "",
        )
    ).strip()

    if not explanation:
        explanation = (
            "The recommendation is based on the available "
            "financial information and safety requirements."
        )

    decision["decision_explanation"] = explanation[:500]

    # Purchase metadata
    decision.setdefault(
        "item_name",
        purchase.get("item_name"),
    )

    decision.setdefault(
        "currency",
        purchase.get(
            "currency",
            user.currency,
        ),
    )

    decision["currency"] = (
        decision.get("currency")
        or user.currency
        or "INR"
    )

    return decision


# ---------------------------------------------------------------------
# Conservative fallback
# ---------------------------------------------------------------------

def _fallback_decision(
    user: User,
    purchase: dict,
) -> dict:

    amount = purchase.get("amount") or 0

    safe_amount = max(
        0.0,
        round(
            user.current_balance
            - user.minimum_balance,
            2,
        ),
    )

    if amount <= safe_amount:

        status_ = "affordable_now"
        method = "full_payment"

    elif safe_amount > 0:

        status_ = "affordable_with_plan"
        method = "partial_payment"

    else:

        status_ = "not_affordable"
        method = "wait"

    return {
        "amount_safe_to_pay": safe_amount,
        "affordability_status": status_,
        "recommended_payment_method": method,
        "payment_plan": [],
        "earliest_date_for_full_payment": None,
        "spending_changes_needed": [],
        "decision_explanation": (
            "The AI agent could not complete the analysis, so a "
            "conservative estimate was used based on the current "
            "balance and minimum balance preference."
        ),
        "item_name": purchase.get("item_name"),
        "currency": (
            purchase.get("currency")
            or user.currency
            or "INR"
        ),
    }


# ---------------------------------------------------------------------
# Main agent
# ---------------------------------------------------------------------

def run_affordability_agent(
    db: Session,
    user: User,
    purchase_input: dict,
) -> dict:

    purchase = dict(purchase_input)

    # ---------------------------------------------------------------
    # First-pass extraction
    # ---------------------------------------------------------------

    if (
        purchase.get("raw_text")
        and not purchase.get("amount")
    ):

        try:

            extracted = extract_purchase_information(
                purchase["raw_text"]
            )

            purchase.setdefault(
                "item_name",
                extracted.get("item_name"),
            )

            purchase.setdefault(
                "amount",
                extracted.get("amount"),
            )

        except Exception:
            # Extraction failure should not crash the purchase request.
            pass

    purchase.setdefault(
        "currency",
        user.currency or "INR",
    )

    # ---------------------------------------------------------------
    # Groq configuration
    # ---------------------------------------------------------------

    if not settings.groq_api_key:
        return _fallback_decision(
            user,
            purchase,
        )

    client = Groq(
        api_key=settings.groq_api_key
    )

    tools = _tool_definitions()

    messages: List[dict] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": _build_user_message(
                purchase,
                date.today(),
            ),
        },
    ]

    upcoming_total_seen = 0.0

    # ---------------------------------------------------------------
    # Agentic financial information gathering
    # ---------------------------------------------------------------

    try:

        for _ in range(
            max(
                1,
                settings.agent_max_tool_turns,
            )
        ):

            response = client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.1,
                max_tokens=1200,
            )

            assistant_message = (
                response.choices[0].message
            )

            assistant_dict = {
                "role": "assistant",
                "content": assistant_message.content,
            }

            if assistant_message.tool_calls:

                assistant_dict["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": (
                                tool_call.function.name
                            ),
                            "arguments": (
                                tool_call.function.arguments
                            ),
                        },
                    }
                    for tool_call in assistant_message.tool_calls
                ]

            messages.append(
                assistant_dict
            )

            # No tool call means the model thinks it has enough
            # information.
            if not assistant_message.tool_calls:
                break

            for tool_call in assistant_message.tool_calls:

                tool_name = (
                    tool_call.function.name
                )

                try:

                    tool_input = json.loads(
                        tool_call.function.arguments
                        or "{}"
                    )

                except json.JSONDecodeError:

                    tool_input = {}

                result = _dispatch_tool(
                    db,
                    user,
                    tool_name,
                    tool_input,
                )

                if (
                    tool_name
                    == "get_upcoming_commitments"
                ):

                    try:

                        upcoming_total_seen = max(
                            upcoming_total_seen,
                            float(
                                result.get(
                                    "total_upcoming",
                                    0.0,
                                )
                            ),
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):
                        pass

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(
                            result,
                            default=str,
                        ),
                    }
                )

    except Exception:
        # If the agentic information-gathering phase fails,
        # fall back safely instead of returning HTTP 500.
        return _fallback_decision(
            user,
            purchase,
        )

    # ---------------------------------------------------------------
    # Final decision WITHOUT tools
    # ---------------------------------------------------------------

    final_messages = list(messages)

    final_messages.append(
        {
            "role": "user",
            "content": FINAL_DECISION_INSTRUCTIONS,
        }
    )

    try:

        final_response = (
            client.chat.completions.create(
                model=settings.groq_model,
                messages=final_messages,
                response_format={
                    "type": "json_object"
                },
                temperature=0.1,
                max_tokens=1200,
            )
        )

        final_content = (
            final_response
            .choices[0]
            .message
            .content
        )

        final_decision = json.loads(
            final_content
        )

    except Exception:

        # Never allow an AI formatting problem to become
        # an HTTP 500.
        return _fallback_decision(
            user,
            purchase,
        )

    # ---------------------------------------------------------------
    # Normalize
    # ---------------------------------------------------------------

    final_decision = _normalize_decision(
        final_decision,
        purchase,
        user,
    )

    # ---------------------------------------------------------------
    # Deterministic safety validation
    # ---------------------------------------------------------------

    final_decision = _apply_safety_guardrails(
        final_decision,
        user,
        upcoming_total_seen,
    )

    # ---------------------------------------------------------------
    # Final metadata
    # ---------------------------------------------------------------

    final_decision["item_name"] = (
        final_decision.get("item_name")
        or purchase.get("item_name")
        or "Unnamed request"
    )

    final_decision["currency"] = (
        final_decision.get("currency")
        or purchase.get("currency")
        or user.currency
        or "INR"
    )

    return final_decision