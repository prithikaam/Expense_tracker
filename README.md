# Expense Tracker System

**Candidate:** Prithika M  
**Assessment:** Monarch Softwares – Final Round Selection Task (issued 28 Sep 2026)

A web application to record, categorise and analyse daily expenses, with category-wise, daily, weekly and monthly reports and an interactive dashboard.

## Technologies
| Part | Technology |
|---|---|
| Language / backend | Python 3.9+, Flask |
| Database | **PostgreSQL** (via `psycopg2`) with automatic local **SQLite** fallback |
| SQL used | `SUM()`, `AVG()`, `COUNT()`, `GROUP BY`, `HAVING`, `ORDER BY`, date functions (`TO_CHAR`/`strftime`, `CURRENT_DATE`), subqueries, window functions |
| Frontend | HTML/Jinja templates, CSS, JavaScript, Chart.js (loaded from a CDN) |

## Features (mapped to the task document)
- **Expense management:** add, edit, delete, view history (search, filter by category / payment method / date range, sort).
- **Category management:** create, edit, delete categories; assign every expense to a category; optional monthly budget with progress bar (this month's spending vs the limit).
- **Analysis and reports:** daily, weekly (ISO week), monthly, category-wise (with % share) and average monthly expenditure; high-spending categories using `HAVING`; CSV export.
- **Dashboard:** total expenses, monthly expenses, highest spending category, recent transactions (plus average monthly spend and three charts).
- **SQL Query Inspector page:** shows the main SQL queries next to their live results.
- **Validation:** empty / non-numeric / negative amounts, invalid or future dates, unknown category, duplicate category names (case-insensitive), negative budgets, bad colour codes and over-long text all show a clear message. A category that still has expenses cannot be deleted.

## Database design
Three tables (see `database/er_diagram.png` and `database/schema.sql`):

| Table | Purpose | Keys |
|---|---|---|
| `users` | user information | PK `id`; `username`, `email` unique |
| `categories` | expense categories per user | PK `id`; FK `user_id → users.id`; unique `(user_id, LOWER(name))` |
| `expenses` | expense records | PK `id`; FK `user_id → users.id`; FK `category_id → categories.id` (`ON DELETE RESTRICT`); `CHECK amount > 0` |

Relationships: one user → many categories, one user → many expenses, one category → many expenses.

## Project structure
```
Expense_Tracker/
├── app.py                # Flask routes
├── config.py             # settings read from environment variables
├── database.py           # PostgreSQL connection + query helpers + SQLite auto-fallback
├── validators.py         # input validation
├── init_db.py            # create / reset tables and sample data
├── models/               # user.py, category.py, expense.py (SQL queries)
├── templates/  static/   # pages, CSS, JS
├── database/
│   ├── schema.sql        # tables + sample data
│   ├── queries.sql       # report queries with one-line notes
│   ├── er_diagram.png    # ER diagram
│   └── generate_er_diagram.py
├── screenshots/          # high-resolution screenshots of all views
│   ├── 01_dashboard.png
│   ├── 02_expense_management.png
│   ├── 03_category_management.png
│   ├── 04_reports_analytics.png
│   └── 05_sql_inspector.png
├── requirements.txt
└── .env.example
```

## Setup and run
1. **Create a virtual environment and install packages:**
   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows   (Linux/macOS: source venv/bin/activate)
   pip install -r requirements.txt
   ```
2. **Database Configuration:**
   - **Default (Zero-Config):** Automatically connects to a local SQLite database (`database/expense_tracker.db`) pre-seeded with sample data if PostgreSQL is not running.
   - **PostgreSQL:** Copy `.env.example` to `.env` and fill in your PostgreSQL credentials. Create the database:
     ```bash
     psql -U postgres -c "CREATE DATABASE expense_tracker;"
     ```
3. **Run the app:**
   ```bash
   python app.py
   ```
   Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

To reset everything to the sample data: `python init_db.py --reset` (deletes all current data and reloads sample dataset).

## Sample data
1 user, 8 categories and 37 expenses (INR) from July to September 2026, so every report works without typing data. Values to check against:
total expenses ₹66,727.90 · September ₹23,133.00 · average monthly ₹22,242.63 · highest category Rent & Housing (₹36,000). `HAVING` threshold ₹5,000 returns Rent & Housing, Groceries, Shopping and Utilities.

## Deliverables Checklist
1. **Source Code**: Full Python Flask project folder with modular models, routes, and validation.
2. **Database Script**: `database/schema.sql` (schema tables and 3 months of pre-seeded sample data).
3. **ER Diagram**: `database/er_diagram.png` (high-res table relationships diagram).
4. **SQL Queries File**: `database/queries.sql` (all SQL report queries documented with one-line descriptions).
5. **README File**: `README.md` (complete project guide, tech stack, setup, and submission notes).
6. **Screenshots**: `screenshots/` directory containing high-resolution screenshots for all views.

## Assumptions and incomplete points
- **No login screen.** The `users` table is in the design, but the demo runs as one user (`user_id = 1`, Prithika M). Multiple users would need a login/session layer, which I did not build.
- **Currency** is INR (₹) and future-dated expenses are rejected.
- The dashboard charts, icons and fonts load from CDNs, so they need internet access.
- Weekly reports use ISO weeks (Monday start, e.g. `2026-W39`).

