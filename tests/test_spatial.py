"""Parser, coordinates, raycasting, reference graph and shared runtime regression."""
from pathlib import Path
import sys
import json
import unittest
import subprocess
import struct
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.spatial.geometry import read_nil, Mesh
from rcm.spatial.assets import Assets, normalize
from rcm.spatial.math3d import Raycaster, inside, ray_box, ray_sphere, snap
from rcm.spatial.relations import references, affected
from rcm.paths import Workspace
from rcm.service import Backend, project_source
from rcm.document import Document
from rcm.generator import runtime_java
import yaml

def spatial_source():
    data=yaml.safe_load((ROOT/'chronicles/east_demo.yaml').read_text(encoding='utf8'))
    data['chronicle']['id']='spatial_test'
    data['state']['flags'].update(entered=2,sphere=3)
    data['actors'].append(dict(id='actor2',name='Segunda Victoria',template='businessWoman',transform=dict(position=[128,0,0],orientation=[0,0,90])))
    data['triggers']=[dict(id='entry',name='Entrada',shape='box',transform=dict(position=[0,0,50],orientation=[0,0,45]),size=[160,160,100],once=True),
        dict(id='round',name='Esfera',shape='sphere',transform=dict(position=[500,0,50],orientation=[0,0,0]),radius=80,once=False)]
    data['events'].extend([dict(id='ambush',when='trigger_enter',trigger='entry',conditions=[dict(flag='alliance',is_set=False)],actions=[dict(spawn='actor2'),dict(set_flag='entered')]),
        dict(id='round_event',when='trigger_enter',trigger='round',actions=[dict(set_flag='sphere')])])
    return data

class SpatialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ws=Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption'))
        cls.backend=Backend(cls.ws)
        cls.mesh=read_nil((ROOT/'research/original/l1_east.nil').read_bytes())

    def test_original_east_geometry_and_bounds(self):
        self.assertEqual((self.mesh.sectors,len(self.mesh.material_ids),len(self.mesh.materials)),(131,45927,109))
        np.testing.assert_allclose(self.mesh.bounds[0],[-5120,-4608,-80])
        self.assertEqual(self.mesh.source_end,3096883)

    def test_all_original_levels_have_measured_sector_layout(self):
        report=json.loads((ROOT/'research/viewport/nil_scan.json').read_text())
        self.assertEqual(len(report),112)
        self.assertTrue(all(r['success'] for r in report))

    def test_truncated_geometry_and_unknown_version_fail(self):
        original=(ROOT/'research/original/l1_east.nil').read_bytes()
        for data in [original[:100],original[:5000],original[:4]+struct.pack('<I',99)+original[8:]]:
            with self.assertRaises(ValueError):read_nil(data)

    def test_raycast_engine_coordinates_and_parallel_axes(self):
        m=Mesh(np.array([[0,0,0,0,0],[100,0,0,1,0],[0,100,0,0,1]],np.float32),np.array([0]),['floor'],1,0,[])
        caster=Raycaster(m)
        hit=caster.cast([10,20,100],[0,0,-1],True)
        np.testing.assert_allclose(hit.position,[10,20,0]);self.assertEqual(hit.distance,100)
        self.assertIsNone(caster.cast([150,150,100],[0,0,-1]))
        self.assertIsNone(caster.cast([10,20,-100],[0,0,-1]))

    def test_ray_box_and_grid_snap(self):
        self.assertEqual(ray_box([0,0,10],[0,0,-1],[-1,-1,-1],[1,1,1]),9)
        self.assertIsNone(ray_box([2,0,10],[0,0,-1],[-1,-1,-1],[1,1,1]))
        np.testing.assert_allclose(snap([15,31,47],16),[16,32,48])

    def test_sphere_picking_rejects_bounding_box_corners(self):
        self.assertEqual(ray_sphere([0,0,10],[0,0,-1],1),9)
        self.assertEqual(ray_sphere([0,0,0],[0,0,-1],1),0)
        self.assertIsNone(ray_sphere([.9,.9,10],[0,0,-1],1))
        self.assertIsNone(ray_sphere([0,0,10],[0,0,1],1))

    def test_oriented_trigger_and_sphere_boundaries(self):
        data=spatial_source();box=data['triggers'][0]
        self.assertTrue(inside(box,[0,0,50]));self.assertFalse(inside(box,[100,100,50]))
        self.assertTrue(inside(data['triggers'][1],[580,0,50]));self.assertFalse(inside(data['triggers'][1],[581,0,50]))

    def test_level_materials_model_textures_and_cache(self):
        assets=Assets(self.backend);one=assets.load('EastLondon',templates={'businessWoman'});two=assets.load('EastLondon')
        self.assertTrue(two.cache_hit)
        self.assertEqual(sum(m.warning is None for m in one.materials),109)
        model,materials=one.models['businessWoman']
        self.assertEqual(len(model.material_ids),1704)
        self.assertTrue(all(m.warning is None for m in materials))
        np.testing.assert_array_equal(one.mesh.vertices,two.mesh.vertices)

    def test_unknown_material_fallback_and_safe_resolution(self):
        assets=Assets(self.backend);m=assets.material('Missing/unknown_material')
        self.assertTrue(m.warning);self.assertEqual((m.width,m.height),(2,2))
        for p in ['../bad','H:/game','/absolute']:
            with self.assertRaises(ValueError):normalize(p)

    def test_corrupt_geometry_cache_is_regenerated_from_original(self):
        import tempfile
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            assets=Assets(self.backend)
            assets.ws=Workspace(Path(folder),self.ws.game)
            one=assets.load('EastLondon')
            cache=next((Path(folder)/'cache/geometry').glob('*.npz'))
            np.savez_compressed(cache,vertices=one.mesh.vertices,ids=np.full(len(one.mesh.material_ids),9999),materials=np.array(one.mesh.materials),sectors=131,end=one.mesh.source_end)
            two=assets.load('EastLondon')
            self.assertFalse(two.cache_hit)
            np.testing.assert_array_equal(one.mesh.material_ids,two.mesh.material_ids)
            self.assertTrue(assets.load('EastLondon').cache_hit)

    def test_reference_graph_uses_real_events_conversations_and_flags(self):
        data=spatial_source();incoming,outgoing=references(data,('actors',0))
        self.assertTrue(any(x.source==('conversations',0) for x in incoming))
        self.assertTrue(any(x.label=='spawn' for x in incoming))
        self.assertIn(('actors',1),affected(data,('triggers',0)))
        doc=Document(self.ws,data);doc.rename('triggers',0,'renamed')
        self.assertEqual(data['events'][1]['trigger'],'renamed')

    def test_trigger_model_roundtrip_and_legacy_near_player_untouched(self):
        data=spatial_source();validation=self.backend.validate(data)
        self.assertTrue(validation.valid,validation.problems)
        self.assertEqual(self.backend.validate(project_source(validation.project)).project,validation.project)
        self.assertNotIn('position',data['actors'][0]['transform'])
        area=ROOT/'build/tests/spatial_project.yaml';doc=Document(self.ws,data);doc.save(area)
        self.assertEqual(Document.load(self.ws,area).data,data)

    def test_invalid_volumes_and_unknown_triggers_block_build(self):
        for edit in [lambda d:d['triggers'][0].update(size=[0,10,10]),lambda d:d['triggers'][0].update(radius=20),lambda d:d['events'][1].update(trigger='missing'),lambda d:d['triggers'][1]['transform'].update(orientation=[0,0,90])]:
            d=spatial_source();edit(d);self.assertFalse(self.backend.validate(d).valid)

    def test_trigger_java_compiles_against_real_codex(self):
        # Normal build performs the real ECJ bootclasspath/API compilation.
        path=ROOT/'build/tests/spatial_source.yaml';Document(self.ws,spatial_source()).save(path)
        result=self.backend.build(spatial_source())
        self.assertTrue(all(version=='45.3' for version in result['class_versions'].values()))

    def test_trigger_runtime_scenarios_with_doubles(self):
        p=self.backend.validate(spatial_source()).project
        name,code=runtime_java(p);out=ROOT/'build/tests/spatial_java';out.mkdir(parents=True,exist_ok=True)
        source=out/(name+'.java');source.write_text(code)
        run=subprocess.run(['javac','-d',str(out),str(ROOT/'tests/java/MockEngine.java'),str(ROOT/'tests/java/SpatialHarness.java'),str(source)],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)
        run=subprocess.run(['java','-cp',str(out),'SpatialHarness'],cwd=ROOT/'build/tests',capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        (out/'harness.log').write_text(run.stdout+run.stderr,encoding='utf8')
        self.assertIn('11 spatial runtime checks',run.stdout)
