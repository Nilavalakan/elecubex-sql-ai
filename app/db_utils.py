import sqlite3
from typing import Tuple, List

def extract_sqlite_schema(db_path: str) -> str:
    """
    Return a human-readable schema description for the SQLite DB.
    """
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()
    schema_lines = []
    for (tname,) in tables:
        cols = cur.execute(f"PRAGMA table_info('{tname}')").fetchall()
        col_names = [c[1] for c in cols]  # 2nd column is name
        schema_lines.append(f"Table {tname}: columns = {col_names}")

    con.close()
    return "\n".join(schema_lines)

def execute_sql_select(db_path: str, sql: str) -> Tuple[List[Tuple], List[str]]:
    """
    Execute a SELECT query and return (rows, column_names).
    """
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    column_names = [d[0] for d in cur.description] if cur.description else []
    con.close()
    return rows, column_names
