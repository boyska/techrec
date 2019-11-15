# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ["server/cli.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("server/default_config.py", "."),
        ("server/pages/", "pages/"),
        ("server/static/", "static/"),
    ],
    hiddenimports=[
        "techrec.cli",
        "techrec.config_manager",
        "techrec.db",
        "techrec.default_config",
        "techrec.forge",
        "techrec.maint",
        "techrec.processqueue",
        "techrec.server",
        "techrec.test_forge",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="techrec",
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
# vim: set ft=python:
