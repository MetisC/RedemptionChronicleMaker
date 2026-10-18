"""Multiple owned chronicles under one existing -user directory."""
import hashlib,json,time
from .deployment import configured_game,game_running,safe_target
from .packages import archive_path
from .model import identifier

def deploy_many(ws,chronicles,directory,current_sources=None,preserve_siblings=False):
    if not chronicles or len(set(chronicles))!=len(chronicles):raise ValueError('Lista de crónicas inválida')
    game=configured_game(ws)
    if game_running():raise ValueError('Cierra Vampire antes de actualizar recursos')
    dest=safe_target(game,game/'RCM'/directory);manifest=safe_target(game,dest/'.rcm_deployment.json')
    files={};owners={};shared=set();current_sources=current_sources or {}
    for ident in chronicles:
        identifier(ident,'Crónica',18);root=ws.output('build/'+ident);report=json.loads((root/'build_report.json').read_text(encoding='utf8'))
        if report.get('status')!='compiled-unverified-in-game':raise ValueError('Build compilado necesario: '+ident)
        if ident in current_sources:
            from .service import source_fingerprint,build_inputs_fingerprint
            source=current_sources[ident]
            if report.get('authoring_source_sha256')!=source_fingerprint(source) or report.get('build_inputs_sha256')!=build_inputs_fingerprint(ws,source):raise ValueError('Proyecto cambiado desde build: '+ident)
        owners[ident]=list(report['distribution_files'])
        from .wtd import local_dependencies
        for name,data in local_dependencies(ws,report).items():
            target=safe_target(game,dest/name)
            if target in files and files[target]!=data:raise ValueError('Imported content packs conflict')
            files[target]=data;shared.add(name)
        for relative,record in report['distribution_files'].items():
            archive_path(relative);target=safe_target(game,dest/relative);data=ws.output(root/'bundle'/relative).read_bytes()
            if hashlib.sha256(data).hexdigest()!=record['sha256']:raise ValueError('Build modificado: '+relative)
            if target in files and files[target]!=data:raise ValueError('Recursos compartidos incompatibles: '+relative)
            files[target]=data
    previous=json.loads(manifest.read_text(encoding='utf8')) if manifest.is_file() else dict(format=1,files={})
    if previous.get('format')!=1 or not isinstance(previous.get('files'),dict):raise ValueError('Manifest inválido')
    if preserve_siblings:
        for ident,names in previous.get('owners',{}).items():
            if ident in chronicles:continue
            owners[ident]=names
            for relative in names:
                archive_path(relative);target=safe_target(game,dest/relative);data=target.read_bytes()
                if hashlib.sha256(data).hexdigest()!=previous['files'].get(relative):raise ValueError('Crónica conservada modificada: '+relative)
                if target in files and files[target]!=data:raise ValueError('Cambiaría un recurso de otra crónica: '+relative)
                files[target]=data
    from .profile_compatibility import compatibility_files,profile_signature
    compatibility=compatibility_files(game,[data for p,data in files.items() if p.suffix=='.nob'])
    for name,data in compatibility.items():
        target=safe_target(game,dest/name)
        if target not in files:files[target]=data
    for target,data in files.items():
        if target.exists():
            digest=hashlib.sha256(target.read_bytes()).hexdigest()
            owned=previous['files'].get(target.relative_to(dest).as_posix())
            if digest!=hashlib.sha256(data).hexdigest() and digest!=owned:raise ValueError('Archivo ajeno o modificado: '+target.name)
    obsolete=[]
    for relative,digest in previous['files'].items():
        archive_path(relative);target=safe_target(game,dest/relative)
        if target in files or not target.exists():continue
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=digest:raise ValueError('Archivo modificado: se conserva '+relative)
        obsolete.append(target)
    ownership=dict(format=1,chronicle=chronicles[0],chronicles=list(owners),owners=owners,shared_content_files=sorted(shared),compatibility_files=list(compatibility),profile_refs_sha256=profile_signature(game),files={p.relative_to(dest).as_posix():hashlib.sha256(d).hexdigest() for p,d in files.items()})
    files[manifest]=json.dumps(ownership,indent=2).encode('utf8')
    from .file_transaction import replace_files
    backup=ws.output('research/runtime_test/backups/deploy_multi_'+str(time.time_ns())+'.zip');backup.parent.mkdir(parents=True,exist_ok=True)
    replace_files(files,obsolete,backup,game/'RCM',lambda p:safe_target(game,p))
    for ident in owners:safe_target(game,game/'RCM'/ident).mkdir(parents=True,exist_ok=True)
    result=dict(chronicle=chronicles[0],chronicles=list(owners),destination=str(dest),backup=str(backup),removed_owned_files=[p.relative_to(game/'RCM').as_posix() for p in obsolete],native_engine_test=False)
    ws.write('research/runtime_test/deployment_multi.json',json.dumps(result,indent=2));return result
