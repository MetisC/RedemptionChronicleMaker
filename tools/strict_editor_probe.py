"""Bilingual non-mutating view of the new author controls; no game automation."""
import argparse,json,os,sys,tempfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--language',choices=['en','es'],required=True);args=parser.parse_args()
    from PySide6.QtWidgets import QApplication,QLabel,QPushButton,QComboBox,QDialog
    from PySide6.QtGui import QFont,QFontDatabase
    from rcm.paths import Workspace
    from rcm.service import Backend
    from rcm.document import Document
    from rcm.app_settings import AppSettings
    from rcm.editor.i18n import save_language,configure,install_qt,catalogue
    from rcm.editor.window import MainWindow
    from rcm.editor.environment import EnvironmentDialog
    from rcm.editor.native_scripts import NativeScriptDialog
    from rcm.editor.instance_overrides import edit_overrides
    app=QApplication([]);app.setStyle('Fusion')
    for name in ('segoeui.ttf','segoeuib.ttf','segoeuii.ttf'):
        font=Path(os.environ.get('SystemRoot',r'C:\Windows'))/'Fonts'/name
        if font.is_file():QFontDatabase.addApplicationFont(str(font))
    from rcm.editor.theme import editor_palette
    app.setPalette(editor_palette(app.palette()));app.setFont(QFont('Segoe UI',10))
    output=Workspace(ROOT).output('build/tests/strict_editor/'+args.language);output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
        ws=Workspace(ROOT);ws.app_settings=AppSettings(Path(folder)/'settings');save_language(ws,args.language);configure(ws);install_qt(app)
        backend=Backend(ws);win=MainWindow(backend);win.doc=Document.load(ws,'chronicles/strict_acceptance/project.yaml');before=win.doc.snapshot();win.refresh();win.show();app.processEvents();screens=[];untranslated=[]
        def capture(widget,name):
            widget.show();app.processEvents();widget.grab().save(str(output/(name+'.png')));screens.append(name)
            if args.language=='en':
                texts=[w.text() for w in widget.findChildren(QLabel)]+[w.text() for w in widget.findChildren(QPushButton)]
                for box in widget.findChildren(QComboBox):texts.extend(box.itemText(i) for i in range(box.count()))
                untranslated.extend(t for t in texts if t in catalogue() and catalogue()[t]!=t)
        win.select(('chronicle',));capture(win,'difficulty')
        environment=EnvironmentDialog(win);capture(environment,'environment');environment.reject()
        row=next(r for r in win.doc.data['objects'] if r['id']=='cargo_mover');native=NativeScriptDialog(win,row);capture(native,'native_script');assert native.frames==['cargo_high'];assert len(native.controls)==4;native.reject()
        def cancel(dialog):capture(dialog,'instance');return QDialog.DialogCode.Rejected
        with patch('rcm.editor.instance_overrides.QDialog.exec',cancel):edit_overrides(win,win.doc.data['actors'][0],True)
        from rcm.editor.content_libraries import manage_libraries
        def manager(dialog):capture(dialog,'libraries');return QDialog.DialogCode.Rejected
        with patch('rcm.editor.content_libraries.QDialog.exec',manager):manage_libraries(win)
        assert win.doc.snapshot()==before
        # Authored names are intentionally not translated.
        untranslated=[t for t in untranslated if t not in ('Normal',)]
        if untranslated:raise ValueError(sorted(set(untranslated)))
        win.doc=None;win.close();app.processEvents()
        result=dict(language=args.language,successful=True,screens=screens,project_unchanged=True,native_game_test=False,offscreen=True)
        (output/'report.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))


if __name__=='__main__':main()
