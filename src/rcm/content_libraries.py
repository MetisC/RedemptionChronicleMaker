"""Explicit, data-only NOT/NOB libraries with bounded local dependency closure.

Only selected templates, ancestors and referenced data are copied. Menus,
chronicles, world files, executables and mod code never enter this pipeline.
Third-party data stays a local dependency, outside exported chronicle ZIPs.
"""
import copy,hashlib,io,json,re,zipfile
from pathlib import Path,PurePosixPath
from .formats import NotFile,cstring,u32

ROOT='content_packs/libraries'
DEPENDENCIES='rcm/library_dependencies.json'
ALLOWED={'.nod','.nad','.nms','.nai','.nag','.nam','.tga','.wav','.mp3','.ncp'}


def sha(data):return hashlib.sha256(data).hexdigest()


def manifests(ws):
    result=[]
    for path in sorted(ws.output(ROOT).glob('*/import.json')):
        record=json.loads(path.read_text(encoding='utf8'))
        if not isinstance(record,dict) or record.get('format')!=1 or not re.fullmatch(r'lib_[0-9a-f]{12}',record.get('id','')) or path.parent.name!=record['id']:raise ValueError('Invalid local content library manifest')
        if record.get('archive')!='rcm_'+record['id']+'.nob':raise ValueError('Invalid local library archive name')
        data=ws.output(ROOT+'/'+record['id']+'/'+record['archive']).read_bytes()
        if sha(data)!=record.get('sha256'):raise ValueError('Local content library changed: '+record['name'])
        result.append(record)
    by_id={r['id']:r for r in result}
    for record in result:
        for ref in record.get('dependencies',[]):
            if not isinstance(ref,dict) or ref.get('id') not in by_id or any(ref.get(k)!=by_id[ref['id']][k] for k in ('archive','sha256')):raise ValueError('Missing or changed parent library: '+record['name'])
    return result


def read_entry(ws,entry):
    record=next((r for r in manifests(ws) if 'library:'+r['id']==entry.get('imported_pack')),None)
    if not record or record['sha256']!=entry.get('import_sha256'):raise ValueError('Required local content library is missing or changed')
    with zipfile.ZipFile(ws.output(ROOT+'/'+record['id']+'/'+record['archive'])) as z:return z.read(entry['path'])


def inspect_source(source):
    source=Path(source)
    if source.stat().st_size>128*1024*1024:raise ValueError('Content library exceeds 128 MiB')
    if source.suffix.lower()=='.not':return {source.name:source.read_bytes()}
    if source.suffix.lower()!='.nob':raise ValueError('Choose a NOT or NOB content library')
    from .wtd import _index
    with zipfile.ZipFile(source) as z:
        index=_index(z)
        return {name:z.read(info) for name,info in index.values() if PurePosixPath(name).suffix.lower() in ALLOWED|{'.not','.nls'}}


def preview(source):
    files=inspect_source(source)
    return {name:[t.name for t in NotFile.read(data).templates] for name,data in files.items() if name.lower().endswith('.not')}


def asset_preview(source):
    return sorted(name for name in inspect_source(source) if PurePosixPath(name).suffix.lower() in ALLOWED)


def import_identity(source,library,selected,assets=()):
    selection=[library,sorted(selected)]
    if assets:selection.append(sorted(assets))
    return 'lib_'+sha(Path(source).read_bytes()+json.dumps(selection).encode())[:12]


