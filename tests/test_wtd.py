"""User-supplied content imports: filtering, isolation, traits and native API."""
import io
import json
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
import shutil
import struct
import tempfile
import subprocess
from unittest import TestCase
from unittest.mock import patch
import zipfile
from PySide6.QtWidgets import QApplication,QDialog,QWidget,QVBoxLayout,QPushButton
from rcm.paths import Workspace
from rcm.service import Backend,build_inputs_fingerprint
from rcm.formats import NotFile,Template,Tag
from rcm.wtd import prepare_import,import_content,manifest,ROOT as IMPORT_ROOT,ARCHIVE,local_dependencies
from rcm.catalogue import rows
from rcm.campaign_document import CampaignDocument
from rcm.editor.window import MainWindow
from rcm.editor.wtd import TraitsDialog,summary
from rcm.editor.browser import ResourceBrowser
from test_release10 import blank
from test_stability_revision import compile_scenario

ROOT=Path(__file__).resolve().parents[1]
GAME=Path(r'H:\GOG\Vampire The Masquerade - Redemption')


class WTDImport(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        cls.base=Backend(Workspace(ROOT,GAME))
        cls.good_script='DisciplineBloodHealing'
    def setUp(self):
        # Synthetic imports must not depend on the developer's installed pack.
        shared=patch('rcm.wtd.shared_dependencies',return_value={});shared.start();self.addCleanup(shared.stop)
        (ROOT/'build/tests').mkdir(parents=True,exist_ok=True);self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'build/tests');self.root=Path(self.tmp.name)
        self.ws=Workspace(self.root,GAME)
        for file in ('levels','resources','scene_hints'):self.ws.write('cache/'+file+'.json',ROOT.joinpath('cache/'+file+'.json').read_bytes())
        for name in self.base.levels['EastLondon']['scenes']:
            entry=self.base.hints[name.casefold()]['source'];relative='research/original/'+entry['archive']+'/'+entry['path'];self.ws.write(relative,ROOT.joinpath(relative).read_bytes())
        shutil.copytree(ROOT/'research/original/Chronicles',self.ws.output('research/original/Chronicles'))
        self.backend=Backend(self.ws)
    def tearDown(self):self.tmp.cleanup()
    def source(self):
        from rcm.wtd import _original
        def base_table(ext):
            entry=next(e for e in self.base.base_resources['entries'] if e['path'].lower()=='misc/game.'+ext)
            return _original(self.base.ws,entry)
        discs=list(rows(base_table('ndd').decode('cp1252')));good=list(next(t for _,t in discs if t[3]==self.good_script));good[0]='WTD_TestPower'
        bad=list(good);bad[0]='WTD_MissingPower';bad[3]='MissingModJava'
        clans=list(rows(base_table('ncd').decode('cp1252')));clan=list(clans[0][1]);clan[0]='wtd_testclan';clan[2:4]=['none','none']
        good_actor=Template('WTD_TestActor',[Tag.text(0,'businessWoman')])
        bad_actor=Template('WTD_BrokenActor',[Tag.text(0,'businessWoman'),Tag.text(11,'MissingModJava')])
        child=Template('WTD_BrokenChild',[Tag.text(0,'WTD_BrokenActor')])
        bad_ai=Template('WTD_BrokenAI',[Tag.text(0,'businessWoman'),Tag.text(56,'blackgarouFled.nai')])
        payload={'misc/game.ndd':(' '.join(good)+'\n'+' '.join(bad)+'\n').encode(), 'misc/game.ndg':base_table('ndg'),'misc/game.ncd':(' '.join(clan)+'\n').encode(),
                 'misc/Templates/_Darkness.NOT':NotFile([good_actor,bad_actor,child,bad_ai]).encode(),
                 'misc/AI/blackgarouFled.nai':b'discipline WTD_MissingPower 1\n',
                 'ui/mainMenu.nui':b'forbidden reskin','Chronicles/WTDPenthouse.nsc':b'forbidden demo','ui/TitleScreen.nui':b'forbidden title','not_in_allowlist.class':b'forbidden code'}
        path=self.root/'source.nob'
        with zipfile.ZipFile(path,'w') as z:
            for n,b in payload.items():z.writestr(n,b)
        return path
    def enable(self):
        with patch('rcm.wtd.publish_shared') as publish:
            record=import_content(self.backend,self.source());publish.assert_called_once()
        return record
    def test_no_import_is_identical_and_does_not_detect_root_mods(self):
        self.assertIsNone(manifest(self.ws));self.assertNotIn('wtd',self.backend.resources)
        self.assertEqual(self.backend.base_resources['templates'],self.backend.resources['templates'])
        browser=ResourceBrowser(self.backend);self.assertEqual(browser.category.findData('disciplines'),-1);browser.deleteLater()
        self.assertEqual(self.backend.validate(blank()).project.id,blank()['chronicle']['id'])
    def test_allowlist_dependency_filter_base_preservation_and_persistence(self):
        before=build_inputs_fingerprint(self.ws,blank());record=self.enable();self.assertNotEqual(before,build_inputs_fingerprint(self.ws,blank()))
        self.assertEqual(record['counts']['clans'],1);self.assertEqual(record['counts']['disciplines'],1)
        with zipfile.ZipFile(self.ws.output(IMPORT_ROOT+'/'+ARCHIVE)) as z:
            self.assertFalse(any(n.lower().endswith(('.nui','.nsc','.class')) for n in z.namelist()))
            self.assertNotIn('misc/AI/blackgarouFled.nai',z.namelist())
            powers={t[0] for _,t in rows(z.read('misc/game.ndd').decode())};self.assertIn('WTD_TestPower',powers);self.assertNotIn('WTD_MissingPower',powers)
            actors=[t.name for t in NotFile.read(z.read('misc/Templates/_Darkness.NOT')).templates];self.assertEqual(actors,['WTD_TestActor'])
        reopened=Backend(self.ws);self.assertEqual(manifest(self.ws)['sha256'],record['sha256']);self.assertIn('WTD_TestActor',{t['id'] for t in reopened.resources['templates']})
        self.assertNotIn('WTD_MissingPower',summary(reopened));self.assertEqual(reopened.resources['wtd']['disciplines'][-1]['id'],'WTD_TestPower')
    def test_missing_or_tampered_import_fails_instead_of_using_cached_payload(self):
        self.enable();path=self.ws.output(IMPORT_ROOT+'/'+ARCHIVE);path.write_bytes(b'tampered')
        with self.assertRaises(ValueError):manifest(self.ws)
        self.assertFalse(self.backend.validate(blank()).valid)
    def test_unsafe_zip_and_unknown_archive_leave_previous_import_intact(self):
        record=self.enable();before=self.ws.output(IMPORT_ROOT+'/'+ARCHIVE).read_bytes();path=self.root/'unsafe.nob'
        with zipfile.ZipFile(path,'w') as z:z.writestr('../escape',b'bad')
        with self.assertRaises(ValueError):prepare_import(self.ws,path,self.backend.base_resources)
        with zipfile.ZipFile(path,'w') as z:z.writestr('misc/game.ncd',b'not WTD')
        with self.assertRaises(ValueError):prepare_import(self.ws,path,self.backend.base_resources)
        path.write_bytes(b'not a NOB archive')
        with self.assertRaises(ValueError):import_content(self.backend,path)
        self.assertEqual(self.ws.output(IMPORT_ROOT+'/'+ARCHIVE).read_bytes(),before);self.assertEqual(manifest(self.ws)['sha256'],record['sha256'])
    def test_gui_only_usable_entries_trait_cancel_apply_and_single_undo(self):
        win=MainWindow(self.backend);browser=ResourceBrowser(self.backend);self.enable();browser.refresh();self.assertGreaterEqual(browser.category.findData('disciplines'),0)
        browser.category.setCurrentIndex(browser.category.findData('disciplines'));browser.search.setText('WTD_');self.assertEqual(browser.table.rowCount(),1)
        root=blank();root['scenes'][0]['actors']=[dict(id='mentor',name='Mentor',template='WTD_TestActor',transform=dict(position=[1,2,3],orientation=[0,0,0]))];win.doc=CampaignDocument(self.ws,root);win.refresh();before=win.doc.snapshot()
        dialog=TraitsDialog(win,win.doc.data['actors'][0]);dialog.add();dialog.reject();self.assertEqual(win.doc.snapshot(),before)
        dialog=TraitsDialog(win,win.doc.data['actors'][0]);dialog.clan.setCurrentIndex(dialog.clan.findData('wtd_testclan'));dialog.discipline.setCurrentIndex(dialog.discipline.findData('WTD_TestPower'));dialog.level.setValue(3);dialog.add();dialog.accept()
        self.assertEqual(dialog.result(),QDialog.DialogCode.Accepted,dialog.error.text());self.assertEqual(win.doc.data['actors'][0]['traits'],dict(clan='wtd_testclan',disciplines={'WTD_TestPower':3}));win.undo_project();self.assertEqual(win.doc.snapshot(),before)
        win.doc=None;win.close();browser.deleteLater()
    def test_settings_import_button_uses_selected_nob_and_cancel_does_not_import(self):
        from rcm.editor.wtd import import_widget
        win=MainWindow(self.backend);panel=QWidget();layout=QVBoxLayout(panel);import_widget(win,layout);button=panel.findChild(QPushButton,'settings_import_wtd')
        with patch('rcm.editor.wtd.QFileDialog.getOpenFileName',return_value=('','')):button.click()
        self.assertIsNone(manifest(self.ws))
        with patch('rcm.editor.wtd.QFileDialog.getOpenFileName',return_value=(str(self.source()),'')),patch('rcm.wtd.publish_shared') as publish:button.click();publish.assert_called_once()
        self.assertIsNotNone(manifest(self.ws));self.assertGreaterEqual(win.browser.category.findData('disciplines'),0)
        win.doc=None;win.close();panel.deleteLater()
    def test_native_traits_compile_double_fresh_only_and_no_mod_assets_in_distribution(self):
        self.enable();root=blank();root['chronicle']['id']='wtd_test'
        root['scenes'][0]['actors']=[dict(id='mentor',name='Mentor',template='WTD_TestActor',transform=dict(position=[1,2,3],orientation=[0,0,0]),traits=dict(clan='wtd_testclan',disciplines={'WTD_TestPower':3}))]
        root['scenes'][0]['events']=[dict(id='start',when='scene_start',once=True,actions=[{'spawn':'mentor'},{'set_actor_clan':dict(actor='Player',clan='wtd_testclan')},{'set_discipline':dict(actor='Player',discipline='WTD_TestPower',level=3)}])]
        validation=self.backend.validate(root);self.assertTrue(validation.valid,[p.message for p in validation.problems]);campaign=validation.project;name=campaign.scenes[0][1].prefix+'_Scene'
        harness='''public class StabilityHarness { public static void main(String[] a)throws Exception { SCENE s=new SCENE();java.lang.reflect.Method m=SCENE.class.getDeclaredMethod("spawn",int.class);m.setAccessible(true);m.invoke(s,0);if(CE.clans!=1||CE.discs!=1)throw new RuntimeException("traits not applied");m.invoke(s,0);if(CE.clans!=1||CE.discs!=1)throw new RuntimeException("traits repeated");System.out.println("WTD_TRAITS_PASS");}}'''.replace('SCENE',name)
        def doubles(text):return text.replace('class CE {','class CE {static int clans=0,discs=0;').replace('class CodexActor extends CodexThing {','class CodexActor extends CodexThing {boolean SetActorClan(String n){CE.clans++;return n.equals("wtd_testclan");}boolean SetActorDisciplineLevel(String n,int level){CE.discs++;return n.equals("WTD_TestPower")&&level==3;}')
        compile_scenario(self.root/'java',campaign,harness,doubles);result=subprocess.run(['java','-cp',str(self.root/'java'),'StabilityHarness'],capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        shutil.copytree(ROOT/'research/original/Codex.nob',self.ws.output('research/original/Codex.nob'))
        for name in ('classes.zip','ecj-3.26.0.jar'):self.ws.write('cache/toolchain/'+name,(ROOT/'cache/toolchain'/name).read_bytes())
        report=self.backend.build(root);self.assertEqual(report['status'],'compiled-unverified-in-game');self.assertTrue(all(v=='45.3' for v in report['class_versions'].values()))
        self.assertNotIn(ARCHIVE,report['distribution_files']);self.assertIn(ARCHIVE,local_dependencies(self.ws,report))
        with zipfile.ZipFile(self.ws.output('build/wtd_test/wtd_test_distribution.zip')) as z:self.assertNotIn(ARCHIVE,z.namelist())
        self.ws.output(IMPORT_ROOT+'/import.json').unlink()
        with self.assertRaises(ValueError):local_dependencies(self.ws,report)
        self.assertFalse(self.backend.validate(root).valid)
    def test_trait_event_actions_require_import_and_valid_target_and_use_real_api(self):
        root=blank();root['scenes'][0]['events']=[dict(id='reward',when='scene_start',once=True,actions=[{'set_discipline':dict(actor='Player',discipline='WTD_TestPower',level=2)}])]
        self.assertFalse(self.backend.validate(root).valid);self.enable();self.assertTrue(self.backend.validate(root).valid)
        from rcm.campaign_generator import runtime
        campaign=self.backend.validate(root).project;code=runtime(campaign,*campaign.scenes[0])[1];self.assertIn('new CodexActor(player).SetActorDisciplineLevel("WTD_TestPower",2)',code)
        for edit in (dict(actor='missing'),dict(discipline='WTD_MissingPower'),dict(level=6),dict(level=True)):
            import copy
            changed=copy.deepcopy(root);changed['scenes'][0]['events'][0]['actions'][0]['set_discipline'].update(edit);self.assertFalse(self.backend.validate(changed).valid)
    def test_shared_import_stays_under_rcm_preserves_source_and_rejects_foreign_file(self):
        from rcm.wtd import publish_shared
        source=self.source();data,record=prepare_import(self.ws,source,self.backend.base_resources);before=source.read_bytes()
        game=self.root/'fake_game';game.mkdir();ws=Workspace(self.root/'publish',game)
        with patch('rcm.deployment.game_running',return_value=False):publish_shared(ws,data,record)
        self.assertEqual((game/'RCM'/ARCHIVE).read_bytes(),data);self.assertEqual(source.read_bytes(),before);self.assertFalse((game/ARCHIVE).exists())
        (game/'RCM'/ARCHIVE).write_bytes(b'foreign')
        with patch('rcm.deployment.game_running',return_value=False),self.assertRaises(ValueError):publish_shared(ws,data,record)
    def test_profile_dependency_keeps_pack_instead_of_copying_its_templates(self):
        from rcm.profile_compatibility import compatibility_files
        from rcm.generator import zip_bytes
        game=self.root/'profiles';folder=game/'RCM/first';folder.mkdir(parents=True);(game/'Crypt').mkdir()
        wrapper=zip_bytes({'misc/templates/_own.not':NotFile([Template('R_rcm_wtd_item',[Tag.text(0,'WTDParent')])]).encode()})
        pack=zip_bytes({'misc/templates/_wtd.not':NotFile([Template('WTDParent',[Tag.text(0,'GarinolJournal')])]).encode()})
        from rcm.wtd import sha
        (folder/'first.nob').write_bytes(wrapper);(folder/ARCHIVE).write_bytes(pack);(folder/'.rcm_deployment.json').write_text(json.dumps(dict(format=1,files={'first.nob':sha(wrapper),ARCHIVE:sha(pack)})))
        (game/'Crypt/player.npf').write_bytes(struct.pack('<II',0x1e,1)+b'R_rcm_wtd_item\0'.ljust(32,b'\0'))
        files=compatibility_files(game,zip_bytes({}));self.assertEqual(files[ARCHIVE],pack)
        with zipfile.ZipFile(io.BytesIO(files['rcm_compat.nob'])) as z:self.assertEqual([t.name for t in NotFile.read(z.read('misc/Templates/_rcm_compat.not')).templates],['R_rcm_wtd_item'])
