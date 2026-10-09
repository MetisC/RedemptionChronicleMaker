"""GUI-only campaign creation and build; original assets are read-only."""
from pathlib import Path
import sys,os,time,json
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')];os.environ['QT_QPA_PLATFORM']='windows'
from PySide6.QtCore import Qt,QTimer,QPoint
from PySide6.QtWidgets import QApplication,QLineEdit,QComboBox,QSpinBox,QCheckBox,QPushButton,QMessageBox,QPlainTextEdit
from PySide6.QtTest import QTest
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.editor.window import MainWindow
from rcm.editor.browser import ResourceDialog

app=QApplication([]);app.setStyle('Fusion');win=MainWindow(Backend(Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption'))));win.show();out=ROOT/'build/campaign/acceptance';out.mkdir(parents=True,exist_ok=True)
steps=[];errors=[]
def pump(t=.04):
    end=time.monotonic()+t
    while time.monotonic()<end:app.processEvents();time.sleep(.005)
    if errors:raise AssertionError(errors[-1])
def wait(test,t=90):
    end=time.monotonic()+t
    while not test() and time.monotonic()<end:pump(.05)
    assert test(),'timeout'
def click(widget):widget.click();pump()
def prop(cls,name,scope=None):
    control=(scope or win.properties.widget()).findChild(cls,name);assert control is not None,name;return control
def line(name,value,scope=None):
    w=prop(QLineEdit,name,scope);w.setText(value);w.editingFinished.emit();pump()
def combo(name,value,scope=None):
    w=prop(QComboBox,name,scope);i=w.findData(value);assert i>=0,(name,value);w.setCurrentIndex(i);pump()
def check(value,label):assert value,label;steps.append(label)
def warning_guard():
    d=app.activeModalWidget()
    if isinstance(d,QMessageBox):errors.append(d.text());d.accept()
timer=QTimer();timer.timeout.connect(warning_guard);timer.start(100)
win.open_path(ROOT/'tests/fixtures/chronicles/editor_acceptance/project.yaml');pump();win.center_tabs.setCurrentIndex(1)
with patch('rcm.editor.window.QFileDialog.getSaveFileName',return_value=(str(ROOT/'tests/fixtures/chronicles/phase4_demo/project.yaml'),'YAML')):win.actions['save_as'].trigger();pump()
win.select(('chronicle',));line('chronicle_id','phase4_demo');line('chronicle_name','RCM: El libro de Londres');prop(QPlainTextEdit,'chronicle_description').setPlainText('Una campaña de dos mapas: Victoria, un libro robado y tres enemigos.');pump();click(win.campaign_panel.findChild(QPushButton,'convert_campaign'));panel=win.campaign_panel
check(hasattr(win.doc,'campaign'),'Convert through campaign control')
# Existing branching/remembered conversations were authored by GUI in Phase2.
win.select(('actors',0));combo('actor_placement','near_player');win.select(('level',));line('level_name','Londres: el pacto del libro')
click(panel.findChild(QPushButton,'add_quest'));line('campaign_id','ledger_quest',panel);line('quest_title','El libro desaparecido',panel);line('quest_description','Victoria necesita recuperar su libro del oeste de Londres.',panel)
prop(QSpinBox,'quest_reward',panel).setValue(500);pump();line('quest_step_0','Aceptar el encargo de Victoria',panel)
click(panel.findChild(QPushButton,'add_quest_step'));line('quest_step_1','Recuperar el libro en West London',panel)
click(panel.findChild(QPushButton,'add_quest_step'));line('quest_step_2','Regresar y entregar el libro',panel)
check(len(win.doc.campaign['quests'][0]['steps'])==3,'Quest edited with three steps and native reward')

def actor(name,template='businessWoman',enemy=False):
    win.center_tabs.setCurrentIndex(1);win.select(('actors',));click(win.buttons['actor']);idx=win.selection[1];line('actor_id',name);line('actor_name',name.title())
    def choose():
        d=app.activeModalWidget()
        if isinstance(d,ResourceDialog):d.browser.search.setText(template);pump(.01);d.browser.table.selectRow(next(i for i in range(d.browser.table.rowCount()) if d.browser.table.item(i,0).data(Qt.ItemDataRole.UserRole)[0]==template));d.browser.choose()
    QTimer.singleShot(50,choose);click(prop(QPushButton,'choose_template'))
    if enemy:combo('actor_behavior','enemy');prop(QCheckBox,'actor_spawn').setChecked(False);pump()
    return idx
actor('witness')
# Place a transition volume with the real viewport ground raycast.
win.center_tabs.setCurrentIndex(0);wait(lambda:not win.spatial.loading and win.spatial.viewport.level is not None);v=win.spatial.viewport;win.select(('actors',0));v.focus_selection();pump()
def ground_click():
    for y in range(20,v.height()-10,12):
        for x in range(30,v.width()-20,32):
            ray=v.screen_ray(x,y);hit=v.raycaster.cast(*ray)
            if hit and abs(hit.normal[2])>.9 and 30<hit.distance<6000:
                QTest.mouseClick(v,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,QPoint(x,y));pump();return
    win.grab().save(str(out/'failure.png'));v.grabFramebuffer().save(str(out/'failure_view.png'));print('GROUND',v.pos,v.yaw,v.pitch,v.size());raise AssertionError('No ground hit')
click(win.spatial.findChild(QPushButton,'place_trigger'));ground_click();line('trigger_id','west_gate');line('trigger_name','Paso al oeste');check(len(win.doc.data['triggers'])==1,'Spatial transition marker placed by viewport')
# Add second ORIGINAL map through its resource selector.
def choose_west():
    d=app.activeModalWidget()
    if isinstance(d,ResourceDialog):d.browser.search.setText('WestLondon');pump(.01);d.browser.table.selectRow(0);d.browser.choose()
QTimer.singleShot(50,choose_west);click(panel.findChild(QPushButton,'add_scene'));line('campaign_id','west',panel)
win.select(('level',));line('level_name','Londres: el libro robado');actor('contact');actor('keeper')
for i in range(3):actor('guard'+str(i+1),'brujahFled_MD',True)
click(panel.findChild(QPushButton,'add_encounter'));line('campaign_id','ambush',panel);line('encounter_name','Los custodios del libro',panel)
lst=panel.findChild(__import__('PySide6.QtWidgets',fromlist=['QListWidget']).QListWidget,'encounter_members')
for i in range(lst.count()):lst.item(i).setCheckState(Qt.CheckState.Checked)
pump();check(len(win.doc.campaign['scenes'][1]['encounters'][0]['actors'])==3,'Encounter groups three authored enemies')
# Item comes from catalogue and is placed through the spatial resource browser.
win.select(('resources',));win.browser.category.setCurrentIndex(win.browser.category.findData('items'));win.browser.search.setText('ledger');pump();row=next(i for i in range(win.browser.table.rowCount()) if win.browser.table.item(i,0).data(Qt.ItemDataRole.UserRole)[0]=='ledger');win.browser.table.selectRow(row)
# Ensure West geometry finishes before clicking a point.
win.center_tabs.setCurrentIndex(0);wait(lambda:not win.spatial.loading and v.level and v.level.name=='WestLondon');win.select(('actors',0));v.focus_selection();pump();QTest.keyPress(v,Qt.Key.Key_W);pump(1.2);QTest.keyRelease(v,Qt.Key.Key_W);QTest.keyPress(v,Qt.Key.Key_E);pump(.4);QTest.keyRelease(v,Qt.Key.Key_E);win.select(('resources',));win.browser.table.selectRow(row);click(win.browser.use_button);ground_click();line('actor_id','book');line('actor_name','Libro de Victoria');combo('object_quest_item',True);combo('actor_placement','near_player');check(win.doc.data['objects'][0]['template']=='ledger','Quest item placed from real resource')
click(panel.findChild(QPushButton,'add_sequence'));line('campaign_id','arrival',panel);combo('sequence_actor','contact',panel);combo('sequence_shot','wide',panel)
# Events/actions/conditions use the EXISTING central Event Editor controls.
def event(eid,when,origin=None,result=None,once=False,conditions=None):
    win.center_tabs.setCurrentIndex(1);win.select(('events',));click(win.buttons['event']);ei=win.selection[1];line('event_id',eid);combo('event_when',when)
    key={'actor_clicked':'actor','conversation_ended':'conversation','trigger_enter':'trigger','item_picked_up':'item','encounter_complete':'encounter'}.get(when)
    if key:combo('event_'+key,origin)
    if result is not None:prop(QSpinBox,'event_result').setValue(result);pump()
    if once:combo('event_once',True)
    if conditions:
        for flag,is_set in conditions:
            win.select(('events',ei));click(win.buttons['condition']);combo('condition_flag',flag);combo('condition_state',is_set)
    return ei
def action(ei,kind,target=True):
    win.select(('events',ei));click(win.buttons['action']);combo('action_kind',kind)
    if kind=='reward_xp':prop(QSpinBox,'action_amount').setValue(target);pump()
    elif kind not in {'stop_music','stop_ambient','release_camera'}:combo('action_target',target)
    return win.selection
# West spawn exists for NPC/item. Near-player enemy spawns avoid unverified XYZ paths.
ei=event('ambush_begin','scene_start',once=True);action(ei,'spawn_encounter','ambush');action(ei,'start_music','DA_Boss_1_Modern');action(ei,'play_sequence','arrival')
ei=event('book_found','item_picked_up','book',once=True);action(ei,'advance_quest','ledger_quest')
ei=event('guards_defeated','encounter_complete','ambush',once=True);action(ei,'start_music','London_Hub');action(ei,'reward_xp',100)
# Return path is a conversation (real API Jump), easy to find beside the player.
win.select(('actors',0));win.center_tabs.setCurrentIndex(1);click(win.buttons['conversation']);ci=win.selection[1];line('conversation_id','home');win.select(('conversations',ci,'nodes',0,'lines',0));prop(QPlainTextEdit,'line_text').setPlainText('El libro está aquí. Habla conmigo para regresar con Victoria.');pump()
win.select(('actors',0));combo('actor_conversation','home')
ei=event('return_london','conversation_ended','home',1);action(ei,'jump','london')
# London: accepted branch starts quest and finishes its first objective.
panel.scene.setCurrentIndex(0);pump()
win.select(('conversations',1,'nodes',0));click(win.buttons['answer']);prop(QPlainTextEdit,'answer_text').setPlainText('Vamos al oeste de Londres.');pump()
ei=event('quick_travel','conversation_ended','ally',3,conditions=[('alliance',True)]);action(ei,'jump','west')
ei=event('accept_mission','conversation_ended','intro',3,True);action(ei,'start_quest','ledger_quest');action(ei,'advance_quest','ledger_quest')
ei=event('travel_west','trigger_enter','west_gate',once=False,conditions=[('alliance',True)]);action(ei,'jump','west')
ei=event('quest_finish','conversation_ended','ally',1,True,conditions=[('alliance',True)])
win.select(('events',ei));click(win.buttons['condition']);typebox=next(c for c in win.properties.widget().findChildren(QComboBox) if c.objectName().startswith('condition_type_'));typebox.setCurrentIndex(typebox.findData('quest_step'));pump();combo('condition_quest','ledger_quest');prop(QSpinBox,'condition_quest_step').setValue(2);pump()
win.select(('events',ei));click(win.buttons['condition']);typebox=next(c for c in win.properties.widget().findChildren(QComboBox) if c.objectName().startswith('condition_type_'));typebox.setCurrentIndex(typebox.findData('owns_item'));pump();combo('condition_entity','west.book');action(ei,'take_item','west.book');action(ei,'advance_quest','ledger_quest');action(ei,'complete_quest','ledger_quest');action(ei,'start_music','Haven')
# Change finish text through existing conversation controls.
win.select(('conversations',1,'nodes',0,'lines',0));prop(QPlainTextEdit,'line_text').setPlainText('Si has recuperado el libro, el encargo termina aquí. Gracias por tu ayuda.');pump()
win.actions['save'].trigger();pump();validation=win.validate_from_ui();check(validation.valid,'Campaign integrity validates all authored references')
win.actions['build'].trigger();wait(lambda:not win.busy,120);check(win.last_build and win.last_build['status']=='compiled-unverified-in-game','GUI campaign build compiled against original Codex')
win.center_tabs.setCurrentWidget(panel);panel.search.setText('ledger');pump();check(panel.tree.topLevelItemCount()>0,'Global search includes items quests and event targets');panel.search.clear();panel.navigate(('quests',0));pump();win.grab().save(str(out/'campaign.png'))
report={'successful':True,'steps':steps,'project':str(win.doc.path),'yaml_manually_authored':False,'native_engine_run':False,'build':win.last_build,'problems':[{'severity':p.severity,'message':p.message} for p in validation.problems]};(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='build'},ensure_ascii=False));win.doc._saved=__import__('rcm.service',fromlist=['source_text']).source_text(win.doc.campaign);wait(lambda:not win.spatial.loading);win.close();pump()

