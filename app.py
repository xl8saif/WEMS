import io
import os
import shutil
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    flash,
    url_for,
)
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from xhtml2pdf import pisa

from config import Config
from database.db import (
    get_db_connection,
    init_db,
    get_stats,
    get_recent_jobs,
    get_recent_invoices,
    get_monthly_revenue,
    get_outstanding_clients,
)

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

for directory in [
    Config.INVOICE_DIR,
    Config.EXPORT_DIR,
    Config.BACKUP_DIR,
    Config.STATIC_IMAGE_DIR,
]:
    os.makedirs(directory, exist_ok=True)

init_db()


# ==================== HELPERS ====================


def parse_nonnegative_decimal(value, field_name, allow_zero=True):
    """Parse a monetary/quantity value safely and reject invalid input."""
    raw = str(value if value is not None else "").strip()
    if raw == "":
        return Decimal("0") if allow_zero else None
    try:
        number = Decimal(raw)
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid {field_name}.")
    if not number.is_finite():
        raise ValueError(f"Invalid {field_name}.")
    if number < 0 or (not allow_zero and number <= 0):
        raise ValueError(f"{field_name} must be {'zero or greater' if allow_zero else 'greater than zero'}.")
    return number


def valid_date(value, field_name, required=False):
    value = (value or "").strip()
    if not value:
        if required:
            raise ValueError(f"{field_name} is required.")
        return None
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid {field_name}.")
    return value


def get_invoice_or_404(conn, invoice_id):
    invoice = conn.execute(
        "SELECT * FROM invoices WHERE id = ?", (invoice_id,)
    ).fetchone()
    return invoice


@app.context_processor
def inject_globals():
    return {
        "company_name": Config.COMPANY_NAME,
        "company_address": Config.COMPANY_ADDRESS,
        "company_phone": Config.COMPANY_PHONE,
        "company_email": Config.COMPANY_EMAIL,
        "currency": Config.CURRENCY,
        "current_year": datetime.now().year,
    }


# ==================== DASHBOARD ====================

@app.route("/")
def dashboard():
    stats = get_stats()
    recent_jobs = get_recent_jobs()
    recent_invoices = get_recent_invoices()
    outstanding = get_outstanding_clients()
    monthly_data = get_monthly_revenue()
    months = [row["month"] for row in reversed(monthly_data)]
    revenues = [float(row["revenue"]) for row in reversed(monthly_data)]
    collected = [float(row["collected"]) for row in reversed(monthly_data)]
    return render_template(
        "dashboard.html",
        stats=stats,
        recent_jobs=recent_jobs,
        recent_invoices=recent_invoices,
        outstanding=outstanding,
        months=months,
        revenues=revenues,
        collected=collected,
    )


# ==================== CLIENTS ====================

@app.route("/clients")
def clients_list():
    conn = get_db_connection()
    search = request.args.get("search", "")
    client_type = request.args.get("type", "")
    query = "SELECT * FROM clients WHERE 1=1"
    params = []
    if search:
        query += " AND (name LIKE ? OR phone LIKE ? OR email LIKE ? OR cnic LIKE ?)"
        params.extend([f"%{search}%"] * 4)
    if client_type:
        query += " AND client_type = ?"
        params.append(client_type)
    query += " ORDER BY name"
    clients = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("clients/list.html", clients=clients, search=search, client_type=client_type)


