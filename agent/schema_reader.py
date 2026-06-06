import sqlite3

import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "company.db"
)
def get_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    schema_info = ""

    # Get all tables
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table';
    """)

    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]

        schema_info += f"\nTable: {table_name}\n"

        cursor.execute(
            f"PRAGMA table_info({table_name});"
        )

        columns = cursor.fetchall()

        for column in columns:
            schema_info += (
                f" - {column[1]}\n"
            )

    conn.close()

    return schema_info


if __name__ == "__main__":
    print(get_schema())