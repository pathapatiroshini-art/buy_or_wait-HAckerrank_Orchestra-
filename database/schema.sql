-- =========================================================
-- BUY OR WAIT?
-- DATABASE SCHEMA (v2 - accounts + personalization + agent output)
-- =========================================================

-- =========================================================
-- USERS
-- =========================================================

CREATE TABLE IF NOT EXISTS users (

    id SERIAL PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(255) UNIQUE NOT NULL,

    hashed_password VARCHAR(255) NOT NULL,

    current_balance NUMERIC(14, 2) DEFAULT 0.00,

    monthly_income NUMERIC(14, 2) DEFAULT 0.00,

    minimum_balance NUMERIC(14, 2) DEFAULT 0.00,

    currency VARCHAR(10) DEFAULT 'INR',

    risk_tolerance VARCHAR(20) DEFAULT 'balanced',

    preferred_payment_method VARCHAR(30),

    flexible_expense_willingness NUMERIC(3, 2) DEFAULT 0.50,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_risk_tolerance
        CHECK (risk_tolerance IN ('conservative', 'balanced', 'flexible'))
);


-- =========================================================
-- TRANSACTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS transactions (

    id SERIAL PRIMARY KEY,

    user_id INTEGER NOT NULL,

    description VARCHAR(255) NOT NULL,

    amount NUMERIC(12, 2) NOT NULL,

    category VARCHAR(100) NOT NULL,

    transaction_type VARCHAR(20) NOT NULL,

    flexibility VARCHAR(20) DEFAULT 'essential',

    transaction_date DATE DEFAULT CURRENT_DATE,

    CONSTRAINT fk_transactions_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    CONSTRAINT chk_transaction_type
        CHECK (transaction_type IN ('income', 'expense')),

    CONSTRAINT chk_transaction_flexibility
        CHECK (flexibility IN ('essential', 'flexible')),

    CONSTRAINT chk_transaction_amount
        CHECK (amount >= 0)
);


-- =========================================================
-- COMMITMENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS commitments (

    id SERIAL PRIMARY KEY,

    user_id INTEGER NOT NULL,

    name VARCHAR(255) NOT NULL,

    amount NUMERIC(12, 2) NOT NULL,

    due_date DATE NOT NULL,

    category VARCHAR(100) NOT NULL,

    is_essential BOOLEAN DEFAULT TRUE,

    status VARCHAR(30) DEFAULT 'pending',

    CONSTRAINT fk_commitments_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    CONSTRAINT chk_commitment_amount
        CHECK (amount >= 0),

    CONSTRAINT chk_commitment_status
        CHECK (status IN ('pending', 'paid', 'cancelled'))
);


-- =========================================================
-- PURCHASES  (now stores the full LLM agent decision)
-- =========================================================

CREATE TABLE IF NOT EXISTS purchases (

    id SERIAL PRIMARY KEY,

    user_id INTEGER NOT NULL,

    item_name VARCHAR(255) NOT NULL,

    amount NUMERIC(14, 2) NOT NULL,

    currency VARCHAR(10) DEFAULT 'INR',

    deadline DATE,

    payment_preference VARCHAR(50),

    raw_request_text TEXT,

    status VARCHAR(30) DEFAULT 'pending',

    agent_decision JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_purchases_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    CONSTRAINT chk_purchase_amount
        CHECK (amount >= 0),

    CONSTRAINT chk_purchase_status
        CHECK (status IN ('pending', 'analyzed', 'approved', 'completed', 'cancelled'))
);


-- =========================================================
-- INDEXES
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_commitments_user_id ON commitments(user_id);
CREATE INDEX IF NOT EXISTS idx_commitments_due_date ON commitments(due_date);
CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases(user_id);

-- Demo accounts (with login credentials) and sample financial data are
-- created by `backend/scripts/seed_data.py` instead of raw SQL, so that
-- passwords are hashed correctly with the app's own bcrypt settings.
-- Run: python backend/scripts/seed_data.py
