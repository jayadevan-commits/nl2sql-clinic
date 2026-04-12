import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "clinic.db"

# ── Seed data ────────────────────────────────────────────────────────────────

FIRST_NAMES = [
    "Aarav","Priya","Ravi","Sneha","Kiran","Anjali","Vikram","Divya","Arjun","Meena",
    "Suresh","Lakshmi","Rahul","Pooja","Anil","Nisha","Deepak","Kavya","Sanjay","Rekha",
    "Mohan","Usha","Prakash","Sunita","Rajesh","Geeta","Vijay","Asha","Ramesh","Sita",
    "Ali","Fatima","Omar","Zara","Hassan","Layla","Yusuf","Hana","Tariq","Nadia",
    "James","Emily","Michael","Sarah","David","Emma","Daniel","Olivia","Chris","Sophia",
    "John","Jane","Robert","Mary","William","Patricia","Richard","Linda","Thomas","Barbara",
    "Carlos","Maria","Jose","Ana","Luis","Rosa","Juan","Carmen","Pedro","Isabel",
    "Wei","Mei","Zhang","Fang","Chen","Ling","Liu","Hong","Yang","Xia",
    "Samuel","Grace","Emmanuel","Blessing","Chukwu","Amaka","Tunde","Ngozi","Emeka","Yetunde",
    "Ivan","Olga","Dmitri","Natasha","Boris","Irina","Alexei","Tatiana","Sergei","Vera"
]

LAST_NAMES = [
    "Kumar","Sharma","Patel","Singh","Reddy","Nair","Iyer","Gupta","Mehta","Joshi",
    "Khan","Ali","Ahmed","Hassan","Malik","Sheikh","Chaudhry","Ansari","Siddiqui","Mirza",
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Wilson","Moore",
    "Taylor","Anderson","Thomas","Jackson","White","Harris","Martin","Thompson","Young","Lee",
    "Gonzalez","Rodriguez","Martinez","Hernandez","Lopez","Perez","Torres","Flores","Rivera","Ramirez",
    "Wang","Li","Zhang","Liu","Chen","Yang","Huang","Zhao","Wu","Zhou",
    "Okafor","Adeyemi","Eze","Ibrahim","Musa","Balogun","Adesanya","Owusu","Mensah","Asante"
]

CITIES = [
    "Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Coimbatore"
]

DOCTORS = [
    ("Dr. Arjun Mehta",       "Dermatology",  "Skin & Hair Dept",    "9841001001"),
    ("Dr. Priya Subramaniam", "Dermatology",  "Skin & Hair Dept",    "9841001002"),
    ("Dr. Ramesh Iyer",       "Dermatology",  "Skin & Hair Dept",    "9841001003"),
    ("Dr. Sunita Kapoor",     "Cardiology",   "Heart Care Unit",     "9841002001"),
    ("Dr. Vikram Bose",       "Cardiology",   "Heart Care Unit",     "9841002002"),
    ("Dr. Ananya Pillai",     "Cardiology",   "Heart Care Unit",     "9841002003"),
    ("Dr. Suresh Nair",       "Orthopedics",  "Bone & Joint Dept",   "9841003001"),
    ("Dr. Kavya Reddy",       "Orthopedics",  "Bone & Joint Dept",   "9841003002"),
    ("Dr. Mohan Das",         "Orthopedics",  "Bone & Joint Dept",   "9841003003"),
    ("Dr. Geeta Sharma",      "General",      "General OPD",         "9841004001"),
    ("Dr. Anil Verma",        "General",      "General OPD",         "9841004002"),
    ("Dr. Deepa Krishnan",    "General",      "General OPD",         "9841004003"),
    ("Dr. Rajan Patel",       "Pediatrics",   "Child Care Unit",     "9841005001"),
    ("Dr. Smitha Menon",      "Pediatrics",   "Child Care Unit",     "9841005002"),
    ("Dr. Kiran Joshi",       "Pediatrics",   "Child Care Unit",     "9841005003"),
]

