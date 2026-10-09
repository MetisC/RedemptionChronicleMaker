"""Exercise our own Qt widgets and real OpenGL placement. Never drives Vampire."""
from pathlib import Path
import os,json,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
os.environ['QT_QPA_PLATFORM']='windows'
from PySide6.QtWidgets import QApplication,QLineEdit,QDoubleSpinBox,QComboBox,QPushButton
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtGui import QFont,QFontDatabase
import numpy as np
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.deployment import default_game
from rcm.document import Document
from rcm.editor.window import MainWindow,NewProjectDialog
app=QApplication([]);QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf');app.setFont(QFont('Segoe UI',10));app.setStyle('Fusion')
ws=Workspace(ROOT,default_game(ROOT));out=ws.output('research/phase9/gui');out.mkdir(parents=True,exist_ok=True)
path=out/'authored/project.yaml'
if path.exists():ws.write(out/('previous_'+str(time.time_ns())+'.yaml'),path.read_bytes());path.unlink()
w=MainWindow(Backend(ws));w.show();steps=[]
try:
    dialog=NewProjectDialog(ws,w);dialog.pid.setText('p9_gui');dialog.name.setText('Autoría visual de Fase 9');dialog.directory.setText(str(path.parent));w.create_project(dialog);steps.append('new campaign from dialog fields')
    w.resource_chosen('levels','EastLondon');w.center_tabs.setCurrentIndex(0)
    deadline=time.monotonic()+45
    while w.spatial.loading or w.spatial.loaded_name!='EastLondon':
        if time.monotonic()>deadline:raise ValueError('Carga espacial agotó el plazo')
        app.processEvents();QTest.qWait(20)
    v=w.spatial.viewport
    if not v or not v.isValid():raise ValueError('Sin contexto OpenGL real')
    v.pos=np.array([1016.,-400.,950.]);v.yaw=90;v.pitch=-75;v.update();QTest.qWait(200)
    def place(kind,position,template=''):
        w.spatial.begin_place(kind,template);point=v.project(np.array(position,dtype=float))
        if not point or not v.rect().contains(point.toPoint()):raise ValueError('Punto fuera del viewport')
        before=len(w.doc.data.get(kind,[]));QTest.mouseClick(v,Qt.MouseButton.LeftButton,pos=point.toPoint());app.processEvents()
        if len(w.doc.data[kind])!=before+1:raise ValueError('Click no colocó '+kind)
        actual=w.doc.data[kind][-1]['transform']['position']
        if np.linalg.norm(np.array(actual)-position)>12:raise ValueError('Raycast no coincide con el suelo elegido')
        steps.append('mouse surface placement: '+kind)
    place('entries',[1016,-210,0]);w.properties.widget().findChild(QDoubleSpinBox,'orientation_2').setValue(90);steps.append('entry yaw edited through inspector')
    place('waypoints',[850,-210,0]);place('waypoints',[850,-320,0]);place('actors',[1016,-54,0],'businessWoman')
    w.campaign_panel.findChild(QPushButton,'add_path').click();w.campaign_panel.findChild(QLineEdit,'path_name').setText('Paseo visual');w.commit_properties();steps.append('route created from waypoint order with panel controls')
    w.select(('actors',0));w.add_conversation();w.select(('actors',0));combo=w.properties.widget().findChild(QComboBox,'actor_conversation');combo.setCurrentIndex(combo.findData('conv1'));steps.append('conversation linked with inspector selector')
    w.campaign_panel.findChild(QPushButton,'add_quest').click();w.campaign_panel.findChild(QLineEdit,'quest_title').setText('Quest creada desde controles');w.commit_properties();steps.append('quest title committed through panel')
    w.save_project();source=w.doc.snapshot();reopened=Document.load(ws,path).snapshot()
    if source!=reopened:raise ValueError('Reapertura cambió datos')
    report=w.backend.build(source);steps.append('saved, reopened, validated and compiled against original API')
    w.center_tabs.setCurrentIndex(0);w.select(('entries',0));QTest.qWait(250);w.grab().save(str(out/'authored_editor.png'));v.grabFramebuffer().save(str(out/'authored_viewport.png'))
    # Inspect the actual circuit spatially as a separate curated source.
    w.open_path(ws.output('chronicles/circuit/project.yaml'));w.center_tabs.setCurrentIndex(0)
    deadline=time.monotonic()+45
    while w.spatial.loading or w.spatial.loaded_name!='EastLondon':
        if time.monotonic()>deadline:raise ValueError('Carga del circuito agotó el plazo')
        app.processEvents();QTest.qWait(20)
    v=w.spatial.viewport;v.pos=np.array([1016.,-400.,950.]);v.yaw=90;v.pitch=-75;w.select(('entries',0));v.update();QTest.qWait(350)
    w.grab().save(str(out/'circuit_editor.png'));v.grabFramebuffer().save(str(out/'circuit_viewport.png'))
    result=dict(success=True,steps=steps,real_gl=v.isValid(),viewport_error=v.error,source=str(path),class_versions=report['class_versions'],gui_authored_basic_project=True,full_adventure_gui_acceptance=False,native_engine_test=False)
    ws.write(out/'probe.json',json.dumps(result,indent=2));print(json.dumps(result,indent=2))
finally:
    w.doc=None;w.close();app.processEvents()
