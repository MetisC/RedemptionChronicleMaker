"""User round 0 regressions: actual Qt forms and conservative engine generation."""
import os,copy,json,tempfile
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
import numpy as np
from PySide6.QtCore import Qt,QPointF,QEvent,QUrl
from PySide6.QtGui import QMouseEvent,QKeyEvent
from PySide6.QtWidgets import QApplication,QDialog,QInputDialog
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.document import Document
from rcm.campaign_generator import runtime
from rcm.editor.window import MainWindow
from rcm.editor.viewport import Viewport
from rcm.editor.browser import ResourceBrowser
from rcm.editor.campaign_panel import InventoryDialog
from rcm.campaign_relations import graph
from rcm.safe_edit import delete_candidate
from rcm.deployment_many import deploy_many

ROOT=Path(__file__).resolve().parents[1]

class Round0(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT))
    def setUp(self):
        self.win=MainWindow(self.backend);self.win.doc=Document.load(self.backend.ws,'tests/fixtures/chronicles/tutorial_0913/project.yaml');self.win.refresh();self.win.show();self.app.processEvents()
    def tearDown(self):self.win.doc=None;self.win.close();self.app.processEvents()
    def test_inventory_catalogue_cancel_apply_copies_and_undo(self):
        actor=self.win.doc.data['actors'][0];before=self.win.doc.snapshot();dlg=InventoryDialog(self.win,actor)
        with patch('rcm.editor.campaign_panel.ResourceDialog') as chooser:
            chooser.return_value.exec.return_value=QDialog.DialogCode.Accepted;chooser.return_value.selection='BoneKey'
            dlg.add_catalogue();dlg.add_catalogue()
        self.assertEqual(self.win.doc.snapshot(),before);self.assertEqual(len(dlg.selected_ids),2)
        dlg.apply();self.assertTrue(self.backend.validate(self.win.doc.snapshot()).valid)
        self.assertEqual(len(set(actor['inventory'])),2)
        self.win.undo_project();self.assertEqual(self.win.doc.snapshot(),before)
        dlg.deleteLater()
    def test_inventory_only_offers_unowned_items_not_props_or_spawned(self):
        dlg=InventoryDialog(self.win,self.win.doc.data['actors'][0]);ids={dlg.existing.itemData(i) for i in range(dlg.existing.count())}
        self.assertNotIn('npc_key',ids);self.assertNotIn('npc_book',ids);self.assertNotIn('barrel',ids);self.assertNotIn('reward',ids)
        self.assertIn('key',ids);dlg.deleteLater()
    def test_catalogue_family_origin_search_and_full_tooltips(self):
        view=ResourceBrowser(self.backend,'items');view.family.setCurrentIndex(view.family.findData('weapons'))
        self.assertGreater(view.table.rowCount(),0)
        for i in range(view.table.rowCount()):
            self.assertEqual(view.table.item(i,1).text(),'weapons');self.assertEqual(view.table.item(i,2).toolTip(),view.table.item(i,2).text())
        view.origin.setCurrentIndex(view.origin.findData('Proyecto /'));self.assertEqual(view.table.rowCount(),0)
        view.origin.setCurrentIndex(0);view.search.setText('no_such_weapon');self.assertEqual(view.table.rowCount(),0);view.deleteLater()
    def test_nav_tooltips_and_project_guide_links_select_authored_entities(self):
        for item in self.win.nav_items.values():self.assertEqual(item.toolTip(0),item.text(0))
        self.assertIn('un escenario',self.win.guide_panel.text.toPlainText())
        self.win.guide_panel.navigate(QUrl('rcm://workshop/paths/walker_walk'))
        self.assertEqual(self.win.campaign_panel.path,('scenes',0,'paths',0))
        self.app.processEvents();self.assertGreaterEqual(self.win.campaign_panel.scroll.height(),190)
        self.assertGreaterEqual(self.win.campaign_panel.panes.count(),2)
    def test_scene_can_create_same_geometry_layout_or_copy_without_level_picker(self):
        for mode in ['Nuevo layout vacío sobre este level','Duplicar layout actual']:
            source=self.win.doc.snapshot();self.win.doc.data['level']['environment_scene']='EAST_28_1.nsd';level=copy.deepcopy(self.win.doc.data['level'])
            with patch.object(QInputDialog,'getItem',return_value=(mode,True)),patch('rcm.editor.campaign_panel.ResourceDialog') as picker:self.win.campaign_panel.add_scene();picker.assert_not_called()
            row=self.win.doc.campaign['scenes'][-1];self.assertEqual(row['level'],level)
            self.assertEqual(len(row['actors']),0 if mode.startswith('Nuevo') else len(source['scenes'][0]['actors']))
            self.assertTrue(self.backend.validate(self.win.doc.snapshot()).valid)
            self.win.doc.data=source;self.win.doc.active=0;self.win.refresh()
    def test_window_has_nonempty_own_icon(self):self.assertFalse(self.win.windowIcon().isNull())
    def test_player_start_button_selects_chronicle_entry_from_another_layout(self):
        before=self.win.doc.snapshot();self.win.doc.active=2;self.win.refresh()
        self.win.focus_player_start()
        self.assertEqual(self.win.doc.active,0);self.assertEqual(self.win.selection,('entries',0));self.assertEqual(self.win.center_tabs.currentIndex(),0)
        self.assertEqual(self.win.doc.snapshot(),before)
        self.assertEqual(self.win.doc.data['entries'][0]['transform']['position'],[-176.0,-768.0,384.0])
        java=runtime(self.backend.validate(before).project,*self.backend.validate(before).project.scenes[0])[1]
        self.assertIn('ARRIVAL_BEFORE',java);self.assertIn('ARRIVAL_AFTER',java);self.assertIn('SPAWN_FAILED template=',java)
    def test_native_dialogue_preset_timeline_path_and_release_generated_from_real_api(self):
        campaign=self.backend.validate(self.win.doc.snapshot()).project;scene,project=campaign.scenes[0];java=runtime(campaign,scene,project)[1]
        self.assertIn('case 0: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_OTS_C',java.split('private void dialogueCamera',1)[1])
        self.assertIn('CodexCamera.SetShot(who,CAM_SHOT_OTS_C',java)
        self.assertIn('CodexCamera.PlayPath(player,GetGUID(),"EASTOttoVan.ncp",1.0f)',java)
        self.assertIn('CUTSCENE_SHOT walk_scene/2',java);self.assertIn('stopCinema(); if(cameraPlayer!=0)',java)
        self.assertIn('BeginCutscene(player,0); AIOff();',java)
        self.assertIn('EndCutscene(client,0); AIOn();',java)
        self.assertIn('double tolerance=24.0',java)
        self.assertIn('pollCinema(); pollPatrols()',java)
        legacy=copy.deepcopy(self.win.doc.snapshot());legacy['scenes'][0]['conversations'][0].pop('camera');c=self.backend.validate(legacy).project;s,p=c.scenes[0]
        self.assertIn('CodexCamera.SetShot(who,CAM_SHOT_OTS_C,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP',runtime(c,s,p)[1])
    def test_new_conversation_and_missing_camera_use_shoulder_in_editor(self):
        from PySide6.QtWidgets import QComboBox
        self.win.add_conversation()
        self.assertEqual(self.win.doc.data['conversations'][-1]['camera'],'ots_speaker_close')
        self.win.doc.data['conversations'][-1].pop('camera')
        self.win.select(('conversations',len(self.win.doc.data['conversations'])-1))
        self.app.processEvents()
        combo=self.win.properties.widget().findChild(QComboBox,'conversation_camera')
        self.assertEqual(combo.currentData(),'ots_speaker_close')
        self.assertEqual(combo.itemData(0),'ots_speaker_close')
    def test_bad_camera_timeline_native_path_or_movement_is_rejected(self):
        edits=[lambda r:r['scenes'][0]['conversations'][0].update(camera='invented'),lambda r:r['scenes'][0]['sequences'][0]['steps'][1].update(at=0),lambda r:r['scenes'][0]['sequences'][0]['steps'][1].update(actor='absent'),lambda r:r['scenes'][0]['sequences'][0].update(move_path='absent'),lambda r:r['scenes'][0]['sequences'][1].update(camera_path='absent'),lambda r:r['scenes'][0]['sequences'][1].update(path_speed=float('nan'))]
        for edit in edits:
            root=self.win.doc.snapshot();edit(root);self.assertFalse(self.backend.validate(root).valid)
    def test_cutscene_movement_and_nested_shot_actor_references_protect_deletion(self):
        root=self.win.doc.snapshot();links=graph(root)
        self.assertTrue(any(l.label=='move_path' for l in links))
        self.assertTrue(any(l.detail[-3:-1]==('steps',1) for l in links if l.label=='actor'))
        with self.assertRaises(ValueError):delete_candidate(self.win.doc,('scenes',0,'paths',0),self.backend)
    def move(self,v,buttons,dx=20,dy=10,alt=False):
        v.last_mouse=QPointF(200,200);ev=QMouseEvent(QEvent.Type.MouseMove,QPointF(200+dx,200+dy),QPointF(200+dx,200+dy),Qt.MouseButton.NoButton,buttons,Qt.KeyboardModifier.AltModifier if alt else Qt.KeyboardModifier.NoModifier);v.mouseMoveEvent(ev)
    def test_ue4_two_buttons_pan_middle_pan_dolly_and_left_navigation(self):
        v=Viewport();v.resize(800,600);v.yaw=0;v.pitch=0
        both=Qt.MouseButton.LeftButton|Qt.MouseButton.RightButton;pos=v.pos.copy();self.move(v,both);self.assertEqual(v.yaw,0);self.assertLess(v.pos[2],pos[2]);np.testing.assert_equal(v.pos[:2],pos[:2])
        pos=v.pos.copy();self.move(v,Qt.MouseButton.MiddleButton);self.assertNotEqual(v.pos[1],pos[1]);self.assertNotEqual(v.pos[2],pos[2])
        pos=v.pos.copy();self.move(v,Qt.MouseButton.RightButton,alt=True);self.assertNotEqual(v.pos[0],pos[0]);self.assertEqual(v.yaw,0)
        self.move(v,Qt.MouseButton.LeftButton);self.assertGreater(v.yaw,300);v.deleteLater()
    def test_rmb_click_menu_and_drag_do_not_open_menu(self):
        v=Viewport();events=[];v.menu_requested.connect(events.append)
        for drag in [False,True]:
            v.mousePressEvent(QMouseEvent(QEvent.Type.MouseButtonPress,QPointF(200,200),QPointF(200,200),Qt.MouseButton.RightButton,Qt.MouseButton.RightButton,Qt.KeyboardModifier.NoModifier));v.right_dragged=drag
            v.mouseReleaseEvent(QMouseEvent(QEvent.Type.MouseButtonRelease,QPointF(200,200),QPointF(200,200),Qt.MouseButton.RightButton,Qt.MouseButton.NoButton,Qt.KeyboardModifier.NoModifier))
        self.assertEqual(len(events),1);self.assertFalse(v.looking);v.deleteLater()
    def test_arrows_and_keypad_mirror_fly_keys(self):
        for key,modifier,expected in [(Qt.Key.Key_Up,Qt.KeyboardModifier.NoModifier,Qt.Key.Key_W),(Qt.Key.Key_1,Qt.KeyboardModifier.KeypadModifier,Qt.Key.Key_Z),(Qt.Key.Key_9,Qt.KeyboardModifier.KeypadModifier,Qt.Key.Key_E)]:
            event=QKeyEvent(QEvent.Type.KeyPress,key,modifier);self.assertEqual(Viewport.navigation_key(event),expected)
    def test_curated_examples_and_easy_optional_enemy(self):
        # The workspace may also contain real projects created in the editor.
        # Verify the bundled masters without treating user projects as debris.
        self.assertTrue({'dynamic_lab','mini_chronicle','showcase','tutorial'}.issubset(p.name for p in (ROOT/'chronicles').iterdir()))
        for folder in ['tutorial','mini_chronicle','showcase']:
            doc=Document.load(self.backend.ws,'chronicles/'+folder+'/project.yaml');result=self.backend.validate(doc.snapshot());self.assertTrue(result.valid)
            enemies=[a for s in doc.campaign['scenes'] for a in s['actors'] if a.get('behavior')=='enemy'];self.assertEqual(len(enemies),1);self.assertEqual(enemies[0]['template'],'Rat')
            for s in doc.campaign['scenes']:
                for e in s['events']:
                    if e['when']=='scene_start':self.assertFalse(any(a.get('spawn_encounter') for a in e['actions']))
        self.assertEqual(len({s['level']['source'] for s in self.win.doc.campaign['scenes']}),1)
    def test_multi_deploy_updates_one_sibling_preserves_other_and_foreign(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as name:
            game=Path(name);(game/'Vampire.exe').write_bytes(b'fixture');(game/'Resource.nob').write_bytes(b'fixture')
            with patch('rcm.deployment_many.configured_game',return_value=game),patch('rcm.deployment_many.game_running',return_value=False):
                report=deploy_many(self.backend.ws,['rcm_tutor','rcm_mini'],'both');dest=Path(report['destination']);foreign=dest/'foreign.txt';foreign.write_bytes(b'keep');first=(dest/'rcm_mini.nob').read_bytes()
                deploy_many(self.backend.ws,['rcm_tutor'],'both',preserve_siblings=True)
                self.assertEqual((dest/'rcm_mini.nob').read_bytes(),first);self.assertEqual(foreign.read_bytes(),b'keep')
                owners=json.loads((dest/'.rcm_deployment.json').read_text());self.assertEqual(set(owners['owners']),{'rcm_tutor','rcm_mini'})
