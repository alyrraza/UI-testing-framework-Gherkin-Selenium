# seed_data.py
# Database aur Excel mein test data daalo
# Real world: Store room mein pehle se saman rakh do

import os
import openpyxl
from sqlalchemy import create_engine, text

DB_PATH = os.path.join(os.path.dirname(__file__), "test_data.db")

def create_database():
    # Database tables banao aur data daalo
    engine = create_engine(f"sqlite:///{DB_PATH}")

    with engine.connect() as conn:
        # users table banao
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT,
                user_type TEXT
            )
        """))

        # checkout_data table banao
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS checkout_data (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                zip_code TEXT
            )
        """))

        # data daalo — pehle delete karo phir insert
        conn.execute(text("DELETE FROM users"))
        conn.execute(text("""
            INSERT INTO users (username, password, user_type) VALUES
            ('standard_user', 'secret_sauce', 'standard'),
            ('locked_out_user', 'secret_sauce', 'locked')
        """))

        conn.execute(text("DELETE FROM checkout_data"))
        conn.execute(text("""
            INSERT INTO checkout_data (first_name, last_name, zip_code) VALUES
            ('Ali', 'Raza', '12345')
        """))
        conn.commit()

    print("Database created!")

def create_excel():
    # Excel file banao test data ke saath
    workbook = openpyxl.Workbook()

    # Login sheet
    login_sheet = workbook.active
    login_sheet.title = "Login"

    # Headers
    login_sheet.append(["username", "password", "expected"])

    # Data rows
    login_sheet.append(["standard_user", "secret_sauce", "success"])
    login_sheet.append(["locked_out_user", "secret_sauce", "failure"])
    login_sheet.append(["standard_user", "wrong_pass", "failure"])

    # Checkout sheet
    checkout_sheet = workbook.create_sheet("Checkout")
    checkout_sheet.append(["first_name", "last_name", "zip_code"])
    checkout_sheet.append(["Ali", "Raza", "12345"])
    checkout_sheet.append(["John", "Doe", "54321"])

    excel_path = os.path.join(os.path.dirname(__file__), "test_data.xlsx")
    workbook.save(excel_path)
    print("Excel created!")

if __name__ == "__main__":
    create_database()
    create_excel()