"""Read-only NOT inspection with lossless unknown fields and provenance."""
import struct
from .formats import NotFile,cstring,u32
# Only properties with evidence in original bytes/engine ordered property names.
KNOWN={0:('parent','text'),1:('orientation','vector'),2:('position','vector'),3:('sector','int'),4:('model','text'),6:('foley','text'),9:('motions','text'),11:('script','text'),16:('thing_type','int'),20:('item_type','int'),56:('ai','text'),81:('cast_id','text'),82:('description_id','text'),114:('actor_flags','int')}

def inspect_not(data):
    parsed=NotFile.read(data);rows=[]
    for i,t in enumerate(parsed.templates):
        offset=u32(data,12+i*36+32);props=[]
        for j,tag in enumerate(t.tags):
            name,kind=KNOWN.get(tag.id,('unknown','raw'))
            value=cstring(tag.value) if kind=='text' else list(struct.unpack_from('<3f',tag.value)) if kind=='vector' else u32(tag.value) if kind=='int' else tag.value.hex()
            props.append({'tag':tag.id,'name':name,'value':value,'raw_hex':tag.value.hex(),'offset':offset+4+j*36})
        rows.append({'name':t.name,'offset':offset,'properties':props,'comment_hex':t.comment.hex()})
    return {'version':parsed.version,'templates':rows,'opaque_tail_bytes':len(parsed.trailing),'lossless_roundtrip':parsed.encode()==data}

def inspect_template(ws,resource,payload=None):
    if resource.get('project_owned'):
        data=(payload or {}).get(resource['path'])
        if data is None:raise ValueError('Compila o valida la biblioteca propia antes de inspeccionar sus bytes')
        return next(r for r in inspect_not(data)['templates'] if r['name']==resource['id'])
    from .project_resources import original_bytes
    # Template catalogue path points at NOT, not a generated record.
    rows=inspect_not(original_bytes(ws,resource))['templates']
    return next(r for r in rows if r['name']==resource['id'])
