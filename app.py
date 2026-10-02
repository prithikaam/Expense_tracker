"""
Expense Tracker System - Flask Application Entrypoint
Candidate: Prithika M | Monarch Softwares Final Round Selection Task

This application provides complete financial expense tracking, category budgeting,
periodic analytical reporting, interactive chart visualizations, and SQL analytical evaluation.
"""

import csv
import io
from datetime import date

import psycopg2
from flask import (
    Flask, render_template, request, redirect, url_for, flash, jsonify, Response
)

import config
from database import init_db
from models.user import UserModel
from models.category import CategoryModel
from models.expense import ExpenseModel
from validators import (
    ValidationError, parse_amount, parse_date, parse_id,
    parse_payment_method, parse_text, parse_color,
)

# Initialize Flask App (secret key comes from the environment - see config.py)
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Default Active User ID (single-user demo; the schema supports many users)
USER_ID = 1


@app.context_processor
def inject_globals():
    """Values needed by every page (sidebar user, quick-add modal, currency)."""
    return dict(
        global_categories=CategoryModel.get_all(USER_ID),
        current_user=UserModel.get_by_id(USER_ID) or {'full_name': 'Guest'},
        payment_methods=config.PAYMENT_METHODS,
        today=date.today().isoformat(),
    )


def _read_expense_form():
    """Validate the expense form and return clean values. Raises ValidationError."""
    amount = parse_amount(request.form.get('amount'), 'Amount')
    category_id = parse_id(request.form.get('category_id'), 'Category')
    if not CategoryModel.get_by_id(category_id, USER_ID):
        raise ValidationError('The selected category does not exist.')
    expense_date = parse_date(request.form.get('expense_date'), 'Date')
    payment_method = parse_payment_method(request.form.get('payment_method'))
    description = parse_text(request.form.get('description'), 'Description', 255)
    return category_id, amount, expense_date, payment_method, description


def _read_category_form():
    """Validate the category form and return clean values. Raises ValidationError."""
    name = parse_text(request.form.get('name'), 'Category name', 50, required=True)
    description = parse_text(request.form.get('description'), 'Description', 255)
    color = parse_color(request.form.get('color'))
    raw_budget = request.form.get('budget_limit', '').strip()
    budget_limit = parse_amount(raw_budget, 'Budget limit', allow_zero=True) if raw_budget else 0.0
    return name, description, color, budget_limit


# -----------------------------------------------------------------------------
# 1. DASHBOARD ROUTE
# -----------------------------------------------------------------------------
@app.route('/')
@app.route('/dashboard')
def dashboard():
    total_expenses = ExpenseModel.get_total_expenses(USER_ID)
    monthly_expenses = ExpenseModel.get_monthly_total(USER_ID)
    highest_category = ExpenseModel.get_highest_spending_category(USER_ID)
    recent_expenses = ExpenseModel.get_recent_expenses(USER_ID, limit=8)
    avg_monthly = ExpenseModel.get_average_monthly_expenditure(USER_ID)
    categories = CategoryModel.get_all(USER_ID)

    return render_template(
        'dashboard.html',
        active_page='dashboard',
        total_expenses=total_expenses,
        monthly_expenses=monthly_expenses,
        highest_category=highest_category,
        recent_expenses=recent_expenses,
        avg_monthly=avg_monthly,
        categories=categories
    )


# -----------------------------------------------------------------------------
# 2. EXPENSE MANAGEMENT ROUTES (CRUD + FILTERING)
# -----------------------------------------------------------------------------
@app.route('/expenses')
def expenses():
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', '')
    payment_method = request.args.get('payment_method', 'All')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    sort_by = request.args.get('sort_by', 'expense_date')

    cat_id_int = int(category_id) if category_id and category_id.isdigit() else None

    expense_list = ExpenseModel.get_filtered_history(
        user_id=USER_ID,
        category_id=cat_id_int,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None,
        payment_method=payment_method,
        search_query=search if search else None,
        sort_by=sort_by
    )

    categories = CategoryModel.get_all(USER_ID)

    current_filters = {
        'search': search,
        'category_id': category_id,
        'payment_method': payment_method,
        'start_date': start_date,
        'end_date': end_date,
        'sort_by': sort_by
    }

    return render_template(
        'expenses.html',
        active_page='expenses',
        expenses=expense_list,
        categories=categories,
        current_filters=current_filters
    )


