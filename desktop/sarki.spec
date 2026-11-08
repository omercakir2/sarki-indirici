# PyInstaller spec for the desktop app.
#   python desktop/fetch_tools.py && python desktop/make_icon.py
#   (cd frontend && npm ci && npm run build)
#   pyinstaller desktop/sarki.spec --noconfirm
# macOS → dist/Sarki Indirici.app   Windows → dist/Sarki-Indirici.exe
import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

HERE = Path(SPECPATH)
ROOT = HERE.parent
IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"

datas = [
    (str(ROOT / "frontend" / "dist"), "web"),
    (str(HERE / "bin"), "bin"),
]
hiddenimports = collect_submodules("uvicorn") + collect_submodules("app")

a = Analysis(
    [str(HERE / "launcher.py")],
    pathex=[str(ROOT / "backend")],
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["tkinter", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)

if IS_WIN:
    # One double-clickable .exe: friends never see a folder of DLLs.
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name="Sarki-Indirici",
        console=False,
        icon=str(HERE / "assets" / "icon.ico"),
        upx=False,
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="Sarki-Indirici",
        console=False,
        icon=str(HERE / "assets" / ("icon.png" if IS_MAC else "icon.ico")),
        upx=False,
    )
    coll = COLLECT(exe, a.binaries, a.datas, name="Sarki-Indirici", upx=False)
    if IS_MAC:
        app = BUNDLE(
            coll,
            name="Sarki Indirici.app",
            icon=str(HERE / "assets" / "icon.png"),
            bundle_identifier="io.github.omercakir2.sarki-indirici",
            info_plist={
                "CFBundleDisplayName": "Şarkı İndirici",
                "CFBundleName": "Şarkı İndirici",
                "CFBundleShortVersionString": os.environ.get("APP_VERSION", "0.1.0").lstrip("v"),
                "NSHighResolutionCapable": True,
                "LSMinimumSystemVersion": "11.0",
            },
        )
