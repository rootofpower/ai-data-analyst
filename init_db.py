import pandas as pd
import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "company_data.db"
EXCEL_FILE = "excel_data.xlsx"

def load_excel_to_db():
    table_name = "accrual_accounts"
    try:
        print(f"Loading {EXCEL_FILE} into table '{table_name}'...")
        df = pd.read_excel(EXCEL_FILE)
        conn = sqlite3.connect(DB_NAME)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        print(f"Successfully loaded {len(df)} records into '{table_name}'.")
    except Exception as e:
        print(f"Error loading Excel: {e}")

def create_synthetic_sales():
    print("Generating synthetic sales data with anomalies...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            transaction_id INTEGER PRIMARY KEY,
            date TEXT,
            customer_name TEXT,
            customer_email TEXT,
            amount REAL,
            department TEXT
        )
    ''')
    cursor.execute('DELETE FROM sales')

    departments = ['Electronics', 'Clothing', 'Home', 'Sports', 'Health']
    data_pool = []

    # 1. Normal data (950 records)
    for _ in range(950):
        date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        amount = round(random.uniform(10.0, 500.0), 2)
        name = f"Customer_{random.randint(1000, 9999)}"
        email = f"{name.lower()}@example.com"
        dept = random.choice(departments)
        data_pool.append((date, name, email, amount, dept))

    # 2. Anomalies: Missing emails (20 records)
    for _ in range(20):
        date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        data_pool.append((date, "Unknown User", None, round(random.uniform(20.0, 100.0), 2), "Electronics"))

    # 3. Anomalies: Negative amounts (10 records)
    for _ in range(10):
        date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        data_pool.append((date, "System Error", "error@sys.com", -round(random.uniform(50.0, 500.0), 2), "Home"))

    # 4. Outliers: VIP (5 records)
    for _ in range(5):
        date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        data_pool.append((date, "VIP Client", "vip@luxury.com", round(random.uniform(50000.0, 999999.0), 2), "Health"))

    # 5. Duplicates (10 total records from 5 pairs)
    for _ in range(5):
        date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
        duplicate_record = (date, "Clone User", "clone@test.com", 150.0, "Clothing")
        data_pool.append(duplicate_record)
        data_pool.append(duplicate_record)

    random.shuffle(data_pool)

    final_data = [(index,) + row for index, row in enumerate(data_pool, start=1)]

    cursor.executemany('''
        INSERT INTO sales (transaction_id, date, customer_name, customer_email, amount, department)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', final_data)

    conn.commit()
    conn.close()
    print(f"Successfully inserted {len(final_data)} records into 'sales'.")

if __name__ == "__main__":
    print("Initializing Database Setup...")
    load_excel_to_db()
    create_synthetic_sales()
    print("Database setup complete. You can now run 'streamlit run app.py'.")