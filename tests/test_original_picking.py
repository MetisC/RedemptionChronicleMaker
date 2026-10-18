"""Visual original-object selection and honest fixed-surface transitions."""
import copy
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch,Mock
import numpy as np
from PySide6.QtWidgets import QApplication,QDialog,QPushButton,QMenu,QComboBox
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_document import CampaignDocument
from rcm.spatial.assets import Assets,LevelData
from rcm.spatial.geometry import Mesh
from rcm.spatial.scene_mesh import read_brush,find_brush
from rcm.original_objects import catalogue,selector
from rcm.editor.viewport import Viewport
from rcm.editor.window import MainWindow
from rcm.editor.original_objects import OriginalObjectPicker,PassageDialog,use_selected
from test_release10 import blank

ROOT=Path(__file__).resolve().parents[1]


class OriginalPicking(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        cls.backend=Backend(Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption')));cls.backend.safe_mode=True
        cls.level=Assets(cls.backend).load('ClubTenebrae')
        cls.exit=next(r for r in cls.level.references if r.get('script')=='ClickExit')
    def window(self):
        win=MainWindow(self.backend);root=blank();root['scenes'][0]['level']={'source':'ClubTenebrae'};win.doc=CampaignDocument(self.backend.ws,root);win.refresh()
        v=Viewport(win.spatial);win.spatial.viewport=v;win.spatial.ensure_loaded=lambda:None;win.guard=lambda cb:cb();v.set_level(self.level);v.sync(win.doc.data,());win.refresh()
        self.addCleanup(lambda:(setattr(win,'doc',None),win.close(),v.deleteLater()));return win,v
    def exit_ray(self,v):
        mesh=self.level.models[self.exit['preview_model']][0];tri=mesh.triangles[0];center=tri.mean(0)+self.exit['position'];normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);normal/=np.linalg.norm(normal)
        v.screen_ray=Mock(return_value=(center+normal*20,-normal))
    def test_tenebrae_inline_exit_has_real_mesh_and_fixed_doors_are_nil_surfaces(self):
        self.assertEqual(self.exit['template'],'tracker_thing');self.assertEqual(self.exit['mesh_materials'],['London\\CTdoor_L'])
        mesh=self.level.models[self.exit['preview_model']][0];self.assertEqual(len(mesh.material_ids),48);self.assertTrue(np.isfinite(mesh.vertices).all())
        mid=self.level.mesh.materials.index('London\\CTdoor_L');door=self.level.mesh.triangles[self.level.mesh.material_ids==mid];self.assertEqual(len(door),138)
        self.assertTrue((door.mean(1)[:,0]<700).any());self.assertTrue((door.mean(1)[:,0]>900).any())
        for row in catalogue(self.backend,'ClubTenebrae'):
            if row['template']!='tracker_thing':self.assertNotIn('mesh_offset',row)
    def test_brush_reader_bounds_corruption_and_entity_boundary_are_checked(self):
        source=self.backend.hints['l1_ten1.nsd']['source'];data=self.backend.ws.output('research/original/'+source['archive']+'/'+source['path']).read_bytes()
        mesh=read_brush(data,self.exit['mesh_offset']);self.assertEqual(len(mesh.material_ids),48)
        bad=bytearray(data);bad[mesh.source_end-24:mesh.source_end]=bytes(24)
        with self.assertRaises(ValueError):read_brush(bad,self.exit['mesh_offset'])
        self.assertEqual(find_brush(data,6540,6560),{})
    def test_right_click_uses_pointed_object_even_with_helpers_hidden_and_skips_list(self):
        win,v=self.window();v.hidden={('original',)};self.exit_ray(v);before=win.doc.snapshot();seen=[]
        def menu_exec(menu,*_):
            action=next(a for a in menu.actions() if a.objectName()=='use_original');self.assertIn('CTdoor_L',action.text());action.trigger()
        def dialog_exec(dialog):seen.append(dialog.target);return QDialog.DialogCode.Rejected
        class Menu(QMenu):
            def exec(self,*args):return menu_exec(self,*args)
        class Dialog(PassageDialog):
            def exec(self):return dialog_exec(self)
        with patch('rcm.editor.viewport.QMenu',Menu),patch('rcm.editor.original_objects.PassageDialog',Dialog),patch('rcm.editor.original_objects.OriginalObjectPicker',side_effect=AssertionError('Pointed object must skip list')):
            win.spatial.context_menu(v.mapToGlobal(v.rect().center()))
        self.assertEqual(seen,[selector(self.exit)]);self.assertEqual(win.doc.snapshot(),before);self.assertEqual(win.selection[0],'original')
    def test_fixed_surface_does_not_reuse_stale_selected_object_or_generate_removal(self):
        win,v=self.window();win.select(('original',self.level.references.index(self.exit)));v.screen_ray=Mock(return_value=(np.array([536.,0.,-350.]),np.array([0.,1.,0.])));seen=[]
        def menu_exec(menu,*_):
            action=next(a for a in menu.actions() if a.objectName()=='use_original');self.assertIn('CTdoor_L',action.text());action.trigger()
        def dialog_exec(dialog):seen.append(dialog);return QDialog.DialogCode.Rejected
        class Menu(QMenu):
            def exec(self,*args):return menu_exec(self,*args)
        class Dialog(PassageDialog):
            def exec(self):return dialog_exec(self)
        with patch('rcm.editor.viewport.QMenu',Menu),patch('rcm.editor.original_objects.PassageDialog',Dialog):win.spatial.context_menu(v.mapToGlobal(v.rect().center()))
        self.assertEqual(len(seen),1);dialog=seen[0];self.assertTrue(dialog.fixed);self.assertFalse(dialog.operation.isEnabled());self.assertLess(dialog.target['position'][1],208);self.assertEqual(dialog.when.currentData(),'object_clicked')
        before=win.doc.snapshot();kind=dialog.actions.scroll.widget().findChild(QComboBox,'action_kind');kind.setCurrentIndex(kind.findData('travel'));destination=dialog.actions.scroll.widget().findChild(QComboBox,'travel_scene');destination.setCurrentIndex(destination.findData('home'));entry=dialog.actions.scroll.widget().findChild(QComboBox,'travel_entry');entry.setCurrentIndex(entry.findData('start'));dialog.accept();self.assertEqual(dialog.result(),QDialog.DialogCode.Accepted,dialog.error.text())
        event=win.doc.data['events'][-1];self.assertEqual(event['when'],'object_clicked');self.assertEqual(win.doc.data['triggers'],[]);self.assertEqual(event['actions'],[{'travel':{'scene':'home','entry':'start'}}]);self.assertTrue(win.backend.validate(win.doc.snapshot()).valid);win.undo_project();self.assertEqual(win.doc.snapshot(),before)
    def test_list_locate_focuses_original_without_editing_the_document(self):
        win,v=self.window();before=win.doc.snapshot();v.focus_selection=Mock();picker=OriginalObjectPicker(win,self.exit);button=picker.findChild(QPushButton,'locate_original_object');self.assertTrue(button.isEnabled());button.click()
        self.assertEqual(win.selection,('original',self.level.references.index(self.exit)));v.focus_selection.assert_called_once();self.assertEqual(win.doc.snapshot(),before)
    def test_fixed_surface_has_temporary_bounds_during_menu_and_dialog_cancel(self):
        win,v=self.window();before=win.doc.snapshot();v.pick_at=Mock(return_value=None);v.screen_ray=Mock(return_value=(np.array([536.,0.,-350.]),np.array([0.,1.,0.])));seen=[]
        class Menu(QMenu):
            def exec(self,*args):
                self_case.assertIsNotNone(v.context_surface);seen.append(v.context_surface)
                self_case.assertTrue(v.context_surface['fixed_surface'])
                next(a for a in self.actions() if a.objectName()=='use_original').trigger()
        class Dialog(PassageDialog):
            def exec(self):
                self_case.assertIsNotNone(v.context_surface);return QDialog.DialogCode.Rejected
        self_case=self
        with patch('rcm.editor.viewport.QMenu',Menu),patch('rcm.editor.original_objects.PassageDialog',Dialog):win.spatial.context_menu(v.mapToGlobal(v.rect().center()))
        self.assertEqual(len(seen),1);self.assertIsNone(v.context_surface);self.assertEqual(win.doc.snapshot(),before)
    def test_descriptive_event_id_keeps_template_case_and_can_be_renamed(self):
        win,v=self.window();scene=win.doc.campaign['scenes'][win.doc.active];scene['events']=[dict(id='click'+str(i),when='manual',actions=[{'reward_xp':1}]) for i in range(1,4)]
        row=next(r for r in self.level.references if r['template']=='drippyCandle');dialog=PassageDialog(win,row)
        self.assertEqual(dialog.actions.event['id'],'click_drippyCandle_4');dialog.accept();self.assertEqual(dialog.result(),QDialog.DialogCode.Accepted,dialog.error.text())
        self.assertEqual(win.doc.data['events'][-1]['id'],'click_drippyCandle_4');win.doc.rename('events',3,'click_drippyCandle_renamed_4');self.assertTrue(win.backend.validate(win.doc.snapshot()).valid)
    def test_focus_of_tenebrae_exit_stays_inside_and_has_clear_sight(self):
        win,v=self.window();v.selection=('original',self.level.references.index(self.exit));v.focus_selection();target=np.array(self.exit['position']);delta=target-v.pos
        self.assertIsNotNone(v.raycaster.ground(v.pos,80,1200));self.assertIsNone(v.raycaster.cast(v.pos,delta,max_distance=np.linalg.norm(delta)-.5))
    def test_exact_rotated_mesh_picking_occlusion_and_visibility(self):
        v=Viewport();self.addCleanup(v.deleteLater)
        def mesh(z):return Mesh(np.array([[0,0,z,0,0],[2,0,z,1,0],[0,2,z,0,1]],dtype=np.float32),np.array([0]),['material'],0,0,[])
        scenery=Mesh(np.array([[-20,-20,-10,0,0],[20,-20,-10,0,0],[0,20,-10,0,0]],dtype=np.float32),np.array([0]),['floor'],0,0,[])
        row=dict(template='tracker_thing',position=[0,0,0],orientation=[0,0,0]);level=LevelData('fake',scenery,[],[row],{'tracker_thing':(mesh(0),[])},[],False);v.set_level(level);v.sync({'actors':[]},());v.hidden={('original',)}
        v.screen_ray=Mock(return_value=(np.array([1.8,1.8,10]),np.array([0,0,-1])));self.assertIsNone(v.pick_at(0,0))
        v.screen_ray=Mock(return_value=(np.array([.5,.5,10]),np.array([0,0,-1])));self.assertEqual(v.pick_at(0,0),('original',0))
        v.hidden.add(('original',0));self.assertIsNone(v.pick_at(0,0));v.hidden.remove(('original',0))
        row['orientation']=[60,15,90];rot=v.object_rotation(row['orientation']);v.screen_ray=Mock(return_value=(rot@np.array([.5,.5,10]),rot@np.array([0,0,-1])));self.assertEqual(v.pick_at(0,0),('original',0))
        row['orientation']=[0,0,0];level.mesh=mesh(2);v.set_level(copy.copy(level));v.raycaster=__import__('rcm.spatial.math3d',fromlist=['Raycaster']).Raycaster(level.mesh);v.screen_ray=Mock(return_value=(np.array([.5,.5,10]),np.array([0,0,-1])));self.assertIsNone(v.pick_at(0,0))
    def test_explicit_target_cancel_and_incompatible_source_are_safe(self):
        win,v=self.window();before=win.doc.snapshot()
        with patch.object(PassageDialog,'exec',lambda d:QDialog.DialogCode.Rejected),patch.object(OriginalObjectPicker,'exec',lambda d:(_ for _ in ()).throw(AssertionError('Unexpected picker'))):use_selected(win,target=self.exit)
        self.assertEqual(win.doc.snapshot(),before)
