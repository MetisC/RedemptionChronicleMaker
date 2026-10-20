"""Bilingual offscreen inspection of optional controls, with no game automation."""
import argparse,json,os,sys,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
os.environ['QT_QPA_PLATFORM']='offscreen'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--language',choices=['en','es'],required=True);args=parser.parse_args()
    from PySide6.QtWidgets import QApplication,QDialog,QLabel,QPushButton,QComboBox
    from PySide6.QtGui import QFont,QFontDatabase
    from rcm.paths import Workspace
    from rcm.app_settings import AppSettings
    from rcm.service import Backend
    from rcm.document import Document
    from rcm.editor.window import MainWindow
    from rcm.editor.i18n import configure,save_language,install_qt,catalogue
    from rcm.editor.theme import editor_palette
    from rcm.editor.maps import MapDialog
    from rcm.editor.environment import EnvironmentDialog
    from rcm.editor.native_scripts import NativeScriptDialog
    from rcm.editor.director import CameraPathDialog
    from rcm.editor.zones import edit_zone
    app=QApplication([]);app.setStyle('Fusion')
    for name in ('segoeui.ttf','segoeuib.ttf','segoeuii.ttf'):
        path=Path(os.environ.get('SystemRoot',r'C:\Windows'))/'Fonts'/name
        if path.is_file():QFontDatabase.addApplicationFont(str(path))
    app.setFont(QFont('Segoe UI',10));app.setPalette(editor_palette(app.palette()))
    output=ROOT/'build/tests/completion_editor'/args.language;output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as temporary:
        ws=Workspace(ROOT);ws.app_settings=AppSettings(Path(temporary)/'settings');save_language(ws,args.language);configure(ws);install_qt(app)
        backend=Backend(ws);win=MainWindow(backend);win.doc=Document.load(ws,'chronicles/completion_lab/project.yaml');win.refresh();win.show();app.processEvents();before=win.doc.snapshot();screens=[];untranslated=[]
        def capture(widget,name):
            widget.show();app.processEvents();widget.grab().save(str(output/(name+'.png')));screens.append(name)
            if args.language=='en':
                texts=[w.text() for w in widget.findChildren(QLabel)]+[w.text() for w in widget.findChildren(QPushButton)]
                for box in widget.findChildren(QComboBox):texts.extend(box.itemText(i) for i in range(box.count()))
                untranslated.extend(t for t in texts if t in catalogue() and catalogue()[t]!=t)
        dialog=MapDialog(win);capture(dialog,'maps');dialog.reject()
        dialog=EnvironmentDialog(win);capture(dialog,'environment');dialog.reject()
        scene=win.doc.campaign['scenes'][0];native=NativeScriptDialog(win,scene['triggers'][0]);capture(native,'native_region');native.reject()
        saved=win.spatial.viewport
        win.spatial.viewport=SimpleNamespace(pos=[0,0,0],pitch=0,yaw=0,update=lambda:None)
        dialog=CameraPathDialog(win,('scenes',0,'sequences',0));capture(dialog,'timed_camera');assert dialog.timed.isChecked();dialog.reject();win.spatial.viewport=saved
        for kind in ('sound','light'):
            def cancel(dialog,kind=kind):capture(dialog,kind+'_zone');return QDialog.DialogCode.Rejected
            with patch('rcm.editor.zones.QDialog.exec',cancel):edit_zone(win,scene['triggers'][1],kind)
        from rcm.editor.content_libraries import open_import
        from rcm.generator import zip_bytes
        from rcm.camera_paths import authored
        source=Path(temporary)/'camera_library.nob';source.write_bytes(zip_bytes({'camera/QuietTurn.ncp':authored([dict(position=[0,0,100],orientation=[0,0,0],duration=2),dict(position=[0,0,100],orientation=[0,0,90])],True).encode()}))
        def cancel_import(dialog):capture(dialog,'data_library');return QDialog.DialogCode.Rejected
        with patch('rcm.editor.content_libraries.QFileDialog.getOpenFileName',return_value=(str(source),'')),patch('rcm.editor.content_libraries.QDialog.exec',cancel_import):open_import(win)
        win.campaign_panel.navigate(('scenes',0,'sequences',1));capture(win,'dynamic_camera')
        assert not untranslated,sorted(set(untranslated))
        assert win.doc.snapshot()==before
        win.doc=None;win.close();app.processEvents()
        report=dict(successful=True,language=args.language,screens=screens,project_unchanged=True,offscreen=True,native_engine_test=False,physical_gpu_dpi_test=False)
        (output/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))


if __name__=='__main__':main()
