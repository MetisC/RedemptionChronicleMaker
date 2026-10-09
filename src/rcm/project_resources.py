"""Version 5 project-owned resources, resolved separately from game originals."""
from pathlib import Path
import copy,hashlib,math,re,struct,subprocess,zipfile
from .formats import NotFile,Template,Tag,fixed
from .not_library import patch_template,EDITABLE
from .model import identifier,mapping,sequence

EXTENSIONS={'project_format','metadata','resources','playtests','build_options'}
def resource_identifier(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,30}',value):raise ValueError('Recurso: ID alfanumérico de 1..31 caracteres, sensible a mayúsculas sólo en Java')
    return value
AI_FIELDS={'attackRate':(0,60),'attackAlt':(0,1),'moveDist':(0,100000),'moveRate':(0,60),'chaseDist':(0,100000),'chaseRate':(0,60),'searchDist':(0,100000),'searchRate':(0,60),'wanderRadius':(0,100000),'wakeupDelay':(0,86400)}

def indexed(rows,label):
    result={}
    for row in sequence(rows,label):
        if not isinstance(row,dict):raise ValueError(label+': requiere registros')
        name=resource_identifier(row.get('id'))
        if name.casefold() in {k.casefold() for k in result}:raise ValueError(label+': ID duplicado')
        result[name]=row
    return result

def original_entry(catalogue,kind,name):
    if not isinstance(name,str):raise ValueError('Referencia de recurso requiere texto')
    key=Path(name.replace('\\','/')).stem.casefold()
    entries=[e for e in catalogue['entries'] if e['extension'].lower()==kind and e['id'].casefold()==key]
    if len(entries)!=1:raise ValueError('Recurso ausente o ambiguo: '+str(name))
    return entries[0]

def original_bytes(ws,entry):
    p=ws.output('research/original/'+entry['archive']+'/'+entry['path'])
    if p.exists():return p.read_bytes()
    if not ws.game:raise ValueError('Selecciona la instalación para leer '+entry['id'])
    with zipfile.ZipFile(ws.game/entry['archive']) as z:return z.read(entry['path'])

def ai_edit(data,properties):
    content=data.decode('cp1252');lines=content.splitlines(keepends=True)
    for key,value in properties.items():
        if key not in AI_FIELDS:raise ValueError('Campo AI no soportado: '+key)
        low,high=AI_FIELDS[key]
        if type(value) not in (int,float) or not math.isfinite(value) or not low<=value<=high:raise ValueError('Valor AI fuera de rango: '+key)
        hits=[i for i,l in enumerate(lines) if re.match(r'^\s*'+re.escape(key)+r'\s+',l)]
        if len(hits)!=1:raise ValueError('Campo AI ausente o duplicado: '+key)
        i=hits[0]
        match=re.match(r'^(\s*\S+\s+)(\S+)(.*?)(\r?\n)?$',lines[i])
        lines[i]=match[1]+str(value)+match[3]+(match[4] or '')
    return ''.join(lines).encode('cp1252')

