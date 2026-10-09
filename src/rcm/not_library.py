"""Conservative NOT editing: typed edits only, opaque payloads remain opaque."""
import copy,math
from .formats import NotFile,Template,Tag,fixed,cstring
from .not_inspector import KNOWN

EDITABLE={name:(tag,kind) for tag,(name,kind) in KNOWN.items() if tag not in {3,16}}

def encode_property(name,value):
    if name not in EDITABLE:raise ValueError('Propiedad NOT no soportada: '+name)
    tag,kind=EDITABLE[name]
    if kind=='text':
        if not isinstance(value,str):raise ValueError(name+': requiere texto')
        return Tag.text(tag,value)
    if kind=='int':
        if type(value) is not int or not 0<=value<=0xffffffff:raise ValueError(name+': requiere uint32')
        return Tag.integer(tag,value)
    if not isinstance(value,(list,tuple)) or len(value)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1e8 for v in value):raise ValueError(name+': requiere tres números finitos')
    return Tag.vector(tag,value)

def patch_template(template,properties):
    result=copy.deepcopy(template)
    for name,value in properties.items():
        replacement=encode_property(name,value)
        hits=[i for i,t in enumerate(result.tags) if t.id==replacement.id]
        if len(hits)>1:raise ValueError('Tag duplicado: no se edita de forma ambigua')
        if hits:
            # Typed scalars occupy a prefix; preserve padding/unknown bytes.
            old=result.tags[hits[0]];size=4 if EDITABLE[name][1]=='int' else 12 if EDITABLE[name][1]=='vector' else 32
            result.tags[hits[0]]=Tag(old.id,replacement.value[:size]+old.value[size:])
        else:result.tags.append(replacement)
    return result

class NotLibrary:
    def __init__(self,data):self.file=NotFile.read(data)
    def find(self,name):
        matches=[t for t in self.file.templates if t.name.casefold()==name.casefold()]
        if len(matches)!=1:raise ValueError('Template ausente o ambiguo: '+name)
        return matches[0]
    def add(self,base,name,properties=None,mode='inherit'):
        if self.file.trailing:raise ValueError('Cola opaca: no se modifica la estructura de esta biblioteca')
        fixed(name)
        if any(t.name.casefold()==name.casefold() for t in self.file.templates):raise ValueError('Template duplicado: '+name)
        source=self.find(base)
        if mode=='inherit':t=Template(name,[Tag.text(0,source.name)],b'RCM project template\0')
        elif mode=='copy':t=copy.deepcopy(source);t.name=name;t.name_field=None
        else:raise ValueError('Modo NOT no soportado')
        t=patch_template(t,properties or {});self.file.templates.append(t);return t
    def rename(self,old,new):
        if self.file.trailing:raise ValueError('Cola opaca: no se renombra dentro de esta biblioteca')
        fixed(new);row=self.find(old)
        if any(t is not row and t.name.casefold()==new.casefold() for t in self.file.templates):raise ValueError('Template duplicado')
        row.name=new;row.name_field=None
        for t in self.file.templates:
            for i,tag in enumerate(t.tags):
                if tag.id==0 and cstring(tag.value).casefold()==old.casefold():t.tags[i]=Tag.text(0,new)
    def edit(self,name,properties):
        old=self.find(name);index=self.file.templates.index(old);self.file.templates[index]=patch_template(old,properties)
    def encode(self):return self.file.encode()
