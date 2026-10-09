"""NOT corpus, opaque safety and custom resource pipeline against real Codex."""
import random,struct,zipfile
from unittest import TestCase
from test_campaign import source,ROOT
from rcm.formats import NotFile,Template,Tag,cstring
from rcm.not_library import NotLibrary,patch_template
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.project_resources import ai_edit,prepare

def custom_source():
    d=source();d['chronicle']['id']='p5_test';d['project_format']=5;d['metadata']={'version':'0.1.0','author':'RCM','dependencies':[]}
    path=ROOT/'build/tests/P5TestActor.java';path.parent.mkdir(parents=True,exist_ok=True);path.write_text('public class P5TestActor extends Codex { public P5TestActor() { CodexConsole.Print(0,0,"custom"); } }',encoding='utf8')
    d['resources']={'templates':[dict(id='T_p5_actor',base='businessWoman',mode='inherit',properties={'ai':'AI_p5','script':'P5TestActor'})],'ai_profiles':[dict(id='AI_p5',base='civilian',properties={'wanderRadius':0})],'scripts':[dict(id='P5TestActor',source='build/tests/P5TestActor.java')]};d['scenes'][0]['actors'][0]['template']='T_p5_actor';return d

class Phase5ResourceTests(TestCase):
 @classmethod
 def setUpClass(cls):cls.ws=Workspace(ROOT);cls.b=Backend(cls.ws)
 def test_whole_corpus_lossless(self):
  files=list((ROOT/'research/original').rglob('*.not'));self.assertGreaterEqual(len(files),4)
  for path in files:
   data=path.read_bytes();nf=NotLibrary(data);self.assertEqual(nf.encode(),data);self.assertEqual(len(NotFile.read(nf.encode()).templates),len(nf.file.templates))
 def test_edit_preserves_unknown_tags_and_scalar_padding(self):
  t=Template('actor',[Tag(300,bytes(range(32))),Tag(114,struct.pack('<I',7)+b'Z'*28),Tag.text(4,'Model')],b'comment\0');new=patch_template(t,{'actor_flags':19,'model':'Other'});self.assertEqual(new.tags[0],t.tags[0]);self.assertEqual(new.tags[1].value[4:],b'Z'*28);self.assertEqual(new.comment,t.comment);self.assertEqual(t.tags[2].value,Tag.text(4,'Model').value)
 def test_clone_rename_and_parent_refactor(self):
  lib=NotLibrary(NotFile([Template('base',[Tag.integer(16,0),Tag(300,b'X'*32)])]).encode());lib.add('base','copy',mode='copy');lib.add('copy','child');lib.rename('copy','renamed');self.assertEqual(cstring(lib.find('child').tags[0].value),'renamed');self.assertEqual(lib.find('renamed').tags[-1].value,b'X'*32);NotFile.read(lib.encode())
 def test_opaque_tail_blocks_structural_edits(self):
  lib=NotLibrary(NotFile([Template('base',[])],trailing=b'opaque').encode())
  with self.assertRaises(ValueError):lib.add('base','new')
  with self.assertRaises(ValueError):lib.rename('base','new')
  self.assertTrue(lib.encode().endswith(b'opaque'))
 def test_corruption_truncation_offsets_and_duplicates(self):
  data=NotFile([Template('actor',[Tag.text(4,'Model')])]).encode()
  for n in range(len(data)):
   with self.assertRaises(ValueError):NotFile.read(data[:n])
  broken=bytearray(data);struct.pack_into('<I',broken,44,0xffffffff)
  with self.assertRaises(ValueError):NotFile.read(broken)
  rng=random.Random(512)
  for _ in range(200):
   bad=bytearray(data);bad[rng.randrange(len(data))]=rng.randrange(256)
   try:NotFile.read(bad)
   except ValueError:pass
 def test_ai_edits_preserve_unknown_lines(self):
  data=b'; preserved\r\nattackRate 0.5 // note\r\nwanderRadius 1024.0\r\nunknown future\r\n';out=ai_edit(data,{'wanderRadius':0});self.assertIn(b'unknown future',out);self.assertIn(b'attackRate 0.5 // note',out);self.assertIn(b'wanderRadius 0\r\n',out)
  with self.assertRaises(ValueError):ai_edit(data,{'attackType':999})
 def test_custom_templates_validation_and_real_build(self):
  d=custom_source();v=self.b.validate(d);self.assertTrue(v.valid,[p.message for p in v.problems]);report=self.b.build(d);self.assertIn('P5TestActor',report['class_versions']);self.assertEqual(report['class_versions']['P5TestActor'],'45.3')
  with zipfile.ZipFile(ROOT/'build/p5_test/p5_test.nob') as z:
   nf=NotFile.read(z.read('misc/templates/_R_p5_test_custom.not'));row=nf.templates[0];self.assertEqual(cstring(row.values()[56]),'AI_p5');self.assertEqual(cstring(row.values()[11]),'P5TestActor');self.assertIn(b'NOT _R_p5_test_custom.not',z.read('chronicles/R_p5_test.nmf'));self.assertIn(b'wanderRadius',z.read('misc/AI/AI_p5.nai'))
   child=NotFile.read(z.read('misc/templates/_R_p5_test_s0.not')).templates[0];self.assertEqual(cstring(child.values()[11]),'P5TestActor')
 def test_format9_catalogue_ids_become_real_not_filenames(self):
  for ai,model in [('AI_p5','Rat'),('AI_p5.nai','Rat.nod')]:
   d=custom_source();d['project_format']=9;d['resources']['templates'][0]['properties'].update(ai=ai,model=model)
   _,catalogue,payload,_=prepare(self.ws,d,self.b.original_resources)
   row=NotFile.read(payload['misc/templates/_R_p5_test_custom.not']).templates[0]
   self.assertEqual(cstring(row.values()[56]),'AI_p5.nai');self.assertEqual(cstring(row.values()[4]),'Rat.nod');self.assertEqual(cstring(row.values()[11]),'P5TestActor')
   self.assertEqual(d['resources']['templates'][0]['properties']['ai'],ai)
   entry=next(t for t in catalogue['templates'] if t['id']=='T_p5_actor');self.assertEqual(entry['ai'],'AI_p5.nai')
 def test_invalid_custom_resources_fail_closed(self):
  for update in [lambda d:d['resources']['templates'][0].update(base='missing'),lambda d:d['resources']['templates'][0]['properties'].update(model='missing'),lambda d:d['resources']['templates'][0]['properties'].update(health=10),lambda d:d['resources']['templates'][0].update(base='T_p5_actor'),lambda d:d['resources']['ai_profiles'][0]['properties'].update(attackRate=-1),lambda d:d.update(project_format=99)]:
   d=custom_source();update(d);self.assertFalse(self.b.validate(d).valid)
