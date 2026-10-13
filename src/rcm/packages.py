"""Bounded, verified archives. Filesystem writes stay in workspace or game/RCM."""
from pathlib import Path,PurePosixPath
import copy,hashlib,json,re,time,zipfile
from .model import identifier
from .service import source_text
from .generator import zip_bytes
from .deployment import configured_game,safe_target,game_running

def archive_path(name):
    if not isinstance(name,str) or any(ord(c)<32 or c in '\\:<>"|?*' for c in name):raise ValueError('Ruta insegura de paquete')
    p=PurePosixPath(name)
    if p.is_absolute() or any(x in {'','.', '..'} for x in name.split('/')) or any(x.rstrip(' .')!=x for x in p.parts):raise ValueError('Ruta insegura de paquete')
    for part in p.parts:
        if part.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in '123456789¹²³'],*[f'LPT{i}' for i in '123456789¹²³']}:raise ValueError('Ruta reservada por Windows')
    return p

def read_archive(path):
    try:return _read_archive(path)
    except (zipfile.BadZipFile,RuntimeError,NotImplementedError) as error:raise ValueError('Paquete ZIP corrupto, cifrado o no soportado') from error

def _read_archive(path):
    with zipfile.ZipFile(path) as z:
        items=z.infolist()
        if len(items)>2000 or sum(i.file_size for i in items)>64*1024*1024:raise ValueError('Paquete demasiado grande')
        result={};seen=set()
        for i in items:
            archive_path(i.filename)
            if i.filename.casefold() in seen:raise ValueError('Rutas duplicadas en paquete')
            if (i.external_attr>>16)&0o170000==0o120000:raise ValueError('Enlaces no permitidos en paquete')
            if i.is_dir():raise ValueError('Entradas directorio innecesarias en paquete')
            seen.add(i.filename.casefold());result[i.filename]=z.read(i)
        return result

