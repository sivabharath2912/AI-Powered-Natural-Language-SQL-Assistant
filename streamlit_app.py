import streamlit as st
import pandas as pd
import shutil
import os

from agent.sql_generator import generate_sql
from agent.validator import classify_sql
from agent.executor import execute_query
from agent.explainer import explain_results


st.set_page_config(
    page_title="AI SQL Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

.stApp {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
}

section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
}

div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 20px;
}

.stButton > button {
    background: linear-gradient(to right, #00c6ff, #0072ff);
    color: white;
    border-radius: 20px;
    font-size: 16px;
    font-weight: bold;
}

h1 {
    color: #00e5ff;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
"""
# 🤖 AI-Powered Natural Language SQL Assistant

Interact with databases using natural language powered by Llama 3.3 and Groq API.
"""
)

# ================= Database Upload =================

os.makedirs(
    "uploaded_databases",
    exist_ok=True
)

uploaded_file = st.sidebar.file_uploader(
    "Upload SQLite Database",
    type=["db"]
)

# Default database
db_path = "database/company.db"

if uploaded_file is not None:

    db_path = os.path.join(
        "uploaded_databases",
        uploaded_file.name
    )

    with open(
        db_path,
        "wb"
    ) as file:

        file.write(
            uploaded_file.getbuffer()
        )

    st.sidebar.success(
        f"{uploaded_file.name} uploaded successfully."
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
    "SELECT COUNT(*) AS total_employees FROM employees",
    db_path
)

department_columns, department_rows = execute_query(
    "SELECT COUNT(*) AS total_departments FROM departments",
    db_path
)

salary_columns, salary_rows = execute_query(
    "SELECT AVG(salary) AS average_salary FROM employees",
    db_path
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

with st.container():

    st.subheader(
        "Ask Your Question"
    )

    user_query = st.text_input(
        "",
        placeholder="Example: Show employees earning above 70000"
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
             user_query,
            db_path
        )

        st.session_state.operation_type = classify_sql(
            st.session_state.sql_query
        )

        st.session_state.query_executed = False

if st.session_state.sql_query:

    with st.expander(
        "Generated SQL"
    ):

        st.code(
            st.session_state.sql_query,
            language="sql"
        )

# ===================================================
# SAFE QUERIES (SELECT)
# ===================================================

if (
    st.session_state.operation_type == "SAFE"
    and not st.session_state.query_executed
):

    columns, rows = execute_query(
    st.session_state.sql_query,
    db_path
    )

    df = pd.DataFrame(
        rows,
        columns=columns
    )

    # Query Results

    csv = df.to_csv(
        index=False
    )   
    left_col, right_col = st.columns(
        [3,1]
    )

    with left_col:

        st.subheader(
            "Query Results"
        )

    with right_col:

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="results.csv",
            mime="text/csv"
        )

    st.dataframe(
        df,
        use_container_width=True
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
    """,
    db_path
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
         st.session_state.sql_query,
        db_path
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
    "SELECT * FROM employees",
    db_path
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