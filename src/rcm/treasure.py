"""Native GAME.NTT class catalogue; never generate a parallel loot system."""
import re
from .project_resources import original_entry,original_bytes


def parse(data):
    result=[];description='';current=None;seen=set()
    for line in data.decode('cp1252').splitlines():
        if line.strip().startswith('//') and line.strip()[2:].strip():description=line.strip()[2:].strip()
        match=re.fullmatch(r'CLASS:\s*(\d+)\s*',line)
        if match:
            ident=int(match[1])
            if not 0<=ident<=255 or ident in seen:raise ValueError('NTT: clase fuera de rango o duplicada')
            seen.add(ident);current=dict(id=ident,description=description,items=[]);result.append(current)
        elif line.startswith('CITEM:') and current:current['items'].append(line.split()[1:])
    if not result:raise ValueError('NTT: no hay clases de tesoro')
    return result


def catalogue(ws,resources):
    entry=original_entry(resources,'.ntt','game')
    if ws.game or ws.output('research/original/'+entry['archive']+'/'+entry['path']).is_file():return parse(original_bytes(ws,entry))
    from .deployment import default_game
    from .paths import Workspace
    game=default_game(ws.root)
    if game is None:raise ValueError('Selecciona Redemption para leer sus clases de tesoro')
    return parse(original_bytes(Workspace(ws.root,game),entry))
