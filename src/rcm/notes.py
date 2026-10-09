"""Native NTX text windows, following the original MP_CTD grammar."""
import re
from .model import mapping


def validate_note(value):
    mapping(value,{'title','text'},{'title','text'},'show_note')
    for key,limit in [('title',160),('text',12000)]:
        text=value[key]
        if not isinstance(text,str) or not text.strip() or len(text)>limit:
            raise ValueError('Nota: '+key+' requiere texto, máximo '+str(limit)+' caracteres')
        if any(ord(c)<32 and c not in '\n\r' for c in text) or any(c in text for c in '<>') or ('\n' in text or '\r' in text) and key=='title':
            raise ValueError('Nota: no se admite marcado NTX ni controles en '+key)
        try:text.encode('cp1252')
        except UnicodeEncodeError as error:raise ValueError('Nota: el motor usa Windows-1252') from error
    return value


def note_id(prefix,event,action):
    return prefix+'_t'+str(event)+'_'+str(action)


def encode_notes(records):
    """Own writer: none means no voice, 0 is the original native text flag."""
    rows=[];seen=set()
    for ident,value in records:
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,30}',ident) or ident in seen:raise ValueError('ID de nota inválido o duplicado')
        seen.add(ident);validate_note(value)
        rows += ['<TEXT '+ident+' none 0>','<TITLE '+value['title'].strip()+'>']
        for paragraph in re.split(r'\n\s*\n',value['text'].replace('\r\n','\n').replace('\r','\n').strip()):
            rows += ['<P 0xFFFFFFFF>',' '.join(paragraph.splitlines())]
        rows += ['</TEXT>','']
    return ('\r\n'.join(rows)+'\r\n').encode('cp1252')


def read_notes(data):
    """Strict readback of our no-voice, flag-0 NTX subset; no guessed tags."""
    records=[];current=None;paragraphs=[];seen=set()
    for raw in data.decode('cp1252').splitlines():
        line=raw.strip()
        if not line:continue
        opening=re.fullmatch(r'<TEXT ([A-Za-z_][A-Za-z0-9_]{0,30}) none 0>',line)
        if opening:
            if current is not None or opening[1] in seen:raise ValueError('NTX: bloque anidado o ID duplicado')
            seen.add(opening[1]);current={'id':opening[1]};paragraphs=[]
        elif current is None:raise ValueError('NTX: texto fuera de bloque')
        elif line.startswith('<TITLE ') and line.endswith('>'):
            if 'title' in current or paragraphs:raise ValueError('NTX: título duplicado o fuera de orden')
            current['title']=line[7:-1]
        elif line=='<P 0xFFFFFFFF>':paragraphs.append([])
        elif line=='</TEXT>':
            if not paragraphs or any(not p for p in paragraphs):raise ValueError('NTX: párrafo vacío')
            current['text']='\n\n'.join(' '.join(p) for p in paragraphs)
            validate_note({k:current[k] for k in ('title','text') if k in current})
            records.append(current);current=None
        elif '<' in line or '>' in line or not paragraphs:raise ValueError('NTX: marcado o párrafo inválido')
        else:paragraphs[-1].append(line)
    if current is not None or not records:raise ValueError('NTX: vacío o bloque sin cerrar')
    return records
