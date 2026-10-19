"""Strict author intent: original fields, optional payloads, no native gameplay."""
import copy,json,struct,tempfile,zipfile
from pathlib import Path
from unittest import TestCase
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.environment_fields import patch,read,validate
from rcm.formats import NotFile,Scene,cstring
from rcm.project_resources import prepare
from rcm.not_library import encode_property
from rcm.treasure import catalogue
from test_release10 import blank

ROOT=Path(__file__).resolve().parents[1]


class StrictAuthoring(TestCase):
    @classmethod
    def setUpClass(cls):cls.ws=Workspace(ROOT);cls.backend=Backend(cls.ws)
    def test_environment_patch_only_changes_proven_selected_fields(self):
        original=(ROOT/'research/original/Resource.nob/scenes/EAST_28_1.nsd').read_bytes()[-176:]
        self.assertEqual(patch(original,{},self.backend.resources),original)
        value=dict(music='London_Hub',music_volume=41,ambient='',ambient_volume=0,fog=dict(mode='linear',color=[10,20,30],start=300,end=1700),zclip=1800)
        changed=patch(original,value,self.backend.resources);fields=read(changed)
        self.assertEqual(fields['music'],'London_Hub.mp3');self.assertEqual(fields['music_volume'],41);self.assertEqual(fields['fog_color'],[10,20,30]);self.assertEqual(fields['zclip'],1800)
        for a,b in [(64,68),(76,80),(108,176)]:self.assertEqual(changed[a:b],original[a:b])
        for value in [dict(eax=3),dict(zclip=float('nan')),dict(music_volume=True),dict(fog=dict(mode='linear',color=[0,1,2],start=3,end=2))]:
            with self.assertRaises(ValueError):validate(value,self.backend.resources)
    def test_resource_only_fingerprint_does_not_reload_unrelated_level_catalogues(self):
        from unittest.mock import patch as mock_patch
        from rcm.service import build_inputs_fingerprint
        original=Path.read_text;forbidden={self.ws.output('cache/levels.json'),self.ws.output('cache/scene_hints.json')}
        def read(path,*args,**kwargs):
            if path in forbidden:raise AssertionError('Resource-only cache reloaded geometry/scene catalogues')
            return original(path,*args,**kwargs)
        with mock_patch.object(Path,'read_text',read):self.assertEqual(len(build_inputs_fingerprint(self.ws,dict(chronicle=dict(id='a',name='A'),resources={}))),64)
    def test_environment_original_corpus_and_sky_unknown_preservation(self):
        rows=json.loads((ROOT/'research/embrace_strict_parity/environment_corpus.json').read_text())
        for row in rows:
            tail=(ROOT/'research/original/Resource.nob'/row['path']).read_bytes()[-176:]
            self.assertEqual(patch(tail,{},self.backend.resources),tail)
            self.assertEqual(read(tail)['fog_type'],row['ints'][4])
    def test_treasure_type_catalogue_and_container_restriction(self):
        self.assertEqual(encode_property('treasure_class',228).id,92)
        for value in [True,-1,256,'228']:
            with self.assertRaises(ValueError):encode_property('treasure_class',value)
        self.assertEqual(len(catalogue(self.ws,self.backend.resources)),160)
        root=blank();root['resources']['templates']=[dict(id='T_box',base='businessWoman',properties={'treasure_class':228})]
        self.assertFalse(self.backend.validate(root).valid)
    def test_instance_overrides_keep_source_and_other_actors_unchanged(self):
        root=blank();s=root['scenes'][0];s['actors']=[dict(id='mentor',name='Elena',template='Anezka',transform=dict(position=[-176,-612,384],orientation=[0,0,180]),overrides=dict(foley='npcGeneralFemale',hover_text='La mentora'))]
        before=copy.deepcopy(root);lowered,catalog,payload,info=prepare(self.ws,root,self.backend.original_resources)
        self.assertEqual(root,before);self.assertNotEqual(lowered['scenes'][0]['actors'][0]['template'],'Anezka')
        library=NotFile.read(payload[info['not_path']]);self.assertEqual(len(library.templates),1);self.assertEqual(cstring(library.templates[0].tags[0].value),'Anezka')
        tags={t.id:t for t in library.templates[0].tags};self.assertEqual(cstring(tags[6].value),'npcGeneralFemale.nag');self.assertNotIn(92,tags)
        self.assertTrue(self.backend.validate(root).valid)
    def test_real_build_packages_fog_treasure_description_and_silence(self):
        root=blank();root['chronicle']['id']='strict_test';s=root['scenes'][0]
        s['level'].update(environment=dict(music='',ambient='',fog=dict(mode='linear',color=[20,30,40],start=300,end=1800),zclip=1900),sky={'model':'','animation':''})
        s['objects']=[dict(id='box',name='Barril',template='container_barrel1',transform=dict(position=[-176,-612,384],orientation=[0,0,0]),overrides=dict(treasure_class=228,hover_text='Un barril viejo'))]
        s['events']=[dict(id='arrival',when='scene_start',actions=[{'spawn':'box'}])]
        report=self.backend.build(root);self.assertTrue(all(v=='45.3' for v in report['class_versions'].values()))
        build=ROOT/'build/strict_test'
        with zipfile.ZipFile(build/'strict_test.nob') as z:
            tail=Scene.read(z.read('scenes/R_strict_test_s0.nsd')).environment[-176:];self.assertEqual(read(tail)['zclip'],1900)
            self.assertTrue(any(b'Un barril viejo' in z.read(n) for n in z.namelist() if n.endswith('.nls')))
            own=[z.read(n) for n in z.namelist() if n.endswith('_custom.not')][0]
            self.assertTrue(any(t.id==92 and struct.unpack_from('<I',t.value)[0]==228 for row in NotFile.read(own).templates for t in row.tags))
        code=(build/'generated/java/R_strict_test_s0_Scene.java').read_text(encoding='utf8') if (build/'generated/java/R_strict_test_s0_Scene.java').exists() else (build/'generated/R_strict_test_s0_Scene.java').read_text(encoding='utf8')
        self.assertIn('CodexSound.StopMusic();',code);self.assertIn('CodexSound.StopAmbient();',code)
        self.assertIn('GetThingType()==THING_TYPE_CONTAINER',code)
        from rcm.packages import export_project,import_project
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            p=Path(tmp);export_project(self.ws,root,p/'project.zip');doc=import_project(self.ws,p/'project.zip',p/'imported')
            self.assertEqual(doc.snapshot()['scenes'][0]['objects'][0]['overrides'],s['objects'][0]['overrides'])
    def test_native_constructor_metadata_comes_from_literal_classfiles(self):
        from rcm.native_scripts import catalogue
        rows=catalogue(self.ws,self.backend.resources)
        self.assertEqual(len(rows),380);self.assertEqual(sum(r['literal_metadata'] for r in rows.values()),376)
        self.assertEqual(rows['ClassBobbing']['parameters'][1],dict(type='float',native_type=2,label='Min speed',default=8.0))
        self.assertEqual(rows['ActorAIOff_TriggerOn']['parameters'][0]['type'],'actor')
    def test_explicit_script_removal_does_not_inherit_custom_dispatch(self):
        from rcm.native_scripts import catalogue as constructors
        script=next(k for k,r in constructors(self.ws,self.backend.resources).items() if not r['parameters'])
        root=blank();root['resources']['templates']=[dict(id='Scripted',base='Anezka',properties=dict(script=script)),dict(id='Silent',base='Scripted',properties=dict(script=''))]
        _,catalog,_,_=prepare(self.ws,root,self.backend.original_resources)
        self.assertEqual(next(t for t in catalog['templates'] if t['id']=='Scripted')['custom_script'],script)
        self.assertFalse(next(t for t in catalog['templates'] if t['id']=='Silent').get('custom_script'))
    def test_custom_constructor_metadata_requires_real_codex_subclass_and_signature(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            path=Path(tmp)/'StrictOwner.java';root=blank();root['chronicle']['id']='custom_meta';root['scenes']=root['scenes'][:1]
            root['resources']['scripts']=[dict(id='StrictOwner',source=path.relative_to(ROOT).as_posix(),parameters=[dict(type='integer',label='Value')])]
            for parent,kind,message in [('', 'int','heredar de Codex'),(' extends Codex','float','Constructor Java')]:
                path.write_text('public class StrictOwner'+parent+' {public StrictOwner('+kind+' v){}}')
                with self.assertRaisesRegex(ValueError,message):self.backend.build(root)
            path.write_text('public class StrictOwner extends Codex {public StrictOwner(int v){}}')
            self.assertEqual(self.backend.build(root)['class_versions']['StrictOwner'],'45.3')
    def test_native_parameters_reject_bad_counts_bounds_and_unknown_types(self):
        from rcm.script_parameters import authored,read as read_args
        values=[authored(1,-3,{}),authored(2,1.5,{}),authored(3,'box',{'box':2}),authored(7,'Hola',{}),authored(8,'npc',{'npc':3})]
        data=b''.join(p.encode() for p in values);self.assertEqual(read_args(data,0,5),(values,len(data)))
        for data,count in [(data[:-1],5),(b'',17),(struct.pack('<I',12),1),(struct.pack('<II',7,99999),1)]:
            with self.assertRaises(ValueError):read_args(data,0,count)
        for kind,value in [(1,True),(1,2**31),(2,float('inf')),(7,'a\0b'),(9,3)]:
            with self.assertRaises(ValueError):authored(kind,value,{})
    def test_extended_original_nsd_corpus_preserves_baseline_and_arguments(self):
        rows=json.loads((ROOT/'research/embrace_strict_parity/nsd_extended_roundtrips.json').read_text())
        self.assertEqual(len(rows),64)
        for row in rows:
            data=(ROOT/'research/original/Resource.nob/scenes'/row['path']).read_bytes();self.assertEqual(Scene.read(data).encode(),data)
        self.assertEqual(sum(bool(r['parameters']) for r in rows if not r['frames']),19)
    def native_source(self):
        root=blank();root['chronicle']['id']='native_test';s=root['scenes'][0]
        s['objects']=[dict(id='mover',name='Ruina',template='tracker_thing',transform=dict(position=[-176,-612,384],orientation=[0,0,0]))]+[dict(id='part'+str(i),name='Escombro',template='wallGib',transform=dict(position=[-176+i*24,-612,384],orientation=[0,0,0])) for i in range(5)]
        s['objects'][0]['native_script']={'class':'ClassBreakable','parameters':[dict(type='thing',value='part'+str(i)) for i in range(5)]+[dict(type='float',value=v) for v in (10,10,40,1,1,1)]}
        return root
    def test_native_reference_rename_delete_and_real_codex_build(self):
        from rcm.campaign_document import CampaignDocument
        from rcm.safe_edit import reference_links,delete_candidate,deletion_plan
        root=self.native_source();before=copy.deepcopy(root);self.assertTrue(self.backend.validate(root).valid,self.backend.validate(root).problems)
        self.assertEqual(root,before)
        doc=CampaignDocument(self.ws,root);path=('scenes',0,'objects',1)
        self.assertEqual(len(reference_links(doc,path)),1)
        doc.rename('objects',1,'stone');self.assertEqual(root['scenes'][0]['objects'][0]['native_script']['parameters'][0]['value'],'stone')
        with self.assertRaises(ValueError):delete_candidate(doc,path,self.backend)
        plan=deletion_plan(doc,path,self.backend);self.assertNotIn('native_script',plan.candidate['scenes'][0]['objects'][0]);self.assertTrue(self.backend.validate(plan.candidate).valid)
        report=self.backend.build(root);self.assertTrue(all(v=='45.3' for v in report['class_versions'].values()))
        with zipfile.ZipFile(ROOT/'build/native_test/native_test.nob') as z:
            scene=Scene.read(z.read('scenes/R_native_test_s0.nsd'));self.assertEqual(len(scene.entities),7)
            self.assertEqual(scene.parameters[1][0].raw,struct.pack('<i',2))
            self.assertEqual(scene.parameters[1][5].raw,struct.pack('<f',10))
            self.assertFalse(any(n.endswith('ClassBreakable.class') for n in z.namelist()))
        code=(ROOT/'build/native_test/generated/java/R_native_test_s0_Scene.java').read_text(encoding='utf8')
        self.assertIn('case 0: if(!createdOnce[i])',code)
    def test_interest_records_match_original_defaults_and_distinct_group_selection(self):
        from rcm.interest_spots import validate_record,records
        from rcm.project_resources import ai_edit
        rows=json.loads((ROOT/'research/embrace_strict_parity/interest_reverse_candidates.json').read_text())
        self.assertEqual(len(rows),15)
        for row in rows:
            original=(ROOT/'research/original/Resource.nob/scenes'/row['path']).read_bytes();count=row['count'];offset=row['offset']
            self.assertEqual(struct.unpack_from('<I',original,offset)[0],count)
            for i,record in enumerate(row['records']):
                data=bytes.fromhex(record['raw']);self.assertEqual(validate_record(data),original[offset+4+i*72:offset+4+(i+1)*72])
        s=blank()['scenes'][0];s['waypoints']=[dict(id='interest',name='Interés',interest_group=8,transform=dict(position=[-176,-612,384],orientation=[0,0,0]))]
        data=records(self.ws,self.backend.levels['EastLondon'],s)[0];self.assertEqual(struct.unpack_from('<I',data,56)[0],8);self.assertEqual(data[60:],struct.pack('<fII',128,0,0))
        encoded=Scene('s','l',[],interest_spots=[data]).encode();self.assertEqual(Scene.read(encoded).encode(),encoded)
        self.assertEqual(ai_edit(b'interestNum 8\r\nwanderRadius 500\r\n',{'interestNum':9}),b'interestNum 9\r\nwanderRadius 500\r\n')
        with self.assertRaises(ValueError):ai_edit(b'interestNum \r\nwanderRadius 500\r\n',{'interestNum':9})
    def test_native_motion_frames_order_links_and_cascade(self):
        from rcm.native_scripts import placement,catalogue
        from rcm.campaign_document import CampaignDocument
        from rcm.safe_edit import deletion_plan
        import yaml
        root=yaml.safe_load((ROOT/'chronicles/strict_acceptance/project.yaml').read_text(encoding='utf8'))
        doc=CampaignDocument(self.ws,root);scene=doc.campaign['scenes'][0]
        i=next(i for i,p in enumerate(scene['waypoints']) if p['id']=='cargo_high')
        doc.rename('waypoints',i,'cargo_top');self.assertEqual(next(o for o in scene['objects'] if o['id']=='cargo_mover')['native_frames'],['cargo_top'])
        plan=deletion_plan(doc,('scenes',0,'waypoints',i),self.backend)
        self.assertFalse(any(o['id']=='cargo_mover' for o in plan.candidate['scenes'][0]['objects']))
        self.assertTrue(self.backend.validate(plan.candidate).valid)
        invalid=copy.deepcopy(scene);next(o for o in invalid['objects'] if o['id']=='cargo_mover')['native_script']['parameters'][1]['value']=0
        with self.assertRaises(ValueError):placement(invalid,catalogue(self.ws,self.backend.resources))
        backend=Backend(Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption')))
        report=backend.build(root);self.assertTrue(all(v=='45.3' for v in report['class_versions'].values()))
        with zipfile.ZipFile(ROOT/'build/rcm_strict/rcm_strict.nob') as z:
            model=Scene.read(z.read('scenes/R_rcm_strict_s0.nsd'))
            i=next(i for i,tags in enumerate(model.entities) if any(t.id==81 and cstring(t.value)=='R_rcm_strict_s0_cargo_mover' for t in tags))
            self.assertEqual(struct.unpack('<6f',model.frames[i][0]),(0,0,0,500,-900,-496))
            self.assertEqual(struct.unpack('<6f',model.frames[i][1]),(0,0,0,500,-900,-472))
