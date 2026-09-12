# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

hiddenimports = [
    "sqlite3",
    "xhtml2pdf",
    "PIL",
]

binaries = []
datas = [
    ("templates", "templates"),
    ("static", "static"),
    ("database", "database"),
]

# Include package data required by xhtml2pdf/reportlab where available.
for package in ("xhtml2pdf", "reportlab"):
    try:
        datas += collect_data_files(package)
    except Exception:
        pass


from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT


a = Analysis(
    ["wems_launcher.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="WEMS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="WEMS",
)
