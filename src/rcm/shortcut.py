"""Read Windows .lnk metadata; do not rewrite the user's desktop shortcut."""
from pathlib import Path
import re,struct


def create_shortcut(ws,name,target,arguments='',cwd=None,icon=None):
    """Create on the destination PC, using structured data rather than shell interpolation."""
    import base64,json,subprocess,os
    if os.name!='nt':raise ValueError('Los accesos directos requieren Windows')
    # Name is authored text, never a filesystem path.
    safe=re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',name).strip(' .')[:100] or 'RCM'
    path=ws.output('launchers/'+safe+'.lnk');path.parent.mkdir(parents=True,exist_ok=True)
    payload=dict(path=str(path),target=str(target),arguments=arguments,cwd=str(cwd or Path(target).parent),icon=str(icon or target))
    encoded=base64.b64encode(json.dumps(payload,ensure_ascii=False).encode('utf8')).decode()
    script="$ErrorActionPreference='Stop'; $rcmData=[System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('"+encoded+"')) | ConvertFrom-Json; $rcmShell=New-Object -ComObject WScript.Shell; $rcmLink=$rcmShell.CreateShortcut($rcmData.path); $rcmLink.TargetPath=$rcmData.target; $rcmLink.Arguments=$rcmData.arguments; $rcmLink.WorkingDirectory=$rcmData.cwd; $rcmLink.IconLocation=$rcmData.icon; $rcmLink.Save()"
    subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(script.encode('utf-16-le')).decode()],check=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    return path


def chronicle_shortcut(ws,ident,name):
    from .deployment import configured_game
    from .model import identifier
    identifier(ident,'chronicle',14);game=configured_game(ws)
    return create_shortcut(ws,'Jugar - '+name,game/'Vampire.exe','-user RCM\\'+ident,game)


def application_shortcut(ws):
    import sys
    if not getattr(sys,'frozen',False):raise ValueError('Crea el acceso desde la aplicación portable')
    return create_shortcut(ws,'Redemption Chronicle Maker',sys.executable)


def read_shortcut(path):
    data=Path(path).read_bytes()
    if len(data)<76 or data[:4]!=b'L\0\0\0':raise ValueError('Acceso directo Windows inválido')
    def u32(offset):
        if offset+4>len(data):raise ValueError('Acceso directo truncado')
        return struct.unpack_from('<I',data,offset)[0]
    flags=u32(20);offset=76;target=''
    if flags&1:
        if offset+2>len(data):raise ValueError('IDList truncada')
        offset+=2+struct.unpack_from('<H',data,offset)[0]
    if flags&2:
        size=u32(offset);header=u32(offset+4)
        if size<28 or offset+size>len(data):raise ValueError('LinkInfo inválido')
        start=u32(offset+28) if header>=36 else 0
        if start:
            raw=data[offset+start:offset+size];end=next((i for i in range(0,len(raw)-1,2) if raw[i:i+2]==b'\0\0'),len(raw));target=raw[:end].decode('utf-16-le')
        else:
            start=u32(offset+16)
            if start:target=data[offset+start:offset+size].split(b'\0',1)[0].decode('cp1252')
        offset+=size
    result={'target':target}
    for flag,key in [(4,'name'),(8,'relative'),(16,'cwd'),(32,'arguments'),(64,'icon')]:
        if flags&flag:
            if offset+2>len(data):raise ValueError('StringData truncada')
            count=struct.unpack_from('<H',data,offset)[0];offset+=2;size=count*(2 if flags&128 else 1)
            if offset+size>len(data):raise ValueError('StringData truncada')
            result[key]=data[offset:offset+size].decode('utf-16-le' if flags&128 else 'cp1252');offset+=size
    return result


def launch_info(ws):
    from .deployment import configured_game,safe_target
    from .startup import settings
    selected=settings(ws).get('desktop_shortcut')
    path=Path(selected) if selected else Path.home()/'Desktop'/'Vampire.exe - Acceso directo.lnk'
    if not path.is_file():return None
    info=read_shortcut(path);game=configured_game(ws)
    if Path(info['target']).resolve()!=(game/'Vampire.exe').resolve():raise ValueError('El acceso directo no apunta al Vampire.exe seleccionado')
    if Path(info.get('cwd','')).resolve()!=game:raise ValueError('El acceso directo debe iniciar en la carpeta del juego')
    match=re.fullmatch(r'\s*-user\s+"?(RCM[/\\][A-Za-z0-9_/-]+)"?\s*',info.get('arguments',''),re.I)
    if not match:raise ValueError('El acceso directo debe usar -user RCM\\carpeta')
    directory=safe_target(game,game/Path(match[1]));return {'shortcut':path,'directory':directory,'relative':directory.relative_to(game/'RCM').as_posix()}
