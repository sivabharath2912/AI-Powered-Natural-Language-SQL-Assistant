from groq import Groq
from dotenv import load_dotenv
import os

from agent.schema_reader import get_schema

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_sql(
    user_query,
    db_path
):

    schema = get_schema(
        db_path
    )

    prompt = f"""
Database Schema:

{schema}

User Question:
{user_query}

Rules:
1. Generate only SQLite SQL.
2. Use only tables and columns provided.
3. Return only SQL.
4. No markdown.
5. No explanation.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    sql_query = response.choices[0].message.content.strip()

    return sql_query


# Testing Section
if __name__ == "__main__":

    db_path = "database/company.db"

    question = input(
        "Enter question: "
    )

    sql = generate_sql(
        question,
        db_path
    )

    print(
        "\nGenerated SQL:\n"
    )

    print(sql)