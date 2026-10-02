-- =============================================================================
-- EXPENSE TRACKER SYSTEM - DATABASE SCRIPT (PostgreSQL)
-- Candidate: Prithika M | Monarch Softwares Final Round Selection Task
--
-- Creates the tables, keys, indexes and sample data.
-- Run with:  psql -U postgres -d expense_tracker -f database/schema.sql
-- (The app also runs this file automatically the first time it starts.)
-- WARNING: it DROPS and recreates the three tables, so existing data is lost.
-- =============================================================================

DROP TABLE IF EXISTS expenses;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- -----------------------------------------------------------------------------
-- 1. USERS: one row per person using the system
-- -----------------------------------------------------------------------------
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(100) NOT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 2. CATEGORIES: each user owns their own categories (1 user -> many categories)
-- -----------------------------------------------------------------------------
CREATE TABLE categories (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name         VARCHAR(50)   NOT NULL,
    description  TEXT,
    color        VARCHAR(7)    NOT NULL DEFAULT '#4f46e5',
    budget_limit NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (budget_limit >= 0),
    created_at   TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- A user cannot have two categories with the same name (case-insensitive)
CREATE UNIQUE INDEX uq_categories_user_name ON categories (user_id, LOWER(name));

-- -----------------------------------------------------------------------------
-- 3. EXPENSES: each expense belongs to one user and one category
--    category_id uses ON DELETE RESTRICT so a category that still has expenses
--    can never be deleted by accident (which would silently lose the expenses).
-- -----------------------------------------------------------------------------
CREATE TABLE expenses (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id    INTEGER       NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    amount         NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    expense_date   DATE          NOT NULL,
    payment_method VARCHAR(30)   NOT NULL DEFAULT 'Cash'
                   CHECK (payment_method IN ('Cash','UPI','Credit Card','Debit Card','Net Banking')),
    description    TEXT,
    created_at     TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes that support the report queries (filter by user + date / category)
CREATE INDEX idx_expenses_user_date ON expenses (user_id, expense_date);
CREATE INDEX idx_expenses_category  ON expenses (category_id);
CREATE INDEX idx_categories_user    ON categories (user_id);

-- =============================================================================
-- SAMPLE DATA (all amounts in INR)
-- =============================================================================
INSERT INTO users (id, username, email, password_hash, full_name) VALUES
(1, 'prithika', 'prithika@example.com', 'not-used-in-this-demo', 'Prithika M');

INSERT INTO categories (id, user_id, name, description, color, budget_limit) VALUES
(1, 1, 'Groceries',       'Vegetables, fruits, milk and monthly provisions', '#10b981', 4000.00),
(2, 1, 'Rent & Housing',  'House rent and maintenance',                      '#3b82f6', 12000.00),
(3, 1, 'Dining Out',      'Restaurants, cafes and food delivery',            '#f59e0b', 1400.00),
(4, 1, 'Utilities',       'Electricity, water, internet and mobile recharge','#8b5cf6', 2200.00),
(5, 1, 'Transport',       'Fuel, bus, auto and cab rides',                   '#ec4899', 1300.00),
(6, 1, 'Entertainment',   'Movies, OTT subscriptions and outings',           '#06b6d4', 1200.00),
(7, 1, 'Healthcare',      'Medicines, doctor visits and check-ups',          '#ef4444', 1500.00),
(8, 1, 'Shopping',        'Clothing, accessories and electronics',           '#6366f1', 3000.00);

-- Keep the SERIAL counters ahead of the ids inserted above
SELECT setval(pg_get_serial_sequence('users', 'id'),      (SELECT MAX(id) FROM users));
SELECT setval(pg_get_serial_sequence('categories', 'id'), (SELECT MAX(id) FROM categories));

INSERT INTO expenses (user_id, category_id, amount, expense_date, payment_method, description) VALUES
-- July 2026
(1, 2, 12000.00, '2026-07-01', 'Net Banking', 'Monthly house rent'),
(1, 4,   799.00, '2026-07-03', 'Credit Card', 'Broadband internet bill'),
(1, 1,  1450.50, '2026-07-05', 'UPI',         'Weekly vegetables and provisions'),
(1, 5,   500.00, '2026-07-07', 'Debit Card',  'Petrol'),
(1, 3,   640.00, '2026-07-10', 'UPI',         'Team lunch at restaurant'),
(1, 6,   450.00, '2026-07-12', 'Credit Card', 'Weekend movie tickets'),
(1, 4,  1120.00, '2026-07-15', 'Net Banking', 'Electricity bill'),
(1, 1,   980.20, '2026-07-18', 'UPI',         'Fruits and vegetables'),
(1, 8,  2499.00, '2026-07-20', 'Credit Card', 'Running shoes'),
(1, 7,   750.00, '2026-07-24', 'UPI',         'Routine health check-up'),
(1, 3,   825.00, '2026-07-28', 'Cash',        'Dinner with friends'),
-- August 2026
(1, 2, 12000.00, '2026-08-01', 'Net Banking', 'Monthly house rent'),
(1, 4,   799.00, '2026-08-02', 'Credit Card', 'Broadband internet bill'),
(1, 1,  1658.80, '2026-08-04', 'UPI',         'Monthly provisions stock-up'),
(1, 5,   600.00, '2026-08-06', 'Debit Card',  'Petrol'),
(1, 3,   550.00, '2026-08-09', 'UPI',         'Family dinner'),
(1, 6,   299.00, '2026-08-11', 'Credit Card', 'OTT subscription'),
(1, 4,   924.40, '2026-08-15', 'Net Banking', 'Electricity bill'),
(1, 1,  1100.00, '2026-08-19', 'UPI',         'Groceries and household items'),
(1, 7,  1200.00, '2026-08-22', 'Credit Card', 'Dental check-up'),
(1, 5,   350.00, '2026-08-25', 'UPI',         'Auto and cab rides'),
(1, 8,  2100.00, '2026-08-28', 'Credit Card', 'Festival clothing'),
-- September 2026
(1, 2, 12000.00, '2026-09-01', 'Net Banking', 'Monthly house rent'),
(1, 4,   799.00, '2026-09-02', 'Credit Card', 'Broadband internet bill'),
(1, 1,  1824.00, '2026-09-04', 'UPI',         'Supermarket - vegetables and milk'),
(1, 5,   525.00, '2026-09-06', 'Debit Card',  'Petrol'),
(1, 3,   640.00, '2026-09-08', 'UPI',         'Restaurant dinner'),
(1, 6,   320.00, '2026-09-10', 'Credit Card', 'Concert ticket'),
(1, 4,   880.00, '2026-09-14', 'Net Banking', 'Water and maintenance bill'),
(1, 1,  1250.00, '2026-09-16', 'UPI',         'Mid-month groceries'),
(1, 7,   450.00, '2026-09-18', 'UPI',         'Pharmacy - medicines and vitamins'),
(1, 3,   285.00, '2026-09-20', 'Cash',        'Coffee and snacks'),
(1, 5,   400.00, '2026-09-22', 'UPI',         'Bus pass and parking'),
(1, 8,  1750.00, '2026-09-24', 'Credit Card', 'Laptop accessories'),
(1, 1,   950.00, '2026-09-26', 'UPI',         'Bakery and dairy items'),
(1, 3,   580.00, '2026-09-28', 'UPI',         'Cafe brunch'),
(1, 5,   480.00, '2026-09-29', 'Debit Card',  'Petrol');
