"""Opt-in local WTD import. No mod payload is shipped with the application."""
import copy
import hashlib
import json
import math
import re
import struct
from functools import lru_cache
from pathlib import Path, PurePosixPath
import zipfile
from .formats import NotFile, Tag, cstring, u32
from .catalogue import rows, KINDS

PACK='within_the_darkness'
ARCHIVE='rcm_wtd_content.nob'
ROOT='content_packs/'+PACK
IGNORED_ROOT_ARCHIVES={'rabbit.nob','wtdarkness.nob'}


def policy():
    return json.loads((Path(__file__).parent/'editor/assets/wtd_policy.json').read_text(encoding='utf8'))


def sha(data):return hashlib.sha256(data).hexdigest()


@lru_cache(maxsize=8)
def file_sha(path,size,mtime,ctime):return sha(Path(path).read_bytes())


def manifest(ws):
    path=ws.output(ROOT+'/import.json')
    if not path.is_file():return None
    record=json.loads(path.read_text(encoding='utf8'))
    if not record.get('enabled'):return None
    if record.get('format')!=1 or record.get('id')!=PACK:raise ValueError('El registro de importación WTD no es válido')
    pack=ws.output(ROOT+'/'+ARCHIVE)
    if not pack.is_file():raise ValueError('Falta el contenido WTD importado; vuelve a importarlo desde Configuración')
    stat=pack.stat()
    if file_sha(str(pack),stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns)!=record['sha256']:raise ValueError('El contenido WTD importado ha cambiado; vuelve a importarlo desde Configuración')
    return record


def read_entry(ws,entry):
    record=manifest(ws)
    if not record or record['sha256']!=entry['import_sha256']:raise ValueError('Este recurso necesita el contenido importado de Within The Darkness')
    with zipfile.ZipFile(ws.output(ROOT+'/'+ARCHIVE)) as archive:return archive.read(entry['path'])


def _original(ws,entry):
    path=ws.output('research/original/'+entry['archive']+'/'+entry['path'])
    if path.is_file():return path.read_bytes()
    if not ws.game:raise ValueError('Selecciona primero la instalación de Redemption')
    with zipfile.ZipFile(ws.game/entry['archive']) as archive:return archive.read(entry['path'])


def _index(archive):
    from .packages import archive_path
    result={};total=0
    if len(archive.infolist())>10000:raise ValueError('El archivo WTD contiene demasiadas entradas')
    for entry in archive.infolist():
        name=entry.filename.replace('\\','/');archive_path(name.rstrip('/'))
        if entry.is_dir():continue
        key=name.casefold();total+=entry.file_size
        if key in result or entry.file_size>64*1024*1024 or total>512*1024*1024:raise ValueError('El archivo WTD tiene rutas inseguras o ambiguas')
        if entry.flag_bits&1 or (entry.external_attr>>16)&0o170000==0o120000:raise ValueError('El archivo WTD contiene una entrada no admitida')
        result[key]=(name,entry)
    return result


def _table(data,count):
    result={}
    for number,tokens in rows(data.decode('cp1252')):
        if len(tokens)!=count or tokens[0].casefold() in result:raise ValueError('Tabla de definiciones WTD no válida en la línea '+str(number))
        result[tokens[0].casefold()]=tokens
    return result


def _table_bytes(table):return ('\r\n'.join(' '.join(v) for v in table.values())+'\r\n').encode('cp1252')


def _superclass(data):
    """Read a JVM class reference, without loading or executing the class."""
    if data[:4]!=bytes.fromhex('cafebabe'):raise ValueError('Invalid class')
    pos=10;count=struct.unpack_from('>H',data,8)[0];pool={};i=1
    while i<count:
        tag=data[pos];pos+=1
        if tag==1:
            size=struct.unpack_from('>H',data,pos)[0];pos+=2;pool[i]=data[pos:pos+size].decode('utf8');pos+=size
        elif tag==7:pool[i]=struct.unpack_from('>H',data,pos)[0];pos+=2
        elif tag in (8,16):pos+=2
        elif tag in (3,4,9,10,11,12,18):pos+=4
        elif tag in (5,6):pos+=8;i+=1
        elif tag==15:pos+=3
        else:raise ValueError('Unsupported class')
        i+=1
    parent=struct.unpack_from('>H',data,pos+4)[0]
    return pool[pool[parent]] if parent else None


