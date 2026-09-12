import os
import io
import base64
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
from xhtml2pdf import pisa
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from PIL import Image

from config import Config
from database.db import (
    get_db_connection, init_db, get_stats, get_recent_jobs, 
    get_recent_invoices, get_monthly_revenue, get_outstanding_clients
)

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Ensure directories exist
for directory in [Config.INVOICE_DIR, Config.EXPORT_DIR, Config.BACKUP_DIR, Config.STATIC_IMAGE_DIR]:
    os.makedirs(directory, exist_ok=True)

# Initialize database on startup
init_db()

# ==================== CONTEXT PROCESSORS ====================

@app.context_processor
def inject_globals():
    return {
        'company_name': Config.COMPANY_NAME,
        'company_address': Config.COMPANY_ADDRESS,
        'company_phone': Config.COMPANY_PHONE,
        'company_email': Config.COMPANY_EMAIL,
        'currency': Config.CURRENCY,
        'current_year': datetime.now().year
    }

# ==================== DASHBOARD ====================

@app.route('/')
def dashboard():
    stats = get_stats()
    recent_jobs = get_recent_jobs()
    recent_invoices = get_recent_invoices()
    outstanding = get_outstanding_clients()
    monthly_data = get_monthly_revenue()

    # Prepare chart data
    months = [row['month'] for row in reversed(monthly_data)]
    revenues = [float(row['revenue']) for row in reversed(monthly_data)]
    collected = [float(row['collected']) for row in reversed(monthly_data)]

    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_jobs=recent_jobs,
                         recent_invoices=recent_invoices,
                         outstanding=outstanding,
                         months=months,
                         revenues=revenues,
                         collected=collected)

# ==================== CLIENTS ====================

@app.route('/clients')
def clients_list():
    conn = get_db_connection()
    search = request.args.get('search', '')
    client_type = request.args.get('type', '')

    query = "SELECT * FROM clients WHERE 1=1"
    params = []
    if search:
        query += " AND (name LIKE ? OR phone LIKE ? OR email LIKE ? OR cnic LIKE ?)"
        params.extend([f'%{search}%'] * 4)
    if client_type:
        query += " AND client_type = ?"
        params.append(client_type)

    query += " ORDER BY name"
    clients = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('clients/list.html', clients=clients, search=search, client_type=client_type)

@app.route('/clients/add', methods=['GET', 'POST'])
def client_add():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO clients (name, contact_person, phone, email, address, cnic, client_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form['name'],
            request.form.get('contact_person', ''),
            request.form.get('phone', ''),
            request.form.get('email', ''),
            request.form.get('address', ''),
            request.form.get('cnic', ''),
            request.form.get('client_type', 'Individual')
        ))
        conn.commit()
        conn.close()
        flash('Client added successfully!', 'success')
        return redirect(url_for('clients_list'))
    return render_template('clients/form.html', client=None)

@app.route('/clients/<int:id>')
def client_detail(id):
    conn = get_db_connection()
    client = conn.execute("SELECT * FROM clients WHERE id = ?", (id,)).fetchone()
    jobs = conn.execute("SELECT * FROM jobs WHERE client_id = ? ORDER BY created_at DESC", (id,)).fetchall()
    invoices = conn.execute("SELECT * FROM invoices WHERE client_id = ? ORDER BY created_at DESC", (id,)).fetchall()

    # Calculate totals
    total_billed = conn.execute("SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE client_id = ?", (id,)).fetchone()[0]
    total_paid = conn.execute("SELECT COALESCE(SUM(paid_amount), 0) FROM invoices WHERE client_id = ?", (id,)).fetchone()[0]
    balance = total_billed - total_paid

    conn.close()
    return render_template('clients/detail.html', client=client, jobs=jobs, invoices=invoices,
                         total_billed=total_billed, total_paid=total_paid, balance=balance)

@app.route('/clients/<int:id>/edit', methods=['GET', 'POST'])
def client_edit(id):
    conn = get_db_connection()
    client = conn.execute("SELECT * FROM clients WHERE id = ?", (id,)).fetchone()

    if request.method == 'POST':
        conn.execute("""
            UPDATE clients SET name=?, contact_person=?, phone=?, email=?, address=?, cnic=?, client_type=?
            WHERE id=?
        """, (
            request.form['name'], request.form.get('contact_person', ''),
            request.form.get('phone', ''), request.form.get('email', ''),
            request.form.get('address', ''), request.form.get('cnic', ''),
            request.form.get('client_type', 'Individual'), id
        ))
        conn.commit()
        conn.close()
        flash('Client updated successfully!', 'success')
        return redirect(url_for('client_detail', id=id))

    conn.close()
    return render_template('clients/form.html', client=client)

