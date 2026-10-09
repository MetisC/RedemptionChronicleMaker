"""Native grammar, modal lifecycle and gesture completion regressions, offline."""
import copy,subprocess,zipfile
from pathlib import Path
from unittest import TestCase
from rcm.notes import encode_notes,read_notes,validate_note
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_document import CampaignDocument
from rcm.campaign_relations import graph
from test_phase9 import modern
from test_stability_revision import compile_scenario

ROOT=Path(__file__).resolve().parents[1]
NOTE={'title':'Carta de Londres','text':'Hola, visitante.\n\nLee la nota y vuelve a hablar.'}


def scenario():
    source=modern();scene=source['scenes'][0]
    scene['events']=scene['events'][:3];scene['paths']=[]
    scene['actors'][0]['template']='ST_Christof_MD'
    conversation=scene['conversations'][0];conversation.pop('prompt',None);conversation.pop('choices',None)
    conversation.update(entry='hello',nodes=[dict(id='hello',motion='gesture10',lines=[dict(text='Un saludo.')],choices=[dict(text='Salir.',result=1)]),dict(id='auto',lines=[dict(text='Automática.')],choices=[dict(text='Salir.',result=2)])])
    scene['events'] += [dict(id='read',when='object_clicked',object='book',once=False,actions=[{'show_note':copy.deepcopy(NOTE)}]),dict(id='closed',when='note_closed',actions=[{'reward_xp':7}]),dict(id='note_once',when='timer',seconds=30,once=True,actions=[{'show_note':copy.deepcopy(NOTE)}])]
    return source


class NativeNoteFormatTests(TestCase):
    def test_readback_paragraphs_and_cp1252(self):
        data=encode_notes([('R_test_t0_0',NOTE)])
        self.assertIn(b'<TEXT R_test_t0_0 none 0>\r\n<TITLE Carta de Londres>',data)
        self.assertEqual(read_notes(data),[dict(id='R_test_t0_0',**NOTE)])
        self.assertEqual(read_notes(encode_notes([('one',dict(title='Prólogo',text='Una línea\ncontinuada.\n\nOtra.'))]))[0]['text'],'Una línea continuada.\n\nOtra.')

    def test_actual_ctd_prologue_uses_the_same_grammar(self):
        from rcm.deployment import default_game
        game=default_game(ROOT)
        with zipfile.ZipFile(game/'Local_Eng.nob') as archive:data=archive.read('strings/mp_ctd.ntx')
        block=data[:data.index(b'</TEXT>')+7]
        record=read_notes(block)[0]
        self.assertEqual(record['id'],'IntroTextCTD');self.assertEqual(record['title'],'To Curse the Darkness')
        self.assertIn('\n\n',record['text'])

    def test_invalid_text_cannot_inject_native_markup(self):
        for value in [None,{},dict(title='x',text=''),dict(title='x\ny',text='x'),dict(title='x',text='</TEXT>'),dict(title='x',text='a\0b'),dict(title='x',text='😀'),dict(title='x',text='a'*12001)]:
            with self.subTest(value=str(value)[:60]),self.assertRaises(ValueError):validate_note(value)

    def test_reader_rejects_corrupt_missing_and_duplicate_blocks(self):
        good=encode_notes([('one',NOTE)])
        for data in [b'',good+good,good.replace(b'</TEXT>',b''),good.replace(b'<P 0xFFFFFFFF>',b'<P invented>'),b'outside',good.replace(b'<TITLE Carta de Londres>',b'')]:
            with self.subTest(data=data[:40]),self.assertRaises(ValueError):read_notes(data)


