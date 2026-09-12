import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'waraq-secret-key-2024'
    DATABASE = os.path.join(BASE_DIR, 'database', 'waraq.db')
    INVOICE_DIR = os.path.join(BASE_DIR, 'invoices')
    EXPORT_DIR = os.path.join(BASE_DIR, 'exports')
    BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
    STATIC_IMAGE_DIR = os.path.join(BASE_DIR, 'static', 'images')

    COMPANY_NAME = "Waraq Enterprises"
    COMPANY_ADDRESS = "Gilgit, Pakistan"
    COMPANY_PHONE = "+92-XXX-XXXXXXX"
    COMPANY_EMAIL = "info@waraqenterprises.com"

    # File paths for logo, stamp, signature
    LOGO_PATH = os.path.join(STATIC_IMAGE_DIR, 'logo.png')
    STAMP_PATH = os.path.join(STATIC_IMAGE_DIR, 'stamp.png')
    SIGNATURE_PATH = os.path.join(STATIC_IMAGE_DIR, 'signature.png')

    # Business settings
    CURRENCY = "PKR"
    TAX_RATE = 0.0  # Update as needed

    @staticmethod
    def init_app(app):
        pass
