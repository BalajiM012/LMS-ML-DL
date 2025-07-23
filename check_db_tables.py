import sqlite3
import sys

def main():
    db_path = "c:/Users/admin/library-management-system/library-management-system-2/library_db.sqlite3"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Tables in the database:")
        print(tables)
        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
