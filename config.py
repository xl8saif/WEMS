import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("WEMS_DATA_DIR") or BASE_DIR

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'waraq-secret-key-2024'
    DATABASE = os.path.join(DATA_DIR, 'database', 'waraq.db')
    INVOICE_DIR = os.path.join(DATA_DIR, 'invoices')
    EXPORT_DIR = os.path.join(DATA_DIR, 'exports')
    BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
    
    # Use DATA_DIR for static images in frozen context (PyInstaller)
    STATIC_IMAGE_DIR = os.path.join(DATA_DIR, 'static', 'images')

    COMPANY_NAME = "Waraq Enterprises"
    COMPANY_ADDRESS = "Waraq KIU Road, Konodas, Gilgit, Pakistan"
    COMPANY_PHONE = "+92 310 0989830"
    COMPANY_EMAIL = "xl8.saif@gmail.com"

    # Canonical local assets used by WEMS invoices and documents.
    LOGO_PATH = os.path.join(STATIC_IMAGE_DIR, 'waraq-logo.png')
    STAMP_PATH = os.path.join(STATIC_IMAGE_DIR, 'Waraq-Stamp.jpg')
    SIGNATURE_PATH = os.path.join(STATIC_IMAGE_DIR, 'Waraq-Signature.jpg')

    # Business settings
    CURRENCY = "PKR"
    TAX_RATE = 0.0

    @staticmethod
    def init_app(app):
        pass
