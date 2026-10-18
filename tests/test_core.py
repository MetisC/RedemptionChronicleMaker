import copy
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import unittest
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "cache/vendor")]
from rcm.formats import NotFile, Scene, Tag, Template, fixed, u32
from rcm.model import parse_project
from rcm.paths import Workspace
from rcm.generator import zip_bytes, build


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.levels = json.loads((ROOT / "cache/levels.json").read_text(encoding="utf8"))
        cls.resources = json.loads((ROOT / "cache/resources.json").read_text(encoding="utf8"))
        cls.source = (ROOT / "tests/fixtures/chronicles/east_demo.yaml").read_text(encoding="utf8")
        cls.data = yaml.safe_load(cls.source)
        # Builds are disposable. A clean checkout must prepare its own fixture.
        hints=json.loads((ROOT/'cache/scene_hints.json').read_text(encoding='utf8'))
        build(Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption')),parse_project(cls.source,cls.levels,cls.resources),cls.levels,cls.resources,hints,True)

    def project(self, data=None):
        return parse_project(yaml.safe_dump(data or self.data, allow_unicode=True), self.levels, self.resources)

    def test_demo_source(self):
        p = self.project()
        self.assertEqual(p.level, "EastLondon")
        self.assertEqual(len(p.conversations[0].choices), 2)
        self.assertEqual(p.entities[0].transform.orientation, (0,0,180))

    def test_original_not_roundtrips(self):
        files = list((ROOT / "research/original/Resource.nob/misc/Templates").glob("*.not"))
        self.assertEqual(len(files), 4)
        for f in files:
            with self.subTest(file=f.name):
                self.assertEqual(NotFile.read(f.read_bytes()).encode(), f.read_bytes())

    def test_unknown_tags_and_comments_survive(self):
        f = NotFile([Template("Test", [Tag(999, bytes(range(32)))], b"hello\0")], trailing=b"opaque")
        self.assertEqual(NotFile.read(f.encode()).encode(), f.encode())

    def test_malformed_not_rejected(self):
        f = bytearray(NotFile([Template("Test", [])]).encode())
        struct.pack_into("<I", f, 44, 0xffffffff)
        with self.assertRaises(ValueError): NotFile.read(bytes(f))
        with self.assertRaises(ValueError): NotFile.read(b"NOT\x10")

    def test_original_simple_nsd_roundtrips(self):
        passed = 0; native_conversations=set()
        for f in (ROOT / "research/original/Resource.nob/scenes").glob("*.nsd"):
            try: scene = Scene.read(f.read_bytes())
            except ValueError: continue
            self.assertEqual(scene.encode(), f.read_bytes())
            if scene.conversation_starts:native_conversations.add(f.name)
            else:passed += 1
        self.assertEqual(passed, 24)
        self.assertEqual(native_conversations,{'CURI_28_4.nsd','NEWM_37_4.nsd','SMTY_7_1.nsd','SMYD_4_1.nsd'})

    def test_complex_scene_refused(self):
        with self.assertRaises(ValueError):
            Scene.read((ROOT / "research/original/Resource.nob/scenes/EAST_28_4.nsd").read_bytes())

    def test_scene_writer(self):
        s = Scene("SceneS", "SceneL", [[Tag.text(0,"ghost"), Tag.text(11,"OwnScript"), Tag.vector(2,[1,2,3])]])
        data = s.encode()
        self.assertEqual(u32(data,80),1)
        self.assertEqual(Scene.read(data).encode(),data)
        self.assertNotIn(b"NIL",data)

    def test_unknown_level(self):
        d=copy.deepcopy(self.data); d["level"]["source"]="Missing"
        with self.assertRaises(ValueError): self.project(d)

    def test_unknown_template(self):
        d=copy.deepcopy(self.data); d["actors"][0]["template"]="ImaginaryNPC"
        with self.assertRaises(ValueError): self.project(d)

    def test_unknown_actions_and_geometry_are_errors(self):
        for key in ["geometry", "gui", "triggers"]:
            d=copy.deepcopy(self.data); d[key]={}
            with self.assertRaises(ValueError): self.project(d)
        d=copy.deepcopy(self.data); d["events"][0]["actions"]=[{"teleport":"victoria"}]
        with self.assertRaises(ValueError): self.project(d)

    def test_duplicate_ids_and_results(self):
        d=copy.deepcopy(self.data); d["actors"].append(d["actors"][0])
        with self.assertRaises(ValueError): self.project(d)
        d=copy.deepcopy(self.data); d["conversations"][0]["choices"][1]["result"]=1
        with self.assertRaises(ValueError): self.project(d)

    def test_undefined_and_duplicate_flags(self):
        d=copy.deepcopy(self.data); d["state"]["flags"]={}
        with self.assertRaises(ValueError): self.project(d)
        d=copy.deepcopy(self.data); d["state"]["flags"]["other"]=1
        with self.assertRaises(ValueError): self.project(d)

    def test_nan_and_bad_vectors(self):
        for vector in [[1,2], [1,2,float("nan")], [1,2,float("inf")], [True,2,3]]:
            d=copy.deepcopy(self.data); d["actors"][0]["transform"]["position"]=vector
            d["actors"][0]["transform"]["placement"]="absolute"
            with self.assertRaises(ValueError): self.project(d)

    def test_duplicate_yaml_keys_and_aliases(self):
        for text in ["schema: 1\nschema: 1\n", "a: &x [1]\nb: *x\n", "!!python/object/apply:os.system ['whoami']"]:
            with self.assertRaises((ValueError,yaml.YAMLError)):
                parse_project(text,self.levels,self.resources)

    def test_directory_traversal_and_original_game_write(self):
        ws=Workspace(ROOT,Path(r"H:\GOG\Vampire The Masquerade - Redemption"))
        for p in ["../escape", r"H:\GOG\Vampire The Masquerade - Redemption\generated.nsc"]:
            with self.assertRaises(ValueError): ws.output(p)
        with self.assertRaises(ValueError): Workspace(ws.game,ws.game)

    def test_fixed_string_limit(self):
        with self.assertRaises(ValueError): fixed("a"*32)
        with self.assertRaises(ValueError): fixed("bad\0key")

    def test_catalogue_associations_and_resources(self):
        east=self.levels["EastLondon"]
        self.assertEqual(east["nil"].lower(),"l1_east.nil")
        self.assertTrue(any(r["scene"].lower()=="null" for r in east["references"]))
        self.assertTrue(any(t["id"]=="businessWoman" and t["kind"]=="actors" for t in self.resources["templates"]))
        self.assertEqual(len(self.resources["groups"]["ai"]),136)

    def test_package_has_only_references_to_geometry(self):
        folder=ROOT / "build/east_demo"
        with zipfile.ZipFile(folder / "east_demo_distribution.zip") as z:
            self.assertFalse(any(n.lower().endswith(".nil") for n in z.namelist()))
            self.assertIn("codex/R_east_demo_Scene.class",z.namelist())
            self.assertEqual(z.read("codex/R_east_demo_Scene.class")[:8],bytes.fromhex("cafebabe0003002d"))
            resources=zipfile.ZipFile(io.BytesIO(z.read("east_demo.nob")))
            self.assertFalse(any(n.lower().endswith((".nil", ".class")) for n in resources.namelist()))
            self.assertEqual(len(Scene.read(resources.read("scenes/R_east_demo.nsd")).entities),1)
            templates=NotFile.read(resources.read("misc/templates/_R_east_demo.not"))
            values=templates.templates[0].values()
            self.assertEqual(values[81].split(b"\0")[0],b"R_east_demo_victoria")
            self.assertEqual(values[11].split(b"\0")[0],b"R_east_demo_Passive")

    def test_user_directory_bundle_exposes_chronicle_and_classes(self):
        # Native selector lists NSCs from the registered root NOB index;
        # native JVM separately searches <user>/codex. Neither discovery path
        # may depend on installing loose resources into the game's root.
        folder=ROOT / "build/east_demo"
        with zipfile.ZipFile(folder / "east_demo_distribution.zip") as z:
            self.assertEqual(set(z.namelist()), {"east_demo.nob", "codex/R_east_demo_Scene.class", "codex/R_east_demo_Passive.class"})
            self.assertEqual(z.read("east_demo.nob"), (folder / "east_demo.nob").read_bytes())
            with zipfile.ZipFile(io.BytesIO(z.read("east_demo.nob"))) as resources:
                self.assertIsNone(resources.testzip())
                scene_list=resources.read("chronicles/east_demo.nsc").decode("cp1252")
                self.assertIn("flags 0x3", scene_list)
                location_line=next(line for line in scene_list.splitlines() if line.startswith("location "))
                self.assertEqual(int(location_line.split()[-1],0),0x60)
                metadata=resources.read("chronicles/R_east_demo.nmf").decode("cp1252")
                self.assertIn("NOT _R_east_demo.not\r\n", metadata)
                self.assertIn("misc/templates/_R_east_demo.not", resources.namelist())
                self.assertIn("east_demo Redemption Chronicle Maker: Londres nuevo", resources.read("strings/_R_east_demo.nls").decode("cp1252"))
                self.assertNotIn("strings/chronicles.nls", resources.namelist())
            for path in z.namelist():
                self.assertEqual(z.read(path), (folder / "bundle" / path).read_bytes())

    def test_cross_file_conversation_links(self):
        runtime=ROOT / "build/east_demo/runtime"
        nvo={line.split()[0] for line in (runtime / "strings/R_east_demo.nvo").read_text(encoding="cp1252").splitlines()}
        for f in (runtime / "conversations").glob("*.nco"):
            lines=f.read_text(encoding="cp1252").splitlines()
            answers=[line for line in lines if line.startswith("ANSWERRETURN:")]
            self.assertEqual(len(answers),2)
            for line in lines:
                if line.startswith(("LINE:","ANSWERRETURN:")):
                    self.assertIn(line.split()[1],nvo)

    def test_sky_fields_and_empty_global_arrays(self):
        scene=Scene.read((ROOT / "build/east_demo/runtime/scenes/R_east_demo.nsd").read_bytes())
        self.assertEqual(scene.environment[:16],bytes(16))
        original=(ROOT / "research/original/Resource.nob/scenes/EAST_28_1.nsd").read_bytes()
        self.assertEqual(scene.environment[16:],original[-176:])
        self.assertEqual(scene.environment[-64:],bytes(64))
        self.assertIsNone(self.project().sky)
        d=copy.deepcopy(self.data); d["level"]["sky"]={"model":"Sky","animation":"Sky"}
        self.assertEqual(self.project(d).sky,("Sky","Sky"))
        d["level"]["sky"]["model"]="ImaginarySky"
        with self.assertRaises(ValueError): self.project(d)

    def test_absolute_and_player_placement_are_explicit(self):
        self.assertEqual(self.project().entities[0].transform.placement,"near_player")
        d=copy.deepcopy(self.data); d["actors"][0]["transform"]["position"]=[1016,-54,0]
        with self.assertRaises(ValueError): self.project(d)
        d["actors"][0]["transform"]["placement"]="absolute"
        p=self.project(d)
        from rcm.generator import runtime_java
        self.assertIn('CreateThing("R_east_demo_victoria", new float[]{1016.0f, -54.0f, 0.0f}',runtime_java(p)[1])
        self.assertEqual(p.entities[0].transform.position,(1016,-54,0))

    def test_reproducible_archive(self):
        self.assertEqual(zip_bytes({"b":b"2","a":b"1"}),zip_bytes({"a":b"1","b":b"2"}))

    def test_uncompiled_rebuild_does_not_publish_stale_classes(self):
        d=copy.deepcopy(self.data); d["chronicle"]["id"]="build_check"
        p=self.project(d)
        ws=Workspace(ROOT,Path(r"H:\GOG\Vampire The Masquerade - Redemption"))
        hints=json.loads((ROOT / "cache/scene_hints.json").read_text(encoding="utf8"))
        first=build(ws,p,self.levels,self.resources,hints,True)
        folder=ROOT / "build/build_check"
        self.assertTrue((folder / "build_check_distribution.zip").is_file())
        self.assertEqual(first["class_versions"]["R_build_check_Scene"],"45.3")
        second=build(ws,p,self.levels,self.resources,hints,False)
        self.assertEqual(second["status"],"generated-uncompiled")
        self.assertFalse((folder / "build_check_distribution.zip").exists())
        self.assertFalse((folder / "runtime/codex/R_build_check_Scene.class").exists())
        self.assertFalse((folder / "bundle/codex/R_build_check_Scene.class").exists())

    def test_geometry_catalogue_is_complete(self):
        geometry=json.loads((ROOT / "cache/geometry.json").read_text(encoding="utf8"))
        self.assertEqual(len(geometry),112)
        self.assertEqual(geometry["levels/P2_OLDT.nil"]["location_ids"],[])
        self.assertEqual(len(self.resources["groups"]["music"]),56)

    def test_generated_java_callback_logic(self):
        output=ROOT / "build/tests/java"
        output.mkdir(parents=True,exist_ok=True)
        trace=ROOT / "build/tests/RCM/east_demo/runtime_trace.log"
        trace.parent.mkdir(parents=True,exist_ok=True)
        if trace.exists(): trace.unlink()
        source=ROOT / "build/east_demo/generated/java/R_east_demo_Scene.java"
        compile_result=subprocess.run(["javac","-d",str(output),str(ROOT / "tests/java/MockEngine.java"),str(ROOT / "tests/java/RuntimeHarness.java"),str(source)],capture_output=True,text=True)
        self.assertEqual(compile_result.returncode,0,compile_result.stderr)
        run=subprocess.run(["java","-cp",str(output),"RuntimeHarness"],capture_output=True,text=True,cwd=ROOT / "build/tests")
        (ROOT / "build/tests/runtime_harness.log").write_text(run.stdout+run.stderr,encoding="utf8")
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertIn("PASS:",run.stdout)
        diagnostic=trace.read_text(encoding="utf8")
        self.assertIn("RCM revision 3: scene controller constructed",diagnostic)
        self.assertIn("beginscene",diagnostic)
        self.assertIn("SpawnThingNear GUID=100",diagnostic)
        self.assertIn("SPAWN FAILED after retries",diagnostic)


if __name__ == "__main__": unittest.main()
