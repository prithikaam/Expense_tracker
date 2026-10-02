"""
User Model for Expense Tracker System
Handles user profiles and lookup queries.
"""

from typing import Optional, Dict, Any
from database import execute_query, execute_non_query


class UserModel:
    @staticmethod
    def get_by_id(user_id: int = 1) -> Optional[Dict[str, Any]]:
        query = "SELECT id, username, email, full_name, created_at FROM users WHERE id = %s"
        return execute_query(query, (user_id,), fetch_all=False)

    @staticmethod
    def get_by_username(username: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE username = %s"
        return execute_query(query, (username,), fetch_all=False)
