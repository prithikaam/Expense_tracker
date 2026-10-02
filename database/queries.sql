-- =============================================================================
-- EXPENSE TRACKER SYSTEM - SQL QUERIES USED FOR REPORTS (PostgreSQL)
-- Candidate: Prithika M | Monarch Softwares Final Round Selection Task
-- user_id = 1 is the demo user. In the app the value is passed as a parameter.
-- =============================================================================

-- ------------------------------ DASHBOARD ------------------------------------

-- Q1. Total of all expenses and how many transactions exist. [SUM, COUNT]
SELECT COALESCE(SUM(amount), 0) AS total_expenses, COUNT(id) AS transaction_count
FROM expenses
WHERE user_id = 1;

-- Q2. Total spent in the current calendar month. [SUM, COUNT, date function]
SELECT COALESCE(SUM(amount), 0) AS monthly_expenses, COUNT(id) AS transaction_count
FROM expenses
WHERE user_id = 1
  AND TO_CHAR(expense_date, 'YYYY-MM') = TO_CHAR(CURRENT_DATE, 'YYYY-MM');

-- Q3. Highest spending category (all time). [JOIN, SUM, GROUP BY, ORDER BY, LIMIT]
SELECT c.name AS category_name, SUM(e.amount) AS total_spent
FROM expenses e
JOIN categories c ON c.id = e.category_id
WHERE e.user_id = 1
GROUP BY c.id, c.name
ORDER BY total_spent DESC
LIMIT 1;

-- Q4. Eight most recent transactions. [JOIN, ORDER BY, LIMIT]
SELECT e.id, e.expense_date, c.name AS category_name, e.amount, e.payment_method, e.description
FROM expenses e
JOIN categories c ON c.id = e.category_id
WHERE e.user_id = 1
ORDER BY e.expense_date DESC, e.id DESC
LIMIT 8;

-- ------------------------------ PERIODIC REPORTS -----------------------------

-- Q5. Daily report: total, average and count of transactions per day. [SUM, AVG, COUNT, GROUP BY]
SELECT expense_date,
       SUM(amount) AS daily_total,
       AVG(amount) AS daily_average,
       COUNT(id)   AS transaction_count
FROM expenses
WHERE user_id = 1
GROUP BY expense_date
ORDER BY expense_date;

-- Q6. Weekly report grouped by ISO week (e.g. 2026-W39). [TO_CHAR date function, SUM, AVG, COUNT]
SELECT TO_CHAR(expense_date, 'IYYY-"W"IW') AS iso_week,
       MIN(expense_date) AS first_expense,
       MAX(expense_date) AS last_expense,
       SUM(amount)       AS weekly_total,
       AVG(amount)       AS weekly_average,
       COUNT(id)         AS transaction_count
FROM expenses
WHERE user_id = 1
GROUP BY TO_CHAR(expense_date, 'IYYY-"W"IW')
ORDER BY iso_week DESC;

-- Q7. Monthly spending report. [TO_CHAR date function, SUM, AVG, COUNT, GROUP BY]
SELECT TO_CHAR(expense_date, 'YYYY-MM') AS month_label,
       SUM(amount) AS monthly_total,
       AVG(amount) AS average_transaction,
       COUNT(id)   AS transaction_count
FROM expenses
WHERE user_id = 1
GROUP BY TO_CHAR(expense_date, 'YYYY-MM')
ORDER BY month_label DESC;

-- Q8. Average monthly expenditure: average of the monthly totals. [subquery, SUM, AVG]
SELECT ROUND(AVG(monthly_total), 2) AS average_monthly_expenditure,
       COUNT(month_label)                 AS months_counted
FROM (
    SELECT TO_CHAR(expense_date, 'YYYY-MM') AS month_label, SUM(amount) AS monthly_total
    FROM expenses
    WHERE user_id = 1
    GROUP BY TO_CHAR(expense_date, 'YYYY-MM')
) AS monthly_totals;

-- ------------------------------ CATEGORY ANALYSIS ----------------------------

-- Q9. Category-wise spending with count, average and budget (categories with no spending show 0). [LEFT JOIN, SUM, AVG, COUNT]
SELECT c.name AS category_name, c.budget_limit,
       COALESCE(SUM(e.amount), 0) AS total_spent,
       COALESCE(AVG(e.amount), 0) AS average_expense,
       COUNT(e.id)                AS transaction_count
FROM categories c
LEFT JOIN expenses e ON e.category_id = c.id AND e.user_id = c.user_id
WHERE c.user_id = 1
GROUP BY c.id, c.name, c.budget_limit
ORDER BY total_spent DESC;

-- Q10. Percentage share of each category in total spending. [SUM as window function, ROUND]
SELECT c.name AS category_name,
       SUM(e.amount) AS total_spent,
       ROUND(100.0 * SUM(e.amount) / SUM(SUM(e.amount)) OVER (), 2) AS percent_of_total
FROM expenses e
JOIN categories c ON c.id = e.category_id
WHERE e.user_id = 1
GROUP BY c.id, c.name
ORDER BY total_spent DESC;

-- Q11. High-spending categories: only categories whose total is above 5000. [GROUP BY, HAVING, ORDER BY]
SELECT c.name AS category_name, SUM(e.amount) AS total_spent, COUNT(e.id) AS transaction_count
FROM expenses e
JOIN categories c ON c.id = e.category_id
WHERE e.user_id = 1
GROUP BY c.id, c.name
HAVING SUM(e.amount) > 5000
ORDER BY total_spent DESC;

-- Q12. Categories that went over their budget in a given month (September 2026). [JOIN, GROUP BY, HAVING, date function]
SELECT c.name AS category_name, c.budget_limit, SUM(e.amount) AS spent_this_month
FROM expenses e
JOIN categories c ON c.id = e.category_id
WHERE e.user_id = 1
  AND TO_CHAR(e.expense_date, 'YYYY-MM') = '2026-09'
GROUP BY c.id, c.name, c.budget_limit
HAVING SUM(e.amount) > c.budget_limit
ORDER BY spent_this_month DESC;

-- Q13. Spending by payment method (used by the dashboard chart). [SUM, COUNT, AVG, GROUP BY]
SELECT payment_method, SUM(amount) AS total_amount, COUNT(id) AS transaction_count
FROM expenses
WHERE user_id = 1
GROUP BY payment_method
ORDER BY total_amount DESC;

-- Q14. Expense history filtered by date range and category, newest first. [JOIN, WHERE, ORDER BY]
SELECT e.expense_date, c.name AS category_name, e.amount, e.payment_method, e.description
FROM expenses e
JOIN categories c ON c.id = e.category_id
WHERE e.user_id = 1
  AND e.expense_date BETWEEN '2026-09-01' AND '2026-09-30'
  AND c.name = 'Groceries'
ORDER BY e.expense_date DESC;
