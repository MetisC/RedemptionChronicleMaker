"""Verify the delivered examples, executable and tutorial without game input."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'cache/vendor'), str(ROOT/'cache/devtools')]
from rcm import __version__
from rcm.paths import Workspace
from rcm.deployment import default_game, safe_target
from rcm.service import build_inputs_fingerprint, source_fingerprint
from rcm.document import Document
import pefile


def main():
    ws = Workspace(ROOT)
    app = ws.output('build/portable/RedemptionChronicleMaker')
    exe = app/'RedemptionChronicleMaker.exe'
    pe = pefile.PE(str(exe))
    resource_types = {e.id for e in pe.DIRECTORY_ENTRY_RESOURCE.entries}
    pe.close()
    assert {3,14}.issubset(resource_types), 'Falta el icono Windows'
    for folder in ['tutorial','mini_chronicle']:
        for source in (ROOT/'chronicles'/folder).rglob('*'):
            if source.is_file():
                relative = source.relative_to(ROOT/'chronicles'/folder)
                for dest in [app/'examples'/folder, app/'workspace/chronicles'/folder]:
                    if relative.as_posix()=='project.yaml' and dest.is_relative_to(app/'workspace'):
                        # The editor saves YAML with its own formatting before
                        # compiling. Compare authored data, not whitespace.
                        expected = Document.load(ws,source).snapshot()
                        actual = Document.load(ws,dest/relative).snapshot()
                        assert source_fingerprint(actual)==source_fingerprint(expected), str(dest/relative)
                    else:
                        assert (dest/relative).read_bytes()==source.read_bytes(), str(dest/relative)
    assert sorted(p.name for p in (app/'workspace/chronicles').iterdir())==['mini_chronicle','tutorial']
    assert not (app/'workspace/chronicles/tutorial/project.yaml.autosave').exists(), 'Recuperación antigua pendiente'
    source = Document.load(ws,'chronicles/tutorial/project.yaml').snapshot()
    report = json.loads(ws.output('build/rcm_tutor/build_report.json').read_text(encoding='utf8'))
    assert report['authoring_source_sha256']==source_fingerprint(source)
    assert report['build_inputs_sha256']==build_inputs_fingerprint(ws,source)
    assert report['status']=='compiled-unverified-in-game' and not report['geometry_in_package']
    assert set(report['class_versions'].values())=={'45.3'}
    game = default_game(ROOT)
    destination = safe_target(game,game/'RCM/east_demo')
    manifest = json.loads(safe_target(game,destination/'.rcm_deployment.json').read_text(encoding='utf8'))
    for name in manifest['owners']['rcm_tutor']:
        installed = safe_target(game,destination/name).read_bytes()
        assert hashlib.sha256(installed).hexdigest()==manifest['files'][name]
        assert installed==ws.output('build/rcm_tutor/bundle/'+name).read_bytes()
        assert installed==(app/'workspace/build/rcm_tutor/bundle'/name).read_bytes()
    probe = json.loads(ws.output('research/round0/guided_tutorial/portable_probe.json').read_text(encoding='utf8'))
    assert probe['valid_project'] and probe['process_exit_code']==0
    diagnostics = json.loads((app/'workspace/build/diagnostics/report.json').read_text(encoding='utf8'))
    assert diagnostics['rcm']==__version__
    evidence = ws.output('research/round0/guided_tutorial')
    full = json.loads((evidence/'final_quality/test_report.json').read_text(encoding='utf8'))
    assert full['successful'] and full['tests']>=230
    gui = json.loads(ws.output('research/round0/gui/report.json').read_text(encoding='utf8'))
    assert gui['success'] and gui['real_gl']
    spatial = json.loads((evidence/'spatial_check.json').read_text(encoding='utf8'))
    quality = json.loads(ws.output('build/tests/quality_report.json').read_text(encoding='utf8'))
    assert quality['successful']
    result = dict(version=__version__,title=source['chronicle']['name'],
                  executable=str(exe),exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
                  windows_icon_verified=True,examples_match_sources=True,
                  seven_lessons=len(source['quests'][0]['steps']),
                  deployment_matches_build=True,installed_files=len(manifest['owners']['rcm_tutor']),
                  portable_compilation=probe,source_gui_real_gl=gui['real_gl'],
                  floor_and_headroom_positions=len(spatial),full_regressions=full,
                  static_checks_passed=quality['successful'],native_engine_test=False)
    ws.write(evidence/'delivery.json',json.dumps(result,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
