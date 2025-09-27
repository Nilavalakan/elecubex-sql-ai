import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini with your API key
genai.configure(api_key=os.environ.get("AIzaSyByL8__D8fNR7I77uQpVTmkRvmcfAcmcI0"))

def generate_sql_from_question(schema: str, question: str) -> str:
    """
    Uses Gemini to generate a SQL query from a natural language question.
    Only returns SQL (no explanations).
    """
    prompt = f"""
    You are an assistant that converts natural language to SQL.
    Database schema:
    {schema}

    Generate a single valid SQL SELECT query (no extra explanation) for:
    {question}

    Only output the SQL.
    """

    try:
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
        sql = response.text.strip()
        return sql
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}")
