# Buy or Wait? — Agentic AI Edition 🤖💰

> **This is now a real login + real LLM-agent app.** The old version had
> static buttons and a fixed if/else formula deciding affordability. That
> rule engine is gone. Every recommendation is now produced by an LLM
> (via the [Groq](https://groq.com) API) running an **agentic tool-use
> loop**: given a purchase request, the model decides for itself which
> of the user's financial data to look up (balance, upcoming
> commitments, transaction history, past decisions, cash-flow forecast)
> before returning a structured, personalized decision. See
> `backend/app/services/ai_service.py`.

## What changed

| Before | Now |
|---|---|
| No accounts, one hard-coded demo user | Real signup/login with hashed passwords + JWT (`/auth/register`, `/auth/login`) |
| Fixed formula: `safe = balance - min_balance - upcoming` | Groq-hosted agent reasons over tools (`get_financial_snapshot`, `get_upcoming_commitments`, `get_recent_transactions`, `get_purchase_history`, `get_cash_flow_forecast`) and calls `submit_decision` |
| Same recommendation for anyone with the same balance | Personalized by `risk_tolerance`, `flexible_expense_willingness`, `preferred_payment_method`, and each user's own transactions/commitments |
| Static numbers in every component | Dashboard/charts/timeline are fed live per-user data from the API |
| "Analyze" button did nothing | Calls `POST /purchase/analyze`, which runs the agent and stores the decision |

## Quick start (backend)

```bash
cd backend
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env
# then edit .env:
#   DATABASE_URL=...            (Postgres connection string)
#   GROQ_API_KEY=gsk_...        (required for the agent to actually run)
#   JWT_SECRET_KEY=...          (any long random string)

python scripts/seed_data.py     # creates 3 demo logins, see below
uvicorn app.main:app --reload
```

Demo logins created by `seed_data.py` (password for all: `password123`):

* `asha@buyorwait.com`  — conservative, high minimum balance, low willingness to cut spending
* `rohan@buyorwait.com` — same balance as Asha, but flexible risk tolerance and high willingness to cut spending → gets a different recommendation for the identical purchase
* `priya@buyorwait.com` — tight budget, small buffer

Try it: log in as Asha and Rohan (same balance!) and ask both "Can I afford a MacBook for ₹75,000?" — you should get two different recommendations.

### Evaluate the provided dataset

`backend/data/requests.csv` (the file you attached) can be run straight through the agent:

```bash
cd backend
python scripts/evaluate_dataset.py data/requests.csv results.csv
```

Each row is evaluated against one of the three seeded demo users (round-robin), and the agent's decision for every request is written to `results.csv`.

## Quick start (frontend)

```bash
cd frontend
npm install
npm run dev
```

You'll land on a login/register screen (`src/pages/Login.jsx`) instead of the old static dashboard. `src/context/AuthContext.jsx` holds the session; `src/services/api.js` now sends the JWT on every request.

## Where the "agentic" part lives

`backend/app/services/ai_service.py::run_affordability_agent` is the whole engine:

1. Builds a system prompt describing the safety rules and the personalization requirement.
2. Gives the model a toolbox (`app/services/financial_context.py` functions) instead of pre-computed numbers.
3. Loops: the model calls tools → we execute them against the real DB → results go back to the model → repeat until it calls `submit_decision`.
4. A small safety net (`_apply_safety_guardrails`) only clamps an unsafe number; it never invents the recommendation itself.

If `GROQ_API_KEY` is not set, a conservative non-LLM fallback (`_fallback_decision`) is used instead so the app doesn't crash — but the intended, primary mode is the LLM agent.

---

# Original design notes (kept for reference)

# Buy or Wait? 💰

An AI-powered financial decision agent that helps users decide whether they can safely afford a requested purchase.

Instead of checking only the current bank balance, the system analyzes the user's financial situation, including income, recurring expenses, pending payments, essential spending, financial commitments, payment preferences, and flexible expenses.

The system can recommend whether the user should:

* ✅ Pay in full
* 💳 Pay partially
* 📅 Use installments
* ⏳ Wait until a safer date
* ❌ Not proceed with the purchase

---

## 🎯 Problem Statement

A person may have enough money in their account to buy something today, but that does not necessarily mean they can safely afford it.

For example:

> "I have ₹60,000 in my account. Can I buy a ₹45,000 laptop?"

A simple balance checker might say **yes**.

However, the user may also have:

* ₹15,000 rent due soon
* ₹5,000 loan payment
* ₹8,000 expected essential expenses
* Salary arriving after two weeks
* A preferred minimum balance of ₹10,000

In this situation, spending ₹45,000 immediately may not be financially safe.

**Buy or Wait?** uses future cash-flow forecasting and personalized financial constraints to make a safer recommendation.

---

## 🚀 Key Features

### 1. Purchase Affordability Analysis

The system calculates:

* Amount safe to pay today
* Affordability status
* Earliest date for full payment
* Recommended payment method
* Required spending adjustments

### 2. Cash-Flow Forecasting

The system forecasts the user's financial position over time using:

* Current balance
* Confirmed income
* Recurring expenses
* Pending payments
* Essential expenses
* Existing commitments

### 3. Payment Method Optimization

The system compares different ways of completing a purchase:

* Full payment
* Partial payment
* Installments
* Delayed payment

Each option is simulated before making a recommendation.

### 4. Safety Validation

A payment plan is considered safe only when:

* Essential expenses can still be paid
* All listed payments can be completed
* The user's minimum preferred balance is maintained
* The purchase can be completed within the required deadline
* The user does not take unnecessary financial risk

Unsafe payment plans are rejected before the final recommendation.

### 5. Personalized Recommendations

Two users with the same bank balance can receive different recommendations because their:

* Income
* Expenses
* Commitments
* Financial history
* Payment preferences
* Minimum balance requirements
* Savings goals
* Flexibility toward discretionary spending

may be different.

### 6. Spending Reduction Suggestions

The system identifies flexible expenses that could potentially be reduced.

For example:

> "Reducing entertainment spending by ₹1,500/month could help you reach the purchase goal 2 weeks earlier."

The system prioritizes flexible spending rather than essential expenses.

### 7. Transaction Explanation

The system explains **why** a particular payment method is recommended.

For example:

> "Waiting until your next confirmed salary is safer because paying today would reduce your balance below your preferred minimum."

Or:

> "A short installment plan may be safer than paying in full today because it preserves enough cash for your upcoming essential expenses."

### 8. What-If Savings Simulation

Users can explore scenarios such as:

> "What if I save ₹2,000 every month?"

The system estimates how this changes the earliest safe purchase date.

### 9. Text and Image Information Extraction

The system can extract relevant financial information from supported:

* Messages
* Receipts
* Payment screenshots
* Financial documents

Extracted information is then passed to the financial decision engine.

---

# 🏗️ System Architecture

```text
                    USER
                      │
                      ▼
             ┌─────────────────┐
             │ Purchase Request│
             │ Text / Image    │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Input & AI      │
             │ Understanding   │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Financial       │
             │ Memory          │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Cash Flow       │
             │ Forecast Engine │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Affordability   │
             │ Engine          │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Payment         │
             │ Optimizer       │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Safety          │
             │ Validator       │
             └────────┬────────┘
                      │
             ┌────────┴─────────┐
             ▼                  ▼
    ┌─────────────────┐  ┌─────────────────┐
    │ Savings Coach   │  │ Explanation     │
    │                 │  │ Engine          │
    └────────┬────────┘  └────────┬────────┘
             │                    │
             └──────────┬─────────┘
                        ▼
               ┌─────────────────┐
               │ FINAL FINANCIAL │
               │ RECOMMENDATION  │
               └─────────────────┘
```

---

# 📁 Project Structure

```text
buy-or-wait/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── purchase.py
│   │   │   │   ├── financial_data.py
│   │   │   │   └── savings.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── transaction.py
│   │   │   ├── commitment.py
│   │   │   └── purchase.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── purchase.py
│   │   │   ├── financial.py
│   │   │   └── recommendation.py
│   │   │
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── extraction_service.py
│   │   │   ├── forecast_service.py
│   │   │   ├── affordability_service.py
│   │   │   ├── payment_optimizer.py
│   │   │   ├── safety_validator.py
│   │   │   ├── savings_service.py
│   │   │   └── explanation_service.py
│   │   │
│   │   └── utils/
│   │       └── helpers.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PurchaseInput.jsx
│   │   │   ├── FinancialSummary.jsx
│   │   │   ├── RecommendationCard.jsx
│   │   │   ├── PaymentOptions.jsx
│   │   │   ├── CashFlowChart.jsx
│   │   │   ├── SavingsSuggestions.jsx
│   │   │   └── PaymentTimeline.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   └── PurchaseAnalysis.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   └── package.json
│
├── database/
│   └── schema.sql
│
├── uploads/
│
├── README.md
└── .gitignore
```

---

# 🧠 Core Decision Logic

The system follows this general decision pipeline:

```text
User Request
     │
     ▼
Understand Purchase
     │
     ▼
Understand Financial Situation
     │
     ▼
Build Future Cash-Flow Timeline
     │
     ▼
Calculate Safe Amount
     │
     ▼
Generate Payment Strategies
     │
     ├── Full Payment
     ├── Partial Payment
     ├── Installments
     └── Wait
     │
     ▼
Simulate Each Strategy
     │
     ▼
Safety Validation
     │
     ├── Unsafe → Reject
     │
     └── Safe
          │
          ▼
   Rank Safe Options
          │
          ▼
  Savings Suggestions
          │
          ▼
  Explain Recommendation
          │
          ▼
     Final Decision
```

---

# 📊 Example Input

```json
{
  "purchase": {
    "item": "Laptop",
    "amount": 75000,
    "deadline": "2026-10-15"
  },
  "financial_data": {
    "current_balance": 60000,
    "monthly_income": 45000,
    "minimum_balance": 10000
  }
}
```

---

# 📋 Example Output

```json
{
  "amount_safe_to_pay": 30000,
  "affordability_status": "affordable_with_plan",
  "recommended_payment_method": "partial_payment",

  "payment_plan": [
    {
      "date": "2026-09-12",
      "amount": 30000
    },
    {
      "date": "2026-09-30",
      "amount": 45000
    }
  ],

  "earliest_date_for_full_payment": "2026-09-30",

  "spending_changes_needed": [
    {
      "category": "entertainment",
      "reduction": 2000
    }
  ],

  "decision_explanation":
    "Paying the full amount today would reduce your balance below your preferred minimum. A partial payment now followed by the remaining amount after your confirmed income is safer."
}
```

---

# 🔐 Safety Principle

The system does **not** simply ask:

> "Does the user have enough money right now?"

Instead, it asks:

> "Can the user complete this purchase while still meeting all essential financial obligations throughout the forecast period?"

The deterministic financial engine is responsible for safety calculations.

The AI/LLM is responsible for:

* Understanding natural language
* Extracting information
* Explaining results
* Generating user-friendly suggestions

The AI must **not override the deterministic safety validator**.

---

# 🛠️ Technology Stack

## Backend

* Python
* FastAPI
* Pydantic
* PostgreSQL

## AI

* Large Language Model
* Text extraction
* Document/image understanding
* Financial reasoning support

## Frontend

* React
* JavaScript
* Charts and visualizations

## Database

* PostgreSQL

## Development Tools

* VS Code
* Git
* GitHub
* Docker

---

# 🔄 Development Plan

### Phase 1 — Backend Foundation

Build:

* FastAPI application
* Project structure
* Basic API
* Configuration

### Phase 2 — Financial Engine

Build:

* Financial data model
* Cash-flow timeline
* Forecasting
* Safe-to-pay calculation
* Affordability status

### Phase 3 — Payment Intelligence

Build:

* Full payment
* Partial payment
* Installments
* Wait strategy
* Payment optimizer
* Safety validator

### Phase 4 — Savings Intelligence

Build:

* Expense categorization
* Flexible expense detection
* Spending reduction suggestions
* Savings goals
* What-if simulations

### Phase 5 — AI Integration

Build:

* Natural-language understanding
* Financial information extraction
* Image/document extraction
* AI-generated explanations

### Phase 6 — Database

Build:

* User profiles
* Transactions
* Income
* Expenses
* Commitments
* Preferences
* Purchase history
* Payment plans
* Savings goals

### Phase 7 — Frontend

Build:

* Dashboard
* Purchase input
* Financial summary
* Recommendation card
* Payment comparison
* Cash-flow chart
* Savings suggestions
* Payment timeline

### Phase 8 — Integration & Deployment

Connect:

```text
React
  ↓
FastAPI
  ↓
Financial Engine
  ↓
AI Services
  ↓
PostgreSQL
```

Then test and deploy the complete application.

---

# 🎯 Final Goal

**Buy or Wait?** should act as a personalized financial decision assistant that does not merely tell users whether they have enough money.

It should answer:

> **"What is the safest way for YOU to make this purchase, and what should you change if you cannot afford it yet?"**

---

## ⚠️ Disclaimer

This project is intended as an educational and software-engineering project. Its recommendations should not be treated as professional financial advice.