def records(files):return {k:{'size':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in sorted(files.items())}

def verify_manifest(files,kind):
    try:m=json.loads(files['manifest.json'])
    except (KeyError,ValueError,UnicodeError) as e:raise ValueError('Manifest ausente o inválido') from e
    if not isinstance(m,dict) or m.get('format')!=1 or m.get('kind')!=kind:raise ValueError('Versión/tipo de paquete no soportados')
    identifier(m.get('id'),'package.id',18)
    if not isinstance(m.get('version'),str) or not re.fullmatch(r'\d+\.\d+\.\d+',m['version']):raise ValueError('Versión de paquete inválida')
    if m.get('files')!=records({k:v for k,v in files.items() if k!='manifest.json'}):raise ValueError('Contenido del paquete no coincide con su manifest SHA-256')
    if type(m.get('custom_code')) is not bool:raise ValueError('Indicador de código custom inválido')
    validate_metadata(m)
    requirement=m.get('requires_rcm','0.6.0')
    from . import __version__
    from .versioning import version_key
    if version_key(requirement)>version_key(__version__):raise ValueError('Paquete requiere otra versión de RCM: '+requirement)
    return m

def validate_metadata(m):
    for name in ('name','author','description','requires_game','requires_rcm'):
        if name in m and (not isinstance(m[name],str) or len(m[name])>8192):raise ValueError('Texto inválido en manifest: '+name)
    templates=m.get('templates',[])
    if not isinstance(templates,list) or any(not isinstance(x,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,30}',x) for x in templates) or len({x.casefold() for x in templates})!=len(templates):raise ValueError('Templates inválidos en manifest')
    dependencies=m.get('dependencies',[])
    if not isinstance(dependencies,list):raise ValueError('Dependencias inválidas')
    seen=set()
    for dep in dependencies:
        if not isinstance(dep,dict) or set(dep)!={'id','version'}:raise ValueError('Dependencia inválida')
        identifier(dep['id'],'dependency',18)
        if dep['id']==m['id'] or dep['id'].casefold() in seen or not isinstance(dep['version'],str) or not re.fullmatch(r'\d+\.\d+\.\d+',dep['version']):raise ValueError('Dependencia circular/duplicada o versión inválida')
        seen.add(dep['id'].casefold())

def export_project(ws,source,destination):
    root=copy.deepcopy(source);files={};owned=root.get('resources',{})
    for kind in ['scripts','textures']:
        for row in owned.get(kind,[]):
            path=ws.output(row['source']);name='assets/'+kind+'/'+row['id']+path.suffix;archive_path(name)
            if name in files:raise ValueError('Recurso exportado duplicado')
            files[name]=path.read_bytes();row['source']=name
    files['project.yaml']=source_text(root).encode('utf8');ident=identifier(root['chronicle']['id'],'chronicle',18)
    m=dict(format=1,kind='project',id=ident,name=root['chronicle']['name'],version=root.get('metadata',{}).get('version','0.1.0'),original_game_dependency='Redemption 1.1 installation',custom_code=bool(owned.get('scripts')),files=records(files))
    files['manifest.json']=json.dumps(m,ensure_ascii=False,indent=2).encode('utf8');verify_manifest(files,'project');return ws.write(destination,zip_bytes(files))

def import_project(ws,archive,directory):
    files=read_archive(archive);m=verify_manifest(files,'project');target=ws.output(directory)
    if target.exists() and any(target.iterdir()):raise ValueError('Importar requiere una carpeta vacía dentro del workspace')
    from .input_limits import parse_source
    allowed={'project.yaml','manifest.json'}
    if 'project.yaml' not in files:raise ValueError('Proyecto sin fuente YAML')
    root=parse_source(files['project.yaml'].decode('utf8'))
    if root['chronicle']['id']!=m['id']:raise ValueError('ID de fuente y manifest distintos')
    for kind in ['scripts','textures']:
        for row in root.get('resources',{}).get(kind,[]):
            name=row['source'];archive_path(name)
            if not name.startswith('assets/'+kind+'/') or name not in files:raise ValueError('Recurso propio ausente del proyecto')
            allowed.add(name);row['source']=str((target/name).relative_to(ws.root)).replace('\\','/')
    if set(files)!=allowed:raise ValueError('Archivos ajenos a fuentes propias en proyecto')
    if bool(root.get('resources',{}).get('scripts'))!=m['custom_code']:raise ValueError('Código custom no declarado')
    from .document import Document
    # Validate draft shape before any destination write; semantic errors remain editable.
    if root.get('schema')==2:
        from .campaign_document import CampaignDocument
        CampaignDocument.load_data(ws,root,None)
    else:
        from .document import draft_shape
        draft_shape(root)
    targets={ws.output(target/name):data for name,data in files.items() if name not in {'project.yaml','manifest.json'}}
    if m['custom_code']:targets[ws.output(target/'IMPORTED_CODE_NOTICE.txt')]='Este proyecto contiene Java propio. Revísalo antes de Build. Build compila; Ejecutar carga las clases en Redemption.'.encode('utf8')
    targets[ws.output(target/'project.yaml')]=source_text(root).encode('utf8')
    from .file_transaction import replace_files
    replace_files(targets,[],ws.output('research/package_backups/import_'+str(time.time_ns())+'.zip'),ws.root,ws.output)
    return Document.load(ws,target/'project.yaml')

def create_package(ws,chronicle,destination):
    identifier(chronicle,'chronicle',18);root=ws.output('build/'+chronicle);report=json.loads((root/'build_report.json').read_text(encoding='utf8'))
    if report.get('status')!='compiled-unverified-in-game':raise ValueError('El paquete requiere un build compilado válido')
    files={k:(root/'bundle'/archive_path(k)).read_bytes() for k in report['distribution_files']}
    if records(files)!=report['distribution_files']:raise ValueError('El build ha cambiado; recompila')
    source=json.loads((root/'model.json').read_text(encoding='utf8'));metadata=report.get('project_resources',{}).get('metadata',{})
    from . import __version__
    m=dict(format=1,kind='chronicle',id=chronicle,name=source.get('chronicle',{}).get('name',source.get('name',chronicle)),author=metadata.get('author',''),version=metadata.get('version','0.1.0'),description=metadata.get('description',source.get('chronicle',{}).get('description','')),requires_game=metadata.get('requires_game','Redemption 1.1'),requires_rcm=__version__,class_version='45.3',custom_code=bool(report.get('custom_scripts')),dependencies=metadata.get('dependencies',[]),templates=report.get('project_resources',{}).get('templates',[]),files=records(files))
    files['manifest.json']=json.dumps(m,ensure_ascii=False,indent=2).encode('utf8');ws.write(destination,zip_bytes(files));inspect_package(ws.output(destination));return m

def inspect_package(archive):
    files=read_archive(archive);m=verify_manifest(files,'chronicle')
    for name,data in files.items():
        if name=='manifest.json':continue
        if name==m['id']+'.nob':
            import io
            inner=read_archive(io.BytesIO(data))
            if any(Path(p).suffix.lower() not in {'.nsc','.nmf','.nss','.nco','.nvo','.nls','.ntx','.npc','.nai','.nqd','.nbs','.not','.nsd','.tga','.wav'} for p in inner):raise ValueError('El paquete contiene geometría/modelos/binarios originales o no admitidos')
        elif re.fullmatch(r'codex/[A-Za-z_][A-Za-z0-9_$]*\.class',name):
            if data[:8]!=b'\xca\xfe\xba\xbe\x00\x03\x00\x2d':raise ValueError('Clase no compatible con JVM 45.3')
        else:raise ValueError('Archivo de distribución no permitido: '+name)
    if m['id']+'.nob' not in files:raise ValueError('Paquete sin NOB de crónica')
    generated=re.compile(r'codex/R_'+re.escape(m['id'])+r'(?:_s\d+)?_(?:Scene|Passive)\.class')
    custom=any(name.startswith('codex/') and not generated.fullmatch(name) for name in files)
    if custom!=m['custom_code']:raise ValueError('Código custom no coincide con manifest')
    return m,files

def installed(ws):
    game=configured_game(ws);result={}
    for path in (game/'RCM').glob('*/.rcm_manifest.json'):
        safe_target(game,path);m=json.loads(path.read_text(encoding='utf8'))
        if not isinstance(m,dict) or m.get('kind')!='chronicle' or m.get('format')!=1:raise ValueError('Registro de instalación inválido')
        identifier(m['id'],'installed package',18);validate_metadata(m)
        if not isinstance(m.get('files'),dict):raise ValueError('Registro sin files')
        for name,row in m['files'].items():
            archive_path(name)
            if not isinstance(row,dict) or not isinstance(row.get('sha256'),str) or not re.fullmatch('[0-9a-f]{64}',row['sha256']):raise ValueError('Hash de registro inválido')
        if path.parent.name!=m['id']:raise ValueError('Registro instalado no coincide con carpeta')
        result[m['id']]=m
    return result

def install_plan(ws,archive,accept_custom_code=False):
    m,files=inspect_package(archive);game=configured_game(ws)
    if game_running():raise ValueError('Cierra Vampire antes de instalar paquetes')
    if any(name.endswith('.class') for name in files) and not accept_custom_code:raise ValueError('El paquete contiene Java ejecutable (generado o propio). Revisa y acepta su instalación explícitamente')
    registry=installed(ws);old=registry.get(m['id'],{});dest=safe_target(game,game/'RCM'/m['id']);oldfiles=old.get('files',{})
    original_catalogue=ws.output('cache/resources.json')
    if original_catalogue.is_file():
        originals=json.loads(original_catalogue.read_text(encoding='utf8'))
        import io
        inner=read_archive(io.BytesIO(files[m['id']+'.nob']))
        from .formats import NotFile
        template_ids={t['id'].casefold() for t in originals['templates']}
        original_paths={e['path'].casefold() for e in originals['entries']}
        for name,data in inner.items():
            if name.casefold() in original_paths:raise ValueError('El paquete intenta reemplazar un recurso original: '+name)
            if name.lower().endswith('.not') and any(t.name.casefold() in template_ids for t in NotFile.read(data).templates):raise ValueError('Template del paquete colisiona con original')
    for other in registry.values():
        if other['id']!=m['id'] and {x.casefold() for x in m.get('templates',[])}&{x.casefold() for x in other.get('templates',[])}:raise ValueError('ID de template propio colisiona con paquete '+other['id'])
    for dep in m.get('dependencies',[]):
        if registry.get(dep['id'],{}).get('version')!=dep['version']:raise ValueError('Dependencia local ausente o versión incompatible: '+dep['id'])
    targets={}
    for name in sorted(set(m['files'])|set(oldfiles)):
        archive_path(name);p=safe_target(game,dest/name)
        if p.exists() and (name not in oldfiles or hashlib.sha256(p.read_bytes()).hexdigest()!=oldfiles[name]['sha256']):raise ValueError('Archivo existente ajeno o modificado: '+name)
        if name in m['files']:targets[p]=files[name]
    control=safe_target(game,dest/'.rcm_manifest.json');targets[control]=json.dumps(m,ensure_ascii=False,indent=2).encode('utf8')
    obsolete=[safe_target(game,dest/name) for name in set(oldfiles)-set(m['files'])]
    return m,targets,obsolete

def install_package(ws,archive,accept_custom_code=False):
    m,targets,obsolete=install_plan(ws,archive,accept_custom_code);game=configured_game(ws);backup=ws.output('research/package_backups/install_'+m['id']+'_'+str(time.time_ns())+'.zip');backup.parent.mkdir(parents=True,exist_ok=True)
    # Switching user folders must not orphan our carried inventory definitions.
    # These are verified local RCM bytes, never edits to a Crypt profile.
    from .profile_compatibility import compatibility_files
    dest=safe_target(game,game/'RCM'/m['id']);compat=compatibility_files(game,targets[safe_target(game,dest/(m['id']+'.nob'))])
    prior=installed(ws).get(m['id'],{}).get('files',{})
    for name,data in compat.items():
        target=safe_target(game,dest/name)
        if target in targets:continue
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()!=prior.get(name,{}).get('sha256'):
            raise ValueError('Archivo existente ajeno o modificado: '+name)
        targets[target]=data;m['files'][name]=dict(size=len(data),sha256=hashlib.sha256(data).hexdigest())
        if target in obsolete:obsolete.remove(target)
    m['compatibility_files']=list(compat)
    targets[safe_target(game,dest/'.rcm_manifest.json')]=json.dumps(m,ensure_ascii=False,indent=2).encode('utf8')
    from .product import ensure_runtime_root
    ensure_runtime_root(game)
    from .file_transaction import replace_files
    replace_files(targets,obsolete,backup,game/'RCM',lambda p:safe_target(game,p))
    return {'id':m['id'],'files':[str(p.relative_to(game/'RCM')) for p in targets],'backup':str(backup)}

def uninstall_package(ws,ident):
    identifier(ident,'package',18);game=configured_game(ws)
    if game_running():raise ValueError('Cierra Vampire antes de desinstalar')
    registry=installed(ws)
    if ident not in registry:raise ValueError('Paquete no administrado por RCM')
    if any(d['id']==ident for other in registry.values() if other['id']!=ident for d in other.get('dependencies',[])):raise ValueError('Otro paquete depende de éste')
    m=registry[ident];dest=safe_target(game,game/'RCM'/ident);targets=[]
    for name,row in m['files'].items():
        archive_path(name);p=safe_target(game,dest/name)
        if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Se conserva el paquete: archivo modificado '+name)
        if p.is_file():targets.append(p)
    targets.append(safe_target(game,dest/'.rcm_manifest.json'));backup=ws.output('research/package_backups/uninstall_'+ident+'_'+str(time.time_ns())+'.zip');backup.parent.mkdir(parents=True,exist_ok=True)
    from .file_transaction import replace_files
    replace_files({},targets,backup,game/'RCM',lambda p:safe_target(game,p))
    return {'removed':[str(p.relative_to(game/'RCM')) for p in targets],'backup':str(backup)}