def prepare_import(ws,source,library,selected,base,assets=()):
    from .project_resources import original_bytes
    from .catalogue import KINDS
    files=inspect_source(source)
    if library is not None and (library not in files or not library.lower().endswith('.not')):raise ValueError('Select a NOT library in the archive')
    if not isinstance(selected,list) or len(selected)>1000 or any(not isinstance(n,str) for n in selected) or (not selected and not assets):raise ValueError('Select at least one template or data resource (maximum 1000)')
    if not isinstance(assets,(tuple,list)) or len(assets)>1000 or any(not isinstance(n,str) or n not in files or PurePosixPath(n).suffix.lower() not in ALLOWED for n in assets):raise ValueError('Select supported data resources from this archive')
    original={};templates={};origins={};dependencies=set()
    template_owners={t['id'].casefold():str(t.get('imported_pack','')) for t in base['templates']}
    for entry in base['entries']:
        if entry['extension']=='.not':
            for row in NotFile.read(original_bytes(ws,entry)).templates:original.setdefault(row.name.casefold(),[]).append(row)
    for name,data in files.items():
        if not name.lower().endswith('.not'):continue
        for row in NotFile.read(data).templates:
            key=row.name.casefold()
            if key in templates:raise ValueError('Ambiguous template in external library: '+row.name)
            templates[key]=row;origins[key]=name
    allowed={n.casefold() for n in preview(source)[library]} if library is not None else set()
    if any(n.casefold() not in allowed for n in selected):raise ValueError('Template outside selected NOT library')
    used={};resolved={};visiting=set()
    def template(name):
        key=name.casefold()
        if key in visiting:raise ValueError('Circular external template inheritance')
        if key in resolved:return resolved[key]
        if key in original:
            if len(original[key])!=1:raise ValueError('Ambiguous original parent: '+name)
            if key in templates and templates[key].tags!=original[key][0].tags:raise ValueError('External template overrides original: '+name)
            row=original[key][0]
            if template_owners.get(key,'').startswith('library:'):dependencies.add(template_owners[key][8:])
        elif key in templates:
            row=templates[key];used[key]=row
        else:raise ValueError('Missing external template parent: '+name)
        visiting.add(key);values=row.values();merged=(template(cstring(values[0])) if 0 in values else {})|values;visiting.remove(key);resolved[key]=merged;return merged
    for name in selected:
        if name.casefold() in original:raise ValueError('Choose added templates; original definitions are not replaced')
        template(name)
    payload={};base_names={};external_names={}
    for e in base['entries']:base_names.setdefault(PurePosixPath(e['path']).name.casefold(),[]).append(e)
    for name in files:external_names.setdefault(PurePosixPath(name).name.casefold(),[]).append(name)
    def resource(name):
        name=name.replace('\\','/');leaf=PurePosixPath(name).name;key=leaf.casefold();ext=PurePosixPath(leaf).suffix.lower()
        original=base_names.get(key,[]);external=external_names.get(key,[])
        if len(original)>1 or len(external)>1:raise ValueError('Ambiguous library resource: '+name)
        if original:
            if external and sha(files[external[0]])!=sha(original_bytes(ws,original[0])):raise ValueError('Library would replace an existing resource: '+name)
            owner=str(original[0].get('imported_pack',''))
            if owner.startswith('library:'):dependencies.add(owner[8:])
            return
        if ext=='.class':raise ValueError('External compiled code is not imported. Review Java through project scripts: '+name)
        if ext not in ALLOWED or not external:raise ValueError('Missing or unsupported library dependency: '+name)
        path=external[0]
        if path in payload:return
        data=files[path];payload[path]=data
        if ext=='.nod':
            from .spatial.assets import read_nod
            for material in read_nod(data).materials:
                target=material if material.lower().endswith('.nam') else material+'.nam'
                if PurePosixPath(target).name.casefold() not in base_names and PurePosixPath(target).name.casefold() not in external_names:target=material+'.tga'
                resource(target)
        elif ext in {'.nms','.nai','.nag','.nam'}:
            text=data.decode('cp1252')
            if '\0' in text:raise ValueError('Invalid text library resource: '+name)
            if ext=='.nai':
                from .catalogue import rows
                from .project_resources import original_entry
                powers=[v for _,v in rows(text) if v[0].casefold()=='discipline']
                if powers:
                    table=original_bytes(ws,original_entry(base,'.ndd','game')).decode('cp1252')
                    known={v[0].casefold() for _,v in rows(table)}
                    if any(len(v)!=3 or v[1].casefold() not in known or not v[2].isdigit() or not 0<=int(v[2])<=5 for v in powers):raise ValueError('Library AI requires an unavailable discipline: '+name)
            for line in text.splitlines():
                line=line.split(';',1)[0].split('//',1)[0].split('#',1)[0]
                for token in line.split():
                    if PurePosixPath(token).suffix.lower() in ALLOWED|{'.class'}:resource(token)
        elif ext=='.nad':
            if len(data)<20 or u32(data)!=3:raise ValueError('Unsupported external NAD version: '+name)
        elif ext=='.ncp':
            from .camera_paths import CameraPath
            CameraPath.read(data)
        elif ext=='.tga':
            from PIL import Image
            with Image.open(io.BytesIO(data)) as image:
                if max(image.size)>4096:raise ValueError('Library texture exceeds 4096 pixels')
                image.verify()
        elif ext=='.wav':
            import wave
            with wave.open(io.BytesIO(data)) as sound:
                if sound.getnchannels() not in (1,2) or sound.getsampwidth() not in (1,2):raise ValueError('Unsupported library WAV encoding')
    for name in assets:resource(name)
    for key in list(used):
        values=resolved[key]
        for tag,value in values.items():
            if tag in (0,81,82):continue
            raw=value.split(b'\0',1)[0]
            if any(c<32 or c>126 for c in raw):continue
            value=raw.decode('ascii')
            if re.fullmatch(r'[A-Za-z0-9_./\\ -]+\.[A-Za-z0-9]{2,5}',value):resource(value)
            elif tag==11 and value:resource(value+'.class')
    ident=import_identity(source,library,selected,assets);identity=ident[4:];archive='rcm_'+ident+'.nob';not_path='misc/templates/_L_'+identity+'.not'
    if used:payload[not_path]=NotFile(list(used.values())).encode()
    else:not_path=None
    # Retain only string keys directly used by selected definitions.
    required={cstring(resolved[k][82]) for k in used if 82 in resolved[k]};strings={}
    from .catalogue import rows
    for name,data in files.items():
        if name.lower().endswith('.nls'):
            for _,tokens in rows(data.decode('cp1252')):
                if tokens[0] in required:
                    value=' '.join(tokens[1:])
                    if tokens[0] in strings and strings[tokens[0]]!=value:raise ValueError('Ambiguous library hover string')
                    strings[tokens[0]]=value
    nls_path='strings/L_'+identity+'.nls' if strings else None
    aliases={k:'L_'+identity+'_'+sha(k.encode())[:8] for k in strings}
    if nls_path:
        from .not_library import patch_template
        payload[nls_path]=('\r\n'.join(aliases[k]+' '+v for k,v in sorted(strings.items()))+'\r\n').encode('cp1252')
        payload[not_path]=NotFile([patch_template(t,{'description_id':aliases[cstring(resolved[k][82])]}) if 82 in resolved[k] and cstring(resolved[k][82]) in aliases else t for k,t in used.items()]).encode()
    parent_refs=[{k:r[k] for k in ('id','name','archive','sha256')} for r in manifests(ws) if r['id'] in dependencies]
    if parent_refs:payload[DEPENDENCIES]=json.dumps(dict(format=1,libraries=parent_refs),sort_keys=True).encode('utf8')
    from .generator import zip_bytes
    data=zip_bytes(payload);digest=sha(data)
    entries=[dict(id=PurePosixPath(n).stem,path=n,archive=archive,extension=PurePosixPath(n).suffix.lower(),size=len(v),imported_pack='library:'+ident,import_sha256=digest) for n,v in payload.items()]
    records=[]
    for key,row in used.items():
        from .project_resources import resource_identifier
        resource_identifier(row.name)
        v=resolved[key];kind=KINDS.get(u32(v[16]),'unknown') if 16 in v else 'unknown'
        if kind not in {'actors','items','props','weapons','armour','containers','none'}:raise ValueError('Unsupported external template kind: '+row.name)
        records.append(dict(id=row.name,path=not_path,archive=archive,imported_pack='library:'+ident,import_sha256=digest,kind=kind,parent=cstring(row.values()[0]) if 0 in row.values() else None,model=cstring(v[4]) if 4 in v else None,ai=cstring(v[56]) if 56 in v else None,script=cstring(v[11]) if 11 in v else None,inheritance_complete=True,tag_ids=[t.id for t in row.tags]))
        if 82 in v and cstring(v[82]) in aliases:records[-1]['description_override']=aliases[cstring(v[82])]
    return data,dict(format=1,id=ident,name=Path(source).stem,archive=archive,sha256=digest,source_sha256=sha(Path(source).read_bytes()),entries=entries,templates=records,not_path=not_path,nls_path=nls_path,dependencies=parent_refs,code_imported=False,redistribute=False)


