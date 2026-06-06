from agent.sql_generator import generate_sql
from agent.validator import classify_sql
from agent.executor import execute_query
from agent.explainer import explain_results


def main():

    user_query = input("Ask a question:\n")

    # Generate SQL
    sql_query = generate_sql(user_query)

    print("\nGenerated SQL:\n")
    print(sql_query)

    operation_type = classify_sql(sql_query)

    # ---------------- SAFE ----------------

    if operation_type == "SAFE":

        columns, rows = execute_query(sql_query)

        print("\nRows Returned:\n")

        for row in rows:
            print(row)

        explanation = explain_results(
            user_query,
            rows
        )

        print("\nExplanation:\n")
        print(explanation)

    # ---------------- CONFIRM ----------------

    elif operation_type == "CONFIRM":

        print(
            "\nThis query modifies the database."
        )

        choice = input(
            "Execute query? (Y/N): "
        )

        if choice.upper() == "Y":

            execute_query(sql_query)

            print(
                "\nQuery executed successfully ✅"
            )

        else:

            print(
                "\nOperation cancelled ❌"
            )

    # ---------------- BLOCK ----------------

    else:

        print(
            "\nDangerous query blocked ❌"
        )


if __name__ == "__main__":
    main()