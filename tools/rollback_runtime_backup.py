"""Restore one previously deployed RCM backup, never original game files."""
from pathlib import Path
import argparse,json,sys,zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.deployment import default_game,game_running,safe_target
from rcm.file_transaction import replace_files
from rcm.paths import Workspace

def main():
    ap=argparse.ArgumentParser();ap.add_argument('backup',type=Path);args=ap.parse_args()
    game=default_game(ROOT)
    if game is None:raise ValueError('No se encontró la instalación')
    if game_running():raise ValueError('Cierra Vampire antes de restaurar RCM')
    backup=args.backup.resolve()
    if not backup.is_file():raise ValueError('Backup inexistente')
    dest=safe_target(game,game/'RCM'/'east_demo')
    targets={}
    with zipfile.ZipFile(backup) as z:
        for name in z.namelist():
            prefix='east_demo/'
            if not name.startswith(prefix) or name.endswith('/'):
                continue
            target=safe_target(game,game/'RCM'/name)
            targets[target]=z.read(name)
    if not targets:raise ValueError('Backup sin archivos east_demo')
    ws=Workspace(ROOT,game)
    rollback_backup=ws.output('research/runtime_test/backups/rollback_'+str(__import__('time').time_ns())+'.zip')
    replace_files(targets,[],rollback_backup,game/'RCM',lambda p:safe_target(game,p))
    result={'restored_from':str(backup),'destination':str(dest),'files':len(targets),'current_state_backup':str(rollback_backup),'native_engine_test':False}
    ws.write('research/runtime_test/rollback.json',json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
