"""
Input validation helpers. Each function returns a clean value or raises
ValidationError with a message that is safe to show to the user.
"""

import math
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import config


class ValidationError(Exception):
    """Raised when user input is missing or invalid."""


def parse_amount(raw: str, field: str = "Amount", allow_zero: bool = False) -> float:
    raw = (raw or "").strip()
    if not raw:
        raise ValidationError(f"{field} is required.")
    try:
        value = Decimal(raw)
    except InvalidOperation:
        raise ValidationError(f"{field} must be a valid number.")
    if not value.is_finite():
        raise ValidationError(f"{field} must be a valid number.")
    if value < 0 or (value == 0 and not allow_zero):
        raise ValidationError(f"{field} must be greater than zero." if not allow_zero
                              else f"{field} cannot be negative.")
    if value >= Decimal("100000000"):
        raise ValidationError(f"{field} is too large (maximum 99,999,999.99).")
    return float(round(value, 2))


def parse_date(raw: str, field: str = "Date") -> str:
    raw = (raw or "").strip()
    if not raw:
        raise ValidationError(f"{field} is required.")
    try:
        parsed = datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError(f"{field} must be a valid date (YYYY-MM-DD).")
    if parsed > date.today():
        raise ValidationError(f"{field} cannot be in the future.")
    if parsed.year < 2000:
        raise ValidationError(f"{field} is too far in the past.")
    return parsed.isoformat()


def parse_id(raw: str, field: str = "Category") -> int:
    raw = (raw or "").strip()
    if not raw.isdigit():
        raise ValidationError(f"Please select a valid {field.lower()}.")
    return int(raw)


def parse_payment_method(raw: str) -> str:
    raw = (raw or "").strip() or "Cash"
    if raw not in config.PAYMENT_METHODS:
        raise ValidationError("Please choose a valid payment method.")
    return raw


def parse_text(raw: str, field: str, max_len: int, required: bool = False) -> str:
    value = (raw or "").strip()
    if required and not value:
        raise ValidationError(f"{field} cannot be empty.")
    if len(value) > max_len:
        raise ValidationError(f"{field} must be at most {max_len} characters.")
    return value


def parse_color(raw: str) -> str:
    raw = (raw or "").strip() or "#4f46e5"
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", raw):
        raise ValidationError("Colour must be a hex code like #4f46e5.")
    return raw