def prepare_import(ws,source,base):
    """Filter the user's allowlist, then retain only resolvable definitions.

    Base definitions are kept verbatim as rows; WTD cannot replace a base
    template/clan/discipline as a side effect of importing additional content.
    """
    source=Path(source)
    if source.suffix.lower()!='.nob' or source.stat().st_size>128*1024*1024:raise ValueError('Elige un archivo NOB de Within The Darkness')
    rules=policy();keep={n.casefold() for n in rules['keep']};exclude={n.casefold() for n in rules['exclude']}
    # User-approved exception: reusable Penthouse geometry and its static props,
    # without the demo chronicle, scene list, menu or interface reskin.
    level_files={'levels/wtdpenthouse.nil','scenes/wtdpenthouse.nsd'}
    keep|=level_files;exclude-=level_files
    with zipfile.ZipFile(source) as archive:
        index=_index(archive)
        if not {'misc/game.ncd','misc/game.ndd','misc/game.ndg','misc/templates/_darkness.not'}<=set(index):raise ValueError('El archivo no es un NOB de contenido de Within The Darkness admitido')
        payload={name:archive.read(info) for key,(name,info) in index.items() if key in keep and key not in exclude}
    by_path={n.casefold():n for n in payload}
    original_entries=base['entries'];original_templates={t['id'].casefold():t for t in base['templates']}
    classes={e['id'] for e in original_entries if e['extension']=='.class'}
    class_entries={e['id']:e for e in original_entries if e['extension']=='.class'};parents={}
    def discipline_class(name,trail=()):
        if name=='Discipline':return True
        if name not in class_entries or name in trail:return False
        try:
            if name not in parents:parents[name]=_superclass(_original(ws,class_entries[name]))
            return discipline_class(parents[name],trail+(name,))
        except (ValueError,KeyError,IndexError,struct.error,UnicodeError):return False
    def base_table(extension,count):
        options=[e for e in original_entries if e['path'].casefold()=='misc/game.'+extension]
        if len(options)!=1:raise ValueError('La tabla de definiciones original no existe o es ambigua')
        return _table(_original(ws,options[0]),count)
    discs=base_table('ndd',28);groups=base_table('ndg',4);clans=base_table('ncd',29)
    old_discs=set(discs);old_groups=set(groups);old_clans=set(clans)
    supplied_discs=_table(payload[by_path['misc/game.ndd']],28)
    supplied_groups=_table(payload[by_path['misc/game.ndg']],4)
    # Only reuse actual installed Java implementations, never fabricate powers.
    def valid_power(v):
        try:
            return bool(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,30}',v[0])) and discipline_class(v[3]) and all(math.isfinite(float(n)) for n in v[7:10]) and all(int(n,0)>=0 for n in v[5:7]+v[10:22])
        except ValueError:return False
    usable_discs={k:v for k,v in supplied_discs.items() if k not in discs and valid_power(v) and (v[1].casefold() in groups or v[1].casefold() in supplied_groups)}
    used_groups={v[1].casefold() for v in usable_discs.values()}
    groups.update({k:v for k,v in supplied_groups.items() if k not in groups and k in used_groups})
    discs.update(usable_discs)
    payload[by_path['misc/game.ndd']]=_table_bytes(discs);payload[by_path['misc/game.ndg']]=_table_bytes(groups)
    # An existing AI file is insufficient if it calls a power absent from the
    # filtered runtime tables. Keep only AI with fully resolvable disciplines.
    for name in list(payload):
        if name.lower().endswith('.nai'):
            try:
                powers=[v for _,v in rows(payload[name].decode('cp1252')) if v[0].casefold()=='discipline']
                valid=all(len(v)==3 and v[1].casefold() in discs and 0<=int(v[2])<=5 for v in powers)
            except (ValueError,UnicodeError):valid=False
            if not valid:payload.pop(name)
    by_path={n.casefold():n for n in payload}
    # NOT names are resolved as a library, including inheritance, rather than
    # indiscriminately adding duplicate _actor and player definitions.
    raw={};origin={};libraries={}
    for name,data in payload.items():
        if name.lower().endswith('.not'):
            nf=NotFile.read(data);libraries[name]=nf
            # Emit a new indexed library from selected records. The source's
            # unreferenced trailing bytes are never copied or edited in place.
            for t in nf.templates:
                k=t.name.casefold()
                if k in raw:raise ValueError('Plantilla WTD duplicada')
                if k not in original_templates:raw[k]=t;origin[k]=name
    base_values={}
    for entry in original_entries:
        if entry['extension']=='.not':
            for t in NotFile.read(_original(ws,entry)).templates:base_values[t.name.casefold()]=t.values()
    def resolve(k,trail=()):
        if k in trail:raise ValueError('Herencia circular en WTD')
        template=raw.get(k);v=template.values() if template else base_values.get(k)
        if v is None:raise ValueError('Falta una plantilla padre de WTD')
        if 0 in v:return resolve(cstring(v[0]).casefold(),trail+(k,))|v
        return v
    all_paths={e['path'].casefold() for e in original_entries}|set(by_path)
    all_names={PurePosixPath(n).name for n in all_paths}
    def exists(name):return str(name).replace('\\','/').casefold() in all_paths or PurePosixPath(str(name).replace('\\','/')).name.casefold() in all_names
    # Drop motion slots whose NAD is not supplied by the game/import.
    original_paths={e['path'].casefold() for e in original_entries};motion_aliases={}
    for name in list(payload):
        if name.lower().endswith('.nms'):
            lines=[line for line in payload[name].decode('cp1252').splitlines() if len(line.split(';',1)[0].split())>=2 and exists(line.split(';',1)[0].split()[1])]
            payload[name]=('\r\n'.join(lines)+'\r\n').encode('cp1252')
            if name.casefold() in original_paths:
                renamed='rcm_wtd_'+PurePosixPath(name).name;motion_aliases[PurePosixPath(name).name.casefold()]=renamed
                payload[str(PurePosixPath(name).parent/renamed)]=payload.pop(name)
    candidates=_table(payload[by_path['misc/game.ncd']],29)
    # Clan shapes/beckoning templates are checked again after NOT pruning.
    new_clans={k:v for k,v in candidates.items() if k not in clans and all(g.casefold() in groups or g.lower() in ('none','-') for g in v[7:10])}
    possible_clans=set(clans)|set(new_clans)
    allowed={}
    for k,t in raw.items():
        try:
            v=resolve(k)
            if 11 in v and cstring(v[11]) not in ('','none','null','-') and cstring(v[11]) not in classes:continue
            if any(tag in v and not exists(cstring(v[tag])) for tag in (4,56)):continue
            if 26 in v and cstring(v[26]).casefold() not in possible_clans|{'none','null','-',''}:continue
            allowed[k]=t
        except (ValueError,KeyError):continue
    while True:
        bad={k for k,t in allowed.items() if 0 in t.values() and cstring(t.values()[0]).casefold() not in set(allowed)|set(original_templates)}
        new_bad={k for k,v in new_clans.items() if any(n.casefold() not in set(allowed)|set(original_templates) and n.lower() not in ('none','-') for n in v[2:4])}
        if new_bad:
            for k in new_bad:new_clans.pop(k)
            bad|={k for k in allowed if 26 in resolve(k) and cstring(resolve(k)[26]).casefold() not in set(clans)|set(new_clans)|{'none','null','-',''}}
        if not bad and not new_bad:break
        for k in bad:allowed.pop(k,None)
    clans.update(new_clans);payload[by_path['misc/game.ncd']]=_table_bytes(clans)
    templates=[]
    for name,nf in libraries.items():
        selected=[t for k,t in allowed.items() if origin[k]==name]
        if not selected:payload.pop(name);continue
        payload[name]=NotFile(selected).encode()
        for t in selected:
            v=resolve(t.name.casefold())
            if 9 in v and PurePosixPath(cstring(v[9]).replace('\\','/')).name.casefold() in motion_aliases:
                replacement=motion_aliases[PurePosixPath(cstring(v[9]).replace('\\','/')).name.casefold()]
                t.tags=[a for a in t.tags if a.id!=9]+[Tag.text(9,replacement)]
            templates.append(dict(id=t.name,path=name,archive=ARCHIVE,imported_pack=PACK,parent=cstring(t.values()[0]) if 0 in t.values() else None,kind=KINDS.get(u32(v[16]),'unknown') if 16 in v else 'unknown',model=cstring(v[4]) if 4 in v else None,ai=cstring(v[56]) if 56 in v else None,script=cstring(v[11]) if 11 in v else None,cast_id=cstring(v[81]) if 81 in v else None,actor_flags=u32(v[114]) if 114 in v else 0,tag_ids=[a.id for a in t.tags],inheritance_complete=True))
        payload[name]=NotFile(selected).encode()
    payload['Strings/_RCM_WTD_Content.nls']=b'RCM_WTD_PENTHOUSE Penthouse\r\n'
    from .generator import zip_bytes
    data=zip_bytes(payload)
    entries=[dict(id=PurePosixPath(n).stem,path=n,archive=ARCHIVE,extension=PurePosixPath(n).suffix.lower(),size=len(b),sha256=sha(b),imported_pack=PACK) for n,b in payload.items()]
    catalogue=dict(clans=[dict(id=v[0],groups=v[7:10],imported=k not in old_clans) for k,v in clans.items()],disciplines=[dict(id=v[0],group=v[1],script=v[3],imported=k not in old_discs) for k,v in discs.items()],groups=[dict(id=v[0],imported=k not in old_groups) for k,v in groups.items()])
    record=dict(format=1,id=PACK,name='Within The Darkness',enabled=True,source_sha256=sha(source.read_bytes()),sha256=sha(data),files=len(payload),entries=entries,templates=templates,catalogue=catalogue,counts=dict(clans=len(new_clans),disciplines=len(usable_discs),templates=sum(t['kind'] in {'actors','items','weapons','armour','props'} for t in templates),models=sum(e['extension']=='.nod' for e in entries)),original_tools_used=False,native_engine_test=False)
    for entry in entries+templates:entry['import_sha256']=record['sha256']
    geometry=next((e for e in entries if e['path'].casefold()=='levels/wtdpenthouse.nil'),None)
    static=next((e for e in entries if e['path'].casefold()=='scenes/wtdpenthouse.nsd'),None)
    if geometry and static:
        from .formats import scene_entity_hints
        hints=scene_entity_hints(payload[static['path']])
        if not hints or any(h.get('script') and h['script'] not in classes for h in hints):raise ValueError('La escena estática de Penthouse no se puede resolver contra Codex')
        record['levels']={'WTDPenthouse':dict(nil=PurePosixPath(geometry['path']).name,geometry=[geometry],scenes=['WTDPenthouse.nsd'],static_scene='WTDPenthouse.nsd',references=[dict(chronicle='Within The Darkness',id='WTDPenthouse',nil='WTDPenthouse.nil',scene='WTDPenthouse.nsd',map_ui='foobar.nui',map_label='RCM_WTD_PENTHOUSE',flags='0x0060')],imported_pack=PACK,display_name='Penthouse · Within The Darkness')}
        record['scene_hints']={'wtdpenthouse.nsd':dict(source=static,entities=hints)}
        record['counts']['levels']=1
    return data,record


