"""Actor placement, real model previews, drag history and contextual dialogue."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
import numpy as np
from PySide6.QtCore import Qt, QPointF, QEvent, QThreadPool
from PySide6.QtGui import QMouseEvent, QKeyEvent, QImage, QColor
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QMenu, QMessageBox
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.document import Document
from rcm.editor.window import MainWindow
from rcm.editor.viewport import Viewport
from rcm.editor.browser import ResourceDialog
from rcm.editor.model_preview import ModelPreview, PreviewImage, render_model
from rcm.spatial.geometry import Mesh
from rcm.spatial.assets import Material, Assets

ROOT=Path(__file__).resolve().parents[1]


def sample_mesh():
    return Mesh(np.array([[-1,0,-1,0,0],[1,0,-1,1,0],[0,0,1,.5,1]],dtype=np.float32),
                np.array([0],dtype=np.int32),['sample'],0,0,[])


class ActorAuthoring(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        cls.backend=Backend(Workspace(ROOT));cls.backend.safe_mode=True

    def setUp(self):
        self.win=MainWindow(self.backend)
        self.win.doc=Document.load(self.backend.ws,'tests/fixtures/chronicles/tutorial_0913/project.yaml')
        self.win.refresh()

    def tearDown(self):
        self.win.spatial.finish_gesture()
        self.win.doc=None;self.win.close();self.app.processEvents()

    def viewport(self):
        panel=self.win.spatial;panel.viewport=Viewport(panel)
        panel.viewport.data=self.win.doc.data;panel.sync()
        return panel,panel.viewport

    def level(self):
        return SimpleNamespace(name=self.win.doc.data['level']['source'],mesh=sample_mesh(),
                               models={},references=[],materials=[],warnings=[])

    def test_first_accept_queues_placement_until_level_load_then_places_once(self):
        panel,view=self.viewport();count=len(self.win.doc.data['actors'])
        before=self.win.doc.snapshot()
        with patch('rcm.editor.window.ResourceDialog') as dialog,patch.object(panel,'ensure_loaded'):
            self.win.center_tabs.setCurrentIndex(0)
            dialog.return_value.exec.return_value=QDialog.DialogCode.Accepted
            dialog.return_value.selection='businessWoman'
            self.win.add_actor()
            self.assertEqual(panel.pending_resource,('actors','businessWoman'))
            self.assertEqual(len(self.win.doc.data['actors']),count)
            self.assertIsNone(view.placing)
            panel.loaded(self.level(),None)
            self.assertEqual(view.placing,('actors','businessWoman'))
            panel.place([100,200,32]);panel.place([100,200,32])
        self.assertEqual(len(self.win.doc.data['actors']),count+1)
        actor=self.win.doc.data['actors'][-1]
        self.assertEqual(actor['transform']['position'],[100.,200.,32.])
        self.assertTrue(any(a.get('spawn')==actor['id'] for e in self.win.doc.data['events'] for a in e['actions']))
        self.assertTrue(self.backend.validate(self.win.doc.snapshot()).valid)
        self.win.undo_project();self.assertEqual(self.win.doc.snapshot(),before)

    def test_queued_placement_escape_failure_and_document_switch_cancel(self):
        panel,view=self.viewport()
        view.operation_cancelled.connect(panel.cancel_place)
        with patch.object(panel,'ensure_loaded'):
            panel.begin_place('actors','businessWoman')
            view.keyPressEvent(QKeyEvent(QEvent.Type.KeyPress,Qt.Key.Key_Escape,Qt.KeyboardModifier.NoModifier))
            self.assertIsNone(panel.pending_resource)
            panel.begin_place('actors','businessWoman');panel.failed('test error')
            self.assertIsNone(panel.pending_resource)
            panel.begin_place('actors','businessWoman')
            self.win.doc=Document.load(self.backend.ws,'tests/fixtures/chronicles/tutorial_0913/project.yaml')
            panel.sync();self.assertIsNone(panel.pending_resource)
            panel.loaded(self.level(),None);self.assertIsNone(view.placing)

    def test_pending_selection_survives_refresh_with_previous_geometry_visible(self):
        panel,view=self.viewport();view.level=self.level();view.level.name='previous_level'
        with patch.object(panel,'ensure_loaded'):
            panel.begin_place('actors','businessWoman')
            # A refresh before the new geometry arrives must not discard selection.
            with patch.object(view,'sync'):
                panel.sync();panel.sync()
            self.assertEqual(panel.pending_resource,('actors','businessWoman'))
            panel.loading_identity=(0,None,'previous_level');panel.failed('stale failure')
            self.assertEqual(panel.pending_resource,('actors','businessWoman'))
            panel.loading_identity=panel.load_identity()
            panel.loaded(self.level(),None)
            self.assertEqual(view.placing,('actors','businessWoman'))

    def test_resource_dialog_accepts_first_button_click_without_creating_actor(self):
        before=self.win.doc.snapshot();dlg=ResourceDialog(self.backend,'actors',self.win)
        dlg.browser.search.setText('businessWoman')
        row=next(i for i in range(dlg.browser.table.rowCount()) if dlg.browser.table.item(i,0).text()=='businessWoman')
        dlg.browser.table.selectRow(row)
        button=dlg.buttons.button(QDialogButtonBox.StandardButton.Ok)
        self.assertTrue(button.isEnabled());button.click()
        self.assertEqual(dlg.result(),QDialog.DialogCode.Accepted)
        self.assertEqual(dlg.selection,'businessWoman')
        self.assertEqual(self.win.doc.snapshot(),before);dlg.deleteLater()

    def test_drag_updates_live_without_serializing_each_move_and_is_one_undo(self):
        panel,view=self.viewport();view.level=self.level()
        self.win.selection=('actors',0);panel.sync()
        before=self.win.doc.snapshot();count=len(self.win.history)
        panel.start_gesture()
        with patch.object(self.win,'changed',wraps=self.win.changed) as changed,patch.object(self.win.doc,'snapshot',wraps=self.win.doc.snapshot) as snapshot:
            for angle in (1.,2.,3.5,25.,90.,181.5):panel.transform(('actors',0),{'orientation':[0,0,angle]})
            changed.assert_not_called();snapshot.assert_not_called()
            self.assertEqual(view.data['actors'][0]['transform']['orientation'][2],181.5)
            with patch.object(panel,'ensure_loaded'):panel.finish_gesture()
            changed.assert_called_once()
        self.assertEqual(len(self.win.history),count+1)
        self.win.undo_project();self.assertEqual(self.win.doc.snapshot(),before)

    def test_rotation_is_continuous_by_default_and_snap_is_explicit(self):
        view=Viewport();self.addCleanup(view.deleteLater)
        view.last_mouse=QPointF(100,100)
        view.drag=(('actors',0),'rotate',None,QPointF(100,100),np.zeros(3),[0,0,0],[1,1,1],1)
        changes=[];view.transformed.connect(lambda path,change:changes.append(change))
        def move(x):
            view.mouseMoveEvent(QMouseEvent(QEvent.Type.MouseMove,QPointF(x,100),QPointF(x,100),Qt.MouseButton.NoButton,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier))
        self.assertEqual(view.angle_step,0);self.assertEqual(self.win.spatial.angle.value(),0)
        move(101);move(103)
        self.assertEqual([r['orientation'][2] for r in changes],[.5,1.5])
        view.angle_step=15;move(125);self.assertEqual(changes[-1]['orientation'][2],15)

    def test_context_conversation_binds_selected_actor_and_undo_restores_all(self):
        path=('actors',1);actor=self.win.at(path);before=self.win.doc.snapshot()
        menu=QMenu();self.win.add_conversation_action(menu,path)
        action=next(a for a in menu.actions() if a.objectName()=='context_add_conversation')
        action.trigger()
        conv=self.win.doc.data['conversations'][-1]
        self.assertEqual(conv['speaker'],actor['id']);self.assertEqual(conv['camera'],'ots_speaker_close')
        self.assertEqual(actor['conversation']['default'],conv['id'])
        self.assertTrue(self.backend.validate(self.win.doc.snapshot()).valid)
        self.win.undo_project();self.assertEqual(self.win.doc.snapshot(),before)

    def test_context_conversation_opens_story_editor_from_spatial_overview_and_graph(self):
        speaker=self.win.doc.data['actors'][0]
        label=speaker['name']+' · '+speaker['id']
        for path in [('actors',1),('objects',0)]:
            for tab in [0,2,self.win.center_tabs.indexOf(self.win.graph_panel)]:
                with self.subTest(target=path,tab=tab):
                    self.win.select(path)
                    self.win.center_tabs.setCurrentIndex(tab)
                    menu=QMenu();self.win.add_conversation_action(menu,path)
                    action=next(a for a in menu.actions() if a.objectName()=='context_add_conversation')
                    with patch('PySide6.QtWidgets.QInputDialog.getItem',return_value=(label,True)),patch.object(QMessageBox,'question',return_value=QMessageBox.StandardButton.Yes):
                        action.trigger()
                    index=len(self.win.doc.data['conversations'])-1
                    conv=self.win.doc.data['conversations'][index]
                    self.assertEqual(self.win.center_tabs.currentIndex(),1)
                    self.assertEqual(self.win.selection,('conversations',index))
                    self.assertEqual(self.win.heading.text(),conv['id'])
                    self.assertIn(('conversations',index,'nodes',0,'lines',0),self.win.content_items)
                    self.assertIn(('conversations',index,'nodes',0,'choices',0),self.win.content_items)
                    self.assertTrue(self.backend.validate(self.win.doc.snapshot()).valid)

    def test_actor_click_override_and_new_object_click_use_the_new_conversation(self):
        actor=self.win.doc.data['actors'][1]
        event=dict(id='dialog_click',when='actor_clicked',actor=actor['id'],once=False,
                   actions=[{'start_conversation':self.win.doc.data['conversations'][0]['id']}])
        self.win.doc.data['events'].append(event)
        self.win.conversation_for(('actors',1))
        self.assertEqual(event['actions'][0]['start_conversation'],self.win.doc.data['conversations'][-1]['id'])
        path=('objects',0);ident=self.win.at(path)['id']
        self.win.doc.data['events'][:]=[e for e in self.win.doc.data['events'] if e.get('object')!=ident]
        speaker=self.win.doc.data['actors'][0]
        with patch('PySide6.QtWidgets.QInputDialog.getItem',return_value=(speaker['name']+' · '+speaker['id'],True)):
            self.win.conversation_for(path)
        click=next(e for e in self.win.doc.data['events'] if e.get('object')==ident)
        self.assertEqual(click['when'],'object_clicked')
        self.assertEqual(click['actions'],[{'start_conversation':self.win.doc.data['conversations'][-1]['id']}])
        self.assertTrue(self.backend.validate(self.win.doc.snapshot()).valid)

    def test_object_conversation_creates_click_action_preserves_other_actions_and_can_cancel(self):
        path=('objects',0);ident=self.win.at(path)['id'];data=self.win.doc.data
        event=next((e for e in data['events'] if e['when']=='object_clicked' and e.get('object')==ident),None)
        if event is None:
            event=dict(id='sample_click',when='object_clicked',object=ident,once=False,actions=[]);data['events'].append(event)
        event['actions']=[{'set_flag':'step1'},{'show_note':{'title':'Test','text':'Replace this'}}]
        before=self.win.doc.snapshot()
        with patch('PySide6.QtWidgets.QInputDialog.getItem',return_value=('',False)):
            self.win.conversation_for(path)
        self.assertEqual(self.win.doc.snapshot(),before)
        actor=data['actors'][0];label=actor['name']+' · '+actor['id']
        with patch('PySide6.QtWidgets.QInputDialog.getItem',return_value=(label,True)),patch.object(QMessageBox,'question',return_value=QMessageBox.StandardButton.No):
            self.win.conversation_for(path)
        self.assertEqual(self.win.doc.snapshot(),before)
        with patch('PySide6.QtWidgets.QInputDialog.getItem',return_value=(label,True)),patch.object(QMessageBox,'question',return_value=QMessageBox.StandardButton.Yes):
            self.win.conversation_for(path);self.win.conversation_for(path)
        conv=data['conversations'][-1]
        self.assertEqual(conv['speaker'],actor['id'])
        self.assertEqual(event['actions'][0],{'set_flag':'step1'})
        self.assertEqual([a for a in event['actions'] if 'start_conversation' in a],[{'start_conversation':conv['id']}])
        self.assertTrue(self.backend.validate(self.win.doc.snapshot()).valid)
        menu=QMenu();self.win.add_conversation_action(menu,('triggers',0));self.assertEqual(menu.actions(),[])

    def test_preview_loads_before_placement_and_ignores_stale_results(self):
        before=self.win.doc.snapshot();preview=ModelPreview(self.backend)
        material=Material('sample',bytes([200,60,40,255])*4,2,2,None)
        with patch.object(Assets,'model',return_value=(sample_mesh(),[material])):
            preview.select('actors','businessWoman');preview.load()
            self.assertTrue(QThreadPool.globalInstance().waitForDone(5000));self.app.processEvents()
        self.assertFalse(preview.image.pixmap().isNull())
        preview.select('actors','Christof');token=preview.token
        preview.show_result(token-1,'businesswoman.nod',None,'old error')
        self.assertNotIn('old error',preview.image.toolTip())
        preview.select('actors','');self.assertEqual(preview.model,'')
        self.assertEqual(self.win.doc.snapshot(),before);preview.deleteLater()


class PreviewRaster(TestCase):
    def test_preview_cache_changes_with_project_payload_even_for_same_model_name(self):
        app=QApplication.instance() or QApplication([])
        backend=SimpleNamespace(resources={'templates':[{'id':'x','model':'x.nod'}]},project_payload={})
        preview=ModelPreview(backend);preview.select('actors','x');token=preview.token
        preview.cache[('x.nod',preview.yaw)]=QImage()
        backend.project_payload={'3d/models/x.nod':b'new project model'}
        preview.select('actors','x')
        self.assertGreater(preview.token,token);self.assertEqual(preview.cache,{})
        preview.deleteLater();app.processEvents()
    def test_preview_fits_whole_image_after_resize_instead_of_clipping_head_and_feet(self):
        app=QApplication.instance() or QApplication([])
        label=PreviewImage('');label.resize(270,220);label.show();app.processEvents()
        frame=QImage(320,320,QImage.Format.Format_RGBA8888);frame.fill(Qt.GlobalColor.red)
        label.set_frame(frame)
        self.assertLessEqual(label.pixmap().width(),label.width())
        self.assertLessEqual(label.pixmap().height(),label.height())
        label.resize(230,350);app.processEvents()
        self.assertLessEqual(label.pixmap().width(),label.width())
        self.assertEqual(label.pixmap().width(),label.pixmap().height())
        label.close();label.deleteLater()
    def test_real_original_models_render_textures_without_spawning(self):
        backend=Backend(Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption')))
        assets=Assets(backend)
        for ident in ('businessWoman','Christof'):
            record=next(t for t in backend.resources['templates'] if t['id']==ident)
            mesh,materials=assets.model(record['model'])
            image=render_model(mesh,materials)
            colors=np.frombuffer(image.bits(),dtype=np.uint8).reshape(-1,4)
            self.assertGreater(len(np.unique(colors,axis=0)),100)
            self.assertEqual(image.size().width(),320)
    def test_original_uv_origin_depth_alpha_and_empty_mesh(self):
        # Z up; front triangle uses the top half of the decoded texture.
        mesh=sample_mesh();mesh.vertices[:,3:5]=[.25,.75]
        material=Material('sample',bytes([240,20,30,255])*2+bytes([10,220,50,255])*2,2,2,None)
        image=render_model(mesh,[material],yaw=0,size=100)
        self.assertEqual(image.pixelColor(50,50),QColor(240,20,30,255))
        # A nearer, transparent triangle must not obscure the opaque one.
        front=mesh.vertices.copy();front[:,1]-=1
        mesh.vertices=np.vstack([front,mesh.vertices]);mesh.material_ids=np.array([1,0])
        transparent=Material('transparent',bytes([0,0,0,0])*4,2,2,None)
        self.assertEqual(render_model(mesh,[material,transparent],yaw=0,size=100).pixelColor(50,50),QColor(240,20,30,255))
        mesh.vertices=mesh.vertices[:0]
        with self.assertRaises(ValueError):render_model(mesh,[material])

    def test_preview_failure_is_readable_and_can_be_replaced(self):
        app=QApplication.instance() or QApplication([])
        preview=ModelPreview(SimpleNamespace(resources={'templates':[{'id':'x','model':'x.nod'}]}))
        preview.select('actors','x');preview.show_result(preview.token,'x.nod',None,'missing archive')
        self.assertEqual(preview.image.toolTip(),'missing archive')
        image=QImage(10,10,QImage.Format.Format_RGBA8888);image.fill(Qt.GlobalColor.red)
        preview.show_result(preview.token,'x.nod',image,'')
        self.assertFalse(preview.image.pixmap().isNull());preview.deleteLater();app.processEvents()