@app.route('/expenses/add', methods=['POST'])
def add_expense():
    try:
        category_id, amount, expense_date, payment_method, description = _read_expense_form()
        ExpenseModel.create(USER_ID, category_id, amount, expense_date, payment_method, description)
        flash('Expense record added successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'danger')
    except psycopg2.Error:
        flash('Could not save the expense because of a database error. Please try again.', 'danger')
    return redirect(request.referrer or url_for('expenses'))


@app.route('/expenses/edit/<int:expense_id>', methods=['POST'])
def edit_expense(expense_id):
    try:
        category_id, amount, expense_date, payment_method, description = _read_expense_form()
        updated = ExpenseModel.update(expense_id, USER_ID, category_id, amount,
                                      expense_date, payment_method, description)
        if updated:
            flash('Expense record updated successfully!', 'success')
        else:
            flash('That expense no longer exists.', 'danger')
    except ValidationError as e:
        flash(str(e), 'danger')
    except psycopg2.Error:
        flash('Could not update the expense because of a database error. Please try again.', 'danger')
    return redirect(request.referrer or url_for('expenses'))


@app.route('/expenses/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    try:
        if ExpenseModel.delete(expense_id, USER_ID):
            flash('Expense record deleted successfully!', 'success')
        else:
            flash('That expense no longer exists.', 'danger')
    except psycopg2.Error:
        flash('Could not delete the expense because of a database error.', 'danger')
    return redirect(request.referrer or url_for('expenses'))


# -----------------------------------------------------------------------------
# 3. CATEGORY MANAGEMENT ROUTES (CRUD)
# -----------------------------------------------------------------------------
@app.route('/categories')
def categories():
    category_list = CategoryModel.get_all(USER_ID)
    return render_template('categories.html', active_page='categories', categories=category_list)


@app.route('/categories/add', methods=['POST'])
def add_category():
    try:
        name, description, color, budget_limit = _read_category_form()
        CategoryModel.create(USER_ID, name, description, color, budget_limit)
        flash(f'Category "{name}" created successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'danger')
    except psycopg2.errors.UniqueViolation:
        flash('A category with that name already exists.', 'danger')
    except psycopg2.Error:
        flash('Could not create the category because of a database error.', 'danger')
    return redirect(url_for('categories'))


@app.route('/categories/edit/<int:category_id>', methods=['POST'])
def edit_category(category_id):
    try:
        name, description, color, budget_limit = _read_category_form()
        if CategoryModel.update(category_id, USER_ID, name, description, color, budget_limit):
            flash(f'Category "{name}" updated successfully!', 'success')
        else:
            flash('That category no longer exists.', 'danger')
    except ValidationError as e:
        flash(str(e), 'danger')
    except psycopg2.errors.UniqueViolation:
        flash('A category with that name already exists.', 'danger')
    except psycopg2.Error:
        flash('Could not update the category because of a database error.', 'danger')
    return redirect(url_for('categories'))


@app.route('/categories/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category = CategoryModel.get_by_id(category_id, USER_ID)
    if not category:
        flash('That category no longer exists.', 'danger')
    elif category['expense_count'] > 0:
        # Protect the user's data: expenses are never deleted silently.
        flash(f'"{category["name"]}" has {category["expense_count"]} expense(s). '
              'Move or delete them first, then delete the category.', 'danger')
    else:
        try:
            CategoryModel.delete(category_id, USER_ID)
            flash('Category deleted successfully.', 'success')
        except psycopg2.Error:
            flash('Could not delete the category because of a database error.', 'danger')
    return redirect(url_for('categories'))


# -----------------------------------------------------------------------------
# 4. ANALYSIS & REPORTS ROUTES
# -----------------------------------------------------------------------------
@app.route('/reports')
def reports():
    daily_report = ExpenseModel.get_daily_report(USER_ID)
    weekly_report = ExpenseModel.get_weekly_report(USER_ID)
    monthly_report = ExpenseModel.get_monthly_report(USER_ID)
    category_analysis = ExpenseModel.get_category_wise_analysis(USER_ID)
    avg_monthly = ExpenseModel.get_average_monthly_expenditure(USER_ID)
    high_spending_categories = ExpenseModel.get_high_spending_categories(USER_ID, threshold=config.HIGH_SPENDING_THRESHOLD)

    return render_template(
        'reports.html',
        active_page='reports',
        daily_report=daily_report,
        weekly_report=weekly_report,
        monthly_report=monthly_report,
        category_analysis=category_analysis,
        avg_monthly=avg_monthly,
        high_spending_categories=high_spending_categories
    )


@app.route('/reports/export-csv')
def export_csv():
    """Generates downloadable CSV report of expense records."""
    expenses_data = ExpenseModel.get_filtered_history(user_id=USER_ID)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'Category', 'Amount (INR)', 'Payment Method', 'Description'])

    for exp in expenses_data:
        writer.writerow([
            exp['id'],
            exp['expense_date'],
            exp['category_name'],
            f"{exp['amount']:.2f}",
            exp['payment_method'],
            exp['description'] or ''
        ])

    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=Expense_Report.csv'
    return response


# -----------------------------------------------------------------------------
# 5. SQL ANALYTICS INSPECTOR ROUTE
# -----------------------------------------------------------------------------
@app.route('/sql-analytics')
def sql_analytics():
    total_expenses = ExpenseModel.get_total_expenses(USER_ID)
    monthly_expenses = ExpenseModel.get_monthly_total(USER_ID)
    avg_monthly = ExpenseModel.get_average_monthly_expenditure(USER_ID)
    high_spending_categories = ExpenseModel.get_high_spending_categories(USER_ID, threshold=config.HIGH_SPENDING_THRESHOLD)
    weekly_report = ExpenseModel.get_weekly_report(USER_ID)

    return render_template(
        'SQL_analytics.html',
        active_page='sql_analytics',
        total_expenses=total_expenses,
        monthly_expenses=monthly_expenses,
        avg_monthly=avg_monthly,
        high_spending_categories=high_spending_categories,
        weekly_report=weekly_report
    )


# -----------------------------------------------------------------------------
# 6. JSON API FOR DASHBOARD CHARTS
# -----------------------------------------------------------------------------
@app.route('/api/chart-data')
def chart_data():
    monthly_trend = ExpenseModel.get_monthly_report(USER_ID)
    category_breakdown = ExpenseModel.get_category_wise_analysis(USER_ID)
    payment_breakdown = ExpenseModel.get_payment_method_breakdown(USER_ID)

    # Reverse monthly trend so chronological order is left to right
    monthly_trend_sorted = list(reversed(monthly_trend))

    return jsonify({
        'monthly_trend': monthly_trend_sorted,
        'category_breakdown': category_breakdown,
        'payment_breakdown': payment_breakdown
    })


# -----------------------------------------------------------------------------
# APPLICATION LAUNCH & DB INIT
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # Create tables + sample data on first run (does nothing if they already exist)
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=config.DEBUG)
