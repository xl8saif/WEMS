# Waraq Enterprise Management System (WEMS)

An offline desktop business management system for Waraq Enterprises, Gilgit.

## Features
- **Client Management** - Store and manage client profiles
- **Job Tracking** - Track legal drafting, court files, printing, online registration
- **Invoicing** - Generate professional invoices with PDF export
- **Payments** - Record payments and track outstanding balances
- **Services Catalog** - Pre-configured services with pricing
- **Reports & Analytics** - Revenue charts, monthly summaries
- **Excel Export** - Export clients, invoices, and jobs to Excel
- **Database Backup** - One-click SQLite backup

## Tech Stack
- Python 3.8+ / Flask
- SQLite (offline storage)
- HTML5 / CSS3 / JavaScript
- Chart.js for analytics
- xhtml2pdf for PDF generation
- openpyxl for Excel export

## Installation

1. Install Python 3.8 or higher from https://python.org
2. Open Command Prompt and navigate to this folder:
   ```bash
   cd Waraq-Enterprise-Management-System
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open your browser and go to:
   ```
   http://127.0.0.1:5000
   ```

## Folder Structure
```
Waraq-Enterprise-Management-System/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── database/
│   └── db.py             # Database models & utilities
│   └── waraq.db          # SQLite database (auto-created)
├── templates/            # HTML templates
├── static/
│   ├── css/style.css     # Application styles
│   └── js/app.js         # Frontend scripts
├── invoices/             # Generated PDF invoices
├── exports/              # Excel exports
└── backups/              # Database backups
```

## Customization
- Update `config.py` with your company details
- Add logo.png, stamp.png, signature.png to `static/images/`
- Adjust tax rates and currency in `config.py`

## License
Proprietary - Waraq Enterprises, Gilgit
