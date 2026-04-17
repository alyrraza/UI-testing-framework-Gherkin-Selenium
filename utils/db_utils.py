# db_utils.py
# SQLite database se test data lena
# Real world: Test data ka store room

import os
from sqlalchemy import create_engine, text

# Database file ka path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "test_data.db")

def get_engine():
    # Database connection banao
    # SQLite — ek simple file based database
    # MariaDB jaisi complex setup nahi chahiye
    return create_engine(f"sqlite:///{DB_PATH}")

def get_login_credentials(user_type: str = "standard"):
    # Database se login credentials lao
    # user_type = "standard" ya "locked"
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT username, password FROM users WHERE user_type = :type"),
            {"type": user_type}
        )
        row = result.fetchone()
        if row:
            return {"username": row[0], "password": row[1]}
        # database mein nahi mila — default return karo
        return {"username": "standard_user", "password": "secret_sauce"}

def get_checkout_data():
    # Checkout ke liye test data lao
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT first_name, last_name, zip_code FROM checkout_data LIMIT 1")
        )
        row = result.fetchone()
        if row:
            return {
                "first_name": row[0],
                "last_name": row[1],
                "zip_code": row[2]
            }
        return {"first_name": "Ali", "last_name": "Raza", "zip_code": "12345"}