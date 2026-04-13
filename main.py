"""
main.py - FastAPI Application
 Create the FastAPI Application
 SQL Validation + Step 8: Error Handling
"""

import os
import re
import json
import sqlite3

from google import genai
import plotly.graph_objects as go
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

# ── Load env ──────────────────────────────────────────────────────────────────
load_dotenv()

client  = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
DB_PATH = "clinic.db"

# ── Database schema ───────────────────────────────────────────────────────────
DB_SCHEMA = """
You are an expert SQLite assistant for a clinic management system.
The database has these tables:

patients(id, first_name, last_name, email, phone, date_of_birth, gender, city, registered_date)
  - gender values: ONLY 'M' or 'F' stored in database
  - For gender queries ALWAYS use: gender IN ('F', 'Female') for female, gender IN ('M', 'Male') for male

doctors(id, name, specialization, department, phone)
  - specialization values: 'Dermatology', 'Cardiology', 'Orthopedics', 'General', 'Pediatrics'

appointments(id, patient_id, doctor_id, appointment_date, status, notes)
  - status values: 'Scheduled', 'Completed', 'Cancelled', 'No-Show'

treatments(id, appointment_id, treatment_name, cost, duration_minutes)

invoices(id, patient_id, invoice_date, total_amount, paid_amount, status)
  - status values: 'Paid', 'Pending', 'Overdue'

STRICT RULES:
1. Write ONLY a single valid SQLite SELECT query.
2. Output ONLY the raw SQL - no explanation, no markdown, no code blocks.
3. NEVER use SELECT * - always name the columns explicitly.
4. NEVER show raw ID columns (patient_id, doctor_id) in output - always JOIN and show names.
5. When query asks which X has most/least Y - ALWAYS include both name AND count column.
   Example: SELECT city, COUNT(*) AS patient_count FROM patients GROUP BY city ORDER BY patient_count DESC LIMIT 1
6. For gender queries ALWAYS use IN: WHERE gender IN ('F', 'Female') or WHERE gender IN ('M', 'Male')
7. Use strftime('%Y-%m', date_col) for monthly grouping.
8. Use date('now', '-N months') for date filters.
9. For appointment queries always JOIN patients and doctors to show names not IDs.
"""

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(title="NL2SQL Clinic Chatbot", version="1.0.0")


# ── Request / Response models ─────────────────────────────────────────────────
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    message:    str
    sql_query:  str | None
    columns:    list[str]
    rows:       list[list[Any]]
    row_count:  int
    chart:      dict | None
    chart_type: str | None


# ── SQL Validation (PDF Page 12 - Step 7) ─────────────────────────────────────
FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "EXEC",   "GRANT",  "REVOKE", "SHUTDOWN", "XP_", "SP_",
]
FORBIDDEN_TABLES = ["sqlite_master", "sqlite_sequence", "sqlite_stat"]

def validate_sql(sql: str) -> tuple[bool, str]:
    sql_upper = sql.upper().strip()
    if not sql_upper.lstrip("(").startswith("SELECT"):
        return False, "Only SELECT queries are allowed."
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', sql_upper):
            return False, f"Forbidden keyword: '{kw}'. Only read-only queries allowed."
    for tbl in FORBIDDEN_TABLES:
        if tbl in sql.lower():
            return False, f"Access to system table '{tbl}' is not allowed."
    return True, ""


# ── Generate SQL via Gemini ───────────────────────────────────────────────────
def generate_sql(question: str) -> str:
    prompt   = f"{DB_SCHEMA}\n\nQuestion: {question}\n\nSQL:"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    sql = response.text.strip()
    sql = re.sub(r"```(?:sql)?", "", sql).replace("```", "").strip()
    return sql


# ── Run SQL against clinic.db ─────────────────────────────────────────────────
def run_sql(sql: str) -> tuple[list[str], list[list[Any]]]:
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(sql)
    columns = [d[0] for d in cursor.description] if cursor.description else []
    rows    = [list(row) for row in cursor.fetchall()]
    conn.close()
    return columns, rows


# ── Build Plotly chart ────────────────────────────────────────────────────────
def build_chart(columns: list, rows: list) -> tuple[dict | None, str | None]:
    try:
        if len(columns) == 2 and rows:
            x_vals = [str(r[0]) for r in rows]
            y_vals = [r[1] for r in rows]
            if not all(isinstance(v, (int, float)) for v in y_vals):
                return None, None
            if all(str(x).isdigit() for x in x_vals):
                return None, None
            fig = go.Figure(go.Bar(x=x_vals, y=y_vals, name=columns[1]))
            fig.update_layout(xaxis_title=columns[0], yaxis_title=columns[1])
            return json.loads(fig.to_json()), "bar"
    except Exception:
        pass
    return None, None


# ── POST /chat ────────────────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    question = request.question.strip()

    if not question:
        return ChatResponse(
            message="Please enter a question.",
            sql_query=None, columns=[], rows=[],
            row_count=0, chart=None, chart_type=None,
        )

    try:
        sql = generate_sql(question)
    except Exception as e:
        return ChatResponse(
            message=f"AI could not generate SQL: {str(e)}",
            sql_query=None, columns=[], rows=[],
            row_count=0, chart=None, chart_type=None,
        )

    is_valid, error_msg = validate_sql(sql)
    if not is_valid:
        return ChatResponse(
            message=error_msg,
            sql_query=sql, columns=[], rows=[],
            row_count=0, chart=None, chart_type=None,
        )

    try:
        columns, rows = run_sql(sql)
    except Exception as e:
        return ChatResponse(
            message=f"Database error: {str(e)}",
            sql_query=sql, columns=[], rows=[],
            row_count=0, chart=None, chart_type=None,
        )

    if not rows:
        return ChatResponse(
            message="No data found for your question.",
            sql_query=sql, columns=columns, rows=[],
            row_count=0, chart=None, chart_type=None,
        )

    chart, chart_type = build_chart(columns, rows)

    return ChatResponse(
        message=f"Here are the results for: '{question}'. Found {len(rows)} record(s).",
        sql_query=sql,
        columns=columns,
        rows=rows,
        row_count=len(rows),
        chart=chart,
        chart_type=chart_type,
    )


# ── GET /health ───────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    db_status = "disconnected"
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        db_status = "connected"
    except Exception:
        pass
    return {
        "status":             "ok",
        "database":           db_status,
        "agent_memory_items": 20,
    }


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)