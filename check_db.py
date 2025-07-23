#!/usr/bin/env python3
import sqlite3

def check_database():
    conn = sqlite3.connect('library_db.sqlite3')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Database Tables:")
    for table in tables:
        table_name = table[0]
        print(f"\n{table_name}:")
        
        # Get table structure
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == '__main__':
    check_database()
