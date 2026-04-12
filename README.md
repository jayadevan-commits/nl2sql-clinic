# NL2SQL Clinic Chatbot

A Natural Language to SQL chatbot built for a clinic management system. Users can ask questions in plain English and get results from the database without writing any SQL.

Built with Vanna AI 2.0, FastAPI, Google Gemini, and SQLite.

---

## What it does

- User types a question in plain English
- Google Gemini converts it to a SQL query
- SQL is validated before running
- Query runs on the clinic database
- Results are returned with a chart if applicable

---

## Tech Stack

- Python 3.10+
- Vanna AI 2.0
- FastAPI
- Google Gemini (gemini-2.5-flash)
- SQLite
- Plotly
- Uvicorn

---

## Project Structure

```
project/
├── setup_database.py   # Creates clinic.db and inserts dummy data
├── vanna_setup.py      # Initializes Vanna 2.0 Agent
├── seed_memory.py      # Seeds agent memory with 20 Q&A pairs
├── main.py             # FastAPI application
├── requirements.txt    # All dependencies
├── README.md           # This file
├── RESULTS.md          # Test results for 20 questions
└── clinic.db           # Auto-generated database file
```

---

## Setup Instructions

### Step 1 - Clone the repository

```bash
git clone https://github.com/your-username/nl2sql-clinic.git
cd nl2sql-clinic
```

### Step 2 - Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 - Add your API key

Create a `.env` file in the project folder:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

Get a free Gemini API key from: https://aistudio.google.com/apikey

### Step 4 - Create the database

```bash
python setup_database.py
```

This creates `clinic.db` with:
- 200 patients
- 15 doctors
- 500 appointments
- 350 treatments
- 300 invoices

### Step 5 - Seed agent memory

```bash
python seed_memory.py
```

This loads 20 question-SQL pairs into the Vanna agent memory so it has a head start on clinic queries.

### Step 6 - Start the server

```bash
uvicorn main:app --port 8000
```

Server runs at: http://localhost:8000

---

## How to test

### Option 1 - Swagger UI (Recommended)

FastAPI comes with a built-in test page. Open your browser and go to:

```
http://localhost:8000/docs
```

You will see all available endpoints. Click on POST /chat, click Try it out, type your question and click Execute to see the response.

### Option 2 - Thunder Client (VS Code)

1. Install Thunder Client extension in VS Code
2. Create a new POST request
3. URL: http://localhost:8000/chat
4. Body (JSON):
```json
{
  "question": "How many patients do we have?"
}
```
5. Click Send

---

## API Documentation

### POST /chat

Converts a plain English question to SQL and returns results.

**Request:**
```json
{
  "question": "How many patients do we have?"
}
```

**Response:**
```json
{
  "message": "Here are the results for: 'How many patients do we have?'. Found 1 record(s).",
  "sql_query": "SELECT COUNT(id) FROM patients",
  "columns": ["COUNT(id)"],
  "rows": [[200]],
  "row_count": 1,
  "chart": null,
  "chart_type": null
}
```

**Response with chart:**
```json
{
  "message": "Here are the results for: 'How many appointments does each doctor have?'. Found 15 record(s).",
  "sql_query": "SELECT d.name, COUNT(a.id) AS number_of_appointments FROM doctors d JOIN appointments a ON d.id = a.doctor_id GROUP BY d.id ORDER BY number_of_appointments DESC",
  "columns": ["name", "number_of_appointments"],
  "rows": [
    ["Dr. Ananya Pillai", 37],
    ["Dr. Suresh Nair", 37]
  ],
  "row_count": 15,
  "chart": {"data": [...], "layout": {...}},
  "chart_type": "bar"
}
```

---

### GET /health

Returns the system status.

**Response:**
```json
{
  "status": "ok",
  "database": "connected",
  "agent_memory_items": 20
}
```

---

## SQL Validation Rules

The system validates every SQL query before running it:

- Only SELECT queries are allowed
- INSERT, UPDATE, DELETE, DROP, ALTER, EXEC are blocked
- System tables like sqlite_master cannot be accessed

---

## Architecture Overview

```
User Question (plain English)
        |
        v
FastAPI (POST /chat)
        |
        v
Google Gemini generates SQL
        |
        v
SQL Validation (SELECT only, no dangerous keywords)
        |
        v
SQLite database execution
        |
        v
Results + Chart returned to user
```

---

## LLM Provider

This project uses Google Gemini (gemini-2.5-flash) as the LLM provider.
It is free to use via Google AI Studio.

---

## Run everything in one command

```bash
pip install -r requirements.txt && python setup_database.py && python seed_memory.py && uvicorn main:app --port 8000
```