def remove_content(backend,ident,current_source=None):
    """Uninstall only verified owned copies, never source mods or user projects."""
    records=manifests(backend.ws);record=next((r for r in records if r['id']==ident),None)
    if record is None:raise ValueError('Local library not found')
    dependents=[r['name'] for r in records if any(ref['id']==ident for ref in r.get('dependencies',[]))]
    if dependents:raise ValueError('Other libraries require this content: '+', '.join(dependents))
    names={t['id'].casefold() for t in record['templates']};assets={r['id'].casefold() for r in record['entries']}
    def used(value):
        if isinstance(value,list):return any(used(v) for v in value)
        if not isinstance(value,dict):return False
        return any((k in {'template','base'} and isinstance(v,str) and v.casefold() in names) or (k in {'model','ai','foley','motions','resource','camera_path','music','ambient','play_sound','start_music','start_ambient'} and isinstance(v,str) and PurePosixPath(v.replace('\\','/')).stem.casefold() in assets) or used(v) for k,v in value.items())
    if current_source and used(current_source):raise ValueError('The open chronicle uses this library. Replace its template/resource references first.')
    ws=backend.ws;folder=ROOT+'/'+record['id'];paths=[ws.output(folder+'/'+record['archive']),ws.output(folder+'/import.json')]
    from .file_transaction import replace_files
    rollback=ws.output('build/.library_remove_'+ident+'.zip')
    if rollback.exists():raise ValueError('Library removal rollback already exists')
    replace_files({},paths,rollback,ws.root,ws.output);rollback.unlink();backend.refresh_import()


