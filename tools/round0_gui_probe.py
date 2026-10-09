"""Real Qt/GL rendering of our own editor; no native game automation."""
from pathlib import Path
import json,os,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
os.environ['QT_QPA_PLATFORM']='windows'
from PySide6.QtWidgets import QApplication,QListWidget
from PySide6.QtGui import QFont
from PySide6.QtTest import QTest
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.deployment import default_game
from rcm.editor.window import MainWindow
from rcm.editor.campaign_panel import InventoryDialog
from rcm.editor.browser import ResourceDialog
from rcm.editor.identity import set_identity
app=QApplication([]);app.setStyle('Fusion');app.setFont(QFont('Segoe UI',10));set_identity(app)
backend=Backend(Workspace(ROOT,default_game(ROOT)));out=ROOT/'research/round0/gui';out.mkdir(parents=True,exist_ok=True)
win=MainWindow(backend);win.autosave_timer.stop();win.open_path(ROOT/'chronicles/tutorial/project.yaml');win.show();win.activateWindow()
started=time.monotonic()
while win.spatial.loading or win.spatial.viewport.level is None:
    app.processEvents();QTest.qWait(100)
    if time.monotonic()-started>150:raise RuntimeError('Viewport timeout: '+win.spatial.status.text())
win.select(('actors',0));win.center_tabs.setCurrentIndex(0);win.spatial.viewport.focus_selection();QTest.qWait(150);win.grab().save(str(out/'viewport.png'))
win.campaign_panel.navigate(('scenes',0,'paths',0));QTest.qWait(100);win.grab().save(str(out/'route.png'))
form_height=win.campaign_panel.scroll.height();route=win.campaign_panel.scroll.findChild(QListWidget,'path_points');visible_rows=int(route.viewport().height()/max(1,route.sizeHintForRow(0)))
if form_height<190 or visible_rows<3:raise ValueError('Route content too small')
inventory=InventoryDialog(win,win.doc.data['actors'][2]);inventory.show();QTest.qWait(100);inventory.grab().save(str(out/'inventory.png'));inventory.reject()
catalogue=ResourceDialog(backend,'items',win);catalogue.browser.family.setCurrentIndex(catalogue.browser.family.findData('weapons'));catalogue.show();QTest.qWait(100);catalogue.grab().save(str(out/'catalogue.png'));catalogue.reject()
win.select(('conversations',2));QTest.qWait(100);win.grab().save(str(out/'dialogue_camera.png'))
win.center_tabs.setCurrentWidget(win.guide_panel);QTest.qWait(100);win.grab().save(str(out/'guide.png'))
report=dict(success=True,real_window=True,real_gl=win.spatial.viewport.isValid(),route_form_height=form_height,route_rows_visible=visible_rows,custom_icon=not win.windowIcon().isNull(),elapsed_seconds=time.monotonic()-started,native_game_test=False,hardware_mouse_automation=False)
(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2));win.doc=None;win.close()