def import_content(backend,source):
    ws=backend.ws
    try:data,record=prepare_import(ws,source,backend.base_resources)
    except zipfile.BadZipFile:raise ValueError('El archivo NOB está dañado o no es un archivo compatible') from None
    if ws.game:publish_shared(ws,data,record)
    # Validate the entire replacement before writing or changing preferences.
    from .file_transaction import replace_files
    targets={ws.output(ROOT+'/'+ARCHIVE):data,ws.output(ROOT+'/import.json'):json.dumps(record,ensure_ascii=False,indent=2).encode('utf8')}
    rollback=ws.output(ROOT+'/import-rollback.zip')
    if rollback.exists():raise ValueError('Recupera la importación anterior antes de sustituir el contenido')
    replace_files(targets,[],rollback,ws.root,ws.output);rollback.unlink()
    backend.refresh_import();return record


def publish_shared(ws,data,record):
    """Publish installation-wide content and mirror isolated native user roots.

    Redemption indexes NOBs directly in its selected -user directory, without
    inheriting parent directories. The RCM root owns the pack independently of
    workspace imports; child launch folders receive verified runtime mirrors.
    """
    from .deployment import safe_target,game_running
    from .file_transaction import replace_files
    if game_running():raise ValueError('Cierra Vampire antes de importar contenido a RCM')
    if sha(data)!=record['sha256']:raise ValueError('El contenido WTD no coincide con su registro')
    game=ws.game;folder=safe_target(game,game/'RCM');path=safe_target(game,folder/ARCHIVE);owner=safe_target(game,folder/'.rcm_content.json')
    previous=json.loads(owner.read_text(encoding='utf8')) if owner.is_file() else {}
    if previous and (previous.get('format')!=1 or previous.get('id')!=PACK):raise ValueError('Registro de contenido compartido no válido')
    if path.exists():
        if previous.get('sha256')!=sha(path.read_bytes()):raise ValueError('El paquete de contenido existente en RCM es ajeno o está modificado; se conserva')
    files={path:data,owner:json.dumps(dict(format=1,id=PACK,sha256=record['sha256']),indent=2).encode('utf8')}
    for entry in [*folder.glob('*/.rcm_deployment.json'),*folder.glob('*/.rcm_manifest.json')]:
        entry=safe_target(game,entry);deployment=json.loads(entry.read_text(encoding='utf8'))
        if deployment.get('format')!=1 or not isinstance(deployment.get('files'),dict):raise ValueError('Manifest de deploy inválido')
        target=safe_target(game,entry.parent/ARCHIVE);old=deployment['files'].get(ARCHIVE)
        digest=old.get('sha256') if isinstance(old,dict) else old
        if target.exists() and sha(target.read_bytes()) not in {digest,record['sha256']}:raise ValueError('Contenido compartido ajeno o modificado; se conserva: '+str(target))
        deployment['files'][ARCHIVE]=dict(size=len(data),sha256=record['sha256']) if entry.name=='.rcm_manifest.json' else record['sha256']
        deployment['shared_content_files']=sorted(set(deployment.get('shared_content_files',[]))|{ARCHIVE})
        deployment['compatibility_files']=[name for name in deployment.get('compatibility_files',[]) if name!=ARCHIVE]
        files[target]=data;files[entry]=json.dumps(deployment,indent=2).encode('utf8')
    # Retire only the verified, previously owned staging copy, which the native
    # resource index cannot discover when launching with -user RCM.
    legacy=safe_target(game,folder/'_content/within_the_darkness');obsolete=[]
    legacy_pack=safe_target(game,legacy/ARCHIVE);legacy_owner=safe_target(game,legacy/'import.json')
    if legacy_pack.is_file() and legacy_owner.is_file():
        old=json.loads(legacy_owner.read_text(encoding='utf8'))
        if old.get('format')==1 and old.get('id')==PACK and old.get('sha256')==sha(legacy_pack.read_bytes()):obsolete=[legacy_pack,legacy_owner]
    rollback=ws.output(ROOT+'/shared-import-rollback.zip')
    if rollback.exists():raise ValueError('Recupera primero la importación compartida anterior')
    replace_files(files,obsolete,rollback,game/'RCM',lambda p:safe_target(game,p));rollback.unlink()