class NotesAuthoringTests(TestCase):
    @classmethod
    def setUpClass(cls):cls.backend=Backend(Workspace(ROOT))
    def test_object_reference_rename_delete_and_text_are_independent(self):
        source=scenario();doc=CampaignDocument.load_data(self.backend.ws,source,None)
        links=graph(source);target=('scenes',0,'objects',0)
        self.assertTrue(any(l.target==target and l.label=='object' for l in links))
        doc.rename('objects',0,'letter');self.assertEqual(doc.data['events'][-3]['object'],'letter')
        self.assertEqual(doc.data['events'][-3]['actions'][0]['show_note'],NOTE)
        self.assertTrue(self.backend.validate(doc.snapshot()).valid)
        doc.data['objects'].clear();self.assertFalse(self.backend.validate(doc.snapshot()).valid)
    def test_incompatible_modals_and_invalid_object_filters_fail(self):
        for change in [lambda s:s['events'][-3].update(object='victoria'),lambda s:s['events'][-3].update(actor='victoria'),lambda s:s['events'][-3]['actions'].append({'start_conversation':'intro'}),lambda s:s['events'][-3]['actions'].append({'show_note':NOTE}),lambda s:s['events'][-3]['actions'].append({'travel':dict(scene='west',entry='safe')})]:
            source=scenario();change(source['scenes'][0]);self.assertFalse(self.backend.validate(source).valid)
    def test_legacy_does_not_silently_accept_new_callbacks(self):
        source=scenario();source.pop('project_format');self.assertFalse(self.backend.validate(source).valid)
    def test_structural_note_corruption_rejected_before_widgets(self):
        for value in [None,'text',[],{},dict(title='title',text=1)]:
            source=scenario();source['scenes'][0]['events'][-3]['actions']=[{'show_note':value}]
            with self.assertRaisesRegex(ValueError,'Nota'):CampaignDocument.load_data(self.backend.ws,source,None)
    def test_object_can_open_existing_actor_dialogue(self):
        source=scenario();source['scenes'][0]['events'][-3]['actions']=[{'start_conversation':'intro'}]
        self.assertTrue(self.backend.validate(source).valid)
    def test_notes_real_codex_compile_and_package_registration(self):
        source=scenario();source['chronicle']['id']='note_check'
        report=self.backend.build(source)
        self.assertEqual(set(report['class_versions'].values()),{'45.3'})
        with zipfile.ZipFile(ROOT/'build/note_check/note_check.nob') as archive:
            records=read_notes(archive.read('strings/R_note_check.ntx'))
            self.assertEqual(len(records),2)
            self.assertIn(b'NTX R_note_check.ntx',archive.read('chronicles/R_note_check.nmf'))
        self.assertFalse(report.get('native_engine_test',False))
        from rcm.packages import create_package,inspect_package,read_archive
        import io
        destination='build/note_check/note_check.rcmpack'
        create_package(self.backend.ws,'note_check',destination)
        manifest,files=inspect_package(ROOT/destination)
        self.assertEqual(manifest['id'],'note_check')
        inner=read_archive(io.BytesIO(files['note_check.nob']))
        self.assertEqual(len(read_notes(inner['strings/R_note_check.ntx'])),2)


