import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from collections import Counter

DB_FILE = "entry_log.db"


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sample_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clinic_code TEXT,
                is_in_district INTEGER,
                is_approved INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def log_entry(clinic_code, is_in_district, is_approved):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            INSERT INTO sample_entries (clinic_code, is_in_district, is_approved)
            VALUES (?, ?, ?)
        """, (clinic_code.upper(), int(is_in_district), int(is_approved)))
        conn.commit()


def get_entries_by_filter(in_district=True, approved=None, days=7):
    since = datetime.now() - timedelta(days=days)
    query = "SELECT clinic_code FROM sample_entries WHERE is_in_district=?"
    params = [int(in_district)]

    if approved is not None:
        query += " AND is_approved=?"
        params.append(int(approved))

    query += " AND timestamp >= ?"
    params.append(since)

    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute(query, params).fetchall()

    counter = Counter(row[0] for row in rows)
    return counter


def format_email(name, purpose, clinic_action, closing, counter_dict):
    lines = [f"Dear {name},", ""]
    lines.append(purpose)
    lines.append("")
    for code, count in counter_dict.items():
        lines.append(f"{count} sample(s) in {code}")
    if len(counter_dict) == 0:
        lines.append("No samples found in the past week.")
    lines.append("")
    lines.append(clinic_action)
    lines.append("")
    lines.append("Many thanks,")
    lines.append("")
    lines.append("Vincent")
    return "\n".join(lines)


def send_email(to_address, subject, body):
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    USERNAME = "torch.consortium@gmail.com"
    PASSWORD = "dpyg asuv kstq lcjk"  # Use Gmail App Password here

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = USERNAME
    msg["To"] = to_address

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)


def weekly_email_job():
    in_district_unapproved = get_entries_by_filter(in_district=True, approved=False)
    not_in_district = get_entries_by_filter(in_district=False)

    msg_a = format_email(
        "Dear Susanne",
        "In the last week the following samples have been entered that were in PARR-TB districts but have not approved the study:",
        "Please follow up with the clinic manager to indicate that we have data that may improve the patient's treatment.",
        in_district_unapproved,
        "Many thanks,",
        "Vincent",
    )

    msg_b = format_email(
        "Dear Thys",
        "In the last week the following samples have been entered that were identified as not belonging to PARR-TB districts:",
        "Please confirm that the clinic codes are valid and are indeed not in the PARR-TB districts.",
        not_in_district,
        "Many thanks,",
        "Vincent",
    )

    send_email("stonsing@sun.ac.za", "Unapproved Samples in PARR-TB Districts", msg_a)
    send_email("thys@epcon.ai", "Samples Not in PARR-TB Districts", msg_b)


init_db()
