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


def execute_query(sql_query):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(sql_query)

    # SELECT queries
    if sql_query.upper().strip().startswith("SELECT"):

        rows = cursor.fetchall()

        column_names = [
            description[0]
            for description in cursor.description
        ]

        conn.close()

        return column_names, rows

    # INSERT and UPDATE queries
    else:

        conn.commit()

        conn.close()

        return [], []


if __name__ == "__main__":

    sql = input("Enter SQL Query:\n")

    columns, rows = execute_query(sql)

    print("\nColumns:")
    print(columns)

    print("\nRows:")

    for row in rows:
        print(row)