def prepare(ws,source,catalogue):
    """Return legacy-compatible source, merged catalogue and OWN payload bytes."""
    root=copy.deepcopy(source)
    if 'project_format' not in root:
        if any(k in root for k in EXTENSIONS):raise ValueError('Recursos propios requieren Upgrade a formato 5')
        return root,catalogue,{},{}
    if type(root['project_format']) is not int or root['project_format'] not in (5,9) or root.get('schema')!=2:raise ValueError('project_format soportado: 5 o 9 con schema 2')
    modern=root['project_format']==9
    if modern:root['runtime_profile']='phase9'
    metadata=mapping(root.get('metadata',{}),{'author','version','description','requires_game','dependencies'},label='metadata')
    if not re.fullmatch(r'\d+\.\d+\.\d+',metadata.get('version','0.1.0')):raise ValueError('Versión debe ser major.minor.patch')
    for k in ('author','description','requires_game'):
        if k in metadata and not isinstance(metadata[k],str):raise ValueError('metadata.'+k+': requiere texto')
    for dep in sequence(metadata.get('dependencies',[]),'dependencies'):
        mapping(dep,{'id','version'},{'id','version'},'dependency');identifier(dep['id'],'dependency',18)
        if not isinstance(dep['version'],str) or not re.fullmatch(r'\d+\.\d+\.\d+',dep['version']):raise ValueError('Dependencia requiere versión exacta')
    options=mapping(root.get('build_options',{}),{'debug'},label='build_options')
    if type(options.get('debug',True)) is not bool:raise ValueError('debug requiere booleano')
    for p in sequence(root.get('playtests',[]),'playtests'):
        mapping(p,{'id','name','instructions'},{'id','name','instructions'},'playtest');identifier(p['id'],'playtest')
        if not all(isinstance(p[k],str) for k in ('name','instructions')):raise ValueError('Playtest requiere textos')
    owned=mapping(root.get('resources',{}),{'templates','ai_profiles','scripts','textures'},label='resources')
    ts=indexed(owned.get('templates',[]),'templates');ais=indexed(owned.get('ai_profiles',[]),'ai_profiles');scripts=indexed(owned.get('scripts',[]),'scripts');textures=indexed(owned.get('textures',[]),'textures')
    originals={}
    for t in catalogue['templates']:originals.setdefault(t['id'].casefold(),[]).append(t)
    # Custom inventory templates must exist during LAN character restoration.
    not_path='misc/templates/_R_'+root['chronicle']['id']+'_custom.not'
    entries=copy.deepcopy(catalogue['entries']);templates=copy.deepcopy(catalogue['templates']);payload={};resolved={};visiting=set()
    for name,row in ais.items():
        mapping(row,{'id','base','properties'},{'id','base'},'AI '+name)
        if any(e['extension'].lower()=='.nai' and e['id'].casefold()==name.casefold() for e in entries):raise ValueError('AI propia colisiona con original')
        base=original_entry(catalogue,'.nai',row['base']);data=ai_edit(original_bytes(ws,base),row.get('properties',{}));path='misc/AI/'+name+'.nai';payload[path]=data
        entries.append(dict(id=name,path=path,archive='PROJECT',extension='.nai',size=len(data),project_owned=True))
    for name,row in scripts.items():
        mapping(row,{'id','source'},{'id','source'},'script')
        if any(e['extension'].lower()=='.class' and e['id'].casefold()==name.casefold() for e in entries):raise ValueError('Script colisiona con original')
        prefix='R_'+root['chronicle']['id']
        if name.startswith(prefix+'_'):raise ValueError('Script colisiona con namespace generado: '+prefix+'_')
        if ws.output(row['source']).is_relative_to(ws.output('build/'+root['chronicle']['id'])):raise ValueError('Java fuente debe estar fuera de su directorio de build')
        path=ws.output(row['source']);data=path.read_text(encoding='utf8')
        if path.suffix!='.java' or path.stem!=name or not re.search(r'\bclass\s+'+re.escape(name)+r'\b',data) or re.search(r'\bpackage\s+',data):raise ValueError('Java custom debe declarar su clase sin package y conservar nombre')
        entries.append(dict(id=name,path='codex/'+name+'.class',archive='PROJECT',extension='.class',project_owned=True))
    for name,row in textures.items():
        mapping(row,{'id','source'},{'id','source'},'texture')
        if any(e['extension'].lower()=='.tga' and e['id'].casefold()==name.casefold() for e in entries):raise ValueError('Textura colisiona con original')
        from PIL import Image
        image=Image.open(ws.output(row['source']))
        if max(image.size)>4096 or min(image.size)<1:raise ValueError('Textura: máximo 4096 por eje')
        import io
        buffer=io.BytesIO();image.convert('RGBA').save(buffer,format='TGA',compression=None);data=buffer.getvalue();path='3d/materials/'+name+'.tga';payload[path]=data
        entries.append(dict(id=name,path=path,archive='PROJECT',extension='.tga',project_owned=True,size=len(data)))
    def resolve(name):
        if name in resolved:return resolved[name]
        if name in visiting:raise ValueError('Herencia de templates circular: '+name)
        visiting.add(name);row=ts[name]
        mapping(row,{'id','base','mode','properties'},{'id','base'},'template '+name);fixed(name)
        if name.casefold() in originals:raise ValueError('Template propio colisiona con original: '+name)
        base=row['base'];props=row.get('properties',{})
        mapping(props,set(EDITABLE)-{'parent'},label='propiedades de template')
        if base in ts:parent,record=resolve(base)
        else:
            matches=originals.get(str(base).casefold(),[])
            if len(matches)!=1:raise ValueError('Base ausente o ambigua: '+str(base))
            record=matches[0];nf=NotFile.read(original_bytes(ws,record));parent=next(t for t in nf.templates if t.name==record['id'])
        mode=row.get('mode','inherit')
        if mode=='inherit':new=Template(name,[Tag.text(0,parent.name)],b'RCM custom template\0')
        elif mode=='copy':new=copy.deepcopy(parent);new.name=name;new.name_field=None
        else:raise ValueError('Template mode: inherit/copy')
        engine_props=dict(props)
        for key,extension in [('ai','.nai'),('model','.nod')]:
            if modern and key in engine_props:
                entry=original_entry({'entries':entries},extension,engine_props[key])
                # The editor selects catalogue IDs; NOT stores filenames,
                # as in businessWoman's inherited original "ped.nai" field.
                engine_props[key]=Path(entry['path']).name
        new=patch_template(new,{'cast_id':name,'description_id':name,**engine_props});record={**record,'id':name,'parent':base,'archive':'PROJECT','path':not_path,'project_owned':True}
        if 'motions' in engine_props:record['motions']=engine_props['motions']
        for k in ('model','ai','script'):
            if k in engine_props:record[k]=engine_props[k]
            if record.get(k):original_entry({'entries':entries},{'model':'.nod','ai':'.nai','script':'.class'}[k],record[k])
        if props.get('script'):record['custom_script']=props['script']
        resolved[name]=(new,record);visiting.remove(name);return new,record
    for name in ts:resolve(name)
    if ts:
        payload[not_path]=NotFile([x[0] for x in resolved.values()]).encode();templates += [x[1] for x in resolved.values()]
    for k in EXTENSIONS:root.pop(k,None)
    return root,{**catalogue,'entries':entries,'templates':templates},payload,{'templates':list(ts),'ai_profiles':list(ais),'scripts':scripts,'textures':list(textures),'metadata':metadata,'debug':options.get('debug',True),'not_path':not_path}