@app.route("/clients/add", methods=["GET", "POST"])
def client_add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Client name is required.", "error")
            return render_template("clients/form.html", client=None)
        conn = get_db_connection()
        conn.execute(
            """INSERT INTO clients
            (name, contact_person, phone, email, address, cnic, client_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                name,
                request.form.get("contact_person", "").strip(),
                request.form.get("phone", "").strip(),
                request.form.get("email", "").strip(),
                request.form.get("address", "").strip(),
                request.form.get("cnic", "").strip(),
                request.form.get("client_type", "Individual"),
            ),
        )
        conn.commit()
        conn.close()
        flash("Client added successfully!", "success")
        return redirect(url_for("clients_list"))
    return render_template("clients/form.html", client=None)


@app.route("/clients/<int:id>")
def client_detail(id):
    conn = get_db_connection()
    client = conn.execute("SELECT * FROM clients WHERE id = ?", (id,)).fetchone()
    if not client:
        conn.close()
        return "Client not found", 404
    jobs = conn.execute("SELECT * FROM jobs WHERE client_id = ? ORDER BY created_at DESC", (id,)).fetchall()
    invoices = conn.execute("SELECT * FROM invoices WHERE client_id = ? ORDER BY created_at DESC", (id,)).fetchall()
    total_billed = conn.execute("SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE client_id = ?", (id,)).fetchone()[0]
    total_paid = conn.execute("SELECT COALESCE(SUM(paid_amount), 0) FROM invoices WHERE client_id = ?", (id,)).fetchone()[0]
    balance = total_billed - total_paid
    conn.close()
    return render_template("clients/detail.html", client=client, jobs=jobs, invoices=invoices,
                           total_billed=total_billed, total_paid=total_paid, balance=balance)


@app.route("/clients/<int:id>/edit", methods=["GET", "POST"])
def client_edit(id):
    conn = get_db_connection()
    client = conn.execute("SELECT * FROM clients WHERE id = ?", (id,)).fetchone()
    if not client:
        conn.close()
        return "Client not found", 404
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            conn.close()
            flash("Client name is required.", "error")
            return redirect(url_for("client_detail", id=id))
        conn.execute(
            """UPDATE clients SET name=?, contact_person=?, phone=?, email=?, address=?, cnic=?, client_type=? WHERE id=?""",
            (name, request.form.get("contact_person", ""), request.form.get("phone", ""),
             request.form.get("email", ""), request.form.get("address", ""),
             request.form.get("cnic", ""), request.form.get("client_type", "Individual"), id),
        )
        conn.commit()
        conn.close()
        flash("Client updated successfully!", "success")
        return redirect(url_for("client_detail", id=id))
    conn.close()
    return render_template("clients/form.html", client=client)


@app.route("/clients/<int:id>/delete", methods=["POST"])
def client_delete(id):
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM clients WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        flash("Client not found.", "error")
    else:
        flash("Client deleted successfully!", "success")
    return redirect(url_for("clients_list"))


# ==================== SERVICES ====================

@app.route("/services")
def services_list():
    conn = get_db_connection()
    services = conn.execute("SELECT * FROM services ORDER BY category, service_name").fetchall()
    conn.close()
    return render_template("services/list.html", services=services)


@app.route("/services/add", methods=["POST"])
def service_add():
    try:
        base_price = parse_nonnegative_decimal(request.form.get("base_price", "0"), "base price")
        service_name = request.form.get("service_name", "").strip()
        category = request.form.get("category", "").strip()
        if not service_name or not category:
            raise ValueError("Service name and category are required.")
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("services_list"))
    conn = get_db_connection()
    conn.execute("INSERT INTO services (service_name, category, description, base_price) VALUES (?, ?, ?, ?)",
                 (service_name, category, request.form.get("description", ""), float(base_price)))
    conn.commit()
    conn.close()
    flash("Service added successfully!", "success")
    return redirect(url_for("services_list"))


@app.route("/services/<int:id>/edit", methods=["POST"])
def service_edit(id):
    try:
        base_price = parse_nonnegative_decimal(request.form.get("base_price", "0"), "base price")
        service_name = request.form.get("service_name", "").strip()
        category = request.form.get("category", "").strip()
        if not service_name or not category:
            raise ValueError("Service name and category are required.")
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("services_list"))
    conn = get_db_connection()
    exists = conn.execute("SELECT id FROM services WHERE id = ?", (id,)).fetchone()
    if not exists:
        conn.close()
        return "Service not found", 404
    conn.execute("UPDATE services SET service_name=?, category=?, description=?, base_price=? WHERE id=?",
                 (service_name, category, request.form.get("description", ""), float(base_price), id))
    conn.commit()
    conn.close()
    flash("Service updated!", "success")
    return redirect(url_for("services_list"))


@app.route("/services/<int:id>/delete", methods=["POST"])
def service_delete(id):
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM services WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Service deleted!" if cursor.rowcount else "Service not found.", "success" if cursor.rowcount else "error")
    return redirect(url_for("services_list"))


# ==================== JOBS ====================

@app.route("/jobs")
def jobs_list():
    conn = get_db_connection()
    status = request.args.get("status", "")
    category = request.args.get("category", "")
    search = request.args.get("search", "")
    query = """SELECT j.*, c.name as client_name, s.service_name
               FROM jobs j JOIN clients c ON j.client_id = c.id
               LEFT JOIN services s ON j.service_id = s.id WHERE 1=1"""
    params = []
    if status:
        query += " AND j.status = ?"
        params.append(status)
    if category:
        query += " AND j.category = ?"
        params.append(category)
    if search:
        query += " AND (j.job_title LIKE ? OR c.name LIKE ? OR j.description LIKE ?)"
        params.extend([f"%{search}%"] * 3)
    query += " ORDER BY j.created_at DESC"
    jobs = conn.execute(query, params).fetchall()
    categories = conn.execute("SELECT DISTINCT category FROM jobs ORDER BY category").fetchall()
    conn.close()
    return render_template("jobs/list.html", jobs=jobs, categories=categories, status=status, category=category, search=search)


@app.route("/jobs/add", methods=["GET", "POST"])
def job_add():
    conn = get_db_connection()
    clients = conn.execute("SELECT id, name FROM clients ORDER BY name").fetchall()
    services = conn.execute("SELECT * FROM services WHERE is_active=1 ORDER BY service_name").fetchall()
    if request.method == "POST":
        try:
            client_id = int(request.form.get("client_id", "0"))
            if not conn.execute("SELECT id FROM clients WHERE id=?", (client_id,)).fetchone():
                raise ValueError("Selected client does not exist.")
            service_id = request.form.get("service_id") or None
            if service_id:
                service_id = int(service_id)
                if not conn.execute("SELECT id FROM services WHERE id=?", (service_id,)).fetchone():
                    raise ValueError("Selected service does not exist.")
            job_title = request.form.get("job_title", "").strip()
            category = request.form.get("category", "").strip()
            if not job_title or not category:
                raise ValueError("Job title and category are required.")
            cost = parse_nonnegative_decimal(request.form.get("cost", "0"), "cost")
            start_date = valid_date(request.form.get("start_date"), "start date")
            due_date = valid_date(request.form.get("due_date"), "due date")
            if start_date and due_date and due_date < start_date:
                raise ValueError("Due date cannot be earlier than start date.")
        except (ValueError, TypeError) as exc:
            conn.close()
            flash(str(exc), "error")
            return redirect(url_for("job_add"))
        conn.execute("""INSERT INTO jobs
            (client_id, service_id, job_title, category, description, priority, assigned_to, start_date, due_date, cost, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (client_id, service_id, job_title, category, request.form.get("description", ""),
             request.form.get("priority", "Normal"), request.form.get("assigned_to", ""),
             start_date, due_date, float(cost), request.form.get("notes", "")))
        conn.commit()
        conn.close()
        flash("Job created successfully!", "success")
        return redirect(url_for("jobs_list"))
    conn.close()
    return render_template("jobs/form.html", job=None, clients=clients, services=services)


@app.route("/jobs/<int:id>")
def job_detail(id):
    conn = get_db_connection()
    job = conn.execute("""SELECT j.*, c.name as client_name, c.phone as client_phone, c.address as client_address,
                         s.service_name, s.base_price FROM jobs j JOIN clients c ON j.client_id=c.id
                         LEFT JOIN services s ON j.service_id=s.id WHERE j.id=?""", (id,)).fetchone()
    conn.close()
    if not job:
        return "Job not found", 404
    return render_template("jobs/detail.html", job=job)


@app.route("/jobs/<int:id>/edit", methods=["GET", "POST"])
def job_edit(id):
    conn = get_db_connection()
    job = conn.execute("SELECT * FROM jobs WHERE id=?", (id,)).fetchone()
    if not job:
        conn.close()
        return "Job not found", 404
    clients = conn.execute("SELECT id, name FROM clients ORDER BY name").fetchall()
    services = conn.execute("SELECT * FROM services WHERE is_active=1 ORDER BY service_name").fetchall()
    if request.method == "POST":
        try:
            client_id = int(request.form.get("client_id", "0"))
            if not conn.execute("SELECT id FROM clients WHERE id=?", (client_id,)).fetchone():
                raise ValueError("Selected client does not exist.")
            service_id = request.form.get("service_id") or None
            if service_id:
                service_id = int(service_id)
                if not conn.execute("SELECT id FROM services WHERE id=?", (service_id,)).fetchone():
                    raise ValueError("Selected service does not exist.")
            status = request.form.get("status", job["status"])
            completed_date = job["completed_date"]
            if status == "Completed" and job["status"] != "Completed":
                completed_date = datetime.now().strftime("%Y-%m-%d")
            elif status != "Completed":
                completed_date = None
            cost = parse_nonnegative_decimal(request.form.get("cost", "0"), "cost")
            start_date = valid_date(request.form.get("start_date"), "start date")
            due_date = valid_date(request.form.get("due_date"), "due date")
            if start_date and due_date and due_date < start_date:
                raise ValueError("Due date cannot be earlier than start date.")
            job_title = request.form.get("job_title", "").strip()
            category = request.form.get("category", "").strip()
            if not job_title or not category:
                raise ValueError("Job title and category are required.")
        except (ValueError, TypeError) as exc:
            conn.close()
            flash(str(exc), "error")
            return redirect(url_for("job_edit", id=id))
        conn.execute("""UPDATE jobs SET client_id=?, service_id=?, job_title=?, category=?, description=?, status=?,
                     priority=?, assigned_to=?, start_date=?, due_date=?, completed_date=?, cost=?, notes=? WHERE id=?""",
            (client_id, service_id, job_title, category, request.form.get("description", ""), status,
             request.form.get("priority", "Normal"), request.form.get("assigned_to", ""), start_date,
             due_date, completed_date, float(cost), request.form.get("notes", ""), id))
        conn.commit()
        conn.close()
        flash("Job updated successfully!", "success")
        return redirect(url_for("job_detail", id=id))
    conn.close()
    return render_template("jobs/form.html", job=job, clients=clients, services=services)


@app.route("/jobs/<int:id>/delete", methods=["POST"])
def job_delete(id):
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM jobs WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Job deleted!" if cursor.rowcount else "Job not found.", "success" if cursor.rowcount else "error")
    return redirect(url_for("jobs_list"))


# ==================== INVOICES ====================

@app.route("/invoices")
def invoices_list():
    conn = get_db_connection()
    status = request.args.get("status", "")
    search = request.args.get("search", "")
    query = """SELECT i.*, c.name as client_name, c.phone as client_phone
               FROM invoices i JOIN clients c ON i.client_id=c.id WHERE 1=1"""
    params = []
    if status:
        query += " AND i.status=?"
        params.append(status)
    if search:
        query += " AND (i.invoice_number LIKE ? OR c.name LIKE ?)"
        params.extend([f"%{search}%"] * 2)
    query += " ORDER BY i.created_at DESC"
    invoices = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("invoices/list.html", invoices=invoices, status=status, search=search)


@app.route("/invoices/create", methods=["GET", "POST"])
def invoice_create():
    conn = get_db_connection()
    clients = conn.execute("SELECT id, name FROM clients ORDER BY name").fetchall()
    services = conn.execute("SELECT * FROM services WHERE is_active=1 ORDER BY service_name").fetchall()
    if request.method == "POST":
        try:
            client_id = int(request.form.get("client_id", "0"))
            if not conn.execute("SELECT id FROM clients WHERE id=?", (client_id,)).fetchone():
                raise ValueError("Selected client does not exist.")
            job_id = request.form.get("job_id") or None
            if job_id:
                job_id = int(job_id)
                job = conn.execute("SELECT id, client_id FROM jobs WHERE id=?", (job_id,)).fetchone()
                if not job:
                    raise ValueError("Selected job does not exist.")
                if job["client_id"] != client_id:
                    raise ValueError("Selected job does not belong to the selected client.")
            issue_date = valid_date(request.form.get("issue_date"), "issue date", required=True)
            due_date = valid_date(request.form.get("due_date"), "due date")
            if due_date and due_date < issue_date:
                raise ValueError("Due date cannot be earlier than issue date.")
            descriptions = request.form.getlist("item_description[]")
            quantities = request.form.getlist("item_quantity[]")
            unit_prices = request.form.getlist("item_unit_price[]")
            if not descriptions:
                raise ValueError("An invoice must contain at least one item.")
            items = []
            subtotal = Decimal("0")
            for index, desc in enumerate(descriptions):
                desc = desc.strip()
                if not desc:
                    continue
                qty_raw = quantities[index] if index < len(quantities) else "1"
                price_raw = unit_prices[index] if index < len(unit_prices) else "0"
                qty = parse_nonnegative_decimal(qty_raw, "quantity", allow_zero=False)
                price = parse_nonnegative_decimal(price_raw, "unit price")
                total = qty * price
                subtotal += total
                items.append((desc, qty, price, total))
            if not items:
                raise ValueError("An invoice must contain at least one non-empty item.")
            tax_amount = subtotal * Decimal(str(Config.TAX_RATE))
            discount = parse_nonnegative_decimal(request.form.get("discount", "0"), "discount")
            gross_total = subtotal + tax_amount
            if discount > gross_total:
                raise ValueError("Discount cannot exceed the invoice subtotal and tax.")
            total_amount = gross_total - discount
            # Serialize invoice-number generation inside the transaction. MAX(id) is
            # stable for existing records and the UNIQUE constraint remains the final guard.
            next_id = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM invoices").fetchone()[0]
            invoice_number = f"WARQ-{datetime.now().strftime('%Y%m')}-{next_id:04d}"
            while conn.execute("SELECT 1 FROM invoices WHERE invoice_number=?", (invoice_number,)).fetchone():
                next_id += 1
                invoice_number = f"WARQ-{datetime.now().strftime('%Y%m')}-{next_id:04d}"
            conn.execute("""INSERT INTO invoices
                (invoice_number, client_id, job_id, issue_date, due_date, subtotal, tax_amount, discount,
                 total_amount, paid_amount, balance_due, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, 'Unpaid', ?)""",
                (invoice_number, client_id, job_id, issue_date, due_date, float(subtotal), float(tax_amount),
                 float(discount), float(total_amount), float(total_amount), request.form.get("notes", "")))
            invoice_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            for desc, qty, price, total in items:
                conn.execute("INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?)",
                             (invoice_id, desc, float(qty), float(price), float(total)))
            conn.commit()
        except (ValueError, TypeError, InvalidOperation) as exc:
            conn.rollback()
            conn.close()
            flash(str(exc), "error")
            return redirect(url_for("invoice_create"))
        conn.close()
        flash(f"Invoice {invoice_number} created successfully!", "success")
        return redirect(url_for("invoice_detail", id=invoice_id))
    conn.close()
    return render_template("invoices/create.html", clients=clients, services=services)


@app.route("/invoices/<int:id>")
def invoice_detail(id):
    conn = get_db_connection()
    invoice = conn.execute("""SELECT i.*, c.name as client_name, c.phone as client_phone,
                              c.email as client_email, c.address as client_address, c.cnic as client_cnic
                              FROM invoices i JOIN clients c ON i.client_id=c.id WHERE i.id=?""", (id,)).fetchone()
    if not invoice:
        conn.close()
        return "Invoice not found", 404
    items = conn.execute("SELECT * FROM invoice_items WHERE invoice_id=?", (id,)).fetchall()
    payments = conn.execute("SELECT * FROM payments WHERE invoice_id=? ORDER BY payment_date", (id,)).fetchall()
    conn.close()
    return render_template("invoices/detail.html", invoice=invoice, items=items, payments=payments)


@app.route("/invoices/<int:id>/pdf")
def invoice_pdf(id):
    conn = get_db_connection()
    invoice = conn.execute("""SELECT i.*, c.name as client_name, c.phone as client_phone,
                              c.email as client_email, c.address as client_address, c.cnic as client_cnic
                              FROM invoices i JOIN clients c ON i.client_id=c.id WHERE i.id=?""", (id,)).fetchone()
    if not invoice:
        conn.close()
        return "Invoice not found", 404
    items = conn.execute("SELECT * FROM invoice_items WHERE invoice_id=?", (id,)).fetchall()
    conn.close()
    lang = "en" if request.args.get("lang") == "en" else "ur"
    html = render_template("invoices/invoice_pdf.html", invoice=invoice, items=items, lang=lang)
    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.StringIO(html), result)
    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f'inline; filename=Invoice_{invoice["invoice_number"]}.pdf'
        return response
    flash("Error generating PDF", "error")
    return redirect(url_for("invoice_detail", id=id))


