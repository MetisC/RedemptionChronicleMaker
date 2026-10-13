"""One status model and one save/validate/build/deploy/run product circuit."""
from dataclasses import dataclass
import hashlib
import json
import time

from .service import source_fingerprint, build_inputs_fingerprint


@dataclass
class ProjectStatus:
    dirty: bool = False
    valid: bool | None = None
    build: str = 'missing'
    deploy: str = 'missing'
    game_running: bool = False
    last_playtest: dict | None = None


def current_build(ws, source):
    ident = source['chronicle']['id']
    try:
        report = json.loads(ws.output('build/'+ident+'/build_report.json').read_text(encoding='utf8'))
        if report.get('status') != 'compiled-unverified-in-game':return None
        if report.get('authoring_source_sha256') != source_fingerprint(source) or report.get('build_inputs_sha256') != build_inputs_fingerprint(ws,source):return None
        for relative, row in report['distribution_files'].items():
            from .packages import archive_path
            archive_path(relative)
            if hashlib.sha256(ws.output('build/'+ident+'/bundle/'+relative).read_bytes()).hexdigest() != row['sha256']:return None
        return report
    except (OSError,ValueError,KeyError):return None


def current_deploy(ws, report):
    from .deployment import configured_game,safe_target
    try:
        game = configured_game(ws); dest = safe_target(game,game/'RCM'/report['chronicle'])
        manifest = json.loads((dest/'.rcm_deployment.json').read_text(encoding='utf8'))
        expected = {name:row['sha256'] for name,row in report['distribution_files'].items()}
        actual=manifest.get('files',{})
        from .profile_compatibility import profile_signature
        if manifest.get('profile_refs_sha256')!=profile_signature(game):return False
        if manifest.get('chronicle') != report['chronicle'] or any(actual.get(k)!=v for k,v in expected.items()):return False
        if set(actual)-set(expected)-set(manifest.get('compatibility_files',[])):return False
        return all(hashlib.sha256(safe_target(game,dest/name).read_bytes()).hexdigest() == digest for name,digest in actual.items())
    except (OSError,ValueError,KeyError):return False


def prepare_playtest(backend, source, progress=lambda _:None):
    """Source was committed/saved by UI before calling; never launch on failure."""
    from .deployment import game_running,deploy
    validation = backend.validate(source)
    if not validation.valid:raise ValueError('\n'.join(p.message for p in validation.problems if p.severity == 'ERROR'))
    if game_running():raise ValueError('Cierra Vampire antes de iniciar otra prueba. No se ha cerrado el juego automáticamente.')
    report = current_build(backend.ws,source)
    built = report is None
    if built:
        progress('Construyendo la crónica…'); report = backend.build(source,progress=progress)
    deployed = not current_deploy(backend.ws,report)
    if deployed:
        progress('Preparando la prueba en Redemption…')
        deploy(backend.ws,source['chronicle']['id'],current_source=source)
    return dict(report=report,built=built,deployed=deployed)


def launch_playtest(ws, ident):
    from .deployment import run_game
    process = run_game(ws,ident)
    record = dict(chronicle=ident,started=time.time(),pid=process.pid,ended=None,exit_code=None,native_verified=False)
    ws.write('cache/last_playtest.json',json.dumps(record,indent=2))
    return process,record


def finish_playtest(ws, record, code):
    record = dict(record,ended=time.time(),exit_code=code)
    ws.write('cache/last_playtest.json',json.dumps(record,indent=2))
    return record
