"""Read back generated formats and verify links before publishing a build."""
from pathlib import PurePosixPath
import zipfile
from .formats import NotFile, Scene
from .catalogue import parse_chronicle, rows


def verify_output(ws, report, catalogue):
    root = 'build/'+report['chronicle']
    with zipfile.ZipFile(ws.output(root+'/'+report['chronicle']+'.nob')) as archive:
        payload = {name:archive.read(name) for name in archive.namelist()}
    known = {str(PurePosixPath(name)).casefold() for name in payload}
    original = {entry['path'].casefold() for entry in catalogue['entries']}
    original_names = {PurePosixPath(name).name for name in original}
    known_names = {PurePosixPath(name).name for name in known}
    def exists(name):return name.casefold() in known or name.casefold() in original or PurePosixPath(name).name.casefold() in original_names|known_names
    strings = set()
    voices = set()
    for name, data in payload.items():
        if name.lower().endswith(('.nvo','.nls')):
            keys = []
            for _, fields in rows(data.decode('cp1252')):
                keys.append(fields[0])
                if name.lower().endswith('.nvo') and (len(fields)<3 or not exists(fields[1]+'.wav')):
                    raise ValueError('Voz ausente en '+name)
            if len(set(keys)) != len(keys):raise ValueError('Strings duplicadas en '+name)
            (voices if name.lower().endswith('.nvo') else strings).update(keys)
    for name, data in payload.items():
        suffix = PurePosixPath(name).suffix.lower()
        if suffix == '.not':
            if NotFile.read(data).encode()!=data:raise ValueError('NOT no conserva bytes: '+name)
        elif suffix == '.nsd':
            if Scene.read(data).encode()!=data:raise ValueError('NSD no conserva bytes: '+name)
        elif suffix == '.nsc':
            chronicle = parse_chronicle(data)
            ids = [row['id'] for row in chronicle['locations']]
            if not ids or len(ids)!=len(set(ids)):raise ValueError('Locations vacías/duplicadas')
            for row in chronicle['locations']:
                if not exists(row['nil']) or not exists(row['scene']):raise ValueError('Level/escena ausente: '+row['id'])
            for reference in chronicle['settings'].get('metafile',[]):
                if not exists(reference):raise ValueError('Metafile ausente')
        elif suffix == '.nmf':
            for _, fields in rows(data.decode('cp1252')):
                if fields[0] in {'NOT','NLS','NVO'} and (len(fields)!=2 or not exists(fields[1])):raise ValueError('Recurso NMF ausente: '+name)
        elif suffix == '.nco':
            commands = [fields for _, fields in rows(data.decode('cp1252'))]
            events = [f[1] for f in commands if f[0]=='EVENT:' and len(f)==2]
            if len(events)!=len(set(events)):raise ValueError('Events NCO duplicados')
            for fields in commands:
                if fields[0]=='ANSWERGOTO:' and (len(fields)!=3 or fields[2] not in events):raise ValueError('Destino NCO ausente')
                if fields[0] in {'LINE:','ANSWERGOTO:','ANSWERRETURN:'} and (len(fields)!=3 or fields[1] not in voices):raise ValueError('Texto NVO ausente')
                if fields[0]=='ANSWERRETURN:':
                    try:int(fields[2])
                    except (ValueError,IndexError) as error:raise ValueError('RETURN NCO inválido') from error
        elif suffix == '.nqd':
            for _, fields in rows(data.decode('cp1252')):
                if fields[0]!='QUEST' or len(fields)!=7 or fields[3] not in strings or fields[4] not in strings:raise ValueError('Quest NQD inválida')
    budgets={}
    for name, record in report.get('distribution_files',{}).items():
        data = ws.output(root+'/bundle/'+name).read_bytes()
        import hashlib
        if len(data)!=record['size'] or hashlib.sha256(data).hexdigest()!=record['sha256']:raise ValueError('Manifest de distribución incorrecto')
        if name.endswith('.class') and data[:8]!=bytes.fromhex('cafebabe0003002d'):raise ValueError('Classfile incompatible')
        if name.endswith('.class'):
            from .classfile_limits import inspect_class
            budgets[name]=inspect_class(data)
    return {'files_checked':len(payload),'conversations':sum(n.endswith('.nco') for n in payload),'classfiles':len(report.get('class_versions',{})),'classfile_budgets':budgets,'native_engine_test':False}
