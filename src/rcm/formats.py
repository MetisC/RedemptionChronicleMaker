"""Independent binary codecs derived from installation bytes.

Unknown NOT tags and trailing data survive a roundtrip. NSD supports simple
entities, native frames/constructor arguments and our bounded click brushes.
See FORMAT_NOTES.md.
"""
from dataclasses import dataclass
import struct


def u32(data: bytes, offset: int = 0) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise ValueError("Entero truncado")
    return struct.unpack_from("<I", data, offset)[0]


def cstring(data: bytes) -> str:
    return data.split(b"\0", 1)[0].decode("cp1252")


def fixed(value: str, size: int = 32) -> bytes:
    b = value.encode("cp1252")
    if b"\0" in b or len(b) >= size:
        raise ValueError(f"Cadena inválida para campo de {size} bytes: {value!r}")
    return b + bytes(size - len(b))


@dataclass(frozen=True)
class Tag:
    id: int
    value: bytes

    def __post_init__(self):
        if len(self.value) != 32 or not 0 <= self.id <= 0xffffffff:
            raise ValueError("Un tag contiene un identificador uint32 y 32 bytes")

    @classmethod
    def text(cls, id: int, value: str):
        return cls(id, fixed(value))

    @classmethod
    def integer(cls, id: int, value: int):
        return cls(id, struct.pack("<I", value) + bytes(28))

    @classmethod
    def vector(cls, id: int, value):
        return cls(id, struct.pack("<3f", *value) + bytes(20))

    def encode(self) -> bytes:
        return struct.pack("<I", self.id) + self.value


def read_tags(data: bytes, offset: int):
    count = u32(data, offset)
    offset += 4
    if count > 4096 or offset + count * 36 > len(data):
        raise ValueError("Tabla de tags truncada o excesiva")
    tags = [Tag(u32(data, offset + i * 36), data[offset + i * 36 + 4:offset + (i + 1) * 36]) for i in range(count)]
    return tags, offset + count * 36


def encode_tags(tags) -> bytes:
    return struct.pack("<I", len(tags)) + b"".join(t.encode() for t in tags)


@dataclass
class Template:
    name: str
    tags: list[Tag]
    comment: bytes = b"\0"
    name_field: bytes | None = None

    def encode(self):
        return encode_tags(self.tags) + struct.pack("<I", len(self.comment)) + self.comment

    def values(self):
        return {t.id: t.value for t in self.tags}


@dataclass
class NotFile:
    templates: list[Template]
    version: int = 1
    trailing: bytes = b""

    @classmethod
    def read(cls, data: bytes):
        if len(data) < 12 or data[:4] != b"NOT\x10" or u32(data, 4) != 1:
            raise ValueError("NOT no reconocido (se admite NOT 0x10 / versión 1)")
        n = u32(data, 8)
        table_end = 12 + n * 36
        if n > 100000 or table_end > len(data):
            raise ValueError("Índice NOT truncado")
        templates, end, names = [], table_end, set()
        for i in range(n):
            name_field = data[12 + i * 36:44 + i * 36]
            if b'\0' not in name_field or not name_field.split(b'\0',1)[0]:raise ValueError('Nombre NOT vacío o sin terminador')
            key=cstring(name_field).casefold()
            if key in names:raise ValueError('Plantillas NOT duplicadas')
            names.add(key)
            ptr = u32(data, 44 + i * 36)
            if ptr != end:
                raise ValueError("Índice NOT no contiguo; no se reconstruye de forma insegura")
            tags, p = read_tags(data, ptr)
            length = u32(data, p)
            end = p + 4 + length
            if not length or end > len(data) or data[end - 1] != 0:
                raise ValueError("Comentario NOT truncado o sin terminador")
            templates.append(Template(cstring(name_field), tags, data[p + 4:end], name_field))
        return cls(templates, 1, data[end:])

    def encode(self):
        chunks, table = [], []
        pos = 12 + len(self.templates) * 36
        names = set()
        for t in self.templates:
            if t.name.casefold() in names:
                raise ValueError("Plantillas NOT duplicadas")
            names.add(t.name.casefold())
            if not t.comment or t.comment[-1] != 0:
                raise ValueError("Comentario NOT sin terminador")
            chunk = t.encode()
            name_field = t.name_field if t.name_field and cstring(t.name_field) == t.name else fixed(t.name)
            table.append(name_field + struct.pack("<I", pos))
            chunks.append(chunk)
            pos += len(chunk)
        return b"NOT\x10" + struct.pack("<II", self.version, len(chunks)) + b"".join(table + chunks) + self.trailing