TREATMENTS = {
    "Dermatology":  ["Acne Treatment","Skin Biopsy","Chemical Peel","Laser Therapy","Mole Removal"],
    "Cardiology":   ["ECG","Echocardiogram","Stress Test","Angioplasty","Holter Monitor"],
    "Orthopedics":  ["X-Ray","Physiotherapy","Joint Injection","Fracture Casting","MRI Scan"],
    "General":      ["Blood Test","Vaccination","General Checkup","IV Drip","Wound Dressing"],
    "Pediatrics":   ["Growth Assessment","Immunization","Fever Management","Nutrition Counseling","Vision Test"],
}

STATUSES_APPT   = ["Scheduled", "Completed", "Cancelled", "No-Show"]
STATUSES_APPT_W = [0.15, 0.60, 0.15, 0.10]          # weights
STATUSES_INV    = ["Paid", "Pending", "Overdue"]
STATUSES_INV_W  = [0.55, 0.25, 0.20]

random.seed(42)


def random_date(days_back: int) -> str:
    """Return a random datetime string within the past `days_back` days."""
    delta = random.randint(0, days_back)
    dt = datetime.now() - timedelta(days=delta)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def random_dob() -> str:
    """Random date of birth between 1950 and 2010."""
    start = datetime(1950, 1, 1)
    end   = datetime(2010, 12, 31)
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).strftime("%Y-%m-%d")


def maybe_null(value, probability: float = 0.15):
    """Return None with given probability to simulate real-world NULLs."""
    return None if random.random() < probability else value


# ── Database setup ────────────────────────────────────────────────────────────

def create_tables(cursor: sqlite3.Cursor) -> None:
    cursor.executescript("""
        DROP TABLE IF EXISTS treatments;
        DROP TABLE IF EXISTS invoices;
        DROP TABLE IF EXISTS appointments;
        DROP TABLE IF EXISTS doctors;
        DROP TABLE IF EXISTS patients;

        CREATE TABLE patients (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name      TEXT NOT NULL,
            last_name       TEXT NOT NULL,
            email           TEXT,
            phone           TEXT,
            date_of_birth   DATE,
            gender          TEXT,
            city            TEXT,
            registered_date DATE
        );

        CREATE TABLE doctors (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            specialization  TEXT,
            department      TEXT,
            phone           TEXT
        );

        CREATE TABLE appointments (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id        INTEGER,
            doctor_id         INTEGER,
            appointment_date  DATETIME,
            status            TEXT,
            notes             TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id)  REFERENCES doctors(id)
        );

        CREATE TABLE treatments (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id    INTEGER,
            treatment_name    TEXT,
            cost              REAL,
            duration_minutes  INTEGER,
            FOREIGN KEY (appointment_id) REFERENCES appointments(id)
        );

        CREATE TABLE invoices (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id    INTEGER,
            invoice_date  DATE,
            total_amount  REAL,
            paid_amount   REAL,
            status        TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        );
    """)


def insert_doctors(cursor: sqlite3.Cursor) -> None:
    cursor.executemany(
        "INSERT INTO doctors (name, specialization, department, phone) VALUES (?,?,?,?)",
        DOCTORS
    )