@app.route('/clients/<int:id>/delete', methods=['POST'])
def client_delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM clients WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Client deleted successfully!', 'success')
    return redirect(url_for('clients_list'))

# ==================== SERVICES ====================

@app.route('/services')
def services_list():
    conn = get_db_connection()
    services = conn.execute("SELECT * FROM services ORDER BY category, service_name").fetchall()
    conn.close()
    return render_template('services/list.html', services=services)

@app.route('/services/add', methods=['POST'])
def service_add():
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO services (service_name, category, description, base_price)
        VALUES (?, ?, ?, ?)
    """, (
        request.form['service_name'], request.form['category'],
        request.form.get('description', ''), request.form.get('base_price', 0)
    ))
    conn.commit()
    conn.close()
    flash('Service added successfully!', 'success')
    return redirect(url_for('services_list'))

@app.route('/services/<int:id>/edit', methods=['POST'])
def service_edit(id):
    conn = get_db_connection()
    conn.execute("""
        UPDATE services SET service_name=?, category=?, description=?, base_price=?
        WHERE id=?
    """, (
        request.form['service_name'], request.form['category'],
        request.form.get('description', ''), request.form.get('base_price', 0), id
    ))
    conn.commit()
    conn.close()
    flash('Service updated!', 'success')
    return redirect(url_for('services_list'))

@app.route('/services/<int:id>/delete', methods=['POST'])
def service_delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM services WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Service deleted!', 'success')
    return redirect(url_for('services_list'))

# ==================== JOBS ====================

@app.route('/jobs')
def jobs_list():
    conn = get_db_connection()
    status = request.args.get('status', '')
    category = request.args.get('category', '')
    search = request.args.get('search', '')

    query = """
        SELECT j.*, c.name as client_name, s.service_name 
        FROM jobs j 
        JOIN clients c ON j.client_id = c.id 
        LEFT JOIN services s ON j.service_id = s.id
        WHERE 1=1
    """
    params = []
    if status:
        query += " AND j.status = ?"
        params.append(status)
    if category:
        query += " AND j.category = ?"
        params.append(category)
    if search:
        query += " AND (j.job_title LIKE ? OR c.name LIKE ? OR j.description LIKE ?)"
        params.extend([f'%{search}%'] * 3)

    query += " ORDER BY j.created_at DESC"
    jobs = conn.execute(query, params).fetchall()

    # Get categories for filter
    categories = conn.execute("SELECT DISTINCT category FROM jobs").fetchall()
    conn.close()
    return render_template('jobs/list.html', jobs=jobs, categories=categories, 
                         status=status, category=category, search=search)

@app.route('/jobs/add', methods=['GET', 'POST'])
def job_add():
    conn = get_db_connection()
    clients = conn.execute("SELECT id, name FROM clients ORDER BY name").fetchall()
    services = conn.execute("SELECT * FROM services WHERE is_active=1 ORDER BY service_name").fetchall()

    if request.method == 'POST':
        conn.execute("""
            INSERT INTO jobs (client_id, service_id, job_title, category, description, 
                            priority, assigned_to, start_date, due_date, cost, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form['client_id'], request.form.get('service_id') or None,
            request.form['job_title'], request.form['category'],
            request.form.get('description', ''), request.form.get('priority', 'Normal'),
            request.form.get('assigned_to', ''), request.form.get('start_date'),
            request.form.get('due_date'), request.form.get('cost', 0),
            request.form.get('notes', '')
        ))
        conn.commit()
        conn.close()
        flash('Job created successfully!', 'success')
        return redirect(url_for('jobs_list'))

    conn.close()
    return render_template('jobs/form.html', job=None, clients=clients, services=services)

@app.route('/jobs/<int:id>')
def job_detail(id):
    conn = get_db_connection()
    job = conn.execute("""
        SELECT j.*, c.name as client_name, c.phone as client_phone, c.address as client_address,
               s.service_name, s.base_price
        FROM jobs j 
        JOIN clients c ON j.client_id = c.id 
        LEFT JOIN services s ON j.service_id = s.id
        WHERE j.id = ?
    """, (id,)).fetchone()
    conn.close()
    return render_template('jobs/detail.html', job=job)

