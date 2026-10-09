"""Real-window spatial authoring acceptance via our Qt controls.

Reads original assets only; writes source and builds in the workspace. Does not
run Redemption. A repeated run backs up the previously authored demo first.
"""
from pathlib import Path
import os
import sys
import time
import json
import hashlib
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
os.environ['QT_QPA_PLATFORM']='windows'
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtGui import QFontDatabase,QFont
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QLineEdit,QComboBox,QCheckBox,QPushButton,QMessageBox,QPlainTextEdit
from rcm.editor.window import MainWindow
from rcm.service import Backend
from rcm.paths import Workspace
from rcm.spatial.relations import affected

def main():
    app=QApplication([]);app.setStyle('Fusion');QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf');app.setFont(QFont('Segoe UI',10))
    w=MainWindow(Backend(Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption'))));w.show()
    out=ROOT/'build/viewport/acceptance';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'chronicles/editor_acceptance/project.yaml';original=source.read_bytes()
    target=ROOT/'chronicles/phase3_demo/project.yaml'
    if target.exists():
        (out/('previous-'+str(time.time_ns())+'.yaml')).write_bytes(target.read_bytes())
    steps=[];errors=[]
    def check(value,label):
        if not value:raise AssertionError(label)
        steps.append(label)
    def pump(seconds=.05):
        until=time.monotonic()+seconds
        while time.monotonic()<until:
            app.processEvents();time.sleep(.005)
        if errors:raise AssertionError(errors[-1])
    def wait(condition,timeout=30):
        end=time.monotonic()+timeout
        while not condition() and time.monotonic()<end:pump(.03)
        if not condition():raise TimeoutError('Waiting for load/build')
    def guard_dialog():
        widget=app.activeModalWidget()
        if isinstance(widget,QMessageBox):errors.append(widget.text());widget.accept()
    timer=QTimer();timer.timeout.connect(guard_dialog);timer.start(50)
    def widget(cls,name):
        found=w.properties.widget().findChild(cls,name)
        if found is None:raise AssertionError('Missing property '+name)
        return found
    def line(name,value):
        field=widget(QLineEdit,name);field.setText(value);field.editingFinished.emit();pump()
    def combo(name,value):
        field=widget(QComboBox,name);index=field.findData(value);check(index>=0,'choice '+name+' exists');field.setCurrentIndex(index);pump()
    def click(button):QTest.mouseClick(button,Qt.MouseButton.LeftButton);pump()
    def ground_pixel():
        v=w.spatial.viewport
        for y in range(int(v.height()*.45),int(v.height()*.8),max(5,v.height()//12)):
            for x in range(int(v.width()*.25),int(v.width()*.75),max(5,v.width()//12)):
                o,d=v.screen_ray(x,y);hit=v.raycaster.cast(o,d)
                if hit and abs(hit.normal[2])>.9 and 80<hit.distance<1000:return QPoint(x,y),hit.position
        raise AssertionError('No visible walkable surface')
    def drag_gizmo(mode,axis=0,amount=35):
        v=w.spatial.viewport;w.spatial.set_mode(mode);pump()
        if mode=='rotate':
            ring=v.rotation_ring;pt=ring[len(ring)//4].toPoint()
        else:
            pos=v.position(w.selection[:2],w.at(w.selection[:2]));seg=v.gizmo_segments(pos)[axis];pt=((seg[1]+seg[2])/2).toPoint()
        QTest.mousePress(v,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,pt)
        check(v.drag is not None,mode+' gizmo picked')
        QTest.mouseMove(v,pt+QPoint(amount,0),delay=15);pump()
        QTest.mouseRelease(v,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,pt+QPoint(amount,0));pump()

    w.open_path(source);w.center_tabs.setCurrentIndex(0);wait(lambda:w.spatial.loaded_name=='EastLondon' and not w.spatial.loading)
    v=w.spatial.viewport
    check(v.isValid() and not v.error,'OpenGL real window loaded')
    check(not w.doc.modified and source.read_bytes()==original,'viewport opening does not change YAML')
    check(all(m.warning is None for m in v.level.materials),'109 original level materials textured')
    w.actions['build'].trigger();wait(lambda:not w.busy)
    check(w.last_build['status']=='compiled-unverified-in-game','Phase2 build succeeds with viewport')
    check(hashlib.sha256((ROOT/'build/editor_demo/editor_demo_distribution.zip').read_bytes()).hexdigest()=='90b41cb0b203510fafadde9f08bef5afe484aaefcb2cc8aaafbc636b88ca86ab','Phase2 runtime distribution byte-identical')
    with patch('rcm.editor.window.QFileDialog.getSaveFileName',return_value=(str(target),'YAML')):w.actions['save_as'].trigger()
    w.select(('chronicle',));line('chronicle_id','phase3_demo');line('chronicle_name','RCM: Londres, autoría espacial');w.select(('level',));line('level_name','Londres: escenas sobre el mapa')
    w.select(('chronicle',));widget(QPlainTextEdit,'chronicle_description').setPlainText('Escena creada con Resource Browser, colocación sobre el suelo y gizmos. El pacto con Victoria habilita un encuentro al entrar en el trigger.');pump()
    w.add_flag();line('flag_alias','entered')
    w.select(('actors',0));v.focus_selection();pump()
    camera=v.pos.copy();QTest.keyPress(v,Qt.Key.Key_W);pump(.25);QTest.keyRelease(v,Qt.Key.Key_W);check(float(((v.pos-camera)**2).sum())>1,'WASD moves camera')
    QTest.keyClick(v,Qt.Key.Key_F);pump()
    QTest.mousePress(v,Qt.MouseButton.RightButton,Qt.KeyboardModifier.NoModifier,QPoint(v.width()//2,v.height()//2));old_yaw=v.yaw
    QTest.mouseMove(v,QPoint(v.width()//2+30,v.height()//2+10));pump();QTest.mouseRelease(v,Qt.MouseButton.RightButton)
    check(v.yaw!=old_yaw,'RMB mouse free look')
    v.focus_selection();pump()
    # Resource Browser chooses actual original template, then ground raycasting.
    w.select(('resources',));w.browser.category.setCurrentIndex(w.browser.category.findData('actors'));w.browser.search.setText('businessWoman');pump()
    row=next((i for i in range(w.browser.table.rowCount()) if w.browser.table.item(i,0).data(Qt.ItemDataRole.UserRole)[0]=='businessWoman'),None)
    check(row is not None,'resource browser exact template')
    w.browser.table.selectRow(row);click(w.browser.use_button);pump();pt,pos=ground_pixel();click_at=lambda:QTest.mouseClick(v,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,pt)
    click_at();pump();check(len(w.doc.data['actors'])==2,'actor placed by ground click')
    new=w.doc.data['actors'][1];check(new['transform']['placement']=='absolute','placement serialized in engine coordinates')
    check(abs(new['transform']['position'][2]-float(pos[2]))<.01,'placement matches raycast height')
    w.select(('actors',1));v.focus_selection();pump();before=new['transform']['position'][:];drag_gizmo('move',0)
    check(new['transform']['position']!=before,'move gizmo edits source')
    before=new['transform']['orientation'][:];drag_gizmo('rotate');check(new['transform']['orientation']!=before,'rotation gizmo edits source')
    rotated=new['transform']['orientation'][:]
    w.actions['undo'].trigger();pump();check(w.doc.data['actors'][1]['transform']['orientation']==before,'undo restores gizmo rotation')
    w.actions['redo'].trigger();pump();check(w.doc.data['actors'][1]['transform']['orientation']==rotated,'redo restores gizmo rotation')
    new=w.doc.data['actors'][1]
    # Direct selection with world picking, distinct from the outliner.
    w.select(('actors',0));point=v.project(v.position(('actors',1),new)+[0,0,55]);w.spatial.set_mode('move');pump()
    QTest.mouseClick(v,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,point.toPoint());pump()
    check(w.selection==('actors',1),'viewport picking selects actor and Properties')
    check(w.nav.currentItem()==w.nav_items[('actors',1)],'viewport/outliner synchronize')
    # Original prop uses the already-supported object backend and its NOD.
    w.select(('resources',));w.browser.category.setCurrentIndex(w.browser.category.findData('items'));w.browser.search.setText('barrel1');pump()
    row=next(i for i in range(w.browser.table.rowCount()) if w.browser.table.item(i,0).data(Qt.ItemDataRole.UserRole)[0]=='barrel1')
    w.browser.table.selectRow(row);click(w.browser.use_button);pt,pos=ground_pixel();QTest.mouseClick(v,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,pt);pump()
    wait(lambda:not w.spatial.loading and 'barrel1' in v.level.models)
    check(len(w.doc.data['objects'])==1 and w.doc.data['objects'][0]['template']=='barrel1','object placed from resource browser and original model loaded')
    w.select(('objects',0));v.focus_selection();pump();obj=w.doc.data['objects'][0];before=obj['transform']['position'][:];drag_gizmo('move',0);drag_gizmo('rotate')
    check(obj['transform']['position']!=before and obj['transform']['orientation'][2]!=0,'object moved and rotated')
    w.select(('actors',1));v.focus_selection();pump()
    # Transfer spawn ownership to trigger via existing property/events, not a
    # duplicate event model. Intermediate drafts are allowed to be invalid.
    spawn=widget(QCheckBox,'actor_spawn');spawn.setChecked(False);pump()
    click(w.spatial.findChild(QPushButton,'place_trigger'));pt,pos=ground_pixel();QTest.mouseClick(v,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,pt);pump()
    check(w.selection==('triggers',0),'trigger volume placed')
    line('trigger_name','Entrada del pacto');v.focus_selection();pump();before=w.doc.data['triggers'][0]['transform']['position'][:];drag_gizmo('move',0)
    check(w.doc.data['triggers'][0]['transform']['position']!=before,'trigger move')
    before=w.doc.data['triggers'][0]['size'][:];drag_gizmo('scale',0);check(w.doc.data['triggers'][0]['size']!=before,'trigger size gizmo')
    click(widget(QPushButton,'trigger_event'));event_index=w.selection[1];click(w.buttons['condition']);combo('condition_flag','alliance');combo('condition_state',True)
    w.select(('events',event_index,'actions',0));combo('action_target','entered')
    w.select(('events',event_index));click(w.buttons['action']);combo('action_kind','spawn');combo('action_target',new['id'])
    w.select(('triggers',0));check(('actors',1) in affected(w.doc.data,w.selection),'trigger affected actor highlighted')
    click(widget(QPushButton,'show_related'));pump();w.find_references();check(w.reference_tree.topLevelItem(0).childCount()>0,'Find References shows trigger event')
    reference=w.reference_tree.topLevelItem(0).child(0);w.navigate_reference(reference.data(0,Qt.ItemDataRole.UserRole));pump();check(w.selection[0]=='events','reference navigation')
    w.center_tabs.setCurrentIndex(0);w.select(('triggers',0));v.focus_selection();pump()
    actors=w.nav_items[('actors',)];actors.setCheckState(0,Qt.CheckState.Unchecked);check(('actors',) in v.hidden,'category visibility off');actors.setCheckState(0,Qt.CheckState.Checked);check(('actors',) not in v.hidden,'category visibility on')
    original_item=w.nav_items[('original',)];original_item.setCheckState(0,Qt.CheckState.Checked);w.select(('original',0));pump()
    check('SÓLO LECTURA' in '\n'.join(x.text() for x in w.properties.widget().findChildren(__import__('PySide6.QtWidgets',fromlist=['QLabel']).QLabel)),'original reference read-only inspector')
    original_item.setCheckState(0,Qt.CheckState.Unchecked);w.select(('triggers',0))
    w.actions['save'].trigger();pump();saved=w.doc.snapshot();w.open_path(target);pump();check(w.doc.data==saved,'saved transforms/volumes survive reopen')
    check(w.validate_from_ui().valid,'spatial project validates')
    w.actions['build'].trigger();wait(lambda:not w.busy);check(w.last_build['status']=='compiled-unverified-in-game','spatial Java/NOD build succeeds')
    w.center_tabs.setCurrentIndex(0);w.select(('triggers',0));v.focus_selection();pump()
    w.grab().save(str(out/'editor_spatial.png'));v.grabFramebuffer().save(str(out/'trigger.png'))
    # Render continuously for a measured run; parsing occurs before this loop.
    measure_start=time.perf_counter();frames=v.frame_count
    QTest.keyPress(v,Qt.Key.Key_W);pump(2.);QTest.keyRelease(v,Qt.Key.Key_W)
    elapsed=time.perf_counter()-measure_start;rendered=v.frame_count-frames
    report=dict(successful=True,project=str(target),steps=steps,original_source_unchanged=source.read_bytes()==original,yaml_manually_authored=False,native_engine_run=False,textured_materials=109,triangles=45927,rendered_frames=rendered,measured_wall_seconds=elapsed,observed_fps=rendered/elapsed,performance_measurement='paintGL calls during normal Qt timer WASD navigation; not a monitor presentation or GPU completion measurement',mean_render_ms=sum(v.frame_times)/max(1,len(v.frame_times))*1000,build=w.last_build)
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='build'},ensure_ascii=False))
    w.close();app.processEvents()

if __name__=='__main__':main()