@dataclass
class Scene:
    name: str
    layout_name: str
    entities: list[list[Tag]]
    environment: bytes = bytes(192)
    header: bytes | None = None
    brushes: dict[int, bytes] | None = None
    entrances: list[bytes] | None = None
    conversation_starts: list[bytes] | None = None
    parameters: dict[int,list] | None = None
    frames: dict[int,list[bytes]] | None = None
    interest_spots: list[bytes] | None = None
    regions: dict[int,list[int]] | None = None

    @classmethod
    def read(cls, data: bytes):
        if len(data) < 276 or data[:4] != b"NSD\x10" or u32(data, 4) != 8:
            raise ValueError("NSD no reconocido (se admite NSD 0x10 / versión 8)")
        n = u32(data, 80)
        if n > 100000:
            raise ValueError("Número excesivo de entidades")
        if u32(data,76):raise ValueError('NSD: header string table outside supported subset')
        entities, p, brushes, parameters, frames, regions = [], 84, {}, {}, {}, {}
        for _ in range(n):
            tags, p = read_tags(data, p)
            if p + 12 > len(data):raise ValueError('NSD entity truncated')
            count=u32(data,p)
            if count:
                if count>4096 or p+4+24*count>len(data):raise ValueError('NSD movement frames truncated or excessive')
                frames[len(entities)]=[data[p+4+i*24:p+4+(i+1)*24] for i in range(count)]
                p+=24*count
            count=u32(data,p+4);p+=8
            if count:
                from .script_parameters import read
                rows,p=read(data,p,count);parameters[len(entities)]=rows
            mesh=u32(data,p);p+=4
            if mesh:
                if mesh!=1:raise ValueError('NSD: unsupported mesh count')
                from .spatial.scene_mesh import read_brush
                start=p;body=read_brush(data,p);p=body.source_end
                from .click_interactions import box_planes
                expected=box_planes([*body.bounds[0],*body.bounds[1]])
                if data[p:p+len(expected)]!=expected:raise ValueError('NSD: collision planes outside generated subset')
                p+=len(expected);brushes[len(entities)]=data[start:p]
            count=u32(data,p);p+=4
            if count:
                if count>10000 or p+count*4>len(data):raise ValueError('NSD: invalid region sector count')
                sectors=list(struct.unpack_from('<'+str(count)+'I',data,p));p+=count*4
                if len(set(sectors))!=len(sectors) or any(s>=100000 for s in sectors):raise ValueError('NSD: invalid region sector links')
                regions[len(entities)]=sectors
            if u32(data,p):raise ValueError('NSD: lighting blocks outside generated subset')
            p+=4
            entities.append(tags)
        entrances=[]
        if len(data)-p>=192 and data[p:p+4]==bytes(4):
            count=u32(data,p+4)
            if count>4096:raise ValueError('NSD: excessive entrances')
            if count:
                from .native_arrivals import validate_record
                entrances=[validate_record(data[p+8+i*60:p+8+(i+1)*60]) for i in range(count)]
                data=data[:p+4]+bytes(4)+data[p+8+count*60:]
        conversations=[]
        interests=[]
        if len(data)-p>=192 and data[p:p+8]==bytes(8):
            count=u32(data,p+8)
            if count>4096:raise ValueError('NSD: excessive interest spots')
            if count:
                if p+12+72*count>len(data):raise ValueError('NSD: truncated interest spots')
                from .interest_spots import validate_record
                interests=[validate_record(data[p+12+i*72:p+12+(i+1)*72]) for i in range(count)]
                data=data[:p+8]+bytes(4)+data[p+12+count*72:]
        if len(data)-p>=192 and data[p:p+12]==bytes(12):
            count=u32(data,p+12)
            if count>64:raise ValueError('NSD: excessive generated conversation starts')
            if count:
                from .native_arrivals import validate_record
                conversations=[validate_record(data[p+16+i*60:p+16+(i+1)*60]) for i in range(count)]
                if any(u32(row,52)>15 or u32(row,56)!=0 for row in conversations):raise ValueError('NSD: invalid generated conversation group')
                data=data[:p+12]+bytes(4)+data[p+16+count*60:]
        if len(data) - p != 192:
            raise ValueError("NSD con bloques variables: fuera del subconjunto Fase 1")
        return cls(cstring(data[8:40]), cstring(data[40:72]), entities, data[p:], data[:84],brushes or None,entrances or None,conversations or None,parameters or None,frames or None,interests or None,regions or None)

    def encode(self):
        if len(self.environment) != 192:
            raise ValueError("Bloque de entorno NSD debe tener 192 bytes")
        header = bytearray(self.header or b"NSD\x10" + struct.pack("<I", 8) + bytes(76))
        if self.header is None:
            header[8:40], header[40:72] = fixed(self.name), fixed(self.layout_name)
        else:
            if cstring(header[8:40]) != self.name:
                header[8:40] = fixed(self.name)
            if cstring(header[40:72]) != self.layout_name:
                header[40:72] = fixed(self.layout_name)
        struct.pack_into("<I", header, 80, len(self.entities))
        brushes=self.brushes or {}
        if any(type(i) is not int or not 0<=i<len(self.entities) for i in brushes):raise ValueError('NSD: invalid brush entity')
        chunks=[]
        parameters=self.parameters or {}
        frames=self.frames or {}
        regions=self.regions or {}
        if any(type(i) is not int or not 0<=i<len(self.entities) or not sectors or len(sectors)>10000 or len(set(sectors))!=len(sectors) or any(type(s) is not int or not 0<=s<100000 for s in sectors) for i,sectors in regions.items()):raise ValueError('NSD: invalid region sector links')
        if any(type(i) is not int or not 0<=i<len(self.entities) or not 1<=len(rows)<=4096 or any(len(r)!=24 for r in rows) for i,rows in frames.items()):raise ValueError('NSD: invalid movement frame count or width')
        if any(type(i) is not int or not 0<=i<len(self.entities) or not 1<=len(rows)<=16 for i,rows in parameters.items()):raise ValueError('NSD: invalid parameter entity or count')
        for i,tags in enumerate(self.entities):
            body=brushes.get(i)
            if body is not None:
                from .spatial.scene_mesh import read_brush
                from .click_interactions import box_planes
                mesh=read_brush(body,0);end=mesh.source_end;expected=box_planes([*mesh.bounds[0],*mesh.bounds[1]])
                if body[end:]!=expected:raise ValueError('NSD: brush requires six bounded collision planes')
            args=parameters.get(i,[])
            motion=frames.get(i,[])
            prefix=struct.pack('<I',len(motion))+b''.join(motion)+struct.pack('<I',len(args))+b''.join(row.encode() for row in args)
            sectors=regions.get(i,[]);links=struct.pack('<I',len(sectors))+b''.join(struct.pack('<I',s) for s in sectors)+bytes(4)
            chunks.append(encode_tags(tags)+prefix+(struct.pack('<I',1)+body if body is not None else bytes(4))+links)
        environment=self.environment
        if self.conversation_starts:
            from .native_arrivals import validate_record
            records=self.conversation_starts
            if environment[:16]!=bytes(16) or len(records)>64:raise ValueError('NSD: conversation table requires an empty generated global section')
            for record in records:
                validate_record(record)
                if u32(record,52)>15 or u32(record,56)!=0:raise ValueError('NSD: invalid generated conversation group')
            environment=environment[:12]+struct.pack('<I',len(records))+b''.join(records)+environment[16:]
        if self.interest_spots:
            from .interest_spots import validate_record
            if self.environment[:16]!=bytes(16) or len(self.interest_spots)>4096:raise ValueError('NSD: invalid interest records')
            for record in self.interest_spots:validate_record(record)
            environment=environment[:8]+struct.pack('<I',len(self.interest_spots))+b''.join(self.interest_spots)+environment[12:]
        if self.entrances:
            from .native_arrivals import validate_record
            if self.environment[:16]!=bytes(16) or len(self.entrances)>4096:raise ValueError('NSD: entrance table requires an empty generated global section')
            environment=environment[:4]+struct.pack('<I',len(self.entrances))+b''.join(validate_record(r) for r in self.entrances)+environment[8:]
        return bytes(header)+b''.join(chunks)+environment


def scene_entity_hints(data: bytes):
    """Bounded heuristic for original complex scenes; not a full NSD parser."""
    import re
    result = []
    for match in re.finditer(rb"\x00\x00\x00\x00([A-Za-z_][A-Za-z_0-9]{2,31})\x00", data):
        p = match.start() - 4
        if p < 84:
            continue
        n = u32(data, p)
        if not 3 <= n <= 100 or p + 4 + n * 36 > len(data):
            continue
        tags, _ = read_tags(data, p)
        v = {t.id: t.value for t in tags}
        if all(i in v for i in (0, 1, 2, 3)):
            result.append({"offset": p, "template": cstring(v[0]),
                           "position": list(struct.unpack("<3f", v[2][:12])),
                           "orientation": list(struct.unpack("<3f", v[1][:12])),
                           "sector": u32(v[3]), "script": cstring(v[11]) if 11 in v else None,
                           "confidence": "tag-pattern; not full scene parse"})
    return result
