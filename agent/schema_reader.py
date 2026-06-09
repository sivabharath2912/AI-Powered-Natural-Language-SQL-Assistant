import sqlite3


def get_schema(db_path):

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    # Get all tables
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    )

    tables = cursor.fetchall()

    schema = ""

    # Get columns of each table
    for table in tables:

        table_name = table[0]

        schema += f"\nTable: {table_name}\n"

        cursor.execute(
            f"PRAGMA table_info({table_name})"
        )

        columns = cursor.fetchall()

        for column in columns:

            schema += (
                f"{column[1]} ({column[2]})\n"
            )

    conn.close()

    return schema


# Testing Section
if __name__ == "__main__":

    db_path = "database/company.db"

    schema = get_schema(db_path)

    print(schema)