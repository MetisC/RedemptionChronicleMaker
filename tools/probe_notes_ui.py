"""Render note authoring in our own Qt safe mode; no native desktop control."""
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
os.environ['QT_QPA_PLATFORM']='offscreen'
from PySide6.QtWidgets import QApplication,QLineEdit,QPlainTextEdit,QPushButton
from PySide6.QtGui import QFont,QFontDatabase
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.document import Document
from rcm.editor.window import MainWindow

def main():
    app=QApplication([]);app.setStyle('Fusion')
    font=QFontDatabase.addApplicationFont(str(Path(os.environ.get('SystemRoot',r'C:\Windows'))/'Fonts/segoeui.ttf'))
    app.setFont(QFont(QFontDatabase.applicationFontFamilies(font)[0],10))
    backend=Backend(Workspace(ROOT));backend.safe_mode=True
    win=MainWindow(backend);win.autosave_timer.stop();win.resize(1430,900)
    win.doc=Document.load(backend.ws,'chronicles/tutorial/project.yaml');win.refresh();win.show();app.processEvents()
    out=ROOT/'research/round0/notes_motion';out.mkdir(parents=True,exist_ok=True)
    index=next(i for i,e in enumerate(win.doc.data['events']) if e['id']=='welcome_note')
    win.center_tabs.setCurrentIndex(1);win.select(('events',index,'actions',0));app.processEvents()
    form=win.properties.widget()
    assert form.findChild(QLineEdit,'note_title').text()=='Bienvenido al tutorial'
    assert '\n\n' in form.findChild(QPlainTextEdit,'note_text').toPlainText()
    win.grab().save(str(out/'note_editor.png'))
    index=next(i for i,o in enumerate(win.doc.data['objects']) if o['id']=='barrel')
    win.select(('objects',index));app.processEvents()
    assert win.properties.widget().findChild(QPushButton,'object_note') is not None
    win.grab().save(str(out/'object_interaction.png'))
    (out/'gui_probe.json').write_text(json.dumps(dict(safe_mode=True,notes_editor=True,object_shortcuts=True,native_engine_test=False),indent=2))
    win.doc=None;win.close();app.processEvents()

if __name__=='__main__':main()
