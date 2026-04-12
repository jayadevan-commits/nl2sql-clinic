"""
seed_memory.py
Pre-seeds the Vanna 2.0 DemoAgentMemory with 15 question-SQL pairs.
PDF Page 10 — "Pre-seed the agent memory with at least 15 known good
question-SQL pairs so the agent has a head start."

Categories required by PDF:
  - Patient queries   (count, list, filter by city/gender)
  - Doctor queries    (appointments per doctor, busiest doctor)
  - Appointment queries (by status, by month, by doctor)
  - Financial queries (revenue, unpaid invoices, average cost)
  - Time-based queries (last 3 months, monthly trends)
"""

import asyncio
from vanna.capabilities.agent_memory import ToolMemory
from vanna.core.user.models import User
import uuid
from vanna.core.tool import ToolContext
from vanna.integrations.local.agent_memory import DemoAgentMemory

# ── 15 Q&A pairs covering all 5 categories from PDF Page 10 ──────────────────

TRAINING_PAIRS = [

    # ── Category 1: Patient queries ──────────────────────────────────────────

    ToolMemory(
        question="How many patients do we have?",          # Example from PDF
        tool_name="run_sql",
        args={"sql": "SELECT COUNT(*) AS total_patients FROM patients"}
    ),

    ToolMemory(
        question="List all patients and their cities",
        tool_name="run_sql",
        args={"sql": """
            SELECT first_name, last_name, city
            FROM patients
            ORDER BY city, last_name
        """}
    ),

    ToolMemory(
        question="How many female patients do we have?",
        tool_name="run_sql",
        args={"sql": """
            SELECT COUNT(*) AS female_patients
            FROM patients
            WHERE gender = 'F'
        """}
    ),

    ToolMemory(
        question="Which city has the most patients?",      # Example from PDF
        tool_name="run_sql",
        args={"sql": """
            SELECT city, COUNT(*) AS patient_count
            FROM patients
            GROUP BY city
            ORDER BY patient_count DESC
            LIMIT 1
        """}
    ),

    ToolMemory(
        question="List patients who visited more than 3 times",
        tool_name="run_sql",
        args={"sql": """
            SELECT p.first_name, p.last_name, COUNT(a.id) AS visit_count
            FROM patients p
            JOIN appointments a ON p.id = a.patient_id
            GROUP BY p.id
            HAVING visit_count > 3
            ORDER BY visit_count DESC
        """}
    ),

    # ── Category 2: Doctor queries ────────────────────────────────────────────

    ToolMemory(
        question="List all doctors and their specializations",
        tool_name="run_sql",
        args={"sql": """
            SELECT name, specialization, department
            FROM doctors
            ORDER BY specialization, name
        """}
    ),

    ToolMemory(
        question="Which doctor has the most appointments?",
        tool_name="run_sql",
        args={"sql": """
            SELECT d.name, d.specialization, COUNT(a.id) AS total_appointments
            FROM doctors d
            JOIN appointments a ON d.id = a.doctor_id
            GROUP BY d.id
            ORDER BY total_appointments DESC
            LIMIT 1
        """}
    ),

    ToolMemory(
        question="How many appointments does each doctor have?",
        tool_name="run_sql",
        args={"sql": """
            SELECT d.name, d.specialization, COUNT(a.id) AS appointment_count
            FROM doctors d
            LEFT JOIN appointments a ON d.id = a.doctor_id
            GROUP BY d.id
            ORDER BY appointment_count DESC
        """}
    ),

    # ── Category 3: Appointment queries ───────────────────────────────────────

    ToolMemory(
        question="Show me appointments for last month",
        tool_name="run_sql",
        args={"sql": """
            SELECT a.id, p.first_name, p.last_name, d.name AS doctor,
                   a.appointment_date, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            WHERE appointment_date >= date('now', '-1 month')
            ORDER BY appointment_date DESC
        """}
    ),

    ToolMemory(
        question="How many cancelled appointments last quarter?",
        tool_name="run_sql",
        args={"sql": """
            SELECT COUNT(*) AS cancelled_count
            FROM appointments
            WHERE status = 'Cancelled'
            AND appointment_date >= date('now', '-3 months')
        """}
    ),

    ToolMemory(
        question="Show monthly appointment count for the past 6 months",
        tool_name="run_sql",
        args={"sql": """
            SELECT strftime('%Y-%m', appointment_date) AS month,
                   COUNT(*) AS appointment_count
            FROM appointments
            WHERE appointment_date >= date('now', '-6 months')
            GROUP BY month
            ORDER BY month ASC
        """}
    ),

    # ── Category 4: Financial queries ─────────────────────────────────────────

    ToolMemory(
        question="What is the total revenue?",
        tool_name="run_sql",
        args={"sql": """
            SELECT SUM(total_amount) AS total_revenue
            FROM invoices
        """}
    ),

    ToolMemory(
        question="Show revenue by doctor",                 # Example from PDF
        tool_name="run_sql",
        args={"sql": """
            SELECT d.name, SUM(i.total_amount) AS total_revenue
            FROM invoices i
            JOIN appointments a ON a.patient_id = i.patient_id
            JOIN doctors d ON d.id = a.doctor_id
            GROUP BY d.name
            ORDER BY total_revenue DESC
        """}
    ),

    ToolMemory(
        question="Show unpaid invoices",
        tool_name="run_sql",
        args={"sql": """
            SELECT p.first_name, p.last_name,
                   i.invoice_date, i.total_amount, i.paid_amount,
                   (i.total_amount - i.paid_amount) AS balance_due,
                   i.status
            FROM invoices i
            JOIN patients p ON p.id = i.patient_id
            WHERE i.status IN ('Pending', 'Overdue')
            ORDER BY balance_due DESC
        """}
    ),

    # ── Category 5: Time-based queries ────────────────────────────────────────

    ToolMemory(
        question="Show patient registration trend by month",
        tool_name="run_sql",
        args={"sql": """
            SELECT strftime('%Y-%m', registered_date) AS month,
                   COUNT(*) AS new_patients
            FROM patients
            GROUP BY month
            ORDER BY month ASC
        """}
    ),

    ToolMemory(
        question="Revenue trend by month",
        tool_name="run_sql",
        args={"sql": """
            SELECT strftime('%Y-%m', invoice_date) AS month,
                   SUM(total_amount) AS monthly_revenue
            FROM invoices
            GROUP BY month
            ORDER BY month ASC
        """}
    ),

    ToolMemory(
        question="Average appointment duration by doctor",
        tool_name="run_sql",
        args={"sql": """
            SELECT d.name,
                   ROUND(AVG(t.duration_minutes), 2) AS avg_duration_minutes
            FROM doctors d
            JOIN appointments a ON d.id = a.doctor_id
            JOIN treatments t ON a.id = t.appointment_id
            GROUP BY d.id
            ORDER BY avg_duration_minutes DESC
        """}
    ),

    ToolMemory(
        question="List patients with overdue invoices",
        tool_name="run_sql",
        args={"sql": """
            SELECT p.first_name, p.last_name,
                   i.invoice_date,
                   i.total_amount,
                   i.paid_amount,
                   (i.total_amount - i.paid_amount) AS balance_due
            FROM invoices i
            JOIN patients p ON p.id = i.patient_id
            WHERE i.status = 'Overdue'
            ORDER BY balance_due DESC
        """}
    ),

    ToolMemory(
        question="Compare revenue between departments",
        tool_name="run_sql",
        args={"sql": """
            SELECT d.department,
                   SUM(i.total_amount) AS total_revenue
            FROM invoices i
            JOIN appointments a ON a.patient_id = i.patient_id
            JOIN doctors d ON d.id = a.doctor_id
            GROUP BY d.department
            ORDER BY total_revenue DESC
        """}
    ),

    ToolMemory(
        question="Average treatment cost by specialization",
        tool_name="run_sql",
        args={"sql": """
            SELECT d.specialization,
                   ROUND(AVG(t.cost), 2) AS avg_cost
            FROM treatments t
            JOIN appointments a ON t.appointment_id = a.id
            JOIN doctors d ON a.doctor_id = d.id
            GROUP BY d.specialization
            ORDER BY avg_cost DESC
        """}
    ),

]


# ── Seed function ─────────────────────────────────────────────────────────────

async def seed_memory() -> None:
    print("🧠 Starting memory seeding...\n")

    memory = DemoAgentMemory()

    # Build context with all required fields
    import uuid
    user    = User(id="admin", email="admin@clinic.com", group_memberships=["users"])
    context = ToolContext(
        user=user,
        conversation_id=str(uuid.uuid4()),
        request_id=str(uuid.uuid4()),
        agent_memory=memory,
    )

    for i, pair in enumerate(TRAINING_PAIRS, start=1):
        await memory.save_tool_usage(
            question=pair.question,
            tool_name=pair.tool_name,
            args=pair.args,
            context=context,
            success=True,
        )
        print(f"  ✅ [{i:02d}/{len(TRAINING_PAIRS)}] Seeded: {pair.question}")

    print(f"\n🎉 Done! {len(TRAINING_PAIRS)} Q&A pairs seeded into agent memory.")
    print("   The agent now has a head start on clinic queries.")


if __name__ == "__main__":
    asyncio.run(seed_memory())