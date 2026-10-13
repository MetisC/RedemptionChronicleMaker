"""Exercise real Qt UI in one startup language, without writing project content."""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--language',choices=['en','es'],required=True);parser.add_argument('--report-directory',default='build/tests/editor_review');args=parser.parse_args()
    from rcm.paths import Workspace
    from rcm.editor.i18n import configure,save_language,install_qt,tr,language,catalogue
    from PySide6.QtWidgets import QApplication,QMessageBox,QComboBox,QPushButton,QLabel,QDialogButtonBox
    from PySide6.QtGui import QFont,QFontDatabase
    from PySide6.QtCore import QUrl
    app=QApplication([]);app.setStyle('Fusion')
    for name in ['segoeui.ttf','segoeuib.ttf','segoeuii.ttf','segoeuiz.ttf']:
        font=Path(os.environ.get('SystemRoot',r'C:\Windows'))/'Fonts'/name
        if font.is_file():QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont('Segoe UI',12))
    (ROOT/'build/tests').mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
        preferences=Workspace(Path(folder));save_language(preferences,args.language);configure(preferences);install_qt(app)
        from rcm.service import Backend
        from rcm.document import Document
        from rcm.editor.window import MainWindow
        from rcm.editor.browser import ResourceBrowser
        backend=Backend(Workspace(ROOT));backend.safe_mode=True
        win=MainWindow(backend);win.doc=Document.load(backend.ws,'chronicles/tutorial/project.yaml');before=win.doc.snapshot()
        win.refresh();win.show();app.processEvents()
        assert win.actions['save'].text()==('Save' if args.language=='en' else 'Guardar')
        assert win.language_menu.title()==('Language' if args.language=='en' else 'Idioma')
        assert win.language_actions[args.language].isChecked()
        win.select(('conversations',0));app.processEvents()
        camera=win.properties.widget().findChild(QComboBox,'conversation_camera')
        assert camera is not None and camera.currentData()=='ots_speaker_close'
        assert 'hombro' not in camera.itemText(0).casefold() if args.language=='en' else 'hombro' in camera.itemText(0).casefold()
        assert win.doc.snapshot()==before
        # Official Qt controls must follow the choice, rather than Windows.
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        assert buttons.button(QDialogButtonBox.StandardButton.Cancel).text().replace('&','')==('Cancel' if args.language=='en' else 'Cancelar')
        buttons.deleteLater()
        authored=set()
        def authored_strings(value):
            if isinstance(value,str):authored.add(value)
            elif isinstance(value,dict):
                for x in value.values():authored_strings(x)
            elif isinstance(value,list):
                for x in value:authored_strings(x)
        authored_strings(before)
        untranslated=[];inspected=0
        def inspect_labels():
            nonlocal inspected
            inspected+=1
            texts=[w.text() for w in win.findChildren(QLabel)]+[w.text() for w in win.findChildren(QPushButton)]
            for box in win.findChildren(QComboBox):texts.extend(box.itemText(i) for i in range(box.count()))
            if args.language=='en':
                untranslated.extend(text for text in texts if text in catalogue() and catalogue()[text]!=text and text not in authored)
        for kind in ['actors','objects','entries','triggers','conversations','events']:
            for index,row in enumerate(win.doc.data.get(kind,[])):
                win.select((kind,index));inspect_labels()
                for key in ['nodes','actions','conditions','choices']:
                    for j in range(len(row.get(key,[]))):win.select((kind,index,key,j));inspect_labels()
        for kind in ['quests']:
            for index in range(len(win.doc.campaign.get(kind,[]))):win.campaign_panel.navigate((kind,index));inspect_labels()
        for kind in ['paths','sequences','encounters','entries']:
            for index in range(len(win.doc.campaign['scenes'][0].get(kind,[]))):win.campaign_panel.navigate(('scenes',0,kind,index));inspect_labels()
        from rcm.editor.recipe_wizard import RecipeWizard,LABELS
        for kind in LABELS:
            wizard=RecipeWizard(win,kind);wizard.initializePage(1);wizard.show();app.processEvents();inspect_labels()
            wizard.reject();wizard.setParent(None);wizard.deleteLater();app.processEvents()
        assert not untranslated,sorted(set(untranslated))
        assert win.doc.snapshot()==before
        win.guide_panel.refresh();guide=win.guide_panel.text.toPlainText()
        assert ('six-second' in guide) if args.language=='en' else ('seis segundos' in guide)
        win.guide_panel.navigate(QUrl('rcm://square/entries/start'));app.processEvents()
        assert win.campaign_panel.path==('scenes',0,'entries',0)
        browser=ResourceBrowser(backend,'items');browser.family.setCurrentIndex(browser.family.findData('weapons'))
        assert browser.table.rowCount()>0
        browser.origin.setCurrentIndex(browser.origin.findData('Proyecto /'));assert browser.table.rowCount()==0
        assert browser.origin.currentData()=='Proyecto /'
        assert browser.origin.currentText()==('Project' if args.language=='en' else 'Proyecto')
        browser.deleteLater()
        # Persist through the actual menu callback to an isolated workspace.
        old_ws=backend.ws;backend.ws=preferences
        with patch.object(QMessageBox,'information'):
            other='es' if args.language=='en' else 'en';win.language_actions[other].trigger()
        backend.ws=old_ws
        assert json.loads(preferences.output('cache/editor_settings.json').read_text())['language']==other
        assert language()==args.language and win.doc.snapshot()==before
        labels=[w.text() for w in win.findChildren(QLabel)]+[w.text() for w in win.findChildren(QPushButton)]
        assert tr('Guardar') in [a.text() for a in win.actions.values()]
        win.open_editor_guide();assert 'phase3_demo' not in win.guide_panel.text.toPlainText()
        evidence=Workspace(ROOT);directory=evidence.output(args.report_directory);directory.mkdir(parents=True,exist_ok=True)
        win.resize(1100,720);app.processEvents();win.grab().save(str(evidence.output(directory/(args.language+'_minimum.png'))))
        wizard=RecipeWizard(win,'go_to_place');wizard.initializePage(1);wizard.setFont(QFont('Segoe UI',15));wizard.show();app.processEvents();wizard.next();app.processEvents()
        wizard.grab().save(str(evidence.output(directory/(args.language+'_assistant.png'))));wizard.reject();wizard.deleteLater()
        win.resize(1700,1000);app.processEvents();win.grab().save(str(evidence.output(directory/(args.language+'_help.png'))))
        win.center_tabs.setCurrentWidget(win.graph_panel);win.select(('conversations',0));app.processEvents();win.graph_panel.key=None;win.graph_panel.refresh();win.graph_panel.fit()
        app.processEvents()
        win.grab().save(str(evidence.output(directory/(args.language+'_graph.png'))))
        report=dict(language=args.language,tabs=[win.center_tabs.tabText(i) for i in range(win.center_tabs.count())],menus=[a.text() for a in win.menuBar().actions()],labels=labels,forms_inspected=inspected,untranslated_known_labels=sorted(set(untranslated)),project_unchanged=win.doc.snapshot()==before,preference_persisted=True,mode='Qt offscreen; no OpenGL or game',successful=True)
        evidence.write(directory/(args.language+'_probe.json'),json.dumps(report,ensure_ascii=False,indent=2))
        win.doc=None;win.close();app.processEvents();print(json.dumps({k:v for k,v in report.items() if k!='labels'},ensure_ascii=False))

if __name__=='__main__':main()
