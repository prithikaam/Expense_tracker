"""
Category Model for Expense Tracker System
Handles Category CRUD and budget limit aggregation queries (PostgreSQL).
"""

from typing import List, Dict, Any, Optional
from database import execute_query, execute_non_query


class CategoryModel:
    @staticmethod
    def get_all(user_id: int = 1) -> List[Dict[str, Any]]:
        """
        Retrieves all categories along with calculated total expenses and transaction count.
        Demonstrates: LEFT JOIN, SUM(), SUM() FILTER (this month), COUNT(), GROUP BY
        """
        query = """
            SELECT 
                c.id,
                c.name,
                c.description,
                c.color,
                c.budget_limit,
                c.created_at,
                COALESCE(SUM(e.amount), 0.00) AS total_spent,
                COALESCE(SUM(e.amount) FILTER (
                    WHERE TO_CHAR(e.expense_date, 'YYYY-MM') = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
                ), 0.00) AS month_spent,
                COUNT(e.id) AS expense_count
            FROM categories c
            LEFT JOIN expenses e ON c.id = e.category_id AND e.user_id = %s
            WHERE c.user_id = %s
            GROUP BY c.id, c.name, c.description, c.color, c.budget_limit, c.created_at
            ORDER BY c.name ASC
        """
        return execute_query(query, (user_id, user_id), fetch_all=True)

    @staticmethod
    def get_by_id(category_id: int, user_id: int = 1) -> Optional[Dict[str, Any]]:
        query = """
            SELECT 
                c.id,
                c.name,
                c.description,
                c.color,
                c.budget_limit,
                COALESCE(SUM(e.amount), 0.00) AS total_spent,
                COUNT(e.id) AS expense_count
            FROM categories c
            LEFT JOIN expenses e ON c.id = e.category_id AND e.user_id = %s
            WHERE c.id = %s AND c.user_id = %s
            GROUP BY c.id, c.name, c.description, c.color, c.budget_limit
        """
        return execute_query(query, (user_id, category_id, user_id), fetch_all=False)

    @staticmethod
    def create(user_id: int, name: str, description: str, color: str = '#4f46e5', budget_limit: float = 0.0) -> int:
        query = """
            INSERT INTO categories (user_id, name, description, color, budget_limit)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        return execute_non_query(query, (user_id, name, description, color, budget_limit))

    @staticmethod
    def update(category_id: int, user_id: int, name: str, description: str, color: str, budget_limit: float) -> int:
        query = """
            UPDATE categories
            SET name = %s, description = %s, color = %s, budget_limit = %s
            WHERE id = %s AND user_id = %s
        """
        return execute_non_query(query, (name, description, color, budget_limit, category_id, user_id))

    @staticmethod
    def delete(category_id: int, user_id: int = 1) -> int:
        query = "DELETE FROM categories WHERE id = %s AND user_id = %s"
        return execute_non_query(query, (category_id, user_id))
