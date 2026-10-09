"""Actual Qt/OpenGL regression journey for editor usability; no game launch."""
from pathlib import Path
import os
import sys
import json
import time
from unittest.mock import patch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'cache/vendor')]
os.environ['QT_QPA_PLATFORM'] = 'windows'
from PySide6.QtCore import Qt, QPoint, QPointF, QTimer, QEvent
from PySide6.QtGui import QColor, QPalette, QFont, QCursor, QMouseEvent
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QMessageBox
from PySide6.QtTest import QTest
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.deployment import default_game
from rcm.editor.window import MainWindow

app = QApplication([])
app.setStyle('Fusion')
app.setFont(QFont('Segoe UI', 10))
palette = app.palette()
palette.setColor(QPalette.ColorRole.Window, QColor('#20242b'))
app.setPalette(palette)
ws = Workspace(ROOT, default_game(ROOT))
out = ws.output('research/phase9/editor_fixes/gui')
out.mkdir(parents=True, exist_ok=True)
w = MainWindow(Backend(ws))
w.open_path(ws.output('chronicles/circuit/project.yaml'))
w.show()
w.activateWindow()
w.center_tabs.setCurrentIndex(0)
w.spatial.ensure_loaded()
w.autosave_timer.stop()  # Probe edits live only in memory, never user sources.
steps = []


def wait_level():
    end = time.monotonic() + 180
    while w.spatial.loading or w.spatial.loaded_name != 'EastLondon':
        if time.monotonic() > end:
            raise ValueError('Viewport load timeout: ' + w.spatial.status.text() + '\n' + w.log.toPlainText()[-3000:])
        app.processEvents()
        QTest.qWait(20)


def pick_template():
    dialog = app.activeModalWidget()
    if dialog is None or not hasattr(dialog, 'browser'):
        raise ValueError('Template dialog was not opened')
    table = dialog.browser.table
    row = next(i for i in range(table.rowCount()) if table.item(i, 0).text() == 'businessWoman')
    table.setCurrentCell(row, 0)
    dialog.buttons.button(QDialogButtonBox.StandardButton.Ok).click()


def confirm_delete():
    dialog = app.activeModalWidget()
    if not isinstance(dialog, QMessageBox):
        raise ValueError('Delete did not ask for confirmation')
    dialog.button(QMessageBox.StandardButton.Yes).click()


try:
    wait_level()
    v = w.spatial.viewport
    if not v or not v.isValid():
        raise ValueError('No real OpenGL context')
    v.pos = np.array([1016., -400., 950.])
    v.yaw = 90
    v.pitch = -75
    v.update()
    QTest.qWait(200)
    QTimer.singleShot(100, pick_template)
    w.spatial.findChild(__import__('PySide6.QtWidgets', fromlist=['QPushButton']).QPushButton, 'place_actor').click()
    if not v.placing or v.placing[1] != 'businessWoman':
        raise ValueError('Actor was not armed with chosen template')
    point = v.project(np.array([1016., -160., 0.]))
    before = len(w.doc.data['actors'])
    QTest.mouseClick(v, Qt.MouseButton.LeftButton, pos=point.toPoint())
    app.processEvents()
    if len(w.doc.data['actors']) != before + 1 or w.doc.data['actors'][-1]['template'] != 'businessWoman':
        raise ValueError('Actor placement failed')
    wait_level()
    w.center_tabs.setCurrentIndex(0)
    v.setFocus()
    QTimer.singleShot(100, confirm_delete)
    QTest.keyClick(v, Qt.Key.Key_Delete)
    app.processEvents()
    if len(w.doc.data['actors']) != before:
        raise ValueError('Supr did not delete placed actor')
    steps += ['choose actor from real resource dialog', 'place actor by floor click', 'delete actor with viewport Supr and confirmation']
    w.spatial.add_trigger()
    point = v.project(np.array([1016., -160., 0.]))
    before = len(w.doc.data['triggers'])
    QTest.mouseClick(v, Qt.MouseButton.LeftButton, pos=point.toPoint())
    app.processEvents()
    if len(w.doc.data['triggers']) != before + 1:
        raise ValueError('Trigger placement failed')
    v.setFocus()
    QTimer.singleShot(100, confirm_delete)
    QTest.keyClick(v, Qt.Key.Key_Delete)
    if len(w.doc.data['triggers']) != before:
        raise ValueError('Supr did not delete placed trigger')
    steps += ['place trigger by floor click', 'delete trigger with viewport Supr and confirmation']
    v.yaw = 90
    v.pitch = -30
    center = v.rect().center()
    QTest.mousePress(v, Qt.MouseButton.RightButton, pos=center)
    def mouse(position):
        event = QMouseEvent(QEvent.Type.MouseMove, QPointF(position), QPointF(v.mapToGlobal(position)), Qt.MouseButton.NoButton, Qt.MouseButton.RightButton, Qt.KeyboardModifier.NoModifier)
        app.sendEvent(v, event)
    mouse(center + QPoint(40, -20))
    if not v.yaw < 90 or not v.pitch > -30:
        raise ValueError('Camera direction wrong')
    # The sandbox doesn't deliver physical Windows cursor moves to this test
    # window. Verify the exact Qt event path and warp command synthetically,
    # without presenting it as a hardware/driver acceptance result.
    with patch.object(QCursor, 'setPos') as warp:
        mouse(QPoint(5, 10))
    if not warp.called:
        raise ValueError('Viewport did not request cursor recenter')
    old_angles = v.yaw, v.pitch
    mouse(v.rect().center())
    mouse(v.rect().center() + QPoint(10, 10))
    if v.warp_target is not None:
        raise ValueError('OS recenter not consumed')
    if abs(v.pitch-old_angles[1])>3 or abs(((v.yaw-old_angles[0]+180)%360)-180)>3:
        raise ValueError('Recenter introduced an angle jump')
    QTest.mouseRelease(v, Qt.MouseButton.RightButton, pos=v.rect().center())
    steps += ['synthetic Qt RMB horizontal/vertical direction in real viewport', 'synthetic recenter without angle jump']
    tab_y = []
    for index in range(w.center_tabs.count()):
        w.center_tabs.setCurrentIndex(index)
        app.processEvents()
        tab_y.append(w.center_tabs.tabBar().mapToGlobal(QPoint()).y())
    if len(set(tab_y)) != 1:
        raise ValueError('Tab bar shifted between pages')
    steps += ['fixed tab-bar position across all modes']
    w.select(('actors', 0))
    w.center_tabs.setCurrentIndex(1)
    w.content.setFocus()
    w.content.setCurrentItem(w.content_items[('actors', 0)])
    QTest.qWait(120)
    w.grab().save(str(out / 'story_dark.png'))
    w.doc.active = 1
    w.refresh()
    w.select(('conversations', 0))
    w.center_tabs.setCurrentWidget(w.graph_panel)
    w.graph_panel.refresh()
    w.graph_panel.fit()
    QTest.qWait(120)
    w.grab().save(str(out / 'graph_dark.png'))
    result = dict(success=True, steps=steps, real_gl=v.isValid(), viewport_error=v.error,
                  tab_bar_y=tab_y, native_engine_test=False, user_project_modified=False,
                  hardware_cursor_test=False, camera_input='synthetic Qt events; physical Windows movement not delivered in sandbox',
                  screenshots=['story_dark.png', 'graph_dark.png'])
    ws.write(out / 'probe.json', json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
finally:
    w.doc = None
    w.close()
    app.processEvents()
