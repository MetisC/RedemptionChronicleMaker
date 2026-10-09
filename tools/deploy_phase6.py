"""Prepare native acceptance using only authorized RCM destinations."""
from pathlib import Path
import json,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.document import Document
from rcm.catalogue import verify_sources
from rcm.deployment import game_running,deploy,default_game
from rcm.packages import create_package,install_package
from rcm.shortcut import launch_info


def main():
    game=default_game(ROOT)
    if not game:raise ValueError('No se encuentra la instalación configurada')
    ws=Workspace(ROOT,game)
    if game_running():raise ValueError('Cierra Vampire antes de preparar la prueba')
    before=verify_sources(ws,game);shortcut=launch_info(ws)
    if not shortcut:raise ValueError('No se encuentra el acceso exacto del escritorio')
    backend=Backend(ws);builds={};deployments=[]
    for source in ['tests/fixtures/chronicles/phase5_demo/project.yaml','tests/fixtures/chronicles/system_test/project.yaml']:
        root=Document.load(ws,source).snapshot();report=backend.build(root);ident=report['chronicle'];builds[ident]=report['status']
        archive=ws.output('build/'+ident+'/'+ident+'.rcmpack');create_package(ws,ident,archive)
        if ident=='rcm_system':deployments.append(install_package(ws,archive,True))
        else:deployments.append(deploy(ws,ident,current_source=root))
        deployments.append(deploy(ws,ident,shortcut['relative'],current_source=root))
    after=verify_sources(ws,game)
    result={'created_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'game_closed_before_deploy':True,'builds':builds,'deployments':deployments,'shortcut':str(shortcut['shortcut']),'playtest_directory':str(shortcut['directory']),'originals_before':before,'originals_after':after,'native_engine_test':False}
    ws.write('research/phase6/deployment.json',json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
