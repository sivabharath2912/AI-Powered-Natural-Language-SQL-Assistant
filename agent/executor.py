import sqlite3


def execute_query(
    sql_query,
    db_path
):

    conn = sqlite3.connect(
        db_path
    )

    cursor = conn.cursor()

    cursor.execute(
        sql_query
    )

    # SELECT queries
    if sql_query.upper().strip().startswith(
        "SELECT"
    ):

        rows = cursor.fetchall()

        column_names = [

            description[0]

            for description in cursor.description

        ]

        conn.close()

        return (
            column_names,
            rows
        )

    # INSERT and UPDATE queries
    else:

        conn.commit()

        conn.close()

        return (
            [],
            []
        )


# ----------------------
# Testing Section
# ----------------------

if __name__ == "__main__":

    db_path = "database/company.db"

    sql = input(
        "Enter SQL Query:\n"
    )

    columns, rows = execute_query(
        sql,
        db_path
    )

    print(
        "\nColumns:"
    )

    print(
        columns
    )

    print(
        "\nRows:"
    )

    for row in rows:

        print(
            row
        )