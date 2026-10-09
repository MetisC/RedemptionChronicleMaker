"""Inspect our own real Qt OpenGL window and persist diagnostics/screenshots."""
from pathlib import Path
import os
import sys
import time
import json
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'cache/vendor')]
os.environ['QT_QPA_PLATFORM'] = 'windows'
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtTest import QTest
from rcm.service import Backend
from rcm.paths import Workspace
from rcm.editor.window import MainWindow
app = QApplication([])
QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf')
app.setFont(QFont('Segoe UI', 10));app.setStyle('Fusion')
w = MainWindow(Backend(Workspace(ROOT, Path(r'H:\GOG\Vampire The Masquerade - Redemption'))))
w.open_path(ROOT/'tests/fixtures/chronicles/editor_acceptance/project.yaml')
w.show()
w.center_tabs.setCurrentIndex(0)
until = time.monotonic()+25
while not w.spatial.loaded_name and time.monotonic()<until:
    app.processEvents()
    time.sleep(.02)
for _ in range(50):
    app.processEvents()
    time.sleep(.02)
w.select(('actors',0));w.spatial.viewport.focus_selection();QTest.qWait(250)
out=ROOT/'build/viewport';out.mkdir(parents=True,exist_ok=True)
v=w.spatial.viewport
w.grab().save(str(out/'editor.png'))
v.grabFramebuffer().save(str(out/'eastlondon.png'))
report=dict(loaded=w.spatial.loaded_name, error=v.error, valid=v.isValid(), renderer=str(v.context().format()) if v.context() else None, frames=v.frame_count, mean_render_ms=1000*sum(v.frame_times)/max(1,len(v.frame_times)))
(out/'probe.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
w.doc._saved = __import__('rcm.service',fromlist=['source_text']).source_text(w.doc.data)
w.close();app.processEvents()
