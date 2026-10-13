"""Inspect and retire our per-chronicle deployments without adopting legacy folders."""
import hashlib
import json
import time
from .deployment import configured_game,safe_target,game_running


def list_deployments(ws):
    game=configured_game(ws);rows=[]
    for path in (game/'RCM').glob('*/.rcm_deployment.json'):
        safe_target(game,path)
        try:manifest=json.loads(path.read_text(encoding='utf8'))
        except (OSError,ValueError):continue
        if manifest.get('format')!=1 or manifest.get('chronicle')!=path.parent.name:continue
        from .packages import archive_path
        files=manifest.get('files')
        if not isinstance(files,dict):continue
        modified=[]
        for name,digest in files.items():
            archive_path(name);target=safe_target(game,path.parent/name)
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=digest:modified.append(name)
        rows.append(dict(id=path.parent.name,path=path.parent,manifest=manifest,modified=modified))
    return rows


def remove_deployment(ws,ident):
    if game_running():raise ValueError('Cierra Vampire antes de retirar la crónica')
    row=next((r for r in list_deployments(ws) if r['id']==ident),None)
    if row is None:raise ValueError('No es una crónica administrada por RCM')
    game=configured_game(ws);obsolete=[];retained={}
    for name,digest in row['manifest']['files'].items():
        target=safe_target(game,row['path']/name)
        if name in row['modified']:retained[name]=digest
        elif target.exists():obsolete.append(target)
    manifest=safe_target(game,row['path']/'.rcm_deployment.json')
    from .file_transaction import replace_files
    targets={}
    if retained:
        updated=dict(row['manifest'],files=retained);targets[manifest]=json.dumps(updated,indent=2).encode('utf8')
    else:obsolete.append(manifest)
    backup=ws.output('backups/deployments/retire_'+str(time.time_ns())+'.zip')
    replace_files(targets,obsolete,backup,game/'RCM',lambda p:safe_target(game,p))
    return dict(retained=row['modified'],backup=str(backup))
