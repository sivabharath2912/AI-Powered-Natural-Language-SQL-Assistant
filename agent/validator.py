def classify_sql(sql_query):

    sql_upper = sql_query.upper().strip()

    # Read operations
    if sql_upper.startswith("SELECT"):
        return "SAFE"

    # Controlled write operations
    elif (
        sql_upper.startswith("INSERT")
        or sql_upper.startswith("UPDATE")
    ):
        return "CONFIRM"

    # Dangerous operations
    elif (
        sql_upper.startswith("DELETE")
        or sql_upper.startswith("DROP")
        or sql_upper.startswith("ALTER")
        or sql_upper.startswith("TRUNCATE")
        or sql_upper.startswith("CREATE")
    ):
        return "BLOCK"

    else:
        return "BLOCK"


if __name__ == "__main__":

    sql = input("Enter SQL Query:\n")

    result = classify_sql(sql)

    print(result)