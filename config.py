"""
Central configuration. All values come from environment variables (or a local
.env file) so that no credentials or secret keys are stored in the source code.
Copy .env.example to .env and put your own values there.
"""

import os
import secrets

from dotenv import load_dotenv

load_dotenv()  # reads .env if it exists; harmless if it does not

# --- PostgreSQL connection -------------------------------------------------
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "expense_tracker")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

# --- Flask -----------------------------------------------------------------
# If SECRET_KEY is not set a random one is generated for this run only
# (sessions/flash messages still work; they just reset on restart).
SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

# --- Business settings -----------------------------------------------------
CURRENCY_SYMBOL = "₹"
HIGH_SPENDING_THRESHOLD = float(os.environ.get("HIGH_SPENDING_THRESHOLD", "5000"))
PAYMENT_METHODS = ["Cash", "UPI", "Credit Card", "Debit Card", "Net Banking"]
