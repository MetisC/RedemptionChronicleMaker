"""Create the Phase 5 demonstration through Qt authoring controls, then build."""
from pathlib import Path
import sys,os,time,json
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')];os.environ['QT_QPA_PLATFORM']='windows'
from PySide6.QtCore import QTimer,Qt
from PySide6.QtWidgets import QApplication,QLineEdit,QComboBox,QSpinBox,QDoubleSpinBox,QPushButton,QMessageBox,QPlainTextEdit
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.editor.window import MainWindow
from rcm.editor.browser import ResourceDialog
app=QApplication([]);app.setStyle('Fusion');win=MainWindow(Backend(Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption'))));win.show();out=ROOT/'build/phase5_acceptance';out.mkdir(parents=True,exist_ok=True);errors=[];checks=[]
def pump(t=.04):
 end=time.monotonic()+t
 while time.monotonic()<end:app.processEvents();time.sleep(.005)
 if errors:raise AssertionError(errors[-1])
def wait(test,t=90):
 end=time.monotonic()+t
 while not test() and time.monotonic()<end:pump(.05)
 assert test(),'timeout'
def warning():
 d=app.activeModalWidget()
 if isinstance(d,QMessageBox):errors.append(d.text());d.accept()
timer=QTimer();timer.timeout.connect(warning);timer.start(100)
def prop(cls,name,scope=None):
 c=(scope or win.properties.widget()).findChild(cls,name);assert c is not None,name;return c
def line(name,value,scope=None):c=prop(QLineEdit,name,scope);c.setText(value);c.editingFinished.emit();pump()
def combo(name,value,scope=None):c=prop(QComboBox,name,scope);i=c.findData(value);assert i>=0,(name,value);c.setCurrentIndex(i);pump()
def click(c):c.click();pump()
def choose_resource(ident):
 def select():
  d=app.activeModalWidget();assert isinstance(d,ResourceDialog),type(d);d.browser.search.setText(ident);pump(.01);row=next(i for i in range(d.browser.table.rowCount()) if d.browser.table.item(i,0).data(Qt.ItemDataRole.UserRole)[0]==ident);d.browser.table.selectRow(row);d.browser.choose()
 QTimer.singleShot(50,select)
def check(value,label):assert value,label;checks.append(label);print(label,flush=True)
win.open_path(ROOT/'tests/fixtures/chronicles/phase4_demo/project.yaml');pump();win.center_tabs.setCurrentIndex(1)
with patch('rcm.editor.window.QFileDialog.getSaveFileName',return_value=(str(ROOT/'tests/fixtures/chronicles/phase5_demo/project.yaml'),'YAML')):win.actions['save_as'].trigger();pump()
win.select(('chronicle',));line('chronicle_id','phase5_demo');line('chronicle_name','RCM: Las voces de Londres');prop(QPlainTextEdit,'chronicle_description').setPlainText('Dos mapas, dos quests y Victoria con template, AI y script propios.');pump()
rp=win.project_resources_panel;click(rp.findChild(QPushButton,'upgrade_format'));check(win.doc.campaign['project_format']==5,'Explicit project upgrade with backup')
# Clone an ORIGINAL template via the Resource Browser command.
win.select(('resources',));win.browser.category.setCurrentIndex(win.browser.category.findData('actors'));win.browser.search.setText('businessWoman');pump();win.browser.table.selectRow(next(i for i in range(win.browser.table.rowCount()) if win.browser.table.item(i,0).data(Qt.ItemDataRole.UserRole)[0]=='businessWoman'))
with patch('rcm.editor.resource_panel.QInputDialog.getText',return_value=('T_phase5_victoria',True)):click(win.browser.clone_button)
check(win.doc.campaign['resources']['templates'][0]['base']=='businessWoman','Clone original to project without editing original')
rp.kind.setCurrentIndex(rp.kind.findData('ai_profiles'));pump();choose_resource('civilian')
with patch('rcm.editor.resource_panel.QInputDialog.getText',return_value=('AI_phase5_civilian',True)):click(rp.findChild(QPushButton,'clone_project_resource'))
prop(QDoubleSpinBox,'ai_wanderRadius',rp).setValue(0);pump();check(win.doc.campaign['resources']['ai_profiles'][0]['properties']['wanderRadius']==0,'Edit a real project AI profile')
rp.kind.setCurrentIndex(rp.kind.findData('scripts'));pump()
with patch('rcm.editor.resource_panel.QInputDialog.getText',return_value=('RCM5Actor',True)):click(rp.findChild(QPushButton,'clone_project_resource'))
# User-owned code is edited/saved explicitly by its own editor, never by Build.
java='''public class RCM5Actor extends Codex {
 public RCM5Actor() {
  CodexConsole.Print(0,0,"RCM5 custom actor script created");
  try { java.io.PrintStream log=new java.io.PrintStream(new java.io.FileOutputStream("RCM/phase5_demo/custom_actor_trace.log",true)); log.println("RCM5Actor constructor, custom template script loaded by native runtime"); log.close(); } catch(Exception error) {}
 }
}
'''
prop(QPlainTextEdit,'custom_java',rp).setPlainText(java);click(prop(QPushButton,'save_custom_java',rp))
rp.kind.setCurrentIndex(0);pump();rp.list.setCurrentRow(0);pump();combo('resource_ai','AI_phase5_civilian',rp);combo('resource_script','RCM5Actor',rp);combo('resource_model','businesswoman',rp)
check(win.doc.campaign['resources']['templates'][0]['properties']['script']=='RCM5Actor','Project template refers to own compiled Java and AI')
# Assign to Victoria through the actor template selector.
win.center_tabs.setCurrentIndex(1);win.select(('actors',0));choose_resource('T_phase5_victoria');click(prop(QPushButton,'choose_template'));check(win.doc.data['actors'][0]['template']=='T_phase5_victoria','Custom actor assigned in existing actor editor')
# Fifth NPC and second quest, using existing campaign/event controls.
win.select(('actors',));click(win.buttons['actor']);guide=win.selection[1];line('actor_id','guide');line('actor_name','Guía de Londres');combo('actor_placement','near_player');choose_resource('businessWoman');click(prop(QPushButton,'choose_template'))
win.select(('actors',guide));click(win.buttons['conversation']);ci=win.selection[1];line('conversation_id','guide');win.select(('conversations',ci,'nodes',0,'lines',0));prop(QPlainTextEdit,'line_text').setPlainText('Victoria tiene una nueva voz. Habla con ella, acepta su encargo y viaja al oeste.');pump();win.select(('actors',guide));combo('actor_conversation','guide')
panel=win.campaign_panel;click(panel.findChild(QPushButton,'add_quest'));line('campaign_id','guide_quest',panel);line('quest_title','Las voces de Londres',panel);line('quest_description','Habla con la guía para conocer la historia.',panel);line('quest_step_0','Hablar con la guía',panel);prop(QSpinBox,'quest_reward',panel).setValue(50);pump()
def event(ident,when,conv=None):
 win.center_tabs.setCurrentIndex(1);win.select(('events',));click(win.buttons['event']);idx=win.selection[1];line('event_id',ident);combo('event_when',when);combo('event_once',True)
 if conv:combo('event_conversation',conv);prop(QSpinBox,'event_result').setValue(1);pump()
 return idx
def action(idx,kind,target):win.select(('events',idx));click(win.buttons['action']);combo('action_kind',kind);combo('action_target',target)
i=event('guide_begin','scene_start');action(i,'start_quest','guide_quest')
i=event('guide_finish','conversation_ended','guide');action(i,'advance_quest','guide_quest');action(i,'complete_quest','guide_quest')
win.center_tabs.setCurrentWidget(win.debug_panel)
with patch('rcm.editor.debug_panel.QInputDialog.getText',return_value=('Template propio, quests y viaje',True)),patch('rcm.editor.debug_panel.QInputDialog.getMultiLineText',return_value=('Nueva partida. Ver Victoria junto al jugador; hablar con la guía y con Victoria; recuperar libro al oeste; regresar y entregar. Guardar/cargar antes y después del viaje.',True)):click(win.debug_panel.findChild(QPushButton,'debug_bookmark'))
win.actions['save'].trigger();pump();v=win.validate_from_ui();check(v.valid,'Full authoring integrity before build')
win.actions['build'].trigger();wait(lambda:not win.busy,120);check(win.last_build and win.last_build['status']=='compiled-unverified-in-game','GUI build includes own NOT NAI Java, compiled 45.3')
win.center_tabs.setCurrentIndex(0);wait(lambda:not win.spatial.loading and win.spatial.viewport.level is not None);check(win.spatial.viewport.isValid() and 'T_phase5_victoria' in win.spatial.viewport.level.models,'Custom actor model in real spatial viewport')
win.center_tabs.setCurrentWidget(rp);rp.kind.setCurrentIndex(0);rp.list.setCurrentRow(0);pump();win.grab().save(str(out/'templates.png'))
report=dict(successful=True,checks=checks,project=str(win.doc.path),yaml_manually_authored=False,native_engine_test=False,problems=[p.message for p in v.problems],build=win.last_build);(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='build'},ensure_ascii=False));wait(lambda:not win.spatial.loading);win.doc._saved=__import__('rcm.service',fromlist=['source_text']).source_text(win.doc.snapshot());win.close();pump()
