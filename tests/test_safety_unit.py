"""Fast tests use synthetic data only; no game, catalogue, Qt or compiler."""
from pathlib import Path
import io
import json
import os
import tempfile
import unittest
import zipfile
import yaml
from unittest.mock import patch
from rcm.paths import Workspace
from rcm.packages import archive_path,read_archive,verify_manifest,records,inspect_package,install_package,uninstall_package
from rcm.generator import zip_bytes
from rcm.file_transaction import replace_files
from rcm.input_limits import parse_source,check_data
from rcm.build_transaction import StagedWorkspace,clean_build,failed_report

ROOT=Path(__file__).resolve().parents[1]

def package(ident='unit_demo',custom=False,version='0.1.0',dependencies=None,templates=None):
    files={ident+'.nob':zip_bytes({'strings/_unit.nls':b'unit Test\r\n'}),'codex/'+('Own.class' if custom else 'R_'+ident+'_Scene.class'):bytes.fromhex('cafebabe0003002d')+b'fixture'}
    manifest=dict(format=1,kind='chronicle',id=ident,name='Prueba',version=version,custom_code=custom,dependencies=dependencies or [],templates=templates or [],files=records(files))
    files['manifest.json']=json.dumps(manifest).encode();return zip_bytes(files)

class SafetyUnitTests(unittest.TestCase):
    def setUp(self):
        (ROOT/'build/tests').mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'build/tests');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.ws=Workspace(self.root)
    def test_archive_path_bad_windows_and_traversal(self):
        for name in ['../bad','/absolute','a/../bad','a//bad','C:/bad','a\\b','a/CON.txt','a/NUL','a.','a ','a:*','a/?','a/\x01','a/COM1.dll','a/./b','']:
            with self.subTest(name=name),self.assertRaises(ValueError):archive_path(name)
        self.assertEqual(str(archive_path('codex/Test.class')),'codex/Test.class')
    def test_zip_duplicates_casefold(self):
        data=io.BytesIO()
        with zipfile.ZipFile(data,'w') as z:z.writestr('File',b'1');z.writestr('file',b'2')
        with self.assertRaises(ValueError):read_archive(io.BytesIO(data.getvalue()))
    def test_zip_symlink_and_directory_rejected(self):
        for info in [zipfile.ZipInfo('dir/'),zipfile.ZipInfo('link')]:
            if info.filename=='link':info.external_attr=0o120777<<16
            data=io.BytesIO()
            with zipfile.ZipFile(data,'w') as z:z.writestr(info,b'target')
            with self.assertRaises(ValueError):read_archive(io.BytesIO(data.getvalue()))
    def test_zip_entry_limit(self):
        with self.assertRaisesRegex(ValueError,'grande'):read_archive(io.BytesIO(zip_bytes({str(i):b'' for i in range(2001)})))
    def test_manifest_corrupt_hash_and_type(self):
        f=read_archive(io.BytesIO(package()));f['unit_demo.nob']+=b'bad'
        with self.assertRaises(ValueError):verify_manifest(f,'chronicle')
        for payload in [b'[]',b'null',b'{}',b'bad']:
            with self.assertRaises(ValueError):verify_manifest({'manifest.json':payload},'chronicle')
    def test_manifest_invalid_dependencies(self):
        for deps in [[{'id':'unit_demo','version':'0.1.0'}],[{}],['bad'],[{'id':'ok','version':'latest'}]]:
            with self.assertRaises(ValueError):inspect_package(io.BytesIO(package(dependencies=deps)))
    def test_custom_class_must_be_declared(self):
        f=read_archive(io.BytesIO(package(custom=True)));m=json.loads(f['manifest.json']);m['custom_code']=False;f['manifest.json']=json.dumps(m).encode()
        with self.assertRaises(ValueError):inspect_package(io.BytesIO(zip_bytes(f)))
    def test_geometry_package_is_rejected(self):
        f=read_archive(io.BytesIO(package()));f['unit_demo.nob']=zip_bytes({'level.nil':b'original'})
        m=json.loads(f['manifest.json']);m['files']=records({k:v for k,v in f.items() if k!='manifest.json'});f['manifest.json']=json.dumps(m).encode()
        with self.assertRaises(ValueError):inspect_package(io.BytesIO(zip_bytes(f)))
    def test_package_class_version_rejected(self):
        f=read_archive(io.BytesIO(package()));f['codex/R_unit_demo_Scene.class']=bytes.fromhex('cafebabe00000034');m=json.loads(f['manifest.json']);m['files']=records({k:v for k,v in f.items() if k!='manifest.json'});f['manifest.json']=json.dumps(m).encode()
        with self.assertRaises(ValueError):inspect_package(io.BytesIO(zip_bytes(f)))
    def test_transaction_write_failure_restores_and_cleans(self):
        a=self.ws.write('a',b'old');b=self.ws.output('b');replace=os.replace
        def failing(src,dest):
            if dest==b:raise OSError('disk full fixture')
            return replace(src,dest)
        with patch('rcm.file_transaction.os.replace',side_effect=failing),self.assertRaises(OSError):replace_files({a:b'new',b:b'new'},[],self.root/'backup.zip',self.root,self.ws.output)
        self.assertEqual(a.read_bytes(),b'old');self.assertFalse(b.exists());self.assertFalse(list(self.root.glob('*.rcm-tmp')))
    def test_transaction_obsolete_failure_restores(self):
        a=self.ws.write('a',b'A');b=self.ws.write('b',b'B');unlink=Path.unlink
        def failing(path,*args,**kwargs):
            if path==b:raise OSError('locked fixture')
            return unlink(path,*args,**kwargs)
        with patch.object(Path,'unlink',failing),self.assertRaises(OSError):replace_files({},[a,b],self.root/'backup.zip',self.root,self.ws.output)
        self.assertEqual(a.read_bytes(),b'A');self.assertEqual(b.read_bytes(),b'B')
    def test_transaction_preflight_does_not_touch_prior_files(self):
        a=self.ws.write('a',b'A');self.ws.write('b.rcm-tmp',b'user')
        with self.assertRaises(ValueError):replace_files({a:b'new',self.root/'b':b'new'},[],self.root/'backup.zip',self.root,self.ws.output)
        self.assertEqual(a.read_bytes(),b'A')
    def test_workspace_hardlink_blocked(self):
        a=self.ws.write('a',b'A');os.link(a,self.root/'b')
        with self.assertRaises(ValueError):self.ws.write('b',b'changed')
        self.assertEqual(a.read_bytes(),b'A')
    def test_input_depth_cycles_and_types(self):
        nested={};v=nested
        for _ in range(35):v['a']={};v=v['a']
        cycle=[];cycle.append(cycle)
        for data in [nested,cycle,{1:'bad'},{'bad':object()}]:
            with self.assertRaises(ValueError):check_data(data)
    def test_yaml_duplicates_aliases_oversized_and_deep(self):
        for source in ['a: 1\na: 2','a: &x []\nb: *x','a: '+('x'*2097153),'a: '+('['*1500)+(']'*1500)]:
            with self.assertRaises((ValueError,yaml.YAMLError)):parse_source(source)
    def test_staging_publish_clean_preserves_unknown(self):
        self.ws.write('build/demo/user.txt',b'KEEP');s=StagedWorkspace(self.ws,'demo')
        s.write('build/demo/a',b'A');s.write('build/demo/build_report.json','{}');report=s.publish({'status':'compiled-unverified-in-game'});s.close()
        self.assertTrue(report['generated_artifacts']);failed_report(self.ws,{'chronicle':{'id':'demo'}},'bad');removed=clean_build(self.ws,'demo')
        self.assertIn('build/demo/a',removed);self.assertEqual((self.root/'build/demo/user.txt').read_bytes(),b'KEEP')
    def test_clean_forged_path_rejected_before_deletion(self):
        a=self.ws.write('build/demo/a',b'A');self.ws.write('build/demo/build_report.json',json.dumps({'generated_artifacts':['build/demo/a','../danger']}))
        with self.assertRaises(ValueError):clean_build(self.ws,'demo')
        self.assertTrue(a.exists())
    def test_clean_internal_traversal_cannot_delete_another_build(self):
        kept=self.ws.write('build/precious',b'KEEP');self.ws.write('build/demo/build_report.json',json.dumps({'generated_artifacts':['build/demo/../precious']}))
        with self.assertRaises(ValueError):clean_build(self.ws,'demo')
        self.assertEqual(kept.read_bytes(),b'KEEP')
    def test_corrupt_zip_friendly_error(self):
        with self.assertRaisesRegex(ValueError,'corrupto'):read_archive(io.BytesIO(b'not ZIP'))
    def test_shortcut_metadata_and_truncation(self):
        import struct
        from rcm.shortcut import read_shortcut
        header=bytearray(76);struct.pack_into('<I',header,0,76);struct.pack_into('<I',header,20,16|32|128)
        data=bytes(header)
        for value in [r'H:\Game',r'-user RCM\demo']:data+=struct.pack('<H',len(value))+value.encode('utf-16-le')
        path=self.ws.write('test.lnk',data);self.assertEqual(read_shortcut(path)['arguments'],r'-user RCM\demo')
        for n in [0,20,75,len(data)-1]:
            path.write_bytes(data[:n])
            with self.assertRaises(ValueError):read_shortcut(path)
    def game(self):
        game=self.root/'game';game.mkdir();(game/'Vampire.exe').write_bytes(b'fixture');(game/'Resource.nob').write_bytes(b'fixture');return game
    def test_package_install_update_uninstall_preserves_user_file(self):
        game=self.game();path=self.ws.write('demo.rcmpack',package())
        with patch('rcm.packages.configured_game',return_value=game),patch('rcm.packages.game_running',return_value=False):
            install_package(self.ws,path,True);extra=game/'RCM/unit_demo/my_save';extra.write_bytes(b'KEEP');path.write_bytes(package(version='0.2.0'));install_package(self.ws,path,True);uninstall_package(self.ws,'unit_demo')
            self.assertEqual(extra.read_bytes(),b'KEEP');self.assertFalse((extra.parent/'unit_demo.nob').exists())
        self.assertEqual((game/'Resource.nob').read_bytes(),b'fixture')
    def test_install_custom_consent_and_modified_files_block(self):
        game=self.game();path=self.ws.write('demo.rcmpack',package(custom=True))
        with patch('rcm.packages.configured_game',return_value=game),patch('rcm.packages.game_running',return_value=False):
            with self.assertRaises(ValueError):install_package(self.ws,path)
            install_package(self.ws,path,True);(game/'RCM/unit_demo/unit_demo.nob').write_bytes(b'user change')
            with self.assertRaises(ValueError):install_package(self.ws,path,True)
            with self.assertRaises(ValueError):uninstall_package(self.ws,'unit_demo')
    def test_install_collision_and_dependency_block(self):
        game=self.game();a=self.ws.write('a.rcmpack',package(templates=['Unique']));b=self.ws.write('b.rcmpack',package('other',templates=['unique']))
        with patch('rcm.packages.configured_game',return_value=game),patch('rcm.packages.game_running',return_value=False):
            install_package(self.ws,a,True)
            with self.assertRaises(ValueError):install_package(self.ws,b,True)
            b.write_bytes(package('other',dependencies=[{'id':'unit_demo','version':'9.0.0'}]))
            with self.assertRaises(ValueError):install_package(self.ws,b,True)
    def test_install_running_game_block(self):
        game=self.game();path=self.ws.write('demo.rcmpack',package())
        with patch('rcm.packages.configured_game',return_value=game),patch('rcm.packages.game_running',return_value=True),self.assertRaises(ValueError):install_package(self.ws,path)
        self.assertFalse((game/'RCM').exists())
    def test_not_random_unknown_tags_property_roundtrip(self):
        import random
        from rcm.formats import NotFile,Template,Tag
        rng=random.Random(6108)
        for _ in range(100):
            templates=[Template('t'+str(i),[Tag(rng.randrange(1000),rng.randbytes(32)) for _ in range(rng.randrange(10))],rng.randbytes(8)+b'\0') for i in range(rng.randrange(1,12))]
            raw=NotFile(templates,trailing=rng.randbytes(12)).encode();self.assertEqual(NotFile.read(raw).encode(),raw)
    def test_story_graph_real_transitions_cycles_dead_and_orphan(self):
        from rcm.story_graph import conversation_graph,scene_reachability
        root={'entry':'a','scenes':[{'id':'a','events':[{'actions':[{'jump':'b'}]}]},{'id':'b','events':[]},{'id':'c','events':[]}]}
        self.assertEqual(scene_reachability(root),{'c'})
        conv={'entry':'a','nodes':[{'id':'a','choices':[{'goto':'b'},{'result':1}]},{'id':'b','choices':[{'goto':'a'}]},{'id':'c','choices':[{'goto':'c'}]}]};graph=conversation_graph(conv);indexed={n['id']:n for n in graph['nodes']};self.assertTrue(indexed['b']['cycle']);self.assertFalse(indexed['a']['dead']);self.assertTrue(indexed['c']['unreachable']);self.assertTrue(indexed['c']['dead'])
    def test_generated_formats_broken_links_are_rejected(self):
        from rcm.output_validation import verify_output
        from rcm.formats import Scene,NotFile,Template
        base={'chronicles/demo.nsc':b'location a level.nil demo.nsd map label 0x20\r\nmetafile demo.nmf\r\n','chronicles/demo.nmf':b'NOT _demo.not\r\nNLS demo.nls\r\nNVO demo.nvo\r\n','scenes/demo.nsd':Scene('demo','level.nod',[]).encode(),'misc/_demo.not':NotFile([Template('own',[])]).encode(),'strings/demo.nls':b'key Text\r\n','strings/demo.nvo':b'voice silence Text\r\n','sounds/silence.wav':b'fixture','conversations/demo.nco':b'CONVERSATION: demo 0\r\nEVENT: ev_start\r\nLINE: voice own\r\nANSWERRETURN: voice 1\r\n'}
        catalogue={'entries':[{'path':'level.nil'}]};report={'chronicle':'demo','class_versions':{},'distribution_files':{}}
        self.ws.write('build/demo/demo.nob',zip_bytes(base));self.assertGreater(verify_output(self.ws,report,catalogue)['files_checked'],0)
        broken=[('strings/demo.nls',b'key A\r\nkey B\r\n'),('strings/demo.nvo',b'voice missing Text\r\n'),('chronicles/demo.nmf',b'NOT missing.not\r\n'),('conversations/demo.nco',b'EVENT: ev_start\r\nANSWERGOTO: voice ev_missing\r\n'),('conversations/demo.nco',b'EVENT: ev_start\r\nANSWERRETURN: voice abc\r\n'),('conversations/demo.nco',b'EVENT: ev_start\r\nLINE: missing own\r\n'),('scenes/demo.nsd',b'bad'),('misc/_demo.not',b'bad'),('quests/demo.nqd',b'QUEST 0 0 missing other marker 0\r\n')]
        for name,data in broken:
            with self.subTest(name=name,data=data):
                payload=dict(base);payload[name]=data;self.ws.write('build/demo/demo.nob',zip_bytes(payload))
                with self.assertRaises(ValueError):verify_output(self.ws,report,catalogue)
        # An invented 640-byte limit is unsupported by native evidence.
        large = dict(base)
        large['strings/demo.nls'] = ('key ' + ('x' * 1000) + '\r\n').encode('cp1252')
        self.ws.write('build/demo/demo.nob', zip_bytes(large))
        verify_output(self.ws, report, catalogue)
        # Character inventory restoration precedes chronicle selection.
        late = dict(base)
        late['misc/demo.not'] = late.pop('misc/_demo.not')
        late['chronicles/demo.nmf'] = late['chronicles/demo.nmf'].replace(b'_demo.not', b'demo.not')
        self.ws.write('build/demo/demo.nob', zip_bytes(late))
        with self.assertRaisesRegex(ValueError, 'restaurar personajes'):
            verify_output(self.ws, report, catalogue)
    def test_newer_package_requirement_rejected(self):
        files=read_archive(io.BytesIO(package()));m=json.loads(files['manifest.json']);m['requires_rcm']='9.0.0';files['manifest.json']=json.dumps(m).encode()
        with self.assertRaisesRegex(ValueError,'otra versión'):inspect_package(io.BytesIO(zip_bytes(files)))

