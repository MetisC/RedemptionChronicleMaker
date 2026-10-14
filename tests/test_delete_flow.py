"""Create/delete real authoring records and navigate/cancel/cascade/undo in Qt."""
import copy
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QDialog,QMessageBox
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_document import CampaignDocument
from rcm.safe_edit import deletion_plan
from rcm.editor.window import MainWindow
from rcm.editor.deletion import DeleteDialog,editable_reference
from rcm.editor.dynamic_wizard import DynamicWizard
from test_release10 import blank

ROOT=Path(__file__).resolve().parents[1]


class DeleteFlow(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT));cls.backend.safe_mode=True
    def setUp(self):
        self.win=MainWindow(self.backend);self.win.doc=CampaignDocument(self.backend.ws,blank());self.win.refresh()
    def tearDown(self):self.win.doc=None;self.win.close();self.app.processEvents()
    def valid(self,source):
        validation=self.backend.validate(source);self.assertTrue(validation.valid,[p.message for p in validation.problems if p.severity=='ERROR'])
    def wizard(self):
        self.win.doc.campaign['project_format']=10
        wizard=DynamicWizard(self.win,position=[-62,-768,384]);wizard.start.setCurrentIndex(wizard.start.findData('trigger_enter'));wizard.accept();self.app.processEvents()
        self.assertEqual(wizard.result(),QDialog.DialogCode.Accepted,wizard.error.text());wizard.deleteLater()
    def test_new_spawn_point_cascade_can_be_deleted_through_viewport_selection_and_undone(self):
        self.wizard();before=self.win.doc.snapshot();self.valid(before)
        self.win.select(('waypoints',0));plan=deletion_plan(self.win.doc,('scenes',0,'waypoints',0),self.backend)
        self.assertTrue(plan.references);self.assertFalse(plan.candidate['scenes'][0]['generators']);self.assertFalse(plan.candidate['scenes'][0]['events'])
        with patch.object(DeleteDialog,'exec',return_value=QDialog.DialogCode.Accepted):self.win.delete_selected()
        after=self.win.doc.snapshot();self.assertFalse(after['scenes'][0]['waypoints']);self.valid(after)
        self.win.undo_project();self.assertEqual(self.win.doc.snapshot(),before)
        self.win.redo_project();self.assertEqual(self.win.doc.snapshot(),after)
    def test_reference_button_and_reference_search_land_on_editable_action_not_scalar(self):
        self.wizard();root=self.win.doc.snapshot();path=('scenes',0,'generators',0);plan=deletion_plan(self.win.doc,path,self.backend)
        dialog=DeleteDialog(self.win,path,plan);dialog.go()
        self.assertEqual(dialog.destination,('scenes',0,'events',0,'actions',0));self.win.navigate_reference(dialog.destination)
        self.assertEqual(self.win.selection,('events',0,'actions',0));self.assertEqual(self.win.doc.snapshot(),root)
        self.win.find_references(('generators',0));item=self.win.reference_tree.topLevelItem(0).child(0)
        self.assertEqual(item.data(0,Qt.ItemDataRole.UserRole),dialog.destination)
        with patch.object(QMessageBox,'question',return_value=QMessageBox.StandardButton.Yes):self.win.delete_selected()
        self.assertFalse(self.win.doc.data['events']);self.valid(self.win.doc.snapshot());dialog.deleteLater()
    def test_cancel_reference_deletion_preserves_document_and_history(self):
        self.wizard();before=self.win.doc.snapshot();history=copy.deepcopy(self.win.history);self.win.select(('waypoints',0))
        with patch.object(DeleteDialog,'exec',return_value=QDialog.DialogCode.Rejected):self.win.delete_selected()
        self.assertEqual(self.win.doc.snapshot(),before);self.assertEqual(self.win.history,history)
    def test_fresh_actor_and_3d_object_delete_their_own_spawn_and_keep_unrelated_actions(self):
        self.win.doc.data['events'].append(dict(id='start',when='scene_start',actions=[dict(reward_xp=1)]))
        for create,kind in ((lambda:self.win.add_actor(template='Anezka'),'actors'),(lambda:self.win.add_spatial_entity('objects','barrel1',[-62,-768,384]),'objects')):
            create();self.valid(self.win.doc.snapshot());self.assertEqual(self.win.selection[0],kind)
            with patch.object(QMessageBox,'question',return_value=QMessageBox.StandardButton.Yes),patch.object(DeleteDialog,'exec') as dialog:self.win.delete_selected()
            dialog.assert_not_called();self.assertFalse(self.win.doc.data[kind]);self.assertEqual(self.win.doc.data['events'][0]['actions'],[dict(reward_xp=1)])
            self.valid(self.win.doc.snapshot())
    def test_campaign_delete_uses_same_preview_and_cascade(self):
        self.wizard();self.win.campaign_panel.navigate(('scenes',0,'generators',0))
        with patch.object(DeleteDialog,'exec',return_value=QDialog.DialogCode.Accepted):self.win.campaign_panel.delete()
        self.assertFalse(self.win.doc.data['generators']);self.assertFalse(self.win.doc.data['events']);self.valid(self.win.doc.snapshot())
    def test_deleting_one_of_multiple_spawn_points_keeps_generator_and_other_point(self):
        self.wizard();scene=self.win.doc.campaign['scenes'][0];other=copy.deepcopy(scene['waypoints'][0]);other['id']='other';scene['waypoints'].append(other);scene['generators'][0]['spawn_points'].append('other')
        plan=deletion_plan(self.win.doc,('scenes',0,'waypoints',0),self.backend)
        self.assertEqual(plan.candidate['scenes'][0]['generators'][0]['spawn_points'],['other']);self.valid(plan.candidate)
    def test_condition_is_not_silently_removed_and_inventory_detaches_only_selected_item(self):
        root=blank();scene=root['scenes'][0];root['state']['flags']={'guard':1}
        scene['actors']=[dict(id='npc',name='NPC',template='Anezka',inventory=['key','other'],transform=dict(position=[0,0,384],orientation=[0,0,0]))]
        scene['objects']=[dict(id=k,name=k,template='IronKeyLondon',transform=dict(position=[0,0,384],orientation=[0,0,0])) for k in ('key','other')]
        scene['events']=[dict(id='guarded',when='state_changed',conditions=[dict(flag='guard',is_set=True)],actions=[dict(reward_xp=1)])]
        self.win.doc=CampaignDocument(self.backend.ws,root);self.valid(root)
        flag=deletion_plan(self.win.doc,('state','flags','guard'),self.backend);self.assertFalse(flag.candidate['scenes'][0]['events']);self.valid(flag.candidate)
        key=deletion_plan(self.win.doc,('scenes',0,'objects',0),self.backend);self.assertEqual(key.candidate['scenes'][0]['actors'][0]['inventory'],['other']);self.valid(key.candidate)
    def test_every_placeable_and_story_entity_can_be_added_and_removed_without_dangling_references(self):
        from rcm import recipes
        # Each real assistant creates a valid graph of ordinary authoring records.
        for kind in recipes.TYPES:
            root,_=recipes.apply(blank(),kind,'street',{'destination':'home'})
            self.valid(root)
            for collection in ('actors','objects','triggers','entries','waypoints','events','conversations','encounters','sequences','paths'):
                for index in range(len(root['scenes'][0].get(collection,[]))):
                    with self.subTest(recipe=kind,entity=collection,index=index):
                        doc=CampaignDocument(self.backend.ws,copy.deepcopy(root));before=doc.snapshot()
                        plan=deletion_plan(doc,('scenes',0,collection,index),self.backend)
                        self.valid(plan.candidate);self.assertEqual(doc.snapshot(),before)
            for collection,rows in (('quests',root.get('quests',[])),):
                for index in range(len(rows)):self.valid(deletion_plan(CampaignDocument(self.backend.ws,root),(collection,index),self.backend).candidate)
            for flag in root['state']['flags']:self.valid(deletion_plan(CampaignDocument(self.backend.ws,root),('state','flags',flag),self.backend).candidate)
        # The main arrival can change to the other scene; the final scene is protected.
        self.valid(deletion_plan(CampaignDocument(self.backend.ws,blank()),('scenes',0),self.backend).candidate)
        root=blank();root['scenes']=root['scenes'][:1]
        with self.assertRaisesRegex(ValueError,'necesita una escena'):deletion_plan(CampaignDocument(self.backend.ws,root),('scenes',0),self.backend)
        self.assertEqual(editable_reference(blank(),('scenes',0,'entries',0,'id')),('scenes',0,'entries',0))
