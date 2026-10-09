"""Fast real-window rendering check for final light/dark table colors."""
from pathlib import Path
import json
import os
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
os.environ['QT_QPA_PLATFORM']='windows'
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette,QColor,QFont
from PySide6.QtTest import QTest
from rcm.editor.window import MainWindow
from rcm.editor.theme import editor_palette
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.document import Document
app=QApplication([]);app.setStyle('Fusion');app.setFont(QFont('Segoe UI',10))
backend=Backend(Workspace(ROOT));backend.safe_mode=True
out=ROOT/'research/phase9/editor_fixes/gui';out.mkdir(parents=True,exist_ok=True)
records=[]
for mode,color in [('dark','#20242b'),('light','#ffffff')]:
    source=QPalette();source.setColor(QPalette.ColorRole.Window,QColor(color));app.setPalette(editor_palette(source))
    w=MainWindow(backend);w.autosave_timer.stop();w.doc=Document.load(backend.ws,ROOT/'chronicles/circuit/project.yaml');w.refresh();w.select(('actors',0));w.center_tabs.setCurrentIndex(1);w.show();w.activateWindow();QTest.qWait(150)
    try:
        item=w.content.topLevelItem(1);rect=w.content.visualItemRect(item);pixmap=w.content.viewport().grab();img=pixmap.toImage();scale=pixmap.devicePixelRatio()
        sample=img.pixelColor(int((rect.right()-10)*scale),int(rect.center().y()*scale)).name()
        expected=w.palette().color(QPalette.ColorRole.AlternateBase).name()
        if sample!=expected:raise ValueError(mode+' alternate row differs: '+sample+' != '+expected)
        w.validate_project();info=w.problem_table.item(0,0).foreground().color().name()
        w.grab().save(str(out/('story_'+mode+'.png')))
        w.doc.active=1;w.refresh();w.select(('conversations',0));w.center_tabs.setCurrentWidget(w.graph_panel);w.graph_panel.refresh();w.graph_panel.fit();QTest.qWait(100);w.grab().save(str(out/('graph_'+mode+'.png')))
        records.append(dict(mode=mode,alternate_row_pixel=sample,expected_alternate=expected,info_text_color=info))
    finally:w.doc=None;w.close();app.processEvents()
result=dict(success=True,rendered_windows=records,real_window=True,real_gl=False,native_engine_test=False)
(out/'colors.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
