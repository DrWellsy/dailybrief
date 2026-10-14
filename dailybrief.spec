# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
    'dailybrief',
    'dailybrief.cli',
    'dailybrief.cache',
    'dailybrief.doctor',
    'dailybrief.scheduler',
    'dailybrief.mcp_server',
    'dailybrief.voice',
    'dailybrief.eod',
    'dailybrief.git_radar',
    'dailybrief.blockers',
    'dailybrief.actions',
    'dailybrief.git_context',
    'dailybrief.providers',
    'dailybrief.reader',
    'dailybrief.summarizer',
    'dailybrief.memory',
    'dailybrief.config',
    'dailybrief.i18n',
    'rich',
    'click',
    'anthropic',
]

tmp_ret = collect_all('rich')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('dailybrief')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='dailybrief',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
