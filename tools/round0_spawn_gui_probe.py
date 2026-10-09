"""Exercise the new start locator in our own visible Qt/GL editor."""
from pathlib import Path
import os,sys,json,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
os.environ['QT_QPA_PLATFORM']='windows'
from PySide6.QtWidgets import QApplication,QPushButton
from PySide6.QtGui import QColor
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.deployment import default_game
from rcm.editor.window import MainWindow
from rcm.editor.identity import set_identity

app=QApplication([]);app.setStyle('Fusion');set_identity(app)
win=MainWindow(Backend(Workspace(ROOT,default_game(ROOT))));win.autosave_timer.stop()
win.open_path(ROOT/'chronicles/tutorial/project.yaml');win.show()
started=time.monotonic()
button=win.spatial.findChild(QPushButton,'focus_player_start')
QTest.mouseClick(button,Qt.MouseButton.LeftButton)
while win.spatial.loading or win.spatial.viewport.level is None:
    app.processEvents();QTest.qWait(100)
    if time.monotonic()-started>180:raise ValueError('Viewport load timeout')
QTest.qWait(200)
if win.selection!=('entries',0) or win.center_tabs.currentIndex()!=0:raise ValueError('Start not selected')
position=win.spatial.viewport.pos.tolist()
expected=[v+d for v,d in zip(win.doc.data['entries'][0]['transform']['position'],[230,-320,180])]
if position!=expected:raise ValueError('Start not focused: '+str(position))
out=ROOT/'research/round0/spawn_fix';out.mkdir(parents=True,exist_ok=True)
snapshot=win.grab()
snapshot.save(str(out/'start_locator.png'))
view=win.spatial.viewport
origin=view.mapTo(win,view.rect().topLeft())
ratio=snapshot.devicePixelRatio()
pixels=snapshot.toImage().copy(int(origin.x()*ratio),int(origin.y()*ratio),int(view.width()*ratio),int(view.height()*ratio))
marker_color=QColor('#ffd064').rgba()
marker_pixels=sum(pixels.pixel(x,y)==marker_color for y in range(pixels.height()) for x in range(pixels.width()))
if marker_pixels<20:raise ValueError('Selected arrival marker is not visible above GL')
report=dict(start_selected=True,start_focused=True,start_marker_visible=True,selected_marker_pixels=marker_pixels,real_gl=view.isValid(),camera_position=position,entry_position=win.doc.data['entries'][0]['transform']['position'],elapsed_seconds=time.monotonic()-started,native_game_test=False)
(out/'gui_probe.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
win.doc=None;win.close()
