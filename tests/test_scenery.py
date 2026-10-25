"""Parametric native scenery: geometry spec, validation, NSD readback, runtime."""
import copy
import struct
import subprocess
import tempfile
from pathlib import Path
from unittest import TestCase

from PySide6.QtWidgets import QApplication, QComboBox, QWidget

from rcm.paths import Workspace
from rcm.service import Backend
from rcm.formats import Scene, Tag, cstring
from rcm.formats import NotFile
from rcm.spatial.scene_mesh import read_brush
from rcm.campaign_document import CampaignDocument
from rcm.campaign_generator import runtime
from rcm.scenery import MODES, spec, validate_geometry
from rcm.click_interactions import brush
from test_release10 import blank
from test_stability_revision import compile_scenario

ROOT = Path(__file__).resolve().parents[1]


def geometry(mode='decor', size=(64, 32, 128), material='London\\SLwall1_L', uv_scale=64):
    return dict(shape='box', size=list(size), material=material, uv_scale=uv_scale, mode=mode)


def source(mode='decor', object_id='decor1', position=(-62, -768, 384), **kw):
    root = blank()
    scene = root['scenes'][0]
    scene['objects'] = [dict(id=object_id, name='Pieza', template=MODES[mode],
                             transform=dict(placement='absolute', position=list(position), orientation=[0, 0, 45]),
                             geometry=geometry(mode, **kw))]
    return root


class GeometrySpec(TestCase):
    def test_box_emits_outward_normals_world_uvs_and_six_bounded_planes(self):
        g = geometry(size=(64, 32, 128), uv_scale=64)
        value = spec(g, 3)
        self.assertEqual(value['materials'], ['London\\SLwall1_L'])
        self.assertEqual(value['sector'], 3)
        self.assertEqual(len(value['vertices']), 36)
        xs = [p[0] for p in value['vertices']]
        ys = [p[1] for p in value['vertices']]
        zs = [p[2] for p in value['vertices']]
        self.assertEqual((min(xs), max(xs)), (-32, 32))
        self.assertEqual((min(ys), max(ys)), (-16, 16))
        self.assertEqual((min(zs), max(zs)), (0, 128))
        # UVs are world-scale planar projections: width/scale repeats on X faces.
        us = sorted(set(round(p[3], 4) for p in value['vertices']))
        self.assertTrue(max(us) - min(us) > 0)
        # Every triangle normal must point away from the local centre.
        cx, cy, cz = 0, 0, 64
        for i in range(0, 36, 3):
            a, b, c = (value['vertices'][i + j][:3] for j in range(3))
            u = [b[k] - a[k] for k in range(3)]
            v = [c[k] - a[k] for k in range(3)]
            n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
            mid = [(a[k] + b[k] + c[k]) / 3 for k in range(3)]
            dot = sum(n[k] * (mid[k] - (cx, cy, cz)[k]) for k in range(3))
            self.assertGreater(dot, 0, 'triangle %d faces inward' % i)
        body = brush(value)
        read = read_brush(body, 0)
        self.assertEqual(read.materials, ['London\\SLwall1_L'])
        self.assertEqual(len(body), read.source_end + 100)
        self.assertEqual(struct.unpack_from('<I', body, read.source_end)[0], 6)
        scene = Scene('S', 'L', [[Tag.text(0, 'ghost')], [Tag.text(0, 'tracker_thing_null'), Tag.text(82, 'D')]],
                      brushes={1: body})
        encoded = scene.encode()
        self.assertEqual(Scene.read(encoded).encode(), encoded)
        self.assertEqual(Scene.read(encoded).brushes, {1: body})

    def test_geometry_validation_matrix(self):
        base = geometry()
        for mutate in (lambda v: v.update(shape='mesh'),
                       lambda v: v.update(size=[64, 32]),
                       lambda v: v.update(size=[64, 0, 32]),
                       lambda v: v.update(size=[64, float('nan'), 32]),
                       lambda v: v.update(size=[64, 32, 99999]),
                       lambda v: v.update(material=''),
                       lambda v: v.update(material='x' * 32),
                       lambda v: v.update(material='bad\nname'),
                       lambda v: v.update(uv_scale=0),
                       lambda v: v.update(mode='magical')):
            with self.subTest(mutate=mutate):
                value = dict(base)
                mutate(value)
                with self.assertRaises(ValueError):
                    validate_geometry(value)
        valid = validate_geometry(dict(base))
        self.assertEqual(valid['mode'], 'decor')
        self.assertEqual(valid['uv_scale'], 64)


