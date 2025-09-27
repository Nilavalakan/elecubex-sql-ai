from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil, os
from pathlib import Path
from app.db_utils import extract_sqlite_schema, execute_sql_select
from app.gemini_client import generate_sql_from_question
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TEMP_DIR = ROOT / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="SQL-Gemini Backend")

# Allow CORS from frontend (adjust origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to specific origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_db")
async def upload_db(file: UploadFile = File(...)):
    # Only accept .db or .sqlite or .sqlite3 for this starter
    filename = file.filename
    if not filename.lower().endswith((".db", ".sqlite", ".sqlite3")):
        raise HTTPException(status_code=400, detail="Please upload a SQLite .db/.sqlite file")

    dest_path = TEMP_DIR / filename

    # Save uploaded file
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "uploaded", "db_path": str(dest_path)}

@app.post("/ask")
async def ask_question(db_path: str = Form(...), question: str = Form(...)):
    """
    Expects form-data with fields:
      - db_path: path returned from /upload_db (string)
      - question: natural language question (string)
    """
    if not os.path.exists(db_path):
        raise HTTPException(status_code=400, detail="db_path not found on server")

    # 1. Extract schema
    try:
        schema_text = extract_sqlite_schema(db_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract schema: {e}")

    # 2. Ask Gemini (generate SQL)
    try:
        sql_query = generate_sql_from_question(schema=schema_text, question=question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")

    if not isinstance(sql_query, str) or sql_query.strip() == "":
        raise HTTPException(status_code=500, detail="Empty SQL returned by Gemini")

    # 3. Basic safety: allow only SELECT queries for now
    cleaned = sql_query.strip().lower()
    if not cleaned.startswith("select"):
        return {
            "error": "Only SELECT queries are allowed in this starter for safety.",
            "sql": sql_query
        }

    # 4. Execute SQL
    try:
        rows, columns = execute_sql_select(db_path, sql_query)
    except Exception as e:
        return {"error": f"SQL execution error: {e}", "sql": sql_query}

    # 5. Return result
    return {
        "sql": sql_query,
        "columns": columns,
        "rows": rows
    }
