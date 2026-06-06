# AI-Powered Natural Language SQL Assistant

## Overview

This project allows users to interact with a SQLite database using natural language instead of writing SQL queries manually. The system converts user questions into SQL queries, executes them, and provides results along with simple explanations.

## Features

* Natural Language to SQL conversion
* Query validation and execution
* Interactive Streamlit interface
* Query history tracking
* CSV download support
* Salary distribution and department analytics
* Controlled INSERT and UPDATE operations
* Blocking of dangerous queries
* Database reset functionality

## Workflow

```text
User Question
      ↓
SQL Generator
      ↓
SQL Validator
      ↓
Query Executor
      ↓
SQLite Database
      ↓
Result Explainer
      ↓
Streamlit Interface
```

## Technologies Used

* Python
* SQLite
* Streamlit
* Groq API
* Pandas

## Folder Structure

```text
SQL-agent
│
├── streamlit_app.py
├── requirements.txt
├── .env
├── database
├── agent
└── tests
```

## Installation

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
streamlit run streamlit_app.py
```

## Security Measures

* SELECT queries are executed directly.
* INSERT and UPDATE queries require confirmation.
* DELETE, DROP, ALTER, CREATE, and TRUNCATE operations are blocked to maintain database integrity.

## Future Scope

* Multi-database support
* Role-based access control
* Export to Excel/PDF
* Advanced analytics dashboard
* Cloud database integration

## Conclusion

This project demonstrates the integration of Large Language Models with databases to provide a secure, interactive, and user-friendly approach for querying data using natural language.
