import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "cache/vendor")]
from rcm.document import Document
from rcm.service import Backend, source_text, project_source
from rcm.paths import Workspace
from rcm.formats import Scene


def graph_source():
    d = yaml.safe_load((ROOT / "tests/fixtures/chronicles/east_demo.yaml").read_text(encoding="utf8"))
    d["chronicle"].update(description="Notas internas\ncon varias líneas")
    d["level"]["name"] = "Londres: el nuevo pacto"
    d["actors"][0]["comment"] = "Comentario interno\nindependiente del motor"
    d["conversations"][0] = {"id": "intro", "speaker": "victoria", "entry": "opening", "nodes": [
        {"id": "opening", "lines": [{"speaker": "victoria", "text": "¿Quién viene?"}], "choices": [
            {"text": "Un aliado.", "goto": "identity"}, {"text": "Me voy.", "result": 2}]},
        {"id": "identity", "lines": [{"speaker": "victoria", "text": "Escucha mi propuesta."}, {"speaker": "victoria", "text": "La noche es larga."}], "choices": [
            {"text": "Acepto.", "result": 3, "set_flag": "alliance"}, {"text": "Rechazo.", "result": 4}]}]}
    return d


class Phase2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ws = Workspace(ROOT, Path(r"H:\GOG\Vampire The Masquerade - Redemption"))
        cls.backend = Backend(cls.ws)
        cls.area = ROOT / "build/tests/documents"
        cls.area.mkdir(parents=True, exist_ok=True)
        cls.backend.build((ROOT/'tests/fixtures/chronicles/east_demo.yaml').read_text(encoding='utf8'))

    def data(self):
        return graph_source()

    def test_legacy_source_roundtrip(self):
        d = yaml.safe_load((ROOT / "tests/fixtures/chronicles/east_demo.yaml").read_text(encoding="utf8"))
        p = self.backend.validate(d).project
        self.assertEqual(self.backend.validate(project_source(p)).project, p)
        self.assertNotIn("nodes", project_source(p)["conversations"][0])

    def test_graph_roundtrip_preserves_source_and_metadata(self):
        result = self.backend.validate(self.data())
        self.assertTrue(result.valid, result.problems)
        self.assertEqual(self.backend.validate(project_source(result.project)).project, result.project)
        self.assertEqual([c.result for c in result.project.conversations[0].choices], [2, 3, 4])

    def test_broken_goto_navigates_to_node(self):
        d = self.data(); d["conversations"][0]["nodes"][0]["choices"][0]["goto"] = "missing"
        v = self.backend.validate(d)
        self.assertFalse(v.valid)
        self.assertEqual(v.problems[0].path, ("conversations", 0, "nodes", 0))

    def test_duplicate_nodes_and_results_fail(self):
        for field in ["node", "result"]:
            d = self.data(); nodes = d["conversations"][0]["nodes"]
            if field == "node": nodes[1]["id"] = "opening"
            else: nodes[1]["choices"][0]["result"] = 2
            self.assertFalse(self.backend.validate(d).valid)

    def test_missing_entry_and_speaker_fail(self):
        for field, value in [("entry", "missing"), ("speaker", "missing")]:
            d = self.data(); d["conversations"][0][field] = value
            self.assertFalse(self.backend.validate(d).valid)

    def test_orphan_warning_is_navigable(self):
        d = self.data(); nodes = d["conversations"][0]["nodes"]
        nodes.append({"id": "orphan", "lines": [{"text": "Solo."}], "choices": [{"text": "Adiós.", "result": 5}]})
        v = self.backend.validate(d)
        self.assertTrue(v.valid)
        self.assertTrue(any(p.severity == "WARNING" and p.path == ("conversations", 0, "nodes", 2) for p in v.problems))

    def test_entry_without_path_to_return_blocks_build(self):
        d = self.data(); d["conversations"][0]["nodes"][0]["choices"] = [{"text": "Otra vez.", "goto": "opening"}]
        v = self.backend.validate(d)
        self.assertFalse(v.valid)
        self.assertTrue(any(p.severity == "ERROR" and p.path[-1] == 0 for p in v.problems))

    def test_nonentry_trap_is_warning(self):
        d = self.data(); nodes = d["conversations"][0]["nodes"]
        nodes[1]["choices"] = [{"text": "Siempre.", "goto": "identity"}]
        v = self.backend.validate(d)
        self.assertTrue(v.valid)
        self.assertTrue(any("camino" in p.message and p.severity == "WARNING" for p in v.problems))

    def test_invalid_return_and_goto_actions_fail(self):
        for value in [0, -1, True, 32768]:
            d = self.data(); d["conversations"][0]["nodes"][1]["choices"][0]["result"] = value
            self.assertFalse(self.backend.validate(d).valid)
        d = self.data(); d["conversations"][0]["nodes"][0]["choices"][0]["set_flag"] = "alliance"
        self.assertFalse(self.backend.validate(d).valid)

    def test_unknown_runtime_properties_are_rejected(self):
        for field in ["health", "clan", "inventory"]:
            d = self.data(); d["actors"][0][field] = 100
            self.assertFalse(self.backend.validate(d).valid)

    def test_event_references_and_bindings_fail(self):
        d = self.data(); d["events"].append({"when": "actor_clicked", "actor": "victoria", "actions": [{"start_conversation": "intro"}]})
        self.assertFalse(self.backend.validate(d).valid)  # conflicting actor binding
        d["actors"][0].pop("conversation"); d["events"][-1]["actions"][0]["start_conversation"] = "missing"
        self.assertFalse(self.backend.validate(d).valid)

    def test_event_ended_return_filters_are_validated(self):
        d = self.data(); d["events"].append({"when": "conversation_ended", "conversation": "intro", "result": 999, "actions": [{"set_flag": "alliance"}]})
        self.assertFalse(self.backend.validate(d).valid)
        d["events"][-1]["result"] = 3
        self.assertTrue(self.backend.validate(d).valid)

    def test_duplicate_flag_indices_and_unknown_conditions_fail(self):
        d = self.data(); d["state"]["flags"]["other"] = 1
        self.assertFalse(self.backend.validate(d).valid)
        d = self.data(); d["events"][0]["conditions"] = [{"flag": "missing", "is_set": False}]
        self.assertFalse(self.backend.validate(d).valid)

    def test_malformed_types_are_friendly_errors(self):
        for key, value in [("conversations", None), ("actors", 123), ("level", []), ("events", "bad")]:
            d = self.data(); d[key] = value
            self.assertFalse(self.backend.validate(d).valid)
        self.assertFalse(self.backend.validate([1]).valid)
        self.assertFalse(self.backend.validate("schema: [\n").valid)

    def test_utf8_internal_notes_and_runtime_encoding(self):
        d = self.data(); d["chronicle"]["description"] = "Notas 🧛\nSolo autoría"
        self.assertTrue(self.backend.validate(d).valid)
        d["conversations"][0]["nodes"][0]["lines"][0]["text"] = "Hola 🧛"
        self.assertFalse(self.backend.validate(d).valid)

    def test_document_atomic_save_saveas_and_reopen(self):
        doc = Document(self.ws, self.data())
        self.assertTrue(doc.modified)
        path = self.area / "roundtrip.yaml"; doc.save(path)
        self.assertFalse(doc.modified)
        doc.data["chronicle"]["name"] = "Otra crónica"
        self.assertTrue(doc.modified)
        other = self.area / "saved_as.yaml"; doc.save(other)
        self.assertEqual(doc.path, other.resolve())
        self.assertEqual(Document.load(self.ws, other).data, doc.data)
        self.assertNotEqual(Document.load(self.ws, path).data, doc.data)
        self.assertEqual(list(self.area.glob("*.tmp")), [])

    def test_atomic_failure_keeps_saved_file(self):
        path = self.area / "atomic.yaml"; doc = Document(self.ws, self.data()); doc.save(path)
        original = path.read_bytes(); doc.data["chronicle"]["name"] = "Cambio"
        with patch("rcm.document.os.replace", side_effect=OSError("test disk failure")):
            with self.assertRaises(OSError): doc.save()
        self.assertEqual(path.read_bytes(), original)
        self.assertTrue(doc.modified)
        self.assertEqual(list(self.area.glob("*.tmp")), [])

    def test_document_recovery_preserves_original_until_save(self):
        path = self.area / "recovery.yaml"; doc = Document(self.ws, self.data()); doc.save(path)
        original = path.read_bytes(); doc.data["chronicle"]["name"] = "Recuperado"; doc.autosave()
        self.assertEqual(path.read_bytes(), original)
        loaded = Document.load(self.ws, path); self.assertTrue(loaded.recover())
        self.assertEqual(loaded.data["chronicle"]["name"], "Recuperado")
        self.assertTrue(loaded.modified); loaded.save()
        self.assertFalse(loaded.recovery_path.exists())

    def test_document_rejects_corrupt_shape_but_opens_broken_reference(self):
        path = self.area / "draft.yaml"; d = self.data(); d["actors"] = [123]
        self.ws.write(path, source_text(d))
        with self.assertRaises(ValueError): Document.load(self.ws, path)
        d = self.data(); d["conversations"][0]["entry"] = "missing"
        self.ws.write(path, source_text(d)); doc = Document.load(self.ws, path)
        self.assertFalse(self.backend.validate(doc.data).valid)

    def test_rename_rewrites_references(self):
        doc = Document(self.ws, self.data())
        doc.rename("actors", 0, "vicky")
        self.assertEqual(doc.data["events"][0]["actions"][0]["spawn"], "vicky")
        self.assertEqual(doc.data["conversations"][0]["nodes"][1]["lines"][0]["speaker"], "vicky")
        doc.rename("conversations", 0, "hello")
        self.assertEqual(doc.data["actors"][0]["conversation"]["default"], "hello")
        doc.rename_flag("alliance", "pact")
        self.assertEqual(doc.data["conversations"][0]["nodes"][1]["choices"][0]["set_flag"], "pact")
        doc.rename_node(0, 1, "proposal")
        self.assertEqual(doc.data["conversations"][0]["nodes"][0]["choices"][0]["goto"], "proposal")
        self.assertTrue(self.backend.validate(doc.data).valid)

    def test_document_snapshot_and_scope(self):
        doc = Document(self.ws, self.data()); snapshot = doc.snapshot()
        snapshot["actors"][0]["name"] = "Changed"
        self.assertEqual(doc.data["actors"][0]["name"], "Victoria")
        for target in [ROOT.parent / "outside.yaml", self.ws.game / "RCM/east_demo/project.yaml"]:
            with self.assertRaises(ValueError): doc.save(target)

    def test_resource_catalogue_real_ids_and_availability(self):
        self.assertEqual(self.backend.level_label("EastLondon"), "East London")
        self.assertTrue(self.backend.level_usable("EastLondon"))
        self.assertFalse(self.backend.level_usable("InventedMap"))
        self.assertTrue(any(t["id"] == "businessWoman" and t["archive"] == "Resource.nob" for t in self.backend.resources["templates"]))

    def test_phase1_title_fix_and_checkpoint_regression(self):
        folder = ROOT / "build/east_demo"
        Scene.read((folder / "runtime/scenes/R_east_demo.nsd").read_bytes())
        strings = (folder / "runtime/strings/_R_east_demo.nls").read_text(encoding="cp1252")
        self.assertIn("R_east_demoS Redemption Chronicle Maker: Londres nuevo", strings)
        self.assertIn("R_east_demoL Redemption Chronicle Maker: Londres nuevo", strings)
        # The large checkpoint was intentionally retired during cleanup.
        # Retained native deployment hashes still pin the original class bytes.
        baseline=json.loads((ROOT/'tests/fixtures/baselines/native_class_hashes.json').read_text(encoding='utf8'))
        for record in baseline['files']:
            if record['path'].endswith('.class'):
                self.assertEqual(hashlib.sha256((folder/'runtime'/record['path']).read_bytes()).hexdigest(),record['sha256'])
        scene=Scene.read((folder/'runtime/scenes/R_east_demo.nsd').read_bytes())
        original=(ROOT/'research/original/Resource.nob/scenes/EAST_28_1.nsd').read_bytes()
        self.assertEqual(scene.environment,bytes(16)+original[-176:])
        self.assertEqual(len(scene.entities),1)

    def test_historical_gui_fixture_cli_build_matches_pinned_package(self):
        # Pinned regression baselines belong with fixtures, never disposable build/.
        evidence=json.loads((ROOT/'tests/fixtures/baselines/gui_distribution.json').read_text(encoding='utf8'))
        report=next(row for row in evidence if row['project']=='chronicles/editor_acceptance/project.yaml')
        self.assertTrue(report['source_unchanged'])
        project=ROOT/'tests/fixtures/chronicles/editor_acceptance/project.yaml'
        cmd = [sys.executable, str(ROOT / "tools/rcm.py"), "build", str(project)]
        run = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        package = ROOT / "build/editor_demo/editor_demo_distribution.zip"
        # Keep the original GUI evidence intact. Review the runtime migration
        # separately: NOT libraries now preload before LAN restores inventory.
        expected = json.loads((project.parent/'expected.json').read_text(encoding='utf8'))
        self.assertEqual(report['sha256'], expected['original_gui_distribution_sha256'])
        self.assertEqual(hashlib.sha256(project.read_bytes()).hexdigest(), expected['source_sha256'])
        self.assertEqual(hashlib.sha256(package.read_bytes()).hexdigest(), expected['distribution_sha256'])

    def test_graph_packaging_references_entry_speakers_and_nvo(self):
        d = self.data(); d["chronicle"]["id"] = "graph_check"
        d["conversations"][0]["entry"] = "identity"
        progress = []; report = self.backend.build(d, progress=progress.append)
        self.assertEqual(set(report["class_versions"].values()), {"45.3"})
        self.assertGreaterEqual(len(progress), 5)
        folder = ROOT / "build/graph_check"
        with zipfile.ZipFile(folder / "graph_check.nob") as z:
            nco = z.read("conversations/R_graph_check_intro.nco").decode("cp1252").splitlines()
            self.assertEqual(nco[1], "EVENT: ev_identity")
            event_ids = {line.split()[1] for line in nco if line.startswith("EVENT:")}
            nvo = {line.split()[0] for line in z.read("strings/R_graph_check.nvo").decode("cp1252").splitlines()}
            for line in nco:
                if line.startswith(("LINE:", "ANSWERGOTO:", "ANSWERRETURN:")):
                    self.assertIn(line.split()[1], nvo)
                if line.startswith("ANSWERGOTO:"):
                    self.assertIn(line.split()[2], event_ids)
            self.assertFalse(any(n.lower().endswith((".nil", ".class")) for n in z.namelist()))

    def test_build_failure_reports_failure(self):
        d = self.data(); d["chronicle"]["id"] = "failed_check"
        with patch("rcm.service.build", side_effect=ValueError("test compile failure")):
            with self.assertRaises(ValueError): self.backend.build(d)
        report = json.loads((ROOT / "build/failed_check/build_report.json").read_text(encoding="utf8"))
        self.assertEqual(report["status"], "failed")

    def test_advanced_events_generated_java_scenarios(self):
        d = self.data(); d["chronicle"]["id"] = "event_test"
        d["actors"][0].pop("conversation")
        d["state"]["flags"].update(stage=2, seen=3)
        d["events"] = [
            {"when": "scene_start", "conditions": [{"flag": "stage", "is_set": False}], "actions": [{"spawn": "victoria"}, {"set_flag": "stage"}]},
            {"when": "actor_clicked", "actor": "victoria", "conditions": [{"flag": "alliance", "is_set": False}], "actions": [{"start_conversation": "intro"}]},
            {"when": "actor_clicked", "actor": "victoria", "conditions": [{"flag": "alliance", "is_set": True}], "actions": [{"start_conversation": "ally"}]},
            {"when": "conversation_ended", "conversation": "intro", "result": 3, "conditions": [{"flag": "alliance", "is_set": True}], "actions": [{"set_flag": "seen"}]}]
        report = self.backend.build(d)
        self.assertEqual(report["class_versions"]["R_event_test_Scene"], "45.3")
        out = ROOT / "build/tests/java_events"; out.mkdir(parents=True, exist_ok=True)
        source = ROOT / "build/event_test/generated/java/R_event_test_Scene.java"
        compile_run = subprocess.run(["javac", "-d", str(out), str(ROOT / "tests/java/MockEngine.java"), str(ROOT / "tests/java/EventHarness.java"), str(source)], capture_output=True, text=True)
        self.assertEqual(compile_run.returncode, 0, compile_run.stderr)
        run = subprocess.run(["java", "-cp", str(out), "EventHarness"], cwd=ROOT / "build/tests", capture_output=True, text=True)
        self.ws.write("build/tests/event_harness.log", run.stdout + run.stderr)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("PASS:", run.stdout)


if __name__ == "__main__":
    unittest.main()
