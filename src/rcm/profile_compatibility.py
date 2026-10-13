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
    def read_templates(data):
        result={}
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for name in archive.namelist():
                if name.lower().endswith('.not'):
                    for template in NotFile.read(archive.read(name)).templates:result[template.name.casefold()]=template
        return result
    current=read_templates(current_nob);known={};classes={}
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
                try:known.update(read_templates(data))
                except (ValueError,zipfile.BadZipFile):continue
            elif re.fullmatch(r'codex/[A-Za-z_][A-Za-z0-9_$]*\.class',name):classes[name]=data
    missing=(required & known.keys())-current.keys()
    if not missing:return {}
    keep={};scripts=set()
    def collect(name):
        if name in keep or name in current:return
        template=known.get(name)
        if template is None:return  # Parent is an original game definition.
        keep[name]=template;values=template.values()
        if 0 in values:collect(cstring(values[0]).casefold())
        if 11 in values:scripts.add(cstring(values[11]))
    for name in missing:collect(name)
    from .generator import zip_bytes
    files={'rcm_compat.nob':zip_bytes({'misc/Templates/_rcm_compat.not':NotFile(list(keep.values())).encode()})}
    for script in scripts:
        name='codex/'+script+'.class'
        if name in classes:files[name]=classes[name]
        elif script.startswith(('R_','RCM')):raise ValueError('Falta la clase de un objeto RCM conservado: '+script)
    return files


def profile_signature(game):
    required=set()
    for profile in (game/'Crypt').glob('*.npf'):required.update(profile_references(profile.read_bytes()))
    return hashlib.sha256('\n'.join(sorted(required)).encode('ascii')).hexdigest()