def insert_patients(cursor: sqlite3.Cursor, count: int = 200) -> None:
    rows = []
    for _ in range(count):
        first = random.choice(FIRST_NAMES)
        last  = random.choice(LAST_NAMES)
        email = maybe_null(f"{first.lower()}.{last.lower()}{random.randint(1,99)}@email.com")
        phone = maybe_null(f"9{random.randint(600000000, 999999999)}")
        dob   = random_dob()
        gender = random.choice(["M", "F"])
        city   = random.choice(CITIES)
        reg_dt = (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d")
        rows.append((first, last, email, phone, dob, gender, city, reg_dt))

    cursor.executemany(
        """INSERT INTO patients
           (first_name,last_name,email,phone,date_of_birth,gender,city,registered_date)
           VALUES (?,?,?,?,?,?,?,?)""",
        rows
    )


def insert_appointments(cursor: sqlite3.Cursor, count: int = 500) -> list[int]:
    """Insert appointments and return list of completed appointment IDs."""
    cursor.execute("SELECT id FROM patients")
    patient_ids = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT id FROM doctors")
    doctor_ids = [r[0] for r in cursor.fetchall()]

    # Make some patients repeat visitors (realistic)
    weighted_patients = patient_ids + random.choices(patient_ids, k=200)

    completed_ids = []
    rows = []
    for _ in range(count):
        pid    = random.choice(weighted_patients)
        did    = random.choice(doctor_ids)
        dt     = random_date(365)
        status = random.choices(STATUSES_APPT, weights=STATUSES_APPT_W)[0]
        notes  = maybe_null(f"Patient notes for appointment {random.randint(1000,9999)}", 0.40)
        rows.append((pid, did, dt, status, notes))

    cursor.executemany(
        "INSERT INTO appointments (patient_id,doctor_id,appointment_date,status,notes) VALUES (?,?,?,?,?)",
        rows
    )

    cursor.execute("SELECT id FROM appointments WHERE status='Completed'")
    completed_ids = [r[0] for r in cursor.fetchall()]
    return completed_ids


def insert_treatments(cursor: sqlite3.Cursor, completed_ids: list[int], count: int = 350) -> None:
    # Build appointment→specialization map
    cursor.execute("""
        SELECT a.id, d.specialization
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.status = 'Completed'
    """)
    appt_spec = {row[0]: row[1] for row in cursor.fetchall()}

    sample_ids = random.sample(completed_ids, min(count, len(completed_ids)))
    rows = []
    for appt_id in sample_ids:
        spec  = appt_spec.get(appt_id, "General")
        tname = random.choice(TREATMENTS.get(spec, TREATMENTS["General"]))
        cost  = round(random.uniform(50, 5000), 2)
        dur   = random.randint(15, 120)
        rows.append((appt_id, tname, cost, dur))

    cursor.executemany(
        "INSERT INTO treatments (appointment_id,treatment_name,cost,duration_minutes) VALUES (?,?,?,?)",
        rows
    )


def insert_invoices(cursor: sqlite3.Cursor, count: int = 300) -> None:
    cursor.execute("SELECT id FROM patients")
    patient_ids = [r[0] for r in cursor.fetchall()]

    rows = []
    for _ in range(count):
        pid          = random.choice(patient_ids)
        inv_date     = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
        total_amount = round(random.uniform(200, 8000), 2)
        status       = random.choices(STATUSES_INV, weights=STATUSES_INV_W)[0]

        if status == "Paid":
            paid_amount = total_amount
        elif status == "Pending":
            paid_amount = round(random.uniform(0, total_amount * 0.5), 2)
        else:  # Overdue
            paid_amount = round(random.uniform(0, total_amount * 0.3), 2)

        rows.append((pid, inv_date, total_amount, paid_amount, status))

    cursor.executemany(
        "INSERT INTO invoices (patient_id,invoice_date,total_amount,paid_amount,status) VALUES (?,?,?,?,?)",
        rows
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🔧 Creating tables...")
    create_tables(cursor)

    print("👨‍⚕️  Inserting doctors...")
    insert_doctors(cursor)

    print("🧑‍🤝‍🧑 Inserting patients...")
    insert_patients(cursor, 200)

    print("📅 Inserting appointments...")
    completed_ids = insert_appointments(cursor, 500)

    print("💊 Inserting treatments...")
    insert_treatments(cursor, completed_ids, 350)

    print("🧾 Inserting invoices...")
    insert_invoices(cursor, 300)

    conn.commit()

    # ── Summary ───────────────────────────────────────────────────────────────
    def count(table): 
        return cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    print("\n✅ Database created successfully!")
    print(f"   Created {count('patients')} patients")
    print(f"   Created {count('doctors')} doctors")
    print(f"   Created {count('appointments')} appointments")
    print(f"   Created {count('treatments')} treatments")
    print(f"   Created {count('invoices')} invoices")
    print(f"\n📁 Database saved to: {DB_PATH}")

    conn.close()


if __name__ == "__main__":
    main()