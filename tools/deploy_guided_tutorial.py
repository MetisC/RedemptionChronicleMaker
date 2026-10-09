"""Update only the guided tutorial in the existing RCM shortcut directory."""
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.deployment import default_game, game_running, safe_target
from rcm.deployment_many import deploy_many
from rcm.document import Document
from rcm.service import Backend
from rcm.catalogue import verify_sources
from repair_lan_templates import saved_templates, startup_templates


def main():
    game = default_game(ROOT)
    if game is None:
        raise ValueError('No se encuentra la instalación')
    if game_running():
        raise ValueError('Cierra Vampire antes de actualizar el tutorial')
    ws = Workspace(ROOT, game)
    source = Document.load(ws, 'chronicles/tutorial/project.yaml').snapshot()
    validation = Backend(ws).validate(source)
    if not validation.valid:
        raise ValueError('Tutorial inválido')
    bundle = ws.output('build/rcm_tutor/bundle/rcm_tutor.nob').read_bytes()
    with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
        payload = {n: archive.read(n) for n in archive.namelist()}
    names = startup_templates(payload)
    profiles = {p: p.read_bytes() for p in (game/'Crypt').glob('*.npf')}
    required = {r['template'].casefold() for data in profiles.values()
                for r in saved_templates(data)
                if r['template'].casefold().startswith('r_rcm_tutor_')}
    if required - names:
        raise ValueError('El personaje conserva plantillas ausentes: '+str(sorted(required-names)))
    before = verify_sources(ws, game)
    result = deploy_many(ws, ['rcm_tutor'], 'east_demo',
                         current_sources={'rcm_tutor': source}, preserve_siblings=True)
    target = safe_target(game, game/'RCM/east_demo/rcm_tutor.nob')
    if target.read_bytes() != bundle:
        raise ValueError('Paquete desplegado distinto del build')
    manifest = json.loads(safe_target(game, target.parent/'.rcm_deployment.json').read_text(encoding='utf8'))
    for name, digest in manifest['files'].items():
        data = safe_target(game, target.parent/name).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError('Archivo instalado distinto del manifiesto: '+name)
    for path, data in profiles.items():
        if path.read_bytes() != data:
            raise ValueError('El perfil ha cambiado durante el despliegue')
    after = verify_sources(ws, game)
    record = dict(deployment=result, title=source['chronicle']['name'],
                  installed_sha256=hashlib.sha256(bundle).hexdigest(),
                  files_checked=len(manifest['files']),
                  saved_templates_retained=sorted(required),
                  saved_profiles_unchanged=len(profiles),
                  originals_before=before, originals_after=after,
                  new_game_required=True, native_engine_test=False)
    ws.write('research/round0/guided_tutorial/deployment.json', json.dumps(record, indent=2))
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
