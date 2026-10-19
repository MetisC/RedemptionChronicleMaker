"""Preserve RCM inventory definitions when switching per-chronicle user folders.

Only hashed, RCM-owned NOT/class bytes are reused. Crypt profiles are read-only.
No original game assets, scene controllers, or historical chronicles are added.
"""
import hashlib
import io
import json
import re
import struct
import zipfile
from .formats import NotFile,cstring


def profile_references(data):
    # Confirmed native thing record marker, GUID then fixed template[32].
    result=set()
    for match in re.finditer(re.escape(struct.pack('<I',0x1e)),data):
        field=data[match.start()+8:match.start()+40]
        if len(field)!=32 or b'\0' not in field:continue
        value=field.split(b'\0',1)[0]
        if re.fullmatch(rb'[A-Za-z_][A-Za-z0-9_]*',value):result.add(value.decode('ascii').casefold())
    return result


def compatibility_files(game,current_nob):
    from .deployment import safe_target
    required=set()
    for profile in (game/'Crypt').glob('*.npf'):required.update(profile_references(profile.read_bytes()))
    if not required:return {}
    def read_templates(data,boot_only=False):
        result={}
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for name in archive.namelist():
                if name.lower().endswith('.not'):
                    if boot_only and not name.replace('\\','/').rsplit('/',1)[-1].startswith('_'):continue
                    for template in NotFile.read(archive.read(name)).templates:result[template.name.casefold()]=template
        return result
    # A shared -user directory can contain several chronicles. Only startup
    # libraries count: a NOT loaded by an NMF is too late for Crypt restoration.
    archives=[current_nob] if isinstance(current_nob,bytes) else current_nob
    current={}
    for data in archives:current.update(read_templates(data,boot_only=True))
    known={};classes={};imported_packs={};imported_templates={};pack_dependencies={};pack_conflicts=set()
    manifests=[*(game/'RCM').glob('*/.rcm_deployment.json'),*(game/'RCM').glob('*/.rcm_manifest.json')]
    for path in manifests:
        safe_target(game,path)
        try:manifest=json.loads(path.read_text(encoding='utf8'))
        except (ValueError,OSError):continue
        if manifest.get('format')!=1 or not isinstance(manifest.get('files'),dict):continue
        for name,digest in manifest['files'].items():
            if isinstance(digest,dict):digest=digest.get('sha256')
            from .packages import archive_path
            archive_path(name);file=safe_target(game,path.parent/name)
            if not file.is_file():continue
            data=file.read_bytes()
            if hashlib.sha256(data).hexdigest()!=digest:continue
            if name.endswith('.nob'):
                try:
                    found=read_templates(data);known.update(found)
                    if name=='rcm_wtd_content.nob' or re.fullmatch(r'rcm_lib_[0-9a-f]{12}\.nob',name):
                        if name in imported_packs and imported_packs[name]!=data:pack_conflicts.add(name)
                        imported_packs[name]=data;imported_templates.update({key:name for key in found})
                except (ValueError,zipfile.BadZipFile):continue
                if re.fullmatch(r'rcm_lib_[0-9a-f]{12}\.nob',name):
                    from .content_libraries import DEPENDENCIES
                    with zipfile.ZipFile(io.BytesIO(data)) as archive:
                        if DEPENDENCIES in archive.namelist():
                            if archive.getinfo(DEPENDENCIES).file_size>131072:raise ValueError('Local library dependency metadata is excessive')
                            refs=json.loads(archive.read(DEPENDENCIES))
                            if not isinstance(refs,dict) or refs.get('format')!=1 or not isinstance(refs.get('libraries'),list):raise ValueError('Invalid local library dependency metadata')
                            for ref in refs['libraries']:
                                if not isinstance(ref,dict) or not re.fullmatch(r'rcm_lib_[0-9a-f]{12}\.nob',str(ref.get('archive',''))) or not re.fullmatch(r'[0-9a-f]{64}',str(ref.get('sha256',''))):raise ValueError('Invalid local library dependency reference')
                            pack_dependencies[name]=refs['libraries']
            elif re.fullmatch(r'codex/[A-Za-z_][A-Za-z0-9_$]*\.class',name):classes[name]=data
    unavailable=required-current.keys()-known.keys()
    owned=[name for name in unavailable if name.startswith(('r_rcm_','t_rcm_','rcm_'))]
    if owned:raise ValueError('Falta la definición de un objeto RCM del personaje guardado: '+', '.join(sorted(owned)))
    missing=(required & known.keys())-current.keys()
    if not missing:return {}
    keep={};scripts=set();needed_packs=set()
    def collect(name):
        if name in keep or name in current:return
        if name in imported_templates:needed_packs.add(imported_templates[name]);return
        template=known.get(name)
        if template is None:return  # Parent is an original game definition.
        keep[name]=template;values=template.values()
        if 0 in values:collect(cstring(values[0]).casefold())
        if 11 in values:scripts.add(cstring(values[11]))
    for name in sorted(missing):collect(name)
    pending=list(needed_packs)
    while pending:
        name=pending.pop()
        if name in pack_conflicts:raise ValueError('Conflicting saved-inventory library versions: '+name)
        for ref in pack_dependencies.get(name,[]):
            parent=ref['archive'];data=imported_packs.get(parent)
            if data is None or hashlib.sha256(data).hexdigest()!=ref['sha256']:raise ValueError('Missing or changed saved-inventory library dependency: '+parent)
            if parent not in needed_packs:needed_packs.add(parent);pending.append(parent)
    from .generator import zip_bytes
    files={'rcm_compat.nob':zip_bytes({'misc/Templates/_rcm_compat.not':NotFile(list(keep.values())).encode()})}
    files.update({name:imported_packs[name] for name in needed_packs})
    for script in sorted(scripts):
        name='codex/'+script+'.class'
        if name in classes:files[name]=classes[name]
        elif script.startswith(('R_','RCM')):raise ValueError('Falta la clase de un objeto RCM conservado: '+script)
    return files


