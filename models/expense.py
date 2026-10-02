"""
Expense Model for Expense Tracker System
Core module handling Expense CRUD operations and SQL Analytical aggregations:
SUM(), AVG(), COUNT(), GROUP BY, HAVING, ORDER BY, and Date Functions.
"""

from typing import List, Dict, Any, Optional
from database import execute_query, execute_non_query


class ExpenseModel:

    # -------------------------------------------------------------------------
    # CRUD OPERATIONS
    # -------------------------------------------------------------------------

    @staticmethod
    def get_by_id(expense_id: int, user_id: int = 1) -> Optional[Dict[str, Any]]:
        query = """
            SELECT 
                e.id,
                e.user_id,
                e.category_id,
                e.amount,
                e.expense_date,
                e.payment_method,
                e.description,
                e.created_at,
                c.name AS category_name,
                c.color AS category_color
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.id = %s AND e.user_id = %s
        """
        return execute_query(query, (expense_id, user_id), fetch_all=False)

    @staticmethod
    def create(user_id: int, category_id: int, amount: float, expense_date: str, payment_method: str, description: str) -> int:
        query = """
            INSERT INTO expenses (user_id, category_id, amount, expense_date, payment_method, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        return execute_non_query(query, (user_id, category_id, amount, expense_date, payment_method, description))

    @staticmethod
    def update(expense_id: int, user_id: int, category_id: int, amount: float, expense_date: str, payment_method: str, description: str) -> int:
        query = """
            UPDATE expenses
            SET category_id = %s, amount = %s, expense_date = %s, payment_method = %s, description = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s
        """
        return execute_non_query(query, (category_id, amount, expense_date, payment_method, description, expense_id, user_id))

    @staticmethod
    def delete(expense_id: int, user_id: int = 1) -> int:
        query = "DELETE FROM expenses WHERE id = %s AND user_id = %s"
        return execute_non_query(query, (expense_id, user_id))

    # -------------------------------------------------------------------------
    # EXPENSE HISTORY WITH FILTERING, SORTING & SEARCH
    # -------------------------------------------------------------------------

    @staticmethod
    def get_filtered_history(
        user_id: int = 1,
        category_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        payment_method: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        search_query: Optional[str] = None,
        sort_by: str = 'expense_date',
        sort_order: str = 'DESC',
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Flexible filtering and sorting method for expense history table.
        """
        conditions = ["e.user_id = %s"]
        params: List[Any] = [user_id]

        if category_id:
            conditions.append("e.category_id = %s")
            params.append(category_id)

        if start_date:
            conditions.append("e.expense_date >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("e.expense_date <= %s")
            params.append(end_date)

        if payment_method and payment_method != 'All':
            conditions.append("e.payment_method = %s")
            params.append(payment_method)

        if min_amount is not None and min_amount > 0:
            conditions.append("e.amount >= %s")
            params.append(min_amount)

        if max_amount is not None and max_amount > 0:
            conditions.append("e.amount <= %s")
            params.append(max_amount)

        if search_query:
            conditions.append("(e.description ILIKE %s OR c.name ILIKE %s)")
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param])

        where_clause = " AND ".join(conditions)

        # Validate sorting column to prevent SQL injection
        allowed_sort = {
            'expense_date': 'e.expense_date',
            'amount': 'e.amount',
            'category': 'c.name',
            'payment_method': 'e.payment_method',
            'created_at': 'e.created_at'
        }
        order_col = allowed_sort.get(sort_by, 'e.expense_date')
        order_dir = 'ASC' if sort_order.upper() == 'ASC' else 'DESC'

        query = f"""
            SELECT 
                e.id,
                e.amount,
                e.expense_date,
                e.payment_method,
                e.description,
                e.created_at,
                c.id AS category_id,
                c.name AS category_name,
                c.color AS category_color
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE {where_clause}
            ORDER BY {order_col} {order_dir}, e.id DESC
        """

        if limit:
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

        return execute_query(query, params, fetch_all=True)

    # -------------------------------------------------------------------------
    # DASHBOARD HIGHLIGHT METRICS
    # -------------------------------------------------------------------------

    @staticmethod
    def get_total_expenses(user_id: int = 1) -> Dict[str, Any]:
        """Calculates total spent across all records using SQL SUM() and COUNT()."""
        query = """
            SELECT 
                COALESCE(SUM(amount), 0.00) AS total_amount,
                COUNT(id) AS total_count
            FROM expenses
            WHERE user_id = %s
        """
        result = execute_query(query, (user_id,), fetch_all=False)
        return result if result else {'total_amount': 0.00, 'total_count': 0}

    @staticmethod
    def get_monthly_total(user_id: int = 1, month_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculates spending for a given month or current month using date functions.
        Uses: SUM(), COUNT(), TO_CHAR()
        """
        if not month_str:
            query = """
                SELECT 
                    COALESCE(SUM(amount), 0.00) AS monthly_amount,
                    COUNT(id) AS monthly_count
                FROM expenses
                WHERE user_id = %s AND TO_CHAR(expense_date, 'YYYY-MM') = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
            """
            params = (user_id,)
        else:
            query = """
                SELECT 
                    COALESCE(SUM(amount), 0.00) AS monthly_amount,
                    COUNT(id) AS monthly_count
                FROM expenses
                WHERE user_id = %s AND TO_CHAR(expense_date, 'YYYY-MM') = %s
            """
            params = (user_id, month_str)

        result = execute_query(query, params, fetch_all=False)
        return result if result else {'monthly_amount': 0.00, 'monthly_count': 0}

    @staticmethod
    def get_highest_spending_category(user_id: int = 1, month_str: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Finds category with the highest total expenses.
        Uses: JOIN, SUM(), COUNT(), GROUP BY, ORDER BY, LIMIT
        """
        if month_str:
            query = """
                SELECT 
                    c.id AS category_id,
                    c.name AS category_name,
                    c.color AS category_color,
                    SUM(e.amount) AS total_spent,
                    COUNT(e.id) AS expense_count
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE e.user_id = %s AND TO_CHAR(e.expense_date, 'YYYY-MM') = %s
                GROUP BY c.id, c.name, c.color
                ORDER BY total_spent DESC
                LIMIT 1
            """
            params = (user_id, month_str)
        else:
            query = """
                SELECT 
                    c.id AS category_id,
                    c.name AS category_name,
                    c.color AS category_color,
                    SUM(e.amount) AS total_spent,
                    COUNT(e.id) AS expense_count
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE e.user_id = %s
                GROUP BY c.id, c.name, c.color
                ORDER BY total_spent DESC
                LIMIT 1
            """
            params = (user_id,)

        return execute_query(query, params, fetch_all=False)

    @staticmethod
    def get_recent_expenses(user_id: int = 1, limit: int = 8) -> List[Dict[str, Any]]:
        """Fetches recent expense transactions for dashboard feed."""
        query = """
            SELECT 
                e.id,
                e.amount,
                e.expense_date,
                e.payment_method,
                e.description,
                c.name AS category_name,
                c.color AS category_color
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = %s
            ORDER BY e.expense_date DESC, e.id DESC
            LIMIT %s
        """
        return execute_query(query, (user_id, limit), fetch_all=True)

    # -------------------------------------------------------------------------
    # ANALYSIS AND REPORTING METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def get_daily_report(user_id: int = 1, month_str: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Daily expense breakdown with SUM(), AVG(), COUNT(), GROUP BY.
        """
        if not month_str:
            query = """
                SELECT 
                    expense_date,
                    SUM(amount) AS daily_total,
                    AVG(amount) AS daily_average,
                    COUNT(id) AS transaction_count
                FROM expenses
                WHERE user_id = %s
                GROUP BY expense_date
                ORDER BY expense_date ASC
            """
            params = (user_id,)
        else:
            query = """
                SELECT 
                    expense_date,
                    SUM(amount) AS daily_total,
                    AVG(amount) AS daily_average,
                    COUNT(id) AS transaction_count
                FROM expenses
                WHERE user_id = %s AND TO_CHAR(expense_date, 'YYYY-MM') = %s
                GROUP BY expense_date
                ORDER BY expense_date ASC
            """
            params = (user_id, month_str)

        return execute_query(query, params, fetch_all=True)

    @staticmethod
    def get_weekly_report(user_id: int = 1) -> List[Dict[str, Any]]:
        """
        Weekly expense breakdown using ISO week via TO_CHAR(date, 'IYYY-"W"IW').
        Uses: SUM(), AVG(), COUNT(), GROUP BY
        """
        query = """
            SELECT 
                TO_CHAR(expense_date, 'IYYY-"W"IW') AS year_week,
                MIN(expense_date) AS week_start,
                MAX(expense_date) AS week_end,
                SUM(amount) AS weekly_total,
                AVG(amount) AS weekly_average,
                COUNT(id) AS transaction_count
            FROM expenses
            WHERE user_id = %s
            GROUP BY TO_CHAR(expense_date, 'IYYY-"W"IW')
            ORDER BY year_week DESC
        """
        return execute_query(query, (user_id,), fetch_all=True)

    @staticmethod
    def get_monthly_report(user_id: int = 1) -> List[Dict[str, Any]]:
        """
        Monthly spending breakdown across all months.
        Uses: SUM(), AVG(), COUNT(), GROUP BY TO_CHAR(date, 'YYYY-MM')
        """
        query = """
            SELECT 
                TO_CHAR(expense_date, 'YYYY-MM') AS month_year,
                SUM(amount) AS monthly_total,
                AVG(amount) AS monthly_average,
                COUNT(id) AS transaction_count
            FROM expenses
            WHERE user_id = %s
            GROUP BY TO_CHAR(expense_date, 'YYYY-MM')
            ORDER BY month_year DESC
        """
        return execute_query(query, (user_id,), fetch_all=True)

    @staticmethod
    def get_average_monthly_expenditure(user_id: int = 1) -> Dict[str, Any]:
        """
        Calculates the Average Monthly Expenditure across recorded active months.
        Uses: Subquery with SUM(), outer query with AVG()
        """
        query = """
            SELECT 
                ROUND(AVG(monthly_total), 2) AS average_monthly_spending,
                COUNT(month_year) AS months_count,
                SUM(monthly_total) AS total_spending_sum
            FROM (
                SELECT 
                    TO_CHAR(expense_date, 'YYYY-MM') AS month_year,
                    SUM(amount) AS monthly_total
                FROM expenses
                WHERE user_id = %s
                GROUP BY TO_CHAR(expense_date, 'YYYY-MM')
            ) AS monthly_totals
        """
        res = execute_query(query, (user_id,), fetch_all=False)
        return res if res else {'average_monthly_spending': 0.00, 'months_count': 0, 'total_spending_sum': 0.00}

    @staticmethod
    def get_category_wise_analysis(user_id: int = 1, month_str: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Category-wise spending analysis with percentage calculation.
        Uses: JOIN, SUM(), AVG(), COUNT(), GROUP BY
        """
        if month_str:
            query = """
                SELECT 
                    c.id AS category_id,
                    c.name AS category_name,
                    c.color AS category_color,
                    c.budget_limit,
                    COALESCE(SUM(e.amount), 0.00) AS total_spent,
                    COALESCE(AVG(e.amount), 0.00) AS avg_spent,
                    COUNT(e.id) AS transaction_count
                FROM categories c
                LEFT JOIN expenses e ON c.id = e.category_id AND e.user_id = %s AND TO_CHAR(e.expense_date, 'YYYY-MM') = %s
                WHERE c.user_id = %s
                GROUP BY c.id, c.name, c.color, c.budget_limit
                ORDER BY total_spent DESC
            """
            params = (user_id, month_str, user_id)
        else:
            query = """
                SELECT 
                    c.id AS category_id,
                    c.name AS category_name,
                    c.color AS category_color,
                    c.budget_limit,
                    COALESCE(SUM(e.amount), 0.00) AS total_spent,
                    COALESCE(AVG(e.amount), 0.00) AS avg_spent,
                    COUNT(e.id) AS transaction_count
                FROM categories c
                LEFT JOIN expenses e ON c.id = e.category_id AND e.user_id = %s
                WHERE c.user_id = %s
                GROUP BY c.id, c.name, c.color, c.budget_limit
                ORDER BY total_spent DESC
            """
            params = (user_id, user_id)

        rows = execute_query(query, params, fetch_all=True)
        total_all = sum(r['total_spent'] for r in rows) if rows else 0.0

        for r in rows:
            r['percentage'] = round((r['total_spent'] / total_all * 100.0), 2) if total_all > 0 else 0.0

        return rows

    @staticmethod
    def get_high_spending_categories(user_id: int = 1, threshold: float = 5000.0) -> List[Dict[str, Any]]:
        """
        Demonstrates HAVING clause: finds categories where total spent exceeds threshold.
        Uses: JOIN, SUM(), GROUP BY, HAVING, ORDER BY
        """
        query = """
            SELECT 
                c.id AS category_id,
                c.name AS category_name,
                c.color AS category_color,
                c.budget_limit,
                SUM(e.amount) AS total_spent,
                COUNT(e.id) AS transaction_count
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = %s
            GROUP BY c.id, c.name, c.color, c.budget_limit
            HAVING SUM(e.amount) > %s
            ORDER BY total_spent DESC
        """
        return execute_query(query, (user_id, threshold), fetch_all=True)

    @staticmethod
    def get_payment_method_breakdown(user_id: int = 1) -> List[Dict[str, Any]]:
        """
        Groups spending by payment method.
        Uses: SUM(), COUNT(), AVG(), GROUP BY
        """
        query = """
            SELECT 
                payment_method,
                SUM(amount) AS total_amount,
                COUNT(id) AS transaction_count,
                AVG(amount) AS avg_amount
            FROM expenses
            WHERE user_id = %s
            GROUP BY payment_method
            ORDER BY total_amount DESC
        """
        return execute_query(query, (user_id,), fetch_all=True)