def import_content(backend,source,library,selected,assets=()):
    ident=import_identity(source,library,selected,assets)
    existing=next((r for r in manifests(backend.ws) if r['id']==ident),None)
    if existing:return existing
    data,record=prepare_import(backend.ws,source,library,selected,backend.original_resources,assets)
    ws=backend.ws;folder=ROOT+'/'+record['id']
    from .file_transaction import replace_files
    replace_files({ws.output(folder+'/'+record['archive']):data,ws.output(folder+'/import.json'):json.dumps(record,indent=2).encode()},[],ws.output('research/package_backups/library_'+record['id']+'.zip'),ws.root,ws.output)
    backend.refresh_import();return record


def overlay(ws,base):
    records=manifests(ws)
    if not records:return base
    result=copy.deepcopy(base)
    for record in records:
        old={r['id'].casefold() for r in result['templates']}
        if old&{r['id'].casefold() for r in record['templates']}:raise ValueError('Local template library collision: '+record['name'])
        result['entries']+=record['entries'];result['templates']+=record['templates']
    result['local_libraries']=[{k:r[k] for k in ('id','name','archive','sha256')} for r in records];return result


def local_dependencies(ws,report):
    required=report.get('local_libraries',[]);available={r['id']:r for r in manifests(ws)};result={}
    for ref in required:
        record=available.get(ref.get('id'))
        if not record or any(ref.get(k)!=record[k] for k in ('archive','sha256')):raise ValueError('Import the required local template library: '+str(ref.get('name',ref.get('id'))))
        result[record['archive']]=ws.output(ROOT+'/'+record['id']+'/'+record['archive']).read_bytes()
    return result


def add_to_build(ws,report,resources):
    records=manifests(ws)
    if not records:return report
    refs=resources.get('local_libraries',[])
    if refs!=[{k:r[k] for k in ('id','name','archive','sha256')} for r in records]:raise ValueError('Local content changed during build')
    from .generator import zip_bytes
    root='build/'+report['chronicle'];archive=report['chronicle']+'.nob'
    with zipfile.ZipFile(ws.output(root+'/'+archive)) as z:payload={n:z.read(n) for n in z.namelist()}
    key='chronicles/R_'+report['chronicle']+'.nmf'
    lines=[]
    for record in records:
        if record['not_path']:lines.append('NOT '+PurePosixPath(record['not_path']).name)
        if record['nls_path']:lines.append('NLS '+PurePosixPath(record['nls_path']).name)
    payload[key]=('\r\n'.join(lines)+'\r\n').encode('cp1252')+payload[key]
    for n,v in payload.items():ws.write(root+'/runtime/'+n,v)
    data=zip_bytes(payload);ws.write(root+'/'+archive,data);ws.write(root+'/bundle/'+archive,data)
    report['distribution_files'][archive]=dict(size=len(data),sha256=sha(data))
    for n,v in payload.items():report['files'][n]=dict(size=len(v),sha256=sha(v))
    if ws.output(root+'/'+report['chronicle']+'_distribution.zip').exists():ws.write(root+'/'+report['chronicle']+'_distribution.zip',zip_bytes({n:ws.output(root+'/bundle/'+n).read_bytes() for n in report['distribution_files']}))
    report['local_libraries']=refs;return report
