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

st.sidebar.subheader(
    "Database Statistics"
)

import sqlite3

conn = sqlite3.connect(
    db_path
)

cursor = conn.cursor()

# Get all tables
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table';"
)

tables = cursor.fetchall()

# Total number of tables
st.sidebar.metric(
    "Tables",
    len(tables)
)

# Number of rows in each table
for table in tables:

    table_name = table[0]

    try:

        cursor.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        )

        row_count = cursor.fetchone()[0]

        st.sidebar.metric(
            table_name,
            row_count
        )

    except:

        pass

conn.close()

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

# ================= Dynamic Chart =================

    numeric_columns = df.select_dtypes(
        include=["int64", "float64"]
    ).columns

    if (
        "name" in df.columns
        and len(numeric_columns) > 0
    ):

        selected_column = numeric_columns[-1]

        st.subheader(
            f"{selected_column} Distribution"
        )

        chart_df = df[
            ["name", selected_column]
        ]

        st.bar_chart(
            chart_df.set_index(
                "name"
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
        st.session_state.sql_query,
        db_path
    )

    if columns:

        df = pd.DataFrame(
            rows,
            columns=columns
        )

        st.subheader(
            "Updated Table"
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