import pandas as pd
import sqlite3

excel = "excel_data.xlsx"

table_name = "accrual_accounts"

try:
    print(f"Loading {table_name} ...")
    df = pd.read_excel(excel)
    conn = sqlite3.connect("company_data.db")
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print("Successfully loaded excel file.")
except Exception as e:
    print(f"Error: {e}")