@app.route('/jobs/<int:id>/edit', methods=['GET', 'POST'])
def job_edit(id):
    conn = get_db_connection()
    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (id,)).fetchone()
    clients = conn.execute("SELECT id, name FROM clients ORDER BY name").fetchall()
    services = conn.execute("SELECT * FROM services WHERE is_active=1 ORDER BY service_name").fetchall()

    if request.method == 'POST':
        status = request.form.get('status', job['status'])
        completed_date = None
        if status == 'Completed' and job['status'] != 'Completed':
            completed_date = datetime.now().strftime('%Y-%m-%d')
        elif status != 'Completed':
            completed_date = None
        else:
            completed_date = job['completed_date']

        conn.execute("""
            UPDATE jobs SET client_id=?, service_id=?, job_title=?, category=?, description=?,
                          status=?, priority=?, assigned_to=?, start_date=?, due_date=?,
                          completed_date=?, cost=?, notes=?
            WHERE id=?
        """, (
            request.form['client_id'], request.form.get('service_id') or None,
            request.form['job_title'], request.form['category'],
            request.form.get('description', ''), status,
            request.form.get('priority', 'Normal'), request.form.get('assigned_to', ''),
            request.form.get('start_date'), request.form.get('due_date'),
            completed_date, request.form.get('cost', 0), request.form.get('notes', ''), id
        ))
        conn.commit()
        conn.close()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('job_detail', id=id))

    conn.close()
    return render_template('jobs/form.html', job=job, clients=clients, services=services)

@app.route('/jobs/<int:id>/delete', methods=['POST'])
def job_delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM jobs WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Job deleted!', 'success')
    return redirect(url_for('jobs_list'))

# ==================== INVOICES ====================

@app.route('/invoices')
def invoices_list():
    conn = get_db_connection()
    status = request.args.get('status', '')
    search = request.args.get('search', '')

    query = """
        SELECT i.*, c.name as client_name, c.phone as client_phone
        FROM invoices i 
        JOIN clients c ON i.client_id = c.id 
        WHERE 1=1
    """
    params = []
    if status:
        query += " AND i.status = ?"
        params.append(status)
    if search:
        query += " AND (i.invoice_number LIKE ? OR c.name LIKE ?)"
        params.extend([f'%{search}%'] * 2)

    query += " ORDER BY i.created_at DESC"
    invoices = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('invoices/list.html', invoices=invoices, status=status, search=search)

@app.route('/invoices/create', methods=['GET', 'POST'])
def invoice_create():
    conn = get_db_connection()
    clients = conn.execute("SELECT id, name FROM clients ORDER BY name").fetchall()
    services = conn.execute("SELECT * FROM services WHERE is_active=1 ORDER BY service_name").fetchall()

    if request.method == 'POST':
        client_id = request.form['client_id']
        job_id = request.form.get('job_id') or None
        issue_date = request.form.get('issue_date', datetime.now().strftime('%Y-%m-%d'))
        due_date = request.form.get('due_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))

        # Generate invoice number
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM invoices")
        count = cursor.fetchone()[0] + 1
        invoice_number = f"WARQ-{datetime.now().strftime('%Y%m')}-{count:04d}"

        # Calculate totals from items
        descriptions = request.form.getlist('item_description[]')
        quantities = request.form.getlist('item_quantity[]')
        unit_prices = request.form.getlist('item_unit_price[]')

        subtotal = 0
        items = []
        for desc, qty, price in zip(descriptions, quantities, unit_prices):
            if desc.strip():
                qty = float(qty) if qty else 1
                price = float(price) if price else 0
                total = qty * price
                subtotal += total
                items.append((desc, qty, price, total))

        tax_amount = subtotal * Config.TAX_RATE
        discount = float(request.form.get('discount', 0))
        total_amount = subtotal + tax_amount - discount

        conn.execute("""
            INSERT INTO invoices (invoice_number, client_id, job_id, issue_date, due_date,
                                subtotal, tax_amount, discount, total_amount, balance_due, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (invoice_number, client_id, job_id, issue_date, due_date,
              subtotal, tax_amount, discount, total_amount, total_amount, request.form.get('notes', '')))

        invoice_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        for item in items:
            conn.execute("""
                INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
            """, (invoice_id, item[0], item[1], item[2], item[3]))

        conn.commit()
        conn.close()
        flash(f'Invoice {invoice_number} created successfully!', 'success')
        return redirect(url_for('invoice_detail', id=invoice_id))

    conn.close()
    return render_template('invoices/create.html', clients=clients, services=services)

@app.route('/invoices/<int:id>')
def invoice_detail(id):
    conn = get_db_connection()
    invoice = conn.execute("""
        SELECT i.*, c.name as client_name, c.phone as client_phone, 
               c.email as client_email, c.address as client_address, c.cnic as client_cnic
        FROM invoices i 
        JOIN clients c ON i.client_id = c.id 
        WHERE i.id = ?
    """, (id,)).fetchone()

    items = conn.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (id,)).fetchall()
    payments = conn.execute("SELECT * FROM payments WHERE invoice_id = ? ORDER BY payment_date", (id,)).fetchall()
    conn.close()
    return render_template('invoices/detail.html', invoice=invoice, items=items, payments=payments)

@app.route('/invoices/<int:id>/pdf')
def invoice_pdf(id):
    conn = get_db_connection()
    invoice = conn.execute("""
        SELECT i.*, c.name as client_name, c.phone as client_phone, 
               c.email as client_email, c.address as client_address, c.cnic as client_cnic
        FROM invoices i 
        JOIN clients c ON i.client_id = c.id 
        WHERE i.id = ?
    """, (id,)).fetchone()

    items = conn.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (id,)).fetchall()
    conn.close()

    # Render HTML template for PDF
    html = render_template('invoices/invoice_pdf.html', invoice=invoice, items=items)

    # Generate PDF
    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.StringIO(html), result)

    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=Invoice_{invoice["invoice_number"]}.pdf'
        return response

    flash('Error generating PDF', 'error')
    return redirect(url_for('invoice_detail', id=id))

@app.route('/invoices/<int:id>/print')
def invoice_print(id):
    conn = get_db_connection()
    invoice = conn.execute("""
        SELECT i.*, c.name as client_name, c.phone as client_phone, 
               c.email as client_email, c.address as client_address, c.cnic as client_cnic
        FROM invoices i 
        JOIN clients c ON i.client_id = c.id 
        WHERE i.id = ?
    """, (id,)).fetchone()

    items = conn.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (id,)).fetchall()
    conn.close()
    return render_template('invoices/print.html', invoice=invoice, items=items)

@app.route('/invoices/<int:id>/delete', methods=['POST'])
def invoice_delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM invoices WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Invoice deleted!', 'success')
    return redirect(url_for('invoices_list'))

# ==================== PAYMENTS ====================

@app.route('/payments')
def payments_list():
    conn = get_db_connection()
    payments = conn.execute("""
        SELECT p.*, c.name as client_name, i.invoice_number
        FROM payments p 
        JOIN clients c ON p.client_id = c.id 
        JOIN invoices i ON p.invoice_id = i.id
        ORDER BY p.payment_date DESC
    """).fetchall()
    conn.close()
    return render_template('payments/list.html', payments=payments)

@app.route('/payments/add', methods=['POST'])
def payment_add():
    conn = get_db_connection()
    invoice_id = request.form['invoice_id']
    client_id = request.form['client_id']
    amount = float(request.form['amount'])
    payment_date = request.form['payment_date']
    payment_method = request.form.get('payment_method', 'Cash')
    reference_no = request.form.get('reference_no', '')
    notes = request.form.get('notes', '')

    conn.execute("""
        INSERT INTO payments (invoice_id, client_id, amount, payment_date, payment_method, reference_no, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (invoice_id, client_id, amount, payment_date, payment_method, reference_no, notes))

    # Update invoice
    conn.execute("""
        UPDATE invoices 
        SET paid_amount = paid_amount + ?, 
            balance_due = balance_due - ?,
            status = CASE 
                WHEN balance_due - ? <= 0 THEN 'Paid'
                WHEN paid_amount + ? > 0 THEN 'Partial'
                ELSE status
            END
        WHERE id = ?
    """, (amount, amount, amount, amount, invoice_id))

    conn.commit()
    conn.close()
    flash('Payment recorded successfully!', 'success')
    return redirect(url_for('invoice_detail', id=invoice_id))

# ==================== REPORTS ====================

@app.route('/reports')
def reports():
    conn = get_db_connection()

    # Revenue by category
    revenue_by_category = conn.execute("""
        SELECT j.category, COUNT(*) as job_count, COALESCE(SUM(i.total_amount), 0) as revenue
        FROM jobs j
        LEFT JOIN invoices i ON j.id = i.job_id
        GROUP BY j.category
    """).fetchall()

    # Monthly summary
    monthly_summary = conn.execute("""
        SELECT 
            strftime('%Y-%m', created_at) as month,
            COUNT(*) as invoice_count,
            COALESCE(SUM(total_amount), 0) as total,
            COALESCE(SUM(paid_amount), 0) as collected,
            COALESCE(SUM(balance_due), 0) as pending
        FROM invoices
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """).fetchall()

    # Expense summary
    expense_summary = conn.execute("""
        SELECT 
            category,
            COALESCE(SUM(amount), 0) as total
        FROM expenses
        GROUP BY category
    """).fetchall()

    conn.close()
    return render_template('reports.html', 
                         revenue_by_category=revenue_by_category,
                         monthly_summary=monthly_summary,
                         expense_summary=expense_summary)

# ==================== EXPORTS ====================

@app.route('/export/clients')
def export_clients():
    conn = get_db_connection()
    clients = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Clients"

    headers = ['ID', 'Name', 'Contact Person', 'Phone', 'Email', 'Address', 'CNIC', 'Type', 'Created']
    ws.append(headers)

    for client in clients:
        ws.append([
            client['id'], client['name'], client['contact_person'],
            client['phone'], client['email'], client['address'],
            client['cnic'], client['client_type'], client['created_at']
        ])

    # Style header
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2c3e50", end_color="2c3e50", fill_type="solid")
        cell.alignment = Alignment(horizontal='center')

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True, download_name=f'Waraq_Clients_{datetime.now().strftime("%Y%m%d")}.xlsx')

@app.route('/export/invoices')
def export_invoices():
    conn = get_db_connection()
    invoices = conn.execute("""
        SELECT i.*, c.name as client_name 
        FROM invoices i 
        JOIN clients c ON i.client_id = c.id 
        ORDER BY i.created_at DESC
    """).fetchall()
    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Invoices"

    headers = ['Invoice #', 'Client', 'Issue Date', 'Due Date', 'Subtotal', 'Tax', 'Discount', 'Total', 'Paid', 'Balance', 'Status']
    ws.append(headers)

    for inv in invoices:
        ws.append([
            inv['invoice_number'], inv['client_name'], inv['issue_date'],
            inv['due_date'], inv['subtotal'], inv['tax_amount'],
            inv['discount'], inv['total_amount'], inv['paid_amount'],
            inv['balance_due'], inv['status']
        ])

    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2c3e50", end_color="2c3e50", fill_type="solid")
        cell.alignment = Alignment(horizontal='center')

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True, download_name=f'Waraq_Invoices_{datetime.now().strftime("%Y%m%d")}.xlsx')

