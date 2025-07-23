from app import db

def list_tables():
    query = """
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema');
    """
    result = db.engine.execute(query)
    tables = [(row.table_schema, row.table_name) for row in result]
    return tables

if __name__ == '__main__':
    tables = list_tables()
    print("Tables in the database:")
    for schema, table in tables:
        print(f"{schema}.{table}")