def shared_dependencies(game):
    """Read the installed pack, independently of editor/workspace preferences."""
    from .deployment import safe_target
    owner=safe_target(game,game/'RCM/.rcm_content.json')
    if not owner.is_file():return {}
    record=json.loads(owner.read_text(encoding='utf8'))
    if record.get('format')!=1 or record.get('id')!=PACK:raise ValueError('Registro de contenido compartido no válido')
    path=safe_target(game,game/'RCM'/ARCHIVE)
    if not path.is_file() or sha(data:=path.read_bytes())!=record.get('sha256'):raise ValueError('El contenido compartido de RCM falta o está modificado; vuelve a importarlo')
    return {ARCHIVE:data}


def overlay(ws,base):
    record=manifest(ws)
    if not record:return base
    result=copy.deepcopy(base);paths={e['path'].casefold() for e in record['entries']}
    result['entries']=[e for e in result['entries'] if e['path'].casefold() not in paths]+record['entries']
    result['templates']+=record['templates'];result['wtd']=record['catalogue'];result['wtd_import']=dict(id=PACK,sha256=record['sha256'],counts=record['counts'])
    for group,items in result.get('groups',{}).items():
        result['groups'][group]=[e for e in items if e.get('path','').casefold() not in paths]
        result['groups'][group]+=[e for e in record['entries'] if any(e['extension']==old.get('extension') for old in items)]
    return result


