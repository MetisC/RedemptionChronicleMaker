"""Author a small adventure through actual widgets, then save/build/iterate.

Deployment targets a synthetic installation inside the workspace, never the game.
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest
import test_release10 as helpers
from rcm import recipes
from rcm.campaign_document import CampaignDocument
from rcm.document import Document
from rcm.paths import Workspace
from rcm.deployment import deploy

ROOT = Path(__file__).resolve().parents[1]


class AdventureAuthoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        from rcm.service import Backend
        cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT))
    setUp=helpers.RecipeGui.setUp
    tearDown=helpers.RecipeGui.tearDown
    wizard=helpers.RecipeGui.wizard
    def test_tutorial_entities_have_floor_and_headroom(self):
        from rcm.deployment import default_game
        from rcm.spatial.assets import Assets
        from rcm.spatial.geometry import read_nil
        from rcm.spatial.math3d import Raycaster
        from rcm.service import Backend
        backend=Backend(Workspace(ROOT,default_game(ROOT)))
        entry=backend.levels['EastLondon']['geometry'][0]
        ray=Raycaster(read_nil(Assets(backend).read(entry['path'],entry['archive'])))
        source=Document.load(backend.ws,'chronicles/tutorial/project.yaml').snapshot()
        self.assertEqual(source['chronicle']['name'],'RCM · Una carta al amanecer')
        for scene in source['scenes']:
            for row in scene['actors']+scene['objects']+scene['entries']+scene['triggers']:
                position=row['transform']['position'];hit=ray.ground(position,64,128)
                self.assertIsNotNone(hit,(scene['id'],row['id']))
                self.assertLessEqual(abs(float(hit.position[2])-position[2]),20)
                self.assertIsNone(ray.cast(hit.position+[0,0,1],[0,0,1],False,110))
    def test_wizard_navigation_buttons_remain_visible(self):
        from PySide6.QtWidgets import QWizard
        wizard=self.wizard('go_to_place');wizard.show();self.app.processEvents();wizard.next();self.app.processEvents()
        finish=wizard.button(QWizard.WizardButton.FinishButton)
        self.assertTrue(finish.isVisible());self.assertGreater(finish.height(),15)
        self.assertEqual(wizard.currentId(),1)
        wizard.reject();wizard.deleteLater()
    def test_barrel_footprint_has_floor_and_clearance_and_approach_arms_trigger(self):
        import math
        import numpy as np
        from rcm.deployment import default_game
        from rcm.spatial.assets import Assets,read_nod
        from rcm.spatial.geometry import read_nil
        from rcm.spatial.math3d import Raycaster,inside
        from rcm.service import Backend
        backend=Backend(Workspace(ROOT,default_game(ROOT)));assets=Assets(backend)
        entry=backend.levels['EastLondon']['geometry'][0]
        ray=Raycaster(read_nil(assets.read(entry['path'],entry['archive'])))
        source=Document.load(backend.ws,'chronicles/tutorial/project.yaml').snapshot()
        template=next(t for t in backend.resources['templates'] if t['id']=='barrel1')
        low,high=read_nod(assets.read('3d/models/'+template['model'])).bounds
        # Check the occupied footprint, not just an anchor on the ground.
        def supported(position):
            for x in (low[0]-12,0,high[0]+12):
                for y in (low[1]-12,0,high[1]+12):
                    origin=np.array(position)+[x,y,0];hit=ray.ground(origin,8,8)
                    if hit is None or abs(hit.position[2]-origin[2])>1:return False
                    if ray.cast(hit.position+[0,0,1],[0,0,1],False,float(high[2]+20)) is not None:return False
            return True
        self.assertFalse(supported([-480,-1018,379]),'the former placement must fail the footprint check')
        for scene in source['scenes']:
            marker=next(o for o in scene['objects'] if o['id']=='marker')
            position=marker['transform']['position'];self.assertTrue(supported(position),scene['id'])
            area=next(t for t in scene['triggers'] if t['transform']['position']==position)
            self.assertFalse(inside(area,scene['entries'][0]['transform']['position']))
            for degrees in range(0,360,45):
                direction=np.array([math.cos(math.radians(degrees)),math.sin(math.radians(degrees)),0])
                # The player can stop beside the barrel, outside its solid body,
                # and still enter the trigger at the actual floor height.
                walk=ray.ground(np.array(position)+90*direction,32,64)
                self.assertIsNotNone(walk,(scene['id'],degrees))
                self.assertTrue(inside(area,walk.position),(scene['id'],degrees))
                self.assertIsNone(ray.cast(walk.position+[0,0,1],[0,0,1],False,110))
            for z in (8,32,60):
                for degrees in range(0,360,30):
                    direction=[math.cos(math.radians(degrees)),math.sin(math.radians(degrees)),0]
                    self.assertIsNone(ray.cast(np.array(position)+[0,0,z],direction,False,60))
            self.assertTrue(any(e['when']=='scene_start' and {'spawn':'marker'} in e['actions'] for e in scene['events']))
    def test_adventure_widgets_save_build_deploy_edit_rebuild(self):
        from PySide6.QtWidgets import QComboBox, QInputDialog
        source = helpers.blank();source['scenes'].pop();source['chronicle']['id']='gui_adventure'
        self.win.doc = CampaignDocument(self.backend.ws, source);self.win.refresh()
        with patch.object(QInputDialog,'getItem',return_value=('Nuevo layout vacío sobre este level',True)):
            self.win.campaign_panel.add_scene()
        self.assertEqual(len(self.win.doc.campaign['scenes']),2)
        self.win.doc.active=0;self.win.refresh()
        created={}
        for kind in ['go_to_place','quest','pickup','encounter','travel','note']:
            wizard=self.wizard(kind)
            if kind=='quest':wizard.controls['quest_steps'].setPlainText('Reach the square.\nCollect the letter.')
            wizard.accept();self.assertFalse(wizard.error.text());created[kind]=wizard.recipe_id;wizard.deleteLater()
        refs=lambda kind:next(r['refs'] for r in recipes.recipes(self.win.doc.campaign) if r['id']==created[kind])
        quest=refs('quest')['quest']['id']
        def add_action(event_ref,kind):
            rows=self.win.doc.data['events'];index=next(i for i,e in enumerate(rows) if e['id']==event_ref['id'])
            self.win.select(('events',index));self.win.add_event_action()
            combo=self.win.properties.widget().findChild(QComboBox,'action_kind')
            self.assertIsNotNone(combo);combo.setCurrentIndex(combo.findData(kind))
            target=self.win.properties.widget().findChild(QComboBox,'action_target')
            self.assertIsNotNone(target);target.setCurrentIndex(target.findData(quest))
            self.assertTrue(self.win.commit_properties())
        add_action(refs('go_to_place')['end_event'],'advance_quest')
        add_action(refs('pickup')['event'],'advance_quest')
        add_action(refs('pickup')['event'],'complete_quest')
        source=self.win.doc.snapshot();self.assertTrue(self.backend.validate(source).valid)
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as directory:
            path=Path(directory)/'project.yaml';self.win.doc.save(path)
            self.win.doc=Document.load(self.backend.ws,path);self.win.refresh()
            self.assertEqual(self.win.doc.snapshot(),source)
            self.backend.build(source)
            game=Path(directory)/'Game';game.mkdir()
            for name in ['Vampire.exe','Resource.nob']:(game/name).write_bytes(b'untouched fixture')
            ws=Workspace(ROOT,game)
            with patch('rcm.deployment.game_running',return_value=False):deploy(ws,'gui_adventure',current_source=source)
            installed=game/'RCM/gui_adventure/gui_adventure.nob';first=installed.read_bytes()
            wizard=self.wizard('go_to_place',created['go_to_place']);wizard.controls['text'].setPlainText('Follow the street to the square.');wizard.accept();wizard.deleteLater()
            modified=self.win.doc.snapshot()
            with patch('rcm.deployment.game_running',return_value=False):
                with self.assertRaisesRegex(ValueError,'cambió'):deploy(ws,'gui_adventure',current_source=modified)
                self.backend.build(modified);deploy(ws,'gui_adventure',current_source=modified)
            self.assertNotEqual(installed.read_bytes(),first)
            self.assertEqual((game/'Resource.nob').read_bytes(),b'untouched fixture')
            report=json.loads((ROOT/'build/gui_adventure/build_report.json').read_text(encoding='utf8'))
            self.assertEqual(report['status'],'compiled-unverified-in-game')

