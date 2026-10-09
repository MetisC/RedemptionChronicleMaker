"""Own chronicle/ankh icon, independent of the game's executable."""
from pathlib import Path
from PySide6.QtGui import QIcon

def application_icon():
    return QIcon(str(Path(__file__).parent/'assets/chronicle.svg'))

def set_identity(app):
    import sys
    if sys.platform=='win32':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('RCM.ChronicleMaker.Editor')
    app.setWindowIcon(application_icon())