def add_to_build(ws,report,payload,info,compile_java=True):
    from .generator import zip_bytes
    root=Path('build')/report['chronicle'];prefix='R_'+report['chronicle']
    payload=dict(payload)
    if compile_java and info['scripts']:
        out=ws.output(root/'custom_classes');out.mkdir(parents=True,exist_ok=True)
        sources=[str(ws.output(s['source'])) for s in info['scripts'].values()]
        command=['java','-jar',str(ws.output('cache/toolchain/ecj-3.26.0.jar')),'-1.3','-proc:none','-encoding','UTF-8','-bootclasspath',str(ws.output('cache/toolchain/classes.zip')),'-classpath',str(ws.output('research/original/Codex.nob')),'-d',str(out),*sources]
        result=subprocess.run(command,capture_output=True,text=True);ws.write(root/'custom_compiler.log',result.stdout+result.stderr)
        if result.returncode:raise ValueError('Java propio no compila; consulta custom_compiler.log: '+result.stderr[:1000])
        for name in info['scripts']:
            for p in out.glob(name+'*.class'):
                if p.stem!=name and not p.stem.startswith(name+'$'):continue
                data=p.read_bytes()
                if struct.unpack_from('>HH',data,4)!=(3,45):raise ValueError('Clase custom no compatible con JVM 45.3')
                payload['codex/'+p.name]=data;report['class_versions'][p.stem]='45.3'
    # Own paths never replace an original. Only add to our generated archive.
    nob=ws.output(root/(report['chronicle']+'.nob'))
    with zipfile.ZipFile(nob) as z:runtime={n:z.read(n) for n in z.namelist()}
    for k,v in payload.items():
        if not k.startswith('codex/'):
            if k in runtime:raise ValueError('Conflicto de recurso propio: '+k)
            runtime[k]=v
    if info['templates']:
        key='chronicles/'+prefix+'.nmf';runtime[key]=('NOT '+Path(info['not_path']).name+'\r\n').encode('cp1252')+runtime[key]
    nls=[]
    for name in info['templates']:nls.append(name+' '+name)
    if nls:
        key='strings/'+prefix+'_custom.nls';runtime[key]=('\r\n'.join(nls)+'\r\n').encode('cp1252');runtime['chronicles/'+prefix+'.nmf']+=('NLS '+prefix+'_custom.nls\r\n').encode('cp1252')
    for k,v in runtime.items():ws.write(root/'runtime'/k,v)
    data=zip_bytes(runtime);ws.write(root/(report['chronicle']+'.nob'),data)
    distribution={k:ws.output(root/'bundle'/k).read_bytes() for k in report['distribution_files'] if k.startswith('codex/')}
    distribution.update({k:v for k,v in payload.items() if k.startswith('codex/')});distribution[report['chronicle']+'.nob']=data
    for k,v in distribution.items():ws.write(root/'bundle'/k,v)
    if compile_java:ws.write(root/(report['chronicle']+'_distribution.zip'),zip_bytes(distribution))
    report['distribution_files']={k:dict(size=len(v),sha256=hashlib.sha256(v).hexdigest()) for k,v in distribution.items()}
    report['files']={k:dict(size=len(v),sha256=hashlib.sha256(v).hexdigest()) for k,v in {**runtime,**{k:v for k,v in distribution.items() if k.startswith('codex/')}}.items()}
    report['custom_scripts']=list(info.get('scripts',{}))
    report['project_resources']={k:v for k,v in info.items() if k!='scripts'};report['not_writer_status']='experimental-awaiting-native-acceptance';return report