@app.route("/invoices/<int:id>/print")
def invoice_print(id):
    conn = get_db_connection()
    invoice = conn.execute("""SELECT i.*, c.name as client_name, c.phone as client_phone,
                              c.email as client_email, c.address as client_address, c.cnic as client_cnic
                              FROM invoices i JOIN clients c ON i.client_id=c.id WHERE i.id=?""", (id,)).fetchone()
    if not invoice:
        conn.close()
        return "Invoice not found", 404
    items = conn.execute("SELECT * FROM invoice_items WHERE invoice_id=?", (id,)).fetchall()
    conn.close()
    lang = "en" if request.args.get("lang") == "en" else "ur"
    return render_template("invoices/print.html", invoice=invoice, items=items, lang=lang)


@app.route("/invoices/<int:id>/delete", methods=["POST"])
def invoice_delete(id):
    conn = get_db_connection()
    exists = conn.execute("SELECT id FROM invoices WHERE id=?", (id,)).fetchone()
    if not exists:
        conn.close()
        flash("Invoice not found.", "error")
        return redirect(url_for("invoices_list"))
    conn.execute("DELETE FROM invoices WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Invoice deleted!", "success")
    return redirect(url_for("invoices_list"))


# ==================== PAYMENTS ====================

@app.route("/payments")
def payments_list():
    conn = get_db_connection()
    payments = conn.execute("""SELECT p.*, c.name as client_name, i.invoice_number
                               FROM payments p JOIN clients c ON p.client_id=c.id
                               JOIN invoices i ON p.invoice_id=i.id ORDER BY p.payment_date DESC""").fetchall()
    conn.close()
    return render_template("payments/list.html", payments=payments)


