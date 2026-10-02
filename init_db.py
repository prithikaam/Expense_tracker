"""
Create (or reset) the database tables and load the sample data.

    python init_db.py           -> creates tables only if they are missing
    python init_db.py --reset   -> DROPS and recreates everything (all data lost)
"""

import sys

from database import init_db

if __name__ == "__main__":
    init_db(force="--reset" in sys.argv)
