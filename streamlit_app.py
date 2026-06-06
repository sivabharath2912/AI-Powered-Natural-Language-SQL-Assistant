import streamlit as st
import pandas as pd
import shutil

from agent.sql_generator import generate_sql
from agent.validator import classify_sql
from agent.executor import execute_query
from agent.explainer import explain_results


st.set_page_config(
    page_title="AI SQL Assistant",
    layout="wide"
)

st.title(
    "🤖 AI-Powered Natural Language SQL Assistant"
)


# ================= Session State =================

if "sql_query" not in st.session_state:
    st.session_state.sql_query = ""

if "operation_type" not in st.session_state:
    st.session_state.operation_type = ""

if "user_query" not in st.session_state:
    st.session_state.user_query = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "query_executed" not in st.session_state:
    st.session_state.query_executed = False

# ================= Sidebar =================

st.sidebar.title(
    "AI SQL Assistant"
)

# ================= Database Statistics =================

employee_columns, employee_rows = execute_query(
    "SELECT COUNT(*) AS total_employees FROM employees"
)

department_columns, department_rows = execute_query(
    "SELECT COUNT(*) AS total_departments FROM departments"
)

salary_columns, salary_rows = execute_query(
    "SELECT AVG(salary) AS average_salary FROM employees"
)

st.sidebar.subheader(
    "Database Statistics"
)

st.sidebar.metric(
    "Total Employees",
    employee_rows[0][0]
)

st.sidebar.metric(
    "Total Departments",
    department_rows[0][0]
)

st.sidebar.metric(
    "Average Salary",
    round(salary_rows[0][0], 2)
)

st.sidebar.subheader(
    "Query History"
)

for query in reversed(
    st.session_state.history
):

    st.sidebar.write(
        query
    )


if st.sidebar.button(
    "Reset Database"
):

    shutil.copy(
        "database/company_backup.db",
        "database/company.db"
    )

    st.session_state.sql_query = ""
    st.session_state.operation_type = ""
    st.session_state.user_query = ""
    st.session_state.query_executed = False
    st.session_state.history = []

    st.rerun()

# ================= Input =================

user_query = st.text_input(
    "Enter your question:"
)


if st.button(
    "Generate Query"
):

    if user_query:

        st.session_state.user_query = user_query

        st.session_state.history.append(
            user_query
        )

        st.session_state.sql_query = generate_sql(
            user_query
        )

        st.session_state.operation_type = classify_sql(
            st.session_state.sql_query
        )

        st.session_state.query_executed = False

if st.session_state.sql_query:

    st.subheader(
        "Generated SQL"
    )

    st.code(
        st.session_state.sql_query
    )

if st.session_state.sql_query:

    st.subheader(
        "Generated SQL"
    )

    st.code(
        st.session_state.sql_query
    )

# ===================================================
# SAFE QUERIES (SELECT)
# ===================================================

if (
    st.session_state.operation_type == "SAFE"
    and not st.session_state.query_executed
):

    columns, rows = execute_query(
        st.session_state.sql_query
    )

    df = pd.DataFrame(
        rows,
        columns=columns
    )

    # Query Results
    st.subheader(
        "Query Results"
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    # Download CSV
    csv = df.to_csv(
        index=False
    )

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="results.csv",
        mime="text/csv"
    )

    # ================= Salary Distribution =================

    if (
        "name" in df.columns
        and "salary" in df.columns
    ):

        st.subheader(
            "Salary Distribution"
        )

        salary_df = df[
            ["name", "salary"]
        ]

        st.bar_chart(
            salary_df.set_index(
                "name"
            )
        )

    # ================= Department Analytics =================

    dept_columns, dept_rows = execute_query(
    """
    SELECT
        d.department_name,
        COUNT(*) AS employee_count
    FROM employees e
    JOIN departments d
    ON e.department_id = d.department_id
    GROUP BY d.department_name
    """
    )

    dept_df = pd.DataFrame(
        dept_rows,
        columns=dept_columns
    )

    st.subheader(
        "Employees per Department"
    )

    st.bar_chart(
        dept_df.set_index(
            "department_name"
        )
    )

    # ================= Explanation =================

    explanation = explain_results(
        st.session_state.user_query,
        rows
    )

    st.subheader(
        "Explanation"
    )

    st.write(
        explanation
    )

    st.session_state.query_executed = True

# ===================================================
# INSERT / UPDATE
# ===================================================

elif (
    st.session_state.operation_type == "CONFIRM"
    and not st.session_state.query_executed
):

    st.warning(
        "This query modifies the database."
    )

    if st.button(
        "Confirm Execution"
    ):

        execute_query(
            st.session_state.sql_query
        )

        st.success(
            "Query executed successfully ✅"
        )

        st.session_state.query_executed = True

# ===================================================
# UPDATED TABLE
# ===================================================

if (
    st.session_state.query_executed
    and st.session_state.operation_type == "CONFIRM"
):

    columns, rows = execute_query(
        "SELECT * FROM employees"
    )

    df = pd.DataFrame(
        rows,
        columns=columns
    )

    st.subheader(
        "Updated Employees Table"
    )

    st.dataframe(
        df,
        use_container_width=True
    )

# ===================================================
# BLOCKED QUERIES
# ===================================================

elif (
    st.session_state.operation_type == "BLOCK"
):

    st.error(
        "Dangerous query blocked ❌"
    )