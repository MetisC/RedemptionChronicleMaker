"""Regression tests for language boundaries, invalid edits and readable graphs."""
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from rcm.paths import Workspace
from rcm.editor import i18n
from rcm.debugging import trace_file,trace_tail

ROOT=Path(__file__).resolve().parents[1]
(ROOT/'build/tests').mkdir(parents=True,exist_ok=True)

class Languages(TestCase):
    def tearDown(self):
        i18n._language='es'

    def test_default_and_malformed_preferences_are_english(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            ws=Workspace(Path(folder));self.assertEqual(i18n.configure(ws),'en')
            for data in ['{','[]','null','{"language":[]}','{"language":{}}','{"language":"unknown"}']:
                ws.write('cache/editor_settings.json',data);self.assertEqual(i18n.configure(ws),'en')

    def test_persistence_is_separate_from_project_and_game_settings(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            ws=Workspace(Path(folder));game=ws.write('cache/game_settings.json','{"installation":"example"}')
            project=ws.write('chronicles/project.yaml','name: Nombre del autor\n')
            ws.write('cache/editor_settings.json','{"future_preference":42}')
            i18n.save_language(ws,'es');self.assertEqual(i18n.configure(ws),'es')
            i18n.save_language(ws,'en');self.assertEqual(i18n.configure(Workspace(Path(folder))),'en')
            self.assertEqual(json.loads(ws.output('cache/editor_settings.json').read_text())['future_preference'],42)
            self.assertEqual(game.read_text(),'{"installation":"example"}')
            self.assertEqual(project.read_text(),'name: Nombre del autor\n')

    def test_corrupt_settings_backed_up_and_unsupported_language_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            ws=Workspace(Path(folder));ws.write('cache/editor_settings.json','{invalid')
            i18n.save_language(ws,'es');backups=list(ws.output('research/editor').glob('preferences_*.json'))
            self.assertEqual(len(backups),1);self.assertEqual(backups[0].read_text(),'{invalid')
            before=ws.output('cache/editor_settings.json').read_bytes()
            with self.assertRaises(ValueError):i18n.save_language(ws,'fr')
            self.assertEqual(ws.output('cache/editor_settings.json').read_bytes(),before)

    def test_failed_atomic_replace_preserves_preference(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            ws=Workspace(Path(folder));i18n.save_language(ws,'es')
            with patch.object(Path,'replace',side_effect=OSError('locked')):
                with self.assertRaises(OSError):i18n.save_language(ws,'en')
            self.assertEqual(i18n.configure(ws),'es')

    def test_diagnostics_preserve_ids_paths_and_unknown_details(self):
        i18n._language='en'
        self.assertEqual(i18n.tr('Guardar'),'Save')
        self.assertEqual(i18n.diagnostic('Plantilla desconocida o ambigua: T_custom'), 'Unknown or ambiguous template: T_custom')
        self.assertEqual(i18n.diagnostic('workshop: Plantilla desconocida o ambigua: T_custom'), 'workshop: Unknown or ambiguous template: T_custom')
        unknown='custom source.java:23: unexpected author message';self.assertEqual(i18n.diagnostic(unknown),unknown)
        for source,target in i18n.catalogue().items():
            self.assertEqual(sorted(re.findall(r'\{\d+\}',source)),sorted(re.findall(r'\{\d+\}',target)),source)

    def test_ui_in_both_languages_in_fresh_processes(self):
        for code in ['en','es']:
            result=subprocess.run([sys.executable,str(ROOT/'tools/editor_review_probe.py'),'--language',code],cwd=ROOT,capture_output=True,text=True,timeout=75)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

class NativeTrace(TestCase):
    def test_shared_deployment_prefers_actual_shortcut_and_skips_other_owners(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            root=Path(folder);ws=Workspace(root/'workspace');game=root/'game'
            for name,owners in [('east_demo',{'rcm_tutor':{}}),('rcm_tutor',{'rcm_tutor':{}}),('foreign',{'other':{}})]:
                directory=game/'RCM'/name;directory.mkdir(parents=True)
                (directory/'.rcm_deployment.json').write_text(json.dumps({'owners':owners}))
                (directory/'runtime_trace.log').write_text(name)
            with patch('rcm.deployment.configured_game',return_value=game),patch('rcm.shortcut.launch_info',return_value={'directory':game/'RCM/east_demo'}):
                self.assertEqual(trace_file(ws,'rcm_tutor'),game/'RCM/east_demo/runtime_trace.log')
                self.assertIsNone(trace_file(ws,'absent'))
            (game/'RCM/east_demo/.rcm_deployment.json').write_text('invalid')
            with patch('rcm.deployment.configured_game',return_value=game),patch('rcm.shortcut.launch_info',return_value=None):
                self.assertEqual(trace_file(ws,'rcm_tutor'),game/'RCM/rcm_tutor/runtime_trace.log')

    def test_trace_tail_is_bounded_drops_partial_lines_and_decodes_native_text(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            path=Path(folder)/'runtime_trace.log';path.write_bytes(('discard\n'*10000+'Último dato\n').encode('cp1252'))
            tail=trace_tail(path,80);self.assertLessEqual(len(tail),80);self.assertTrue(tail.endswith('Último dato\n'))
            self.assertTrue(tail.startswith('discard\n'))
            path.write_bytes('Último dato\n'.encode('cp1252'));self.assertEqual(trace_tail(path),'Último dato\n')

class EditorFlows(TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        from rcm.service import Backend
        cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT));cls.backend.safe_mode=True

    def setUp(self):
        from rcm.editor.window import MainWindow
        from rcm.document import Document
        i18n._language='es';self.win=MainWindow(self.backend)
        self.win.doc=Document.load(self.backend.ws,'tests/fixtures/chronicles/tutorial_0913/project.yaml');self.win.refresh();self.win.show();self.app.processEvents()

    def tearDown(self):
        self.win.doc=None;self.win.close();self.app.processEvents()

    def test_invalid_edit_restores_project_resource_selection(self):
        panel=self.win.project_resources_panel;panel.index=0;panel.refresh()
        with patch.object(self.win,'commit_properties',return_value=False):panel.list.setCurrentRow(1)
        self.assertEqual(panel.index,0);self.assertEqual(panel.list.currentRow(),0)

    def test_invalid_edit_restores_graph_kind_and_resource(self):
        panel=self.win.graph_panel;self.win.center_tabs.setCurrentWidget(panel);self.win.select(('conversations',0));panel.key=None;panel.refresh()
        with patch.object(self.win,'commit_properties',return_value=False):
            panel.resource.setCurrentIndex(1);self.assertEqual(panel.resource.currentData(),0)
            panel.kind.setCurrentIndex(1);self.assertEqual(panel.kind.currentData(),'conversations')
        self.assertEqual(self.win.selection,('conversations',0))

    def test_graph_card_selection_keeps_graph_visible(self):
        panel=self.win.graph_panel;self.win.center_tabs.setCurrentWidget(panel)
        panel.choose(('conversations',0,'choices',0))
        self.assertIs(self.win.center_tabs.currentWidget(),panel)
        self.assertEqual(self.win.selection,('conversations',0,'choices',0))

    def test_fit_does_not_enlarge_a_single_node_and_tooltip_has_full_text(self):
        from rcm.editor.graph_panel import Card
        panel=self.win.graph_panel;self.win.center_tabs.setCurrentWidget(panel);self.win.select(('conversations',0));panel.refresh();panel.fit()
        self.assertLessEqual(panel.view.transform().m11(),1)
        card=next(item for item in panel.scene.items() if isinstance(item,Card) and item.path[-1]=='prompt')
        self.assertIn(self.win.doc.data['conversations'][0]['prompt'],card.toolTip())

    def test_graph_cards_do_not_overlap_with_many_answers_and_large_font(self):
        from PySide6.QtGui import QFont
        from rcm.editor.graph_panel import Card
        conv=copy.deepcopy(self.win.doc.data['conversations'][0]);original={'id':'opening','lines':[],'choices':[]}
        conv['nodes']=[]
        for i in range(7):
            node=copy.deepcopy(original);node['id']='node'+str(i)
            node['lines']=[{'speaker':'mentor','text':'A long line that needs several rows in the graph. '*3}]
            node['choices']=[{'text':'A very long response that should be elided but fully available in its tooltip. '*3,'result':j} for j in range(8)]
            conv['nodes'].append(node)
        conv['entry']='node0';conv.pop('prompt',None);conv.pop('choices',None);self.win.doc.campaign['scenes'][0]['conversations']=[conv]
        panel=self.win.graph_panel;panel.view.setFont(QFont('Segoe UI',15));self.win.center_tabs.setCurrentWidget(panel);self.win.select(('conversations',0));panel.key=None;panel.refresh()
        cards=[item for item in panel.scene.items() if isinstance(item,Card)];self.assertEqual(len(cards),63)
        for i,card in enumerate(cards):
            for other in cards[i+1:]:self.assertFalse(card.rect().intersects(other.rect()),(card.path,other.path))
        for card in cards:
            if card.path[-2]=='choices':self.assertIn('very long response',card.toolTip())

    def test_event_note_graph_summarises_title_and_preserves_body_in_tooltip(self):
        from rcm.editor.graph_panel import Card
        panel=self.win.graph_panel;self.win.doc.campaign['scenes'][0]['events']=[{'id':'intro','when':'scene_start','actions':[{'show_note':{'id':'note','title':'Authored title','text':'Authored body '*100}}]}]
        self.win.center_tabs.setCurrentWidget(panel);panel.kind.setCurrentIndex(1);self.win.select(('events',0));panel.key=None;panel.refresh()
        cards=[item for item in panel.scene.items() if isinstance(item,Card)];self.assertEqual(len(cards),2)
        note=next(item for item in cards if item.path[-2:] == ('actions',0));self.assertIn('Authored body',note.toolTip())
        self.assertLess(note.rect().height(),200)

    def test_checklist_ids_fill_gaps_without_collision(self):
        from PySide6.QtWidgets import QInputDialog
        self.win.doc.campaign['playtests']=[{'id':'test1','name':'One','instructions':'one'},{'id':'test3','name':'Three','instructions':'three'}]
        with patch.object(QInputDialog,'getText',return_value=('Two',True)),patch.object(QInputDialog,'getMultiLineText',return_value=('two',True)):
            self.win.debug_panel.bookmark()
        self.assertEqual([row['id'] for row in self.win.doc.campaign['playtests']],['test1','test3','test2'])

    def test_help_uses_current_guide_in_editor_without_mutating_project(self):
        before=self.win.doc.snapshot();self.win.open_editor_guide()
        text=self.win.guide_panel.text.toPlainText();self.assertIn('Showcase',text);self.assertNotIn('phase3_demo',text)
        self.assertEqual(self.win.doc.snapshot(),before)
        self.win.open_project_guide()
        self.assertIn('siete lecciones',self.win.guide_panel.text.toPlainText())
        self.assertEqual(self.win.doc.snapshot(),before)

    def test_failed_language_change_keeps_previous_saved_choice(self):
        from PySide6.QtWidgets import QMessageBox
        self.win.preferred_language='en';self.win.language_actions['en'].setChecked(True)
        with patch('rcm.editor.i18n.save_language',side_effect=OSError('locked')),patch.object(QMessageBox,'warning'):
            self.win.language_actions['es'].trigger()
        self.assertTrue(self.win.language_actions['en'].isChecked())
        self.assertEqual(self.win.preferred_language,'en')

    def test_smoke_invalid_project_reports_failure_instead_of_waiting_forever(self):
        from unittest.mock import Mock
        from PySide6.QtTest import QTest
        from rcm.editor.smoke import start
        from rcm.service import Problem,Validation
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            original=self.backend.ws;self.backend.ws=Workspace(Path(folder))
            try:
                application=Mock()
                with patch.object(self.backend,'validate',return_value=Validation(None,[Problem('ERROR','missing level')])):
                    timer=start(self.win,application);QTest.qWait(250)
                report=json.loads(self.backend.ws.output('build/portable_smoke.json').read_text())
                self.assertEqual(report['status'],'validation-failed');self.assertEqual(report['errors'],['missing level'])
                self.assertFalse(timer.isActive());application.exit.assert_called_once_with(1)
            finally:self.backend.ws=original

    def test_worker_progress_updates_only_on_the_gui_thread(self):
        from PySide6.QtCore import QThread
        from PySide6.QtTest import QTest
        from shiboken6 import isValid
        gui_thread=QThread.currentThread()
        observed=[]
        def build(source,progress):
            progress('Generando conversaciones…')
            return {'chronicle':'rcm_tutor','status':'compiled-unverified-in-game'}
        try:
            with patch.object(self.win,'save_project',return_value=True),patch.object(self.backend,'build',side_effect=build),patch.object(self.win.log,'appendPlainText',side_effect=lambda text:observed.append((text,QThread.currentThread()==gui_thread))):
                self.win.build_project()
                for unused in range(100):
                    QTest.qWait(25)
                    if not self.win.busy:break
            self.assertFalse(self.win.busy)
            self.assertIn(('Generando conversaciones…',True),observed)
            self.assertTrue(all(on_gui for text,on_gui in observed))
        finally:
            thread=getattr(self.win,'thread',None)
            if thread is not None and isValid(thread):thread.quit();thread.wait()