@app.route("/payments/add", methods=["POST"])
def payment_add():
    conn = get_db_connection()
    try:
        invoice_id = int(request.form.get("invoice_id", "0"))
        client_id = int(request.form.get("client_id", "0"))
        amount = parse_nonnegative_decimal(request.form.get("amount", ""), "payment amount", allow_zero=False)
        payment_date = valid_date(request.form.get("payment_date"), "payment date", required=True)
        payment_method = request.form.get("payment_method", "Cash")
        reference_no = request.form.get("reference_no", "")
        notes = request.form.get("notes", "")
        invoice = conn.execute("SELECT id, client_id, total_amount, paid_amount, balance_due, status FROM invoices WHERE id=?", (invoice_id,)).fetchone()
        if not invoice:
            raise ValueError("Invoice not found.")
        if invoice["client_id"] != client_id:
            raise ValueError("Selected client does not match the invoice.")
        outstanding = Decimal(str(invoice["balance_due"] or 0))
        if outstanding <= 0:
            raise ValueError("This invoice has no outstanding balance.")
        if amount > outstanding:
            raise ValueError("Payment cannot exceed the outstanding balance.")
        conn.execute("""INSERT INTO payments
            (invoice_id, client_id, amount, payment_date, payment_method, reference_no, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (invoice_id, client_id, float(amount), payment_date, payment_method, reference_no, notes))
        new_paid = Decimal(str(invoice["paid_amount"] or 0)) + amount
        new_balance = outstanding - amount
        status = "Paid" if new_balance <= 0 else "Partial"
        conn.execute("UPDATE invoices SET paid_amount=?, balance_due=?, status=? WHERE id=?",
                     (float(new_paid), float(max(new_balance, Decimal("0"))), status, invoice_id))
        conn.commit()
    except (ValueError, TypeError, InvalidOperation) as exc:
        conn.rollback()
        conn.close()
        flash(str(exc), "error")
        invoice_id = request.form.get("invoice_id")
        if invoice_id and str(invoice_id).isdigit():
            return redirect(url_for("invoice_detail", id=int(invoice_id)))
        return redirect(url_for("payments_list"))
    conn.close()
    flash("Payment recorded successfully!", "success")
    return redirect(url_for("invoice_detail", id=invoice_id))


# ==================== REPORTS ====================

@app.route("/reports")
def reports():
    conn = get_db_connection()
    revenue_by_category = conn.execute("""SELECT j.category, COUNT(*) as job_count,
        COALESCE(SUM(i.total_amount), 0) as revenue FROM jobs j LEFT JOIN invoices i ON j.id=i.job_id
        GROUP BY j.category""").fetchall()
    monthly_summary = conn.execute("""SELECT strftime('%Y-%m', created_at) as month,
        COUNT(*) as invoice_count, COALESCE(SUM(total_amount),0) as total,
        COALESCE(SUM(paid_amount),0) as collected, COALESCE(SUM(balance_due),0) as pending
        FROM invoices GROUP BY month ORDER BY month DESC LIMIT 12""").fetchall()
    expense_summary = conn.execute("""SELECT category, COALESCE(SUM(amount),0) as total
        FROM expenses GROUP BY category""").fetchall()
    conn.close()
    return render_template("reports.html", revenue_by_category=revenue_by_category,
                           monthly_summary=monthly_summary, expense_summary=expense_summary)


# ==================== EXPORTS ====================


def _style_export_header(ws):
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2c3e50", end_color="2c3e50", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")


def _send_workbook(wb, filename):
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True, download_name=filename)


@app.route("/export/clients")
def export_clients():
    conn = get_db_connection()
    clients = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    wb = Workbook()
    ws = wb.active
    ws.title = "Clients"
    ws.append(["ID", "Name", "Contact Person", "Phone", "Email", "Address", "CNIC", "Type", "Created"])
    for c in clients:
        ws.append([c["id"], c["name"], c["contact_person"], c["phone"], c["email"], c["address"], c["cnic"], c["client_type"], c["created_at"]])
    _style_export_header(ws)
    return _send_workbook(wb, f'Waraq_Clients_{datetime.now().strftime("%Y%m%d")}.xlsx')


@app.route("/export/invoices")
def export_invoices():
    conn = get_db_connection()
    invoices = conn.execute("""SELECT i.*, c.name as client_name FROM invoices i
                               JOIN clients c ON i.client_id=c.id ORDER BY i.created_at DESC""").fetchall()
    conn.close()
    wb = Workbook()
    ws = wb.active
    ws.title = "Invoices"
    ws.append(["Invoice #", "Client", "Issue Date", "Due Date", "Subtotal", "Tax", "Discount", "Total", "Paid", "Balance", "Status"])
    for i in invoices:
        ws.append([i["invoice_number"], i["client_name"], i["issue_date"], i["due_date"], i["subtotal"], i["tax_amount"], i["discount"], i["total_amount"], i["paid_amount"], i["balance_due"], i["status"]])
    _style_export_header(ws)
    return _send_workbook(wb, f'Waraq_Invoices_{datetime.now().strftime("%Y%m%d")}.xlsx')


@app.route("/export/jobs")
def export_jobs():
    conn = get_db_connection()
    jobs = conn.execute("""SELECT j.*, c.name as client_name, s.service_name FROM jobs j
                           JOIN clients c ON j.client_id=c.id LEFT JOIN services s ON j.service_id=s.id
                           ORDER BY j.created_at DESC""").fetchall()
    conn.close()
    wb = Workbook()
    ws = wb.active
    ws.title = "Jobs"
    ws.append(["ID", "Client", "Service", "Title", "Category", "Status", "Priority", "Assigned To", "Start", "Due", "Cost"])
    for j in jobs:
        ws.append([j["id"], j["client_name"], j["service_name"], j["job_title"], j["category"], j["status"], j["priority"], j["assigned_to"], j["start_date"], j["due_date"], j["cost"]])
    _style_export_header(ws)
    return _send_workbook(wb, f'Waraq_Jobs_{datetime.now().strftime("%Y%m%d")}.xlsx')


# ==================== BACKUP ====================

@app.route("/backup", methods=["POST"])
def backup():
    """Create a database backup and immediately download it."""
    if not os.path.exists(Config.DATABASE):
        flash("Database file not found.", "error")
        return redirect(url_for("dashboard"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(Config.BACKUP_DIR, f"waraq_backup_{timestamp}.db")
    try:
        shutil.copy2(Config.DATABASE, backup_path)
    except OSError as exc:
        flash(f"Backup failed: {exc}", "error")
        return redirect(url_for("dashboard"))
    return send_file(backup_path, mimetype="application/octet-stream", as_attachment=True,
                     download_name=os.path.basename(backup_path))


# ==================== API ENDPOINTS ====================

@app.route("/api/client/<int:id>/jobs")
def api_client_jobs(id):
    conn = get_db_connection()
    if not conn.execute("SELECT id FROM clients WHERE id=?", (id,)).fetchone():
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    jobs = conn.execute("SELECT id, job_title, cost FROM jobs WHERE client_id=? AND status!='Completed' ORDER BY created_at DESC", (id,)).fetchall()
    conn.close()
    return jsonify([dict(job) for job in jobs])


@app.route("/api/service/<int:id>")
def api_service(id):
    conn = get_db_connection()
    service = conn.execute("SELECT * FROM services WHERE id=?", (id,)).fetchone()
    conn.close()
    if not service:
        return jsonify({"error": "Service not found"}), 404
    return jsonify(dict(service))


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template("base.html", error_message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("base.html", error_message="An internal server error occurred."), 500


# ==================== MAIN ====================

if __name__ == "__main__":
    print("Starting Waraq Enterprise Management System...")
    print(f"Database: {Config.DATABASE}")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=False, host="127.0.0.1", port=5000)