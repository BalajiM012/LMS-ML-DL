from app import db
from sqlalchemy import text

def apply_sql_file(filename):
    with open(filename, 'r') as file:
        sql = file.read()
    with db.engine.connect() as connection:
        connection.execute(text(sql))
        # No commit needed for DDL statements in SQLAlchemy 1.4+

if __name__ == '__main__':
    apply_sql_file('migrations/002_create_borrow_records_table_if_not_exists.sql')
    print("Migration applied successfully.")