class SceneryCampaign(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.backend = Backend(Workspace(ROOT, Path(r'H:\GOG\Vampire The Masquerade - Redemption')))
        cls.backend.safe_mode = True
        (ROOT / 'build/tests').mkdir(parents=True, exist_ok=True)

    def valid(self, root):
        result = self.backend.validate(root)
        self.assertTrue(result.valid, [p.message for p in result.problems if p.severity == 'ERROR'])
        return result.project

    def test_decor_modes_validate_and_map_stock_native_templates(self):
        for mode, template in MODES.items():
            with self.subTest(mode=mode):
                self.valid(source(mode))
        root = source('decor')
        root['scenes'][0]['objects'][0]['template'] = 'backpack'
        self.assertFalse(self.backend.validate(root).valid)

    def test_conflicting_fields_and_legacy_format_are_rejected(self):
        for mutate in (lambda s: s['objects'][0].update(interaction=dict(materials=['a'], vertices=[[0, 0, 0, 0, 0]] * 3, material_ids=[0], sector=0)),
                       lambda s: s['objects'][0].update(quest_item=True),
                       lambda s: s['objects'][0].update(native_script={'class': 'x', 'parameters': []}),
                       lambda s: s['objects'][0].update(native_frames=['wp1']),
                       lambda s: s['objects'][0]['transform'].update(placement='near_player')):
            with self.subTest(mutate=mutate):
                root = source()
                mutate(root['scenes'][0])
                self.assertFalse(self.backend.validate(root).valid)
        legacy = source()
        legacy['project_format'] = 5
        self.assertFalse(self.backend.validate(legacy).valid)

    def test_object_clicked_requires_interactive_mode(self):
        root = source('decor')
        root['scenes'][0]['events'] = [dict(id='use', when='object_clicked', object='decor1', once=False, actions=[{'reward_xp': 7}])]
        self.assertFalse(self.backend.validate(root).valid)
        root = source('interactive')
        root['scenes'][0]['events'] = [dict(id='use', when='object_clicked', object='decor1', once=False, actions=[{'reward_xp': 7}])]
        self.assertTrue(self.backend.validate(root).valid)

    def test_build_writes_native_brush_entity_with_real_sector(self):
        root = source('decor')
        root['chronicle']['id'] = 'decor_test'
        report = self.backend.build(root)
        self.assertEqual(report['status'], 'compiled-unverified-in-game')
        self.assertFalse(report['geometry_in_package'])
        prefix = 'R_decor_test_s0'
        nsd = Scene.read((ROOT / f'build/decor_test_s0/runtime/scenes/{prefix}.nsd').read_bytes())
        self.assertEqual(len(nsd.brushes), 1)
        index = next(iter(nsd.brushes))
        tags = {t.id: t.value for t in nsd.entities[index]}
        self.assertEqual(cstring(tags[0]), prefix + '_decor1')
        sector = struct.unpack_from('<I', tags[3])[0]
        self.assertTrue(0 <= sector < 100000)
        self.assertEqual(cstring(tags[82]), prefix + '_decor1')
        mesh = read_brush(nsd.brushes[index], 0)
        self.assertEqual(mesh.materials, ['London\\SLwall1_L'])
        self.assertEqual(mesh.bounds[0].tolist(), [-32.0, -16.0, 0.0])
        self.assertEqual(mesh.bounds[1].tolist(), [32.0, 16.0, 128.0])
        nots = NotFile.read((ROOT / f'build/decor_test_s0/runtime/misc/templates/_{prefix}.not').read_bytes())
        parents = {t.name: cstring(t.tags[0].value) for t in nots.templates if t.tags and t.tags[0].id == 0}
        self.assertEqual(parents[prefix + '_decor1'], 'tracker_thing_null')
        nls = (ROOT / f'build/decor_test_s0/runtime/strings/_{prefix}.nls').read_text(encoding='cp1252')
        self.assertIn(prefix + '_decor1 Pieza', nls)
        java = (ROOT / f'build/decor_test/generated/java/{prefix}_Scene.java').read_text()
        self.assertIn('bindDecor', java)
        self.assertIn('THING_FLAG_SAVEALWAYS|THING_FLAG_NOSTDELETE', java)
        self.assertNotIn('createAt(0,', java)

    def test_interactive_decor_captures_and_noninteractive_does_not(self):
        for mode, captured in (('interactive', 1), ('decor', 0)):
            with self.subTest(mode=mode):
                root = source(mode)
                if mode == 'interactive':
                    root['scenes'][0]['events'] = [dict(id='use', when='object_clicked', object='decor1', once=False, actions=[{'reward_xp': 7}])]
                campaign = self.valid(root)
                name = campaign.scenes[0][1].prefix + '_Scene'
                harness = '''public class StabilityHarness {
 static void check(boolean value,String why){if(!value)throw new AssertionError(why);}
 public static void main(String[] args) {
 CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);
 int wall=CE.make("PREFIX_decor1",new float[]{-62,-768,384});
 SCENE s=new SCENE();s.beginscene(1,0);
 check(CE.captures==CAPTURED,"capture contract by mode");
 check((CE.world.get(wall).clickFlags&8)!=0 && (CE.world.get(wall).clickFlags&2097152)!=0,"NSD piece keeps SAVEALWAYS|NOSTDELETE");
 s.clicked(wall,1,1);check(CE.xp==XP,"click dispatch contract by mode");
 for(int i=0;i<4;i++)s.timer(9400,0,0,0,0);check(CE.captures==CAPTURED,"bounded binding");
 System.out.println("DECOR_PASS");}}
'''.replace('SCENE', name).replace('PREFIX', campaign.scenes[0][1].prefix).replace('CAPTURED', str(captured)).replace('XP', '7' if captured else '0')
                def doubles(text):
                    text = text.replace('class CE {', 'class CE {static int captures=0;')
                    text = text.replace('static class Thing {String template;', 'static class Thing {int clickFlags=0;String template;')
                    text = text.replace('int ClearThingFlags(int f){return f;}int SetThingFlags(int f){return f;}',
                                        'int ClearThingFlags(int f){return CE.world.get(guid).clickFlags&=~f;}int SetThingFlags(int f){return CE.world.get(guid).clickFlags|=f;}')
                    text = text.replace('static boolean IsPropGuid(int g){return false;}', 'static boolean IsPropGuid(int g){return g!=1 && CE.valid(g);}')
                    text = text.replace('boolean CaptureThing(int g,int i){return CE.valid(g);}', 'boolean CaptureThing(int g,int i){CE.captures++;return CE.valid(g);}')
                    return text.replace('class Codex {', 'class Codex {static final int THING_FLAG_NOHIGHLIGHT=64,THING_FLAG_BLOCKSELECT=524288,THING_FLAG_PROXIMITYTRIGGER=1024,THING_FLAG_VISBLOCK=8192,THING_FLAG_CAMERABLOCK=16384,THING_FLAG_DISABLECOLLIDE=512,THING_FLAG_NOSTDELETE=2097152,THING_FLAG_NOBLOCK=134217728;')
                with tempfile.TemporaryDirectory(dir=ROOT / 'build/tests') as d:
                    out = Path(d)
                    compile_scenario(out, campaign, harness, doubles)
                    run = subprocess.run(['java', '-cp', str(out), 'StabilityHarness'], capture_output=True, text=True)
                    self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                    self.assertIn('DECOR_PASS', run.stdout)

    def test_no_feature_keeps_accepted_runtime_extension_absent(self):
        campaign = self.valid(blank())
        java = runtime(campaign, *campaign.scenes[0])[1]
        self.assertNotIn('bindDecor', java)
        self.assertNotIn('clickCaptured', java)

    def test_document_roundtrip_and_editor_controls(self):
        from rcm.editor.window import MainWindow
        root = source('solid')
        doc = CampaignDocument.load_data(self.backend.ws, copy.deepcopy(root), ROOT / 'chronicles/test_decor.yaml')
        win = MainWindow(self.backend)
        win.doc = doc
        win.refresh()
        self.addCleanup(lambda: (setattr(win, 'doc', None), win.close()))
        win.selection = ('objects', 0)
        win.inspect()
        panel = win.properties.widget()
        self.assertIsNotNone(panel.findChild(QComboBox, 'decor_mode'))
        for name in ('decor_size_x', 'decor_size_y', 'decor_size_z', 'decor_material', 'decor_uv_scale'):
            self.assertIsNotNone(panel.findChild(QWidget, name))
        # Undo/redo roundtrip preserves the parametric record.
        saved = doc.snapshot()
        win.changed(True)
        doc.data['objects'][0]['geometry']['size'][0] = 128
        win.changed(True)
        win.undo_project()
        self.assertEqual(doc.snapshot(), saved)

    def test_prefab_capture_validate_and_instantiate(self):
        from rcm.editor.scenery import capture_prefab, instantiate_prefab
        from rcm.recipes import validate_authoring
        root = source('decor')
        objects = root['scenes'][0]['objects']
        objects.append(dict(id='chair', name='Silla', template='chair',
                            transform=dict(placement='absolute', position=[-60, -760, 384], orientation=[0, 0, 90])))
        prefab = capture_prefab('Conjunto', objects)
        self.assertEqual(prefab['items'][0]['offset'], [0, 0, 0])
        self.assertEqual(prefab['items'][1]['offset'], [2, 8, 0])
        root.setdefault('authoring', {}).setdefault('prefabs', []).append(dict(id='set1', **prefab))
        validate_authoring(root)
        rows = instantiate_prefab(root['authoring']['prefabs'][0], [100, 200, 300])
        self.assertEqual(rows[0]['transform']['position'], [100, 200, 300])
        self.assertEqual(rows[0]['template'], 'tracker_thing_null')
        self.assertEqual(rows[1]['template'], 'chair')
        bad = copy.deepcopy(root['authoring']['prefabs'][0])
        bad['items'][0].pop('offset')
        root['authoring']['prefabs'][0] = bad
        with self.assertRaises(ValueError):
            validate_authoring(root)