def add_to_build(ws,report,resources):
    if not resources.get('wtd_import'):return report
    record=manifest(ws)
    if not record or record['sha256']!=resources['wtd_import']['sha256']:raise ValueError('La importación WTD cambió durante la compilación')
    report['imported_content']=[dict(id=PACK,name=record['name'],sha256=record['sha256'],archive=ARCHIVE)]
    # Imported third-party assets are local dependencies, never silently
    # redistributed inside the generated chronicle's distribution ZIP.
    return report


def local_dependencies(ws,report):
    from .deployment import configured_game
    shared=shared_dependencies(configured_game(ws)) if ws.game or ws.output('cache/game_settings.json').is_file() or getattr(ws,'app_settings',None) else {}
    if not report.get('imported_content'):return shared
    if shared:
        if report['imported_content']!=[dict(id=PACK,name='Within The Darkness',sha256=sha(shared[ARCHIVE]),archive=ARCHIVE)]:raise ValueError('El contenido compartido WTD cambió; vuelve a importar y compilar la crónica')
        return shared
    record=manifest(ws)
    if not record or report['imported_content']!=[dict(id=PACK,name=record['name'],sha256=record['sha256'],archive=ARCHIVE)]:raise ValueError('Importa el contenido necesario de Within The Darkness y vuelve a compilar antes de desplegar')
    return {ARCHIVE:ws.output(ROOT+'/'+ARCHIVE).read_bytes()}


