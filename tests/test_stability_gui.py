"""Authoring usability contracts, using Qt offscreen rather than native input."""
import json
import os
import tempfile
from pathlib import Path
from unittest import TestCase
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtWidgets import QApplication,QComboBox,QListWidget,QPushButton,QLineEdit,QPlainTextEdit
from PySide6.QtGui import QFont
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.document import Document
from rcm.editor.window import MainWindow

ROOT=Path(__file__).resolve().parents[1]


class StabilityGuiTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        cls.backend=Backend(Workspace(ROOT))
    def setUp(self):
        self.win=MainWindow(self.backend);self.win.autosave_timer.stop()
        self.win.doc=Document.load(self.backend.ws,'chronicles/tutorial/project.yaml');self.win.refresh()
        self.ci=next(i for i,c in enumerate(self.win.doc.data['conversations']) if c['id']=='lab')
    def tearDown(self):
        self.win.doc=None;self.win.close();self.app.processEvents()
    def node_index(self,name):return next(i for i,n in enumerate(self.win.doc.data['conversations'][self.ci]['nodes']) if n['id']==name)
    def select_motion(self,path):
        self.win.select(path);return self.win.properties.widget().findChild(QComboBox,'dialogue_motion')

    def test_object_note_shortcut_edit_undo_and_reload(self):
        import copy
        row=copy.deepcopy(self.win.doc.data['objects'][0]);row['id']='new_note';row['name']='Carta'
        self.win.doc.data['objects'].append(row);self.win.changed(True)
        path=('objects',len(self.win.doc.data['objects'])-1);self.win.select(path)
        self.win.properties.widget().findChild(QPushButton,'object_note').click()
        event=self.win.doc.data['events'][-1];self.assertEqual(event['when'],'object_clicked');self.assertEqual(event['object'],'new_note')
        self.assertEqual(self.win.selection,('events',len(self.win.doc.data['events'])-1,'actions',0))
        form=self.win.properties.widget();self.assertIsNotNone(form.findChild(QLineEdit,'note_title'))
        self.assertGreaterEqual(form.findChild(QPlainTextEdit,'note_text').minimumHeight(),180)
        self.win.history_time=0;form.findChild(QPlainTextEdit,'note_text').setPlainText('Uno.\n\nDos.')
        self.assertEqual(event['actions'][0]['show_note']['text'],'Uno.\n\nDos.')
        self.win.undo_project();self.assertNotEqual(self.win.doc.data['events'][-1]['actions'][0]['show_note']['text'],'Uno.\n\nDos.')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as temp:
            self.win.doc.save(Path(temp)/'project.yaml');loaded=Document.load(self.backend.ws,self.win.doc.path)
            self.assertEqual(loaded.data['events'][-1]['object'],'new_note')

    def test_object_dialogue_shortcut_and_existing_event_navigation(self):
        import copy
        row=copy.deepcopy(self.win.doc.data['objects'][0]);row['id']='new_dialogue';row['name']='Interacción'
        self.win.doc.data['objects'].append(row);self.win.changed(True)
        path=('objects',len(self.win.doc.data['objects'])-1);self.win.select(path)
        self.win.properties.widget().findChild(QPushButton,'object_dialogue').click()
        event=self.win.doc.data['events'][-1];self.assertIn('start_conversation',event['actions'][0])
        count=len(self.win.doc.data['events']);self.win.select(path)
        self.win.properties.widget().findChild(QPushButton,'object_note').click()
        self.assertEqual(len(self.win.doc.data['events']),count)
        self.assertEqual(self.win.selection,('events',count-1))

    def test_note_close_callback_and_object_origin_are_exposed(self):
        index=next(i for i,e in enumerate(self.win.doc.data['events']) if e['when']=='object_clicked')
        self.win.select(('events',index));form=self.win.properties.widget()
        self.assertIsNotNone(form.findChild(QComboBox,'event_object'))
        combo=form.findChild(QComboBox,'event_when');self.assertNotEqual(combo.findData('note_closed'),-1)
        combo.setCurrentIndex(combo.findData('note_closed'))
        self.assertNotIn('object',self.win.doc.data['events'][index])

    def test_node_motion_edit_undo_and_save_reload(self):
        ni=self.node_index('stand');path=('conversations',self.ci,'nodes',ni)
        combo=self.select_motion(path);self.assertEqual(combo.currentData(),'stand')
        combo.setCurrentIndex(combo.findData('gesture10'))
        self.assertEqual(self.win.at(path)['motion'],'gesture10')
        self.win.undo_project();self.assertEqual(self.win.at(path)['motion'],'stand')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as temp:
            self.win.doc.path=Path(temp)/'project.yaml';self.win.save_project()
            loaded=Document.load(self.backend.ws,self.win.doc.path)
            self.assertEqual(loaded.data['conversations'][self.ci]['nodes'][ni]['motion'],'stand')

    def test_line_can_inherit_or_override_node_and_defaults_do_not_force_motion(self):
        ni=self.node_index('stand');path=('conversations',self.ci,'nodes',ni,'lines',0)
        combo=self.select_motion(path);self.assertIsNone(combo.currentData())
        combo.setCurrentIndex(combo.findData('talk'));self.assertEqual(self.win.at(path)['motion'],'talk')
        self.win.history_time=0;combo.setCurrentIndex(combo.findData(None));self.assertNotIn('motion',self.win.at(path))
        self.assertEqual(self.win.doc.data['conversations'][self.ci]['nodes'][ni]['motion'],'stand')

    def test_multi_speaker_node_only_offers_common_available_modes(self):
        ni=self.node_index('motions');node=self.win.doc.data['conversations'][self.ci]['nodes'][ni]
        node['lines'].append(dict(speaker='mentor',text='Escucho.'))
        combo=self.select_motion(('conversations',self.ci,'nodes',ni))
        self.assertEqual(combo.findData('gesture10'),-1)
        self.assertIn('Automática',combo.itemText(0))
        self.assertTrue(all(combo.itemData(i) is not None for i in range(1,combo.count())))

    def test_aerial_preset_and_per_shot_angle_are_accessible(self):
        self.win.campaign_panel.navigate(('scenes',0,'sequences',0))
        panel=self.win.campaign_panel
        self.assertEqual(panel.findChild(QComboBox,'sequence_step_angle_0').currentData(),'high')
        first=self.win.doc.campaign['scenes'][0]['sequences'][0]['steps'][0]
        self.assertEqual(first['preset'],'aerial');self.assertEqual(first['transition'],0)
        angle=panel.findChild(QComboBox,'sequence_step_angle_1');angle.setCurrentIndex(angle.findData('high'))
        self.assertEqual(self.win.doc.campaign['scenes'][0]['sequences'][0]['steps'][1]['angle'],'high')

    def test_minimum_window_route_form_remains_scrollable_and_tabs_stay_fixed(self):
        self.win.resize(1100,720);self.win.show();self.app.processEvents()
        self.win.campaign_panel.navigate(('scenes',0,'paths',0));self.app.processEvents()
        panel=self.win.campaign_panel;points=panel.findChild(QListWidget,'path_points')
        self.assertGreaterEqual(panel.scroll.height(),190)
        self.assertGreaterEqual(points.viewport().height()/max(1,points.sizeHintForRow(0)),3)
        top=self.win.center_tabs.tabBar().mapTo(self.win,self.win.center_tabs.tabBar().rect().topLeft())
        records=[]
        for index in range(self.win.center_tabs.count()):
            self.win.center_tabs.setCurrentIndex(index);self.app.processEvents()
            current=self.win.center_tabs.tabBar().mapTo(self.win,self.win.center_tabs.tabBar().rect().topLeft())
            self.assertEqual(current,top)
            records.append(dict(tab=self.win.center_tabs.tabText(index),y=current.y()))
        dest=ROOT/'research/round0/stability_usability';dest.mkdir(parents=True,exist_ok=True)
        (dest/'layout_contract.json').write_text(json.dumps(dict(window=[self.win.width(),self.win.height()],tabs=records,route_form_height=panel.scroll.height(),offscreen=True,native_engine_test=False),indent=2),encoding='utf8')

    def test_large_text_route_content_keeps_vertical_scrolling(self):
        self.win.setFont(QFont('Segoe UI',15));self.win.resize(1430,900);self.win.show()
        self.win.campaign_panel.navigate(('scenes',0,'paths',0));self.app.processEvents()
        panel=self.win.campaign_panel
        self.assertGreaterEqual(panel.scroll.height(),190)
        self.assertTrue(panel.scroll.widgetResizable())
        self.assertIsNotNone(panel.findChild(QListWidget,'path_points'))
