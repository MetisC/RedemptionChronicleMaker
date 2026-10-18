"""Normal UI authoring and atomic undo; Qt offscreen is not game acceptance."""
import os,copy
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
from PySide6.QtWidgets import QApplication,QDialog,QComboBox,QLineEdit,QMessageBox
from rcm.editor.window import MainWindow
from rcm.editor.environment import EnvironmentDialog
from rcm.editor.native_scripts import NativeScriptDialog
from rcm.campaign_document import CampaignDocument
from rcm.paths import Workspace
from rcm.service import Backend
from test_release10 import blank

ROOT=Path(__file__).resolve().parents[1]


class StrictEditor(TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT))
    def setUp(self):
        self.w=MainWindow(self.backend);self.w.doc=CampaignDocument(self.backend.ws,blank());self.w.refresh()
    def tearDown(self):self.w.doc=None;self.w.close();self.app.processEvents()
    def test_environment_cancel_and_atomic_apply_undo_redo(self):
        before=self.w.doc.snapshot();dialog=EnvironmentDialog(self.w);dialog.fields['ambient'].setCurrentIndex(1);dialog.reject();self.assertEqual(self.w.doc.snapshot(),before)
        dialog=EnvironmentDialog(self.w);dialog.fields['ambient'].setCurrentIndex(1);dialog.fields['fog_mode'].setCurrentIndex(dialog.fields['fog_mode'].findData('linear'));dialog.fields['start'].setValue(200);dialog.fields['end'].setValue(1600);dialog.apply()
        self.assertEqual(dialog.result(),QDialog.DialogCode.Accepted);after=self.w.doc.snapshot();self.assertEqual(after['scenes'][0]['level']['environment']['ambient'],'')
        self.w.undo_project();self.assertEqual(self.w.doc.snapshot(),before);self.w.redo_project();self.assertEqual(self.w.doc.snapshot(),after)
    def test_environment_bad_linear_range_leaves_project_unchanged(self):
        before=self.w.doc.snapshot();dialog=EnvironmentDialog(self.w);dialog.fields['fog_mode'].setCurrentIndex(2);dialog.fields['start'].setValue(500);dialog.fields['end'].setValue(100)
        with patch.object(QMessageBox,'warning') as warning:dialog.apply();warning.assert_called_once()
        self.assertEqual(self.w.doc.snapshot(),before)
    def test_native_typed_reference_widgets_replace_initial_spawns_in_one_undo(self):
        s=self.w.doc.campaign['scenes'][0];s['objects']=[dict(id='trigger',name='Efecto',template='tracker_thing',transform=dict(position=[-176,-612,384],orientation=[0,0,0]))]+[dict(id='part'+str(i),name='Escombro',template='wallGib',transform=dict(position=[-176+i*24,-612,384],orientation=[0,0,0])) for i in range(5)]
        s['events']=[dict(id='start',when='scene_start',actions=[dict(spawn=r['id']) for r in s['objects']])];self.w.changed(True);before=self.w.doc.snapshot()
        dialog=NativeScriptDialog(self.w,s['objects'][0]);dialog.choose.setCurrentIndex(dialog.choose.findData('ClassBreakable'))
        self.assertEqual(len(dialog.controls),11)
        for i,(kind,control) in enumerate(dialog.controls):
            if kind=='thing':control.setCurrentIndex(control.findData('part'+str(i)))
            else:control.setValue(20)
        dialog.apply();self.assertEqual(dialog.result(),QDialog.DialogCode.Accepted);self.assertTrue(self.backend.validate(self.w.doc.snapshot()).valid)
        self.assertEqual(self.w.doc.campaign['scenes'][0]['events'],[]);self.assertEqual(self.w.doc.data['objects'][0]['native_script']['parameters'][0],dict(type='thing',value='part0'))
        after=self.w.doc.snapshot();self.w.undo_project();self.assertEqual(self.w.doc.snapshot(),before);self.w.redo_project();self.assertEqual(self.w.doc.snapshot(),after)
    def test_instance_controls_are_local_cancel_safe_and_undoable(self):
        from rcm.editor.instance_overrides import edit_overrides
        self.w.doc.data['actors'].append(dict(id='elena',name='Elena',template='Anezka',transform=dict(position=[-176,-612,384],orientation=[0,0,0])));self.w.changed(True);before=self.w.doc.snapshot()
        def accept(dialog):
            box=dialog.findChild(QComboBox,'instance_foley');box.setCurrentIndex(box.findData('npcGeneralFemale'));dialog.findChild(QLineEdit,'instance_hover_text').setText('La mentora');return QDialog.DialogCode.Accepted
        with patch('rcm.editor.instance_overrides.QDialog.exec',accept):edit_overrides(self.w,self.w.doc.data['actors'][0],True)
        self.assertEqual(self.w.doc.data['actors'][0]['overrides'],dict(foley='npcGeneralFemale',hover_text='La mentora'));self.w.undo_project();self.assertEqual(self.w.doc.snapshot(),before)
        with patch('rcm.editor.instance_overrides.QDialog.exec',return_value=QDialog.DialogCode.Rejected):edit_overrides(self.w,self.w.doc.data['actors'][0],True)
        self.assertEqual(self.w.doc.snapshot(),before)
    def test_interest_is_an_explicit_optional_marker_role(self):
        self.w.doc.data['waypoints'].append(dict(id='point',name='Point',transform=dict(position=[-176,-612,384],orientation=[0,0,0])));self.w.changed(True);before=copy.deepcopy(self.w.doc.data['waypoints'][0]);self.w.select(('waypoints',0))
        box=self.w.properties.widget().findChild(QComboBox,'marker_interest_group');self.assertIsNone(box.currentData());box.setCurrentIndex(box.findData(8));self.assertEqual(self.w.doc.data['waypoints'][0]['interest_group'],8)
        self.w.undo_project();self.assertEqual(self.w.doc.data['waypoints'][0],before)
    def test_native_frames_can_be_authored_through_widgets(self):
        s=self.w.doc.campaign['scenes'][0];s['objects']=[dict(id='mover',name='Mover',template='tracker_thing',transform=dict(position=[-176,-612,384],orientation=[0,0,0])),dict(id='barrel',name='Cargo',template='barrel1',transform=dict(position=[-176,-612,384],orientation=[0,0,0]))]
        s['waypoints']=[dict(id='top',name='Upper position',transform=dict(position=[-176,-612,408],orientation=[0,0,90]))];self.w.changed(True);before=self.w.doc.snapshot()
        dialog=NativeScriptDialog(self.w,s['objects'][0]);dialog.choose.setCurrentIndex(dialog.choose.findData('ClassBobbing'));dialog.frames.append('top')
        dialog.controls[0][1].setCurrentIndex(dialog.controls[0][1].findData('barrel'));dialog.apply()
        self.assertEqual(dialog.result(),QDialog.DialogCode.Accepted);self.assertTrue(self.backend.validate(self.w.doc.snapshot()).valid)
        self.assertEqual(self.w.doc.data['objects'][0]['native_frames'],['top']);self.w.undo_project();self.assertEqual(self.w.doc.snapshot(),before)
    def test_invalid_instance_text_does_not_commit(self):
        from rcm.editor.instance_overrides import edit_overrides
        self.w.doc.data['actors'].append(dict(id='elena',name='Elena',template='Anezka',transform=dict(position=[-176,-612,384],orientation=[0,0,0])));self.w.changed(True);before=self.w.doc.snapshot()
        def accept(dialog):dialog.findChild(QLineEdit,'instance_hover_text').setText('Bad\ntext');return QDialog.DialogCode.Accepted
        with patch('rcm.editor.instance_overrides.QDialog.exec',accept),patch.object(QMessageBox,'warning') as warning:edit_overrides(self.w,self.w.doc.data['actors'][0],True);warning.assert_called_once()
        self.assertEqual(self.w.doc.snapshot(),before)
