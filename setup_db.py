import sqlite3
import random
from datetime import datetime, timedelta


def create_database():
    conn = sqlite3.connect("company_data.db")
    cursor = conn.cursor()

    # Create sales table with transaction details including ID, date, customer info, amount, and department
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS sales
                   (
                       transaction_id
                       INTEGER
                       PRIMARY
                       KEY,
                       date
                       TEXT,
                       customer_name
                       TEXT,
                       customer_email
                       TEXT,
                       amount
                       REAL,
                       department
                       TEXT
                   )
                   ''')

    cursor.execute('DELETE FROM sales')

    departments = ['Electronics', 'Clothing', 'Home', 'Sports', 'Health']
    data_pool = []

    # Generate 950 normal sales records with random dates, amounts ($10-$500), customer names, emails, and departments
    for i in range(950):
        date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        amount = round(random.uniform(10.0, 500.0), 2)
        name = f"Customer_{random.randint(1000, 9999)}"
        email = f"{name.lower()}@example.com"
        dept = random.choice(departments)

        data_pool.append((date, name, email, amount, dept))

    # Generate 20 records with missing email (NULL values) - "Unknown User" entries in Electronics department
    for _ in range(20):
        date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        data_pool.append((date, "Unknown User", None, round(random.uniform(20.0, 100.0), 2), "Electronics"))

    # Generate 10 erroneous records with negative amounts - "System Error" entries in Home department
    for _ in range(10):
        date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        data_pool.append((date, "System Error", "error@sys.com", -round(random.uniform(50.0, 500.0), 2), "Home"))

    # Generate 5 VIP records with extremely high amounts ($50,000-$999,999) in Health department
    for _ in range(5):
        date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        data_pool.append((date, "VIP Client", "vip@luxury.com", round(random.uniform(50000.0, 999999.0), 2), "Health"))

    # Generate 5 duplicate records (each duplicated twice) - "Clone User" with $150 in Clothing department (last 30 days)
    for _ in range(5):
        date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
        duplicate_record = (date, "Clone User", "clone@test.com", 150.0, "Clothing")
        data_pool.append(duplicate_record)
        data_pool.append(duplicate_record)

    # Shuffle all records to mix normal, anomalous, and duplicate data
    random.shuffle(data_pool)

    # Assign sequential transaction IDs to all records
    final_data = []
    for index, row in enumerate(data_pool, start=1):

        final_data.append((index,) + row)

    # Insert all 1000 records (950 normal + 20 missing emails + 10 errors + 5 VIP + 15 duplicates) into sales table
    cursor.executemany('''
                       INSERT INTO sales (transaction_id, date, customer_name, customer_email, amount, department)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ''', final_data)

    conn.commit()
    conn.close()
    print("Created database and sales table.")
    print(f"Inserted {len(final_data)} records into the sales table.")


if __name__ == "__main__":
    create_database()