class NotesMotionRuntimeTests(TestCase):
    @classmethod
    def setUpClass(cls):
        source=scenario();backend=Backend(Workspace(ROOT));result=backend.validate(source)
        assert result.valid,[p.message for p in result.problems]
        cls.out=ROOT/'build/tests/notes_motion'
        harness='''public class StabilityHarness {
         static void check(boolean value,String why){if(!value)throw new AssertionError(why);System.out.println(why);}
         static void tick(R_p9_test_s0_Scene s){s.timer(9400,0,0,0,0);}
         public static void main(String[] args){CE.Thing player=new CE.Thing();player.template="player";CE.world.put(1,player);R_p9_test_s0_Scene s=new R_p9_test_s0_Scene();s.beginscene(1,0);int npc=CodexThing.GuidFromCastID("R_p9_test_s0_victoria"),book=CodexThing.GuidFromCastID("R_p9_test_s0_book");
          if(args[0].startsWith("motion")){
           s.clicked(npc,1,0);s.convreached(1,0,0,4000,npc);
           check(CE.world.get(npc).baseMotion==33&&CE.world.get(npc).motion==194,"persistent base beneath one-shot gesture");
           check(Math.abs(CE.motionDelay-2.3f)<.001f,"motion timer uses returned milliseconds, not line duration");
           if(args[0].equals("motion_next")){s.convreached(1,1,0,4000,npc);CE.world.get(npc).motion=117;s.timer(9500,0,0,0,0);check(CE.world.get(npc).motion==117,"old completion cannot overwrite next automatic line");return;}
           if(args[0].equals("motion_abort")){s.convended(1,true,0);tick(s);check(CE.world.get(npc).motion==33,"abort restores neutral pose");return;}
           if(args[0].equals("motion_removed")){CE.world.remove(npc);s.timer(9500,0,0,0,0);return;}
           tick(s);check(CE.world.get(npc).motion==194,"regular poll does not interrupt gesture");
           CE.world.get(npc).motion=-1;check(CE.world.get(npc).baseMotion==33,"expired action retains visible base pose");
           s.timer(9500,0,0,0,0);check(CE.world.get(npc).motion==33,"completion restores action channel to rest");return;
          }
          CE.failNote=args[0].equals("failure");CE.syncNote=args[0].equals("sync");
          s.clicked(book,1,0);check(CE.noteCalls==1,"object click opens one native note");
          if(args[0].equals("failure")){CE.failNote=false;s.clicked(book,1,0);check(CE.noteCalls==2,"failed note can retry");}
          if(args[0].equals("restore")){s.save(0);R_p9_test_s0_Scene r=new R_p9_test_s0_Scene();r.restore(0);r.restored(0);r.clicked(npc,1,0);check(CE.conversationCalls==1,"restored controller releases transient note ownership");return;}
          s.clicked(npc,1,0);check(CE.conversationCalls==0,"note prevents nested dialogue");
          s.textended(999);if(!CE.syncNote){tick(s);check(CE.xp==0,"foreign close callback ignored");}
          if(!CE.syncNote){s.textended(1);s.textended(1);check(CE.xp==0,"close continuation deferred past native teardown");}
          tick(s);check(CE.xp==7,"close callback dispatches exactly once");s.textended(1);tick(s);check(CE.xp==7,"duplicate close ignored");
          s.clicked(book,1,0);check(CE.noteCalls>=2,"repeatable object reopens the note");
         }
        }'''
        def transform(doubles):
            doubles=doubles.replace('class CE {','class CE {static int noteCalls=0;static float motionDelay=0;static boolean failNote=false,syncNote=false;')
            doubles=doubles.replace('boolean SetTimer(float s,int id){return true;}','boolean SetTimer(float s,int id){if(id>=9500)CE.motionDelay=s;return true;}')
            return doubles.replace('boolean ExecuteText(int owner,int thing,String name){return true;}','boolean ExecuteText(int owner,int thing,String name){CE.noteCalls++;if(CE.failNote)return false;if(CE.syncNote)try{getClass().getMethod("textended",int.class).invoke(this,owner);}catch(Exception e){throw new RuntimeException(e);}return true;}')
        compile_scenario(cls.out,result.project,harness,transform)
    def run_case(self,name):
        run=subprocess.run(['java','-cp',str(self.out),'StabilityHarness',name],cwd=self.out,capture_output=True,text=True)
        (self.out/(name+'.log')).write_text(run.stdout+run.stderr)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
    def test_gesture_completion_and_continuous_base_pose(self):self.run_case('motion_end')
    def test_next_line_cancels_old_gesture_completion(self):self.run_case('motion_next')
    def test_abort_releases_gesture_pose(self):self.run_case('motion_abort')
    def test_removed_actor_completion_is_safe(self):self.run_case('motion_removed')
    def test_object_note_modal_close_and_repeat(self):self.run_case('normal')
    def test_native_execute_text_failure_releases_ownership(self):self.run_case('failure')
    def test_synchronous_text_end_is_deferred(self):self.run_case('sync')
    def test_restore_clears_transient_note(self):self.run_case('restore')