def profile_signature(game):
    required=set()
    for profile in (game/'Crypt').glob('*.npf'):required.update(profile_references(profile.read_bytes()))
    return hashlib.sha256('\n'.join(sorted(required)).encode('ascii')).hexdigest()


def refresh_installed_profiles(ws):
    """Restore startup inventory libraries in owned launch folders, never Crypt.

    Called after a playtest ends because acquiring an item changes the profile
    *after* deployment. A desktop shortcut may then select a different folder.
    All plans are checked before replacing anything; modified files fail closed.
    """
    from .deployment import configured_game,game_running,safe_target
    from .packages import archive_path
    from .file_transaction import replace_files
    import time
    game=configured_game(ws)
    if game_running():raise ValueError('Cierra Vampire antes de actualizar las bibliotecas de inventario')
    signature=profile_signature(game);targets={};obsolete=[];directories=[]
    paths=[*(game/'RCM').glob('*/.rcm_deployment.json'),*(game/'RCM').glob('*/.rcm_manifest.json')]
    for path in paths:
        safe_target(game,path);manifest=json.loads(path.read_text(encoding='utf8'))
        if manifest.get('format')!=1 or not isinstance(manifest.get('files'),dict):continue
        package=path.name=='.rcm_manifest.json';existing=manifest['files'];archives=[]
        for name,row in existing.items():
            archive_path(name);file=safe_target(game,path.parent/name)
            digest=row.get('sha256') if isinstance(row,dict) else row
            if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=digest:
                raise ValueError('Archivo administrado ausente o modificado: '+str(file))
            if name.endswith('.nob') and name not in manifest.get('compatibility_files',[]):archives.append(file.read_bytes())
        compat=compatibility_files(game,archives);updated=dict(existing)
        for name in manifest.get('compatibility_files',[]):
            if name in compat:continue
            # Keep existing class definitions: a retained class can be shared
            # with an active chronicle even in a single-owner deployment.
            if name.endswith('.class'):continue
            if name in existing:
                obsolete.append(safe_target(game,path.parent/name));updated.pop(name)
        for name,data in compat.items():
            file=safe_target(game,path.parent/name)
            if name in existing and name not in manifest.get('compatibility_files',[]):continue
            digest=hashlib.sha256(data).hexdigest()
            if file.exists() and name not in existing:raise ValueError('Archivo ajeno: '+str(file))
            updated[name]=dict(size=len(data),sha256=digest) if package else digest
            if not file.exists() or file.read_bytes()!=data:targets[file]=data
        retained=[name for name in manifest.get('compatibility_files',[]) if name.endswith('.class')]
        revised=dict(manifest,files=updated,compatibility_files=sorted(set(compat)|set(retained)),profile_refs_sha256=signature)
        if revised!=manifest:
            targets[path]=json.dumps(revised,indent=2).encode('utf8');directories.append(path.parent.name)
    if not targets and not obsolete:return dict(updated=[],files=[],native_engine_test=False)
    backup=ws.output('research/runtime_test/backups/profile_libraries_'+str(time.time_ns())+'.zip')
    replace_files(targets,obsolete,backup,game/'RCM',lambda p:safe_target(game,p))
    result=dict(updated=directories,files=[p.relative_to(game/'RCM').as_posix() for p in targets],backup=str(backup),native_engine_test=False)
    ws.write('research/runtime_test/profile_libraries.json',json.dumps(result,indent=2))
    return result