@app.route('/export/jobs')
def export_jobs():
    conn = get_db_connection()
    jobs = conn.execute("""
        SELECT j.*, c.name as client_name, s.service_name
        FROM jobs j 
        JOIN clients c ON j.client_id = c.id 
        LEFT JOIN services s ON j.service_id = s.id
        ORDER BY j.created_at DESC
    """).fetchall()
    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Jobs"

    headers = ['ID', 'Client', 'Service', 'Title', 'Category', 'Status', 'Priority', 'Assigned To', 'Start', 'Due', 'Cost']
    ws.append(headers)

    for job in jobs:
        ws.append([
            job['id'], job['client_name'], job['service_name'],
            job['job_title'], job['category'], job['status'],
            job['priority'], job['assigned_to'], job['start_date'],
            job['due_date'], job['cost']
        ])

    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2c3e50", end_color="2c3e50", fill_type="solid")
        cell.alignment = Alignment(horizontal='center')

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True, download_name=f'Waraq_Jobs_{datetime.now().strftime("%Y%m%d")}.xlsx')

# ==================== BACKUP ====================

@app.route('/backup')
def backup():
    import shutil
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(Config.BACKUP_DIR, f'waraq_backup_{timestamp}.db')
    shutil.copy2(Config.DATABASE, backup_path)
    flash(f'Database backed up to {backup_path}', 'success')
    return redirect(url_for('dashboard'))

# ==================== API ENDPOINTS ====================

@app.route('/api/client/<int:id>/jobs')
def api_client_jobs(id):
    conn = get_db_connection()
    jobs = conn.execute("SELECT id, job_title, cost FROM jobs WHERE client_id = ? AND status != 'Completed'", (id,)).fetchall()
    conn.close()
    return jsonify([dict(job) for job in jobs])

@app.route('/api/service/<int:id>')
def api_service(id):
    conn = get_db_connection()
    service = conn.execute("SELECT * FROM services WHERE id = ?", (id,)).fetchone()
    conn.close()
    return jsonify(dict(service) if service else {})

# ==================== MAIN ====================

if __name__ == '__main__':
    print("Starting Waraq Enterprise Management System...")
    print(f"Database: {Config.DATABASE}")
    print(f"Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, host='127.0.0.1', port=5000)
