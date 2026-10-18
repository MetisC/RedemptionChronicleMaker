"""Original static props: identity, reversible flags, transitions and real API compile."""
import json
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
import tempfile
from unittest import TestCase
from PySide6.QtWidgets import QApplication,QDialog,QComboBox
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_document import CampaignDocument
from rcm.original_objects import catalogue,selector,targets
from rcm.campaign_generator import runtime
from rcm.editor.window import MainWindow
from rcm.editor.original_objects import OriginalObjectPicker,PassageDialog
from test_release10 import blank
from test_stability_revision import compile_scenario

ROOT=Path(__file__).resolve().parents[1]


class OriginalObjects(TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT/'build/tests').mkdir(parents=True,exist_ok=True)
        cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption')));cls.backend.safe_mode=True
        cls.rows=catalogue(cls.backend,'EastLondon');cls.target=selector(next(r for r in cls.rows if r['template'].casefold()=='ironbench'))
    def source(self,operation='hide'):
        root=blank();root['scenes'][0]['events']=[dict(id='original',when='scene_start',once=True,actions=[{'control_original':dict(self.target,operation=operation)}])];return root
    def valid(self,root):
        result=self.backend.validate(root);self.assertTrue(result.valid,[p.message for p in result.problems if p.severity=='ERROR']);return result.project
    def test_catalogue_uses_static_scene_not_replaced_story_layout_and_canonical_template_case(self):
        self.assertGreater(len(self.rows),10);self.assertTrue(all(r['origin'].lower()=='l1_east.nsd' and r['level']=='EastLondon' for r in self.rows))
        self.assertEqual(self.target['template'],'ironBench');self.assertIn('position',self.target)
        self.assertFalse(any(r['template'].lower()=='bobbie' for r in self.rows))
    def test_validation_binds_level_rejects_actors_missing_identity_and_unsafe_frames(self):
        self.valid(self.source())
        motion=self.source();motion['scenes'][0]['events'][0]['actions'][0]['control_original'].update(operation='frame',frame=1,parameter=150);self.valid(motion)
        for edit in (lambda v:v.update(template='businessWoman'),lambda v:v.update(level='WestLondon'),lambda v:v.pop('position'),lambda v:v.update(operation='all'),lambda v:v.update(operation='frame',frame=256,parameter=150),lambda v:v.update(position=[float('nan'),0,0])):
            root=self.source();edit(root['scenes'][0]['events'][0]['actions'][0]['control_original']);self.assertFalse(self.backend.validate(root).valid)
    def test_flags_are_deduplicated_per_target_and_absent_feature_does_not_inject_runtime(self):
        root=self.source();scene=root['scenes'][0];scene['events'].append(dict(id='restore',when='timer',seconds=1,once=True,actions=[{'control_original':dict(self.target,operation='restore')}]))
        campaign=self.valid(root);self.assertEqual(len([k for k in campaign.reserved if k.startswith('original/')]),7);self.assertEqual(len(targets(campaign.scenes[0][0])),1)
        unused=self.valid(blank());self.assertNotIn('originalApply',runtime(unused,*unused.scenes[0])[1])
    def test_gui_picker_passage_zone_travel_cancel_and_single_undo(self):
        win=MainWindow(self.backend);win.doc=CampaignDocument(self.backend.ws,blank());win.refresh();before=win.doc.snapshot()
        picker=OriginalObjectPicker(win,self.target);picker.accept();self.assertEqual(picker.result(),QDialog.DialogCode.Accepted);self.assertEqual(picker.selection,self.target);picker.deleteLater()
        cancelled=PassageDialog(win,self.target);cancelled.reject();self.assertEqual(win.doc.snapshot(),before);cancelled.deleteLater()
        dialog=PassageDialog(win,self.target);dialog.operation.setCurrentIndex(dialog.operation.findData('hide'));kind=dialog.actions.scroll.widget().findChild(QComboBox,'action_kind');kind.setCurrentIndex(kind.findData('travel'));destination=dialog.actions.scroll.widget().findChild(QComboBox,'travel_scene');destination.setCurrentIndex(destination.findData('home'));entry=dialog.actions.scroll.widget().findChild(QComboBox,'travel_entry');entry.setCurrentIndex(entry.findData('start'));dialog.accept()
        self.assertEqual(dialog.result(),QDialog.DialogCode.Accepted,dialog.error.text());after=win.doc.snapshot();self.valid(after)
        event=after['scenes'][0]['events'][0];self.assertEqual(event['actions'][-1],{'travel':{'scene':'home','entry':'start'}});self.assertEqual(after['scenes'][0]['events'][0]['when'],'object_clicked');self.assertEqual(after['scenes'][0]['triggers'],[])
        win.undo_project();self.assertEqual(win.doc.snapshot(),before);dialog.deleteLater();win.doc=None;win.close()
    def test_real_codex_compilation_and_java_double_identity_restore_removal_reentry(self):
        root=self.source();scene=root['scenes'][0]
        for ident,op in [('restore','restore'),('remove','remove')]:scene['events'].append(dict(id=ident,when='timer',seconds=500,once=False,actions=[{'control_original':dict(self.target,operation=op)}]))
        campaign=self.valid(root)
        prefix=campaign.scenes[0][1].prefix;name=prefix+'_Scene';position=','.join(str(float(v))+'f' for v in self.target['position'])
        harness='''import java.lang.reflect.*;
public class StabilityHarness {
 static void check(boolean ok,String m){if(!ok)throw new RuntimeException(m);}
 public static void main(String[] args)throws Exception{
 CE.world.clear();SCENE s=new SCENE();Method apply=SCENE.class.getDeclaredMethod("originalApply",int.class,int.class,int.class,float.class,boolean.class);apply.setAccessible(true);
 int object=CE.make("ironBench",new float[]{POS});CE.world.get(object).prop=true;CE.world.get(object).thingFlags=8192|16384|32;
 int other=CE.make("ironBench",new float[]{99999,0,0});CE.world.get(other).prop=true;
 check((Boolean)apply.invoke(s,0,0,0,1.0f,true),"hide");check(CE.world.get(object).renderFlags==2 && (CE.world.get(object).thingFlags&512)!=0,"hidden with no collision");check(CE.world.get(other).renderFlags==0,"unrelated duplicate template untouched");
 check((Boolean)apply.invoke(s,0,1,0,1.0f,true),"restore");check(CE.world.get(object).renderFlags==0 && CE.world.get(object).thingFlags==(8192|16384|32),"restore exact owned bits");
 int duplicate=CE.make("ironBench",new float[]{POS});CE.world.get(duplicate).prop=true;check(!(Boolean)apply.invoke(s,0,2,0,1.0f,true),"ambiguous removal rejected");check(CE.valid(object)&&CE.valid(duplicate),"ambiguity changed nothing");CE.world.remove(duplicate);
 CE.world.get(object).frames=true;CE.world.get(object).base=CE.world.get(object).pos.clone();check((Boolean)apply.invoke(s,0,3,1,150.0f,true),"open frame door");check(CE.world.get(object).pos[0]>50000,"motion occurred");check((Boolean)apply.invoke(s,0,3,0,150.0f,true),"close identifies moved door by original frame zero");check(!(Boolean)apply.invoke(s,0,3,2,150.0f,true),"absent frame rejected");check((Boolean)apply.invoke(s,0,4,1,150.0f,true),"pivot API");CE.world.get(object).frames=false;
 check((Boolean)apply.invoke(s,0,0,0,1.0f,true),"hide again");CE.world.get(object).renderFlags=0;CE.world.get(object).thingFlags=32|8192|16384;SCENE reentered=new SCENE();Method again=SCENE.class.getDeclaredMethod("originalReapply");again.setAccessible(true);again.invoke(reentered);check(CE.world.get(object).renderFlags==2,"reentry reapplies flag state");
 check((Boolean)apply.invoke(reentered,0,2,0,1.0f,true),"remove");check(!CE.valid(object)&&CE.valid(other),"remove exact target");check((Boolean)apply.invoke(reentered,0,2,0,1.0f,true),"remove idempotent");check(!(Boolean)apply.invoke(reentered,0,1,0,1.0f,true),"cannot recreate removed static script");
 CE.world.get(other).pos=new float[]{POS};CE.world.get(other).location=99;check(!(Boolean)apply.invoke(new SCENE(),0,0,0,1.0f,true),"different location rejected");System.out.println("ORIGINAL_OBJECTS_PASS");}}
'''.replace('SCENE',name).replace('POS',position)
        def doubles(text):
            text=text.replace('static class Thing {','static class Thing { boolean prop=false,frames=false; float[] base; int renderFlags=0,thingFlags=0;')
            text=text.replace('static boolean IsPropGuid(int g){return false;}','static boolean IsPropGuid(int g){return CE.valid(g)&&CE.world.get(g).prop;}')
            constants='static final int THING_RENDERFLAG_DONTRENDER=2,THING_FLAG_DISABLECOLLIDE=512,THING_FLAG_VISBLOCK=8192,THING_FLAG_CAMERABLOCK=16384;'
            text=text.replace('class Codex {','class Codex {'+constants)
            text=text.replace('class CodexThing extends Codex {','class CodexThing extends Codex { int GetRenderFlags(){return CE.world.get(guid).renderFlags;} int SetRenderFlags(int f){return CE.world.get(guid).renderFlags|=f;} int ClearRenderFlags(int f){return CE.world.get(guid).renderFlags&=~f;} int GetThingFlags(){return CE.world.get(guid).thingFlags;} boolean HasFrames(){return CE.world.get(guid).frames;} int GetNumFrames(){return HasFrames()?2:0;} float[] GetFramePosition(int f){return CE.world.get(guid).base;} boolean MoveToFrame(int f,float p){CE.world.get(guid).pos=f==0?CE.world.get(guid).base.clone():new float[]{60000,0,0};return true;} boolean RotatePivot(int f,float p){return true;}')
            text=text.replace('int ClearThingFlags(int f){return f;}int SetThingFlags(int f){return f;}','int ClearThingFlags(int f){return CE.world.get(guid).thingFlags&=~f;}int SetThingFlags(int f){return CE.world.get(guid).thingFlags|=f;}')
            return text
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as d:
            out=Path(d);compile_scenario(out,campaign,harness,doubles)
            import subprocess
            run=subprocess.run(['java','-cp',str(out),'StabilityHarness'],capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stdout+run.stderr);self.assertIn('ORIGINAL_OBJECTS_PASS',run.stdout)
        # Build with the actual classes.zip/Codex API as a distinct verification.
        root['chronicle']['id']='original_test';report=self.backend.build(root);self.assertEqual(report['status'],'compiled-unverified-in-game');self.assertFalse(report['geometry_in_package'])
        ROOT.joinpath('research/runtime_test/original_objects_compile.json').write_text(json.dumps(dict(class_versions=report['class_versions'],native_engine_test=False),indent=2))
