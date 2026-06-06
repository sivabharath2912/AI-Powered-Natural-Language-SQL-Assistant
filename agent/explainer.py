from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def explain_results(user_query, rows):
    """
    Generates a human-friendly explanation
    based on the user's question and database results.
    """

    # Handle empty results
    if not rows:
        return "No matching records were found."

    prompt = f"""
User Question:
{user_query}

Database Results:
{rows}

Instructions:
1. Explain the results in simple English.
2. Keep the explanation concise.
3. Mention important details when appropriate.
4. Do not use markdown.
5. Be user-friendly.
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

    explanation = response.choices[0].message.content.strip()

    return explanation


# -------------------------
# Testing Section
# -------------------------
if __name__ == "__main__":

    user_query = input("Enter Question:\n")

    print("\nEnter rows in Python list format.")
    print("Example:")
    print("[(3,'Sara',1,75000,'sara@company.com',6),"
          "(4,'Priya',3,80000,'priya@company.com',7)]")

    rows = eval(input("\nEnter Rows:\n"))

    explanation = explain_results(
        user_query,
        rows
    )

    print("\nExplanation:\n")
    print(explanation)