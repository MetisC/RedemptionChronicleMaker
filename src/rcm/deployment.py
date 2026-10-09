"""Controlled user-directory deployment. Original game files are never targets."""
from pathlib import Path
import hashlib,json,os,subprocess,time

def installation(path):
    path=Path(path).resolve()
    if not (path/'Vampire.exe').is_file() or not (path/'Resource.nob').is_file():raise ValueError('No es una instalación de Redemption')
    return path

def safe_target(game,path):
    root=game/'RCM';candidate=Path(path)
    if not candidate.resolve().is_relative_to(root.resolve()):raise ValueError('Deploy fuera de RCM')
    for part in [candidate,*candidate.parents]:
        if part==game:break
        if part.is_symlink() or (hasattr(part,'is_junction') and part.is_junction()):raise ValueError('Deploy a través de enlace')
        if part.is_file() and part.stat().st_nlink!=1:raise ValueError('Deploy sobre hardlink')
    return candidate

def game_running():
    if os.name!='nt':return False
    result=subprocess.run(['tasklist','/FI','IMAGENAME eq Vampire.exe','/FO','CSV','/NH'],capture_output=True,text=True)
    if result.returncode:raise ValueError('No se pudo comprobar si Vampire está abierto')
    return 'vampire.exe' in result.stdout.casefold()

def save_settings(ws,path):
    from .startup import settings
    data=settings(ws);path=installation(path);data['installation']=str(path);ws.write('cache/game_settings.json',json.dumps(data,indent=2));return path

def default_game(root):
    from .startup import settings
    from .paths import Workspace
    config=settings(Workspace(Path(root)))
    if config.get('installation') and (Path(config['installation'])/'Vampire.exe').is_file():return Path(config['installation'])
    detected=Path(r'H:\GOG\Vampire The Masquerade - Redemption')
    return detected if (detected/'Vampire.exe').is_file() else None

def configured_game(ws):
    path=ws.output('cache/game_settings.json')
    selected=ws.game or (json.loads(path.read_text(encoding='utf8'))['installation'] if path.exists() else None)
    if not selected:raise ValueError('Selecciona la instalación en Ruta del juego')
    return installation(selected)

def deploy(ws,chronicle,directory=None,current_source=None):
    from .model import identifier
    identifier(chronicle,'Crónica',18);game=configured_game(ws)
    previous=safe_target(game,game/'RCM'/(directory or chronicle)/'.rcm_deployment.json')
    if previous.is_file() and 'owners' in json.loads(previous.read_text(encoding='utf8')):
        from .deployment_many import deploy_many
        return deploy_many(ws,[chronicle],directory or chronicle,{chronicle:current_source} if current_source is not None else None,preserve_siblings=True)
    if game_running():raise ValueError('Cierra Vampire antes de actualizar la crónica')
    root=ws.output(Path('build')/chronicle);report=json.loads((root/'build_report.json').read_text(encoding='utf8'))
    if report.get('status')!='compiled-unverified-in-game':raise ValueError('Haz un build compilado válido antes de deploy')
    if current_source is not None:
        from .service import source_fingerprint,build_inputs_fingerprint
        if report.get('authoring_source_sha256')!=source_fingerprint(current_source):raise ValueError('El proyecto cambió desde el build. Vuelve a compilar antes de Deploy')
        if report.get('build_inputs_sha256')!=build_inputs_fingerprint(ws,current_source):raise ValueError('Los archivos propios cambiaron desde el build; vuelve a compilar')
    dest=safe_target(game,game/'RCM'/(directory or chronicle));files={}
    for relative,record in report['distribution_files'].items():
        from .packages import archive_path
        archive_path(relative)
        path=Path(relative)
        if path.is_absolute() or '..' in path.parts:raise ValueError('Ruta insegura en manifest')
        data=ws.output(root/'bundle'/path).read_bytes()
        if hashlib.sha256(data).hexdigest()!=record['sha256']:raise ValueError('El build cambió después de compilar')
        files[safe_target(game,dest/path)]=data
    # Ownership belongs to the deployment directory, so changing campaign IDs
    # cannot leave another selectable chronicle behind. Foreign files stay put.
    manifest=safe_target(game,dest/'.rcm_deployment.json');obsolete=[]
    if manifest.is_file():
        previous=json.loads(manifest.read_text(encoding='utf8'))
        if previous.get('format')!=1 or not isinstance(previous.get('files'),dict):raise ValueError('Manifest de deploy inválido')
        for relative,digest in previous['files'].items():
            from .packages import archive_path
            archive_path(relative)
            target=safe_target(game,dest/relative)
            if target in files or not target.exists():continue
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=digest:raise ValueError('Archivo de deploy modificado; se conserva: '+relative)
            obsolete.append(target)
    ownership={'format':1,'chronicle':chronicle,'files':{str(p.relative_to(dest)).replace('\\','/'):hashlib.sha256(d).hexdigest() for p,d in files.items()}}
    files[manifest]=json.dumps(ownership,indent=2).encode('utf8')
    # Check every destination before making any mutation.
    backup=ws.output(Path('research/runtime_test/backups')/('deploy_'+chronicle+'_'+str(time.time_ns())+'.zip'));backup.parent.mkdir(parents=True,exist_ok=True)
    from .file_transaction import replace_files
    replace_files(files,obsolete,backup,game/'RCM',lambda p:safe_target(game,p))
    logdir=safe_target(game,game/'RCM'/chronicle);logdir.mkdir(parents=True,exist_ok=True)
    result={'chronicle':chronicle,'destination':str(dest),'backup':str(backup),'removed_owned_files':[str(p.relative_to(game/'RCM')) for p in obsolete],'files':{str(p.relative_to(game/'RCM')):hashlib.sha256(d).hexdigest() for p,d in files.items()},'native_engine_test':False}
    ws.write('research/runtime_test/deployment_'+chronicle+'.json',json.dumps(result,indent=2));return result

def run_game(ws,chronicle):
    from .model import identifier
    identifier(chronicle,'Crónica',18);game=configured_game(ws)
    if game_running():raise ValueError('Vampire ya está abierto')
    from .shortcut import launch_info
    shortcut=launch_info(ws)
    if shortcut:
        if not (shortcut['directory']/(chronicle+'.nob')).is_file():raise ValueError('Despliega primero la crónica en la carpeta que utiliza tu acceso: RCM/'+shortcut['relative'])
        os.startfile(str(shortcut['shortcut']))
        from types import SimpleNamespace
        return SimpleNamespace(pid=None,shortcut=str(shortcut['shortcut']))
    dest=safe_target(game,game/'RCM'/chronicle)
    if not (dest/(chronicle+'.nob')).is_file():raise ValueError('Primero despliega la crónica')
    # Explicit button/user command requests the visible game; no helper console.
    return subprocess.Popen([str(game/'Vampire.exe'),'-user','RCM\\'+chronicle],cwd=game)