def validate_traits(actor,resources):
    if 'traits' not in actor:return
    from .model import mapping
    value=mapping(actor['traits'],{'clan','disciplines'},label='actor.traits')
    if not resources.get('wtd'):raise ValueError('Importa Within The Darkness en Configuración para editar clanes y disciplinas')
    if 'clan' in value and value['clan'] not in {r['id'] for r in resources['wtd']['clans']}:raise ValueError('Elige un clan del contenido importado')
    powers=value.get('disciplines',{})
    if not isinstance(powers,dict) or len(powers)>64:raise ValueError('Las disciplinas del actor admiten un máximo de 64 entradas')
    known={r['id'] for r in resources['wtd']['disciplines']}
    for name,level in powers.items():
        if name not in known or type(level) is not int or not 0<=level<=5:raise ValueError('Elige una disciplina importada y un nivel de 0 a 5')


def actor_java(actor,guid):
    from .generator import java_string
    traits=actor.get('traits',{});code=[]
    if traits.get('clan'):code.append('if(fresh && !new CodexActor('+guid+').SetActorClan('+java_string(traits['clan'])+')) trace("CLAN_FAILED");')
    for name,level in traits.get('disciplines',{}).items():code.append('if(fresh && !new CodexActor('+guid+').SetActorDisciplineLevel('+java_string(name)+','+str(level)+')) trace("DISCIPLINE_FAILED");')
    return code
