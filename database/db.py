import sqlite3
import os
from config import Config


def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    if not os.path.exists(os.path.dirname(Config.DATABASE)):
        os.makedirs(os.path.dirname(Config.DATABASE))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            cnic TEXT,
            client_type TEXT DEFAULT 'Individual',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            base_price REAL DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            service_id INTEGER,
            job_title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            priority TEXT DEFAULT 'Normal',
            assigned_to TEXT,
            start_date DATE,
            due_date DATE,
            completed_date DATE,
            cost REAL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            client_id INTEGER NOT NULL,
            job_id INTEGER,
            issue_date DATE NOT NULL,
            due_date DATE,
            subtotal REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            discount REAL DEFAULT 0,
            total_amount REAL DEFAULT 0,
            paid_amount REAL DEFAULT 0,
            balance_due REAL DEFAULT 0,
            status TEXT DEFAULT 'Unpaid',
            payment_method TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            quantity REAL DEFAULT 1,
            unit_price REAL DEFAULT 0,
            total_price REAL DEFAULT 0,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            client_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date DATE NOT NULL,
            payment_method TEXT DEFAULT 'Cash',
            reference_no TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            expense_date DATE NOT NULL,
            paid_by TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Compatibility triggers repair referential behavior for existing databases
    # without requiring destructive table reconstruction/migration.
    cursor.executescript("""
        CREATE TRIGGER IF NOT EXISTS trg_invoice_delete_children
        AFTER DELETE ON invoices
        BEGIN
            DELETE FROM invoice_items WHERE invoice_id = OLD.id;
            DELETE FROM payments WHERE invoice_id = OLD.id;
        END;

        CREATE TRIGGER IF NOT EXISTS trg_client_delete_children
        BEFORE DELETE ON clients
        BEGIN
            DELETE FROM payments WHERE client_id = OLD.id;
            DELETE FROM invoice_items WHERE invoice_id IN (SELECT id FROM invoices WHERE client_id = OLD.id);
            DELETE FROM invoices WHERE client_id = OLD.id;
            DELETE FROM jobs WHERE client_id = OLD.id;
        END;

        CREATE TRIGGER IF NOT EXISTS trg_job_delete_invoice_reference
        BEFORE DELETE ON jobs
        BEGIN
            UPDATE invoices SET job_id = NULL WHERE job_id = OLD.id;
        END;

        CREATE TRIGGER IF NOT EXISTS trg_service_delete_job_reference
        BEFORE DELETE ON services
        BEGIN
            UPDATE jobs SET service_id = NULL WHERE service_id = OLD.id;
        END;
    """)

    cursor.execute("SELECT COUNT(*) FROM services")
    if cursor.fetchone()[0] == 0:
        default_services = [
            ("Legal Drafting - Agreement", "Legal Drafting", "General legal agreement drafting", 5000),
            ("Legal Drafting - Affidavit", "Legal Drafting", "Affidavit preparation", 2000),
            ("Legal Drafting - Power of Attorney", "Legal Drafting", "Power of attorney document", 3000),
            ("Legal Drafting - Contract", "Legal Drafting", "Business contract drafting", 8000),
            ("Court File Preparation", "Court Services", "Complete court file preparation", 10000),
            ("Court Case Filing", "Court Services", "Filing court cases", 5000),
            ("Printing - Black & White", "Printing", "B&W printing per page", 10),
            ("Printing - Color", "Printing", "Color printing per page", 50),
            ("Printing - Large Format", "Printing", "Large format printing", 200),
            ("Online Registration - Business", "Online Registration", "Business registration service", 15000),
            ("Online Registration - Trademark", "Online Registration", "Trademark registration", 20000),
            ("Online Registration - Domain", "Online Registration", "Domain registration assistance", 5000),
            ("Document Attestation", "Documentation", "Document attestation service", 3000),
            ("Translation Service", "Documentation", "Document translation", 2000),
            ("Consultation", "Other", "General consultation", 2000),
        ]
        cursor.executemany(
            "INSERT INTO services (service_name, category, description, base_price) VALUES (?, ?, ?, ?)",
            default_services
        )

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    stats = {}
    cursor.execute("SELECT COUNT(*) FROM clients")
    stats['total_clients'] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM jobs")
    stats['total_jobs'] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Pending'")
    stats['pending_jobs'] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Completed'")
    stats['completed_jobs'] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM invoices")
    stats['total_invoices'] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM invoices WHERE status = 'Unpaid'")
    stats['unpaid_invoices'] = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM invoices")
    stats['total_revenue'] = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(balance_due), 0) FROM invoices WHERE status != 'Paid'")
    stats['outstanding_balance'] = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM payments")
    stats['total_payments'] = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses")
    stats['total_expenses'] = cursor.fetchone()[0]
    conn.close()
    return stats


def get_recent_jobs(limit=5):
    conn = get_db_connection()
    jobs = conn.execute(
        """SELECT j.*, c.name as client_name FROM jobs j
           JOIN clients c ON j.client_id = c.id
           ORDER BY j.created_at DESC LIMIT ?""", (limit,)
    ).fetchall()
    conn.close()
    return jobs


def get_recent_invoices(limit=5):
    conn = get_db_connection()
    invoices = conn.execute(
        """SELECT i.*, c.name as client_name FROM invoices i
           JOIN clients c ON i.client_id = c.id
           ORDER BY i.created_at DESC LIMIT ?""", (limit,)
    ).fetchall()
    conn.close()
    return invoices


def get_monthly_revenue():
    conn = get_db_connection()
    data = conn.execute("""
        SELECT strftime('%Y-%m', created_at) as month,
               COALESCE(SUM(total_amount), 0) as revenue,
               COALESCE(SUM(paid_amount), 0) as collected
        FROM invoices GROUP BY month ORDER BY month DESC LIMIT 12
    """).fetchall()
    conn.close()
    return data


def get_outstanding_clients():
    conn = get_db_connection()
    clients = conn.execute("""
        SELECT c.id, c.name, c.phone,
               COALESCE(SUM(i.balance_due), 0) as total_due,
               COUNT(i.id) as invoice_count
        FROM clients c JOIN invoices i ON c.id = i.client_id
        WHERE i.balance_due > 0
        GROUP BY c.id ORDER BY total_due DESC LIMIT 10
    """).fetchall()
    conn.close()
    return clients
