"""Independent binary codecs derived from installation bytes.

Unknown NOT tags and trailing data survive a roundtrip. NSD is restricted to
entities without meshes, frames or script parameters. See FORMAT_NOTES.md.
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

    @classmethod
    def read(cls, data: bytes):
        if len(data) < 276 or data[:4] != b"NSD\x10" or u32(data, 4) != 8:
            raise ValueError("NSD no reconocido (se admite NSD 0x10 / versión 8)")
        n = u32(data, 80)
        if n > 100000:
            raise ValueError("Número excesivo de entidades")
        entities, p = [], 84
        for _ in range(n):
            tags, p = read_tags(data, p)
            if p + 20 > len(data) or data[p:p + 20] != bytes(20):
                raise ValueError("NSD con parámetros/meshes/frames: fuera del subconjunto Fase 1")
            p += 20
            entities.append(tags)
        if len(data) - p != 192:
            raise ValueError("NSD con bloques variables: fuera del subconjunto Fase 1")
        return cls(cstring(data[8:40]), cstring(data[40:72]), entities, data[p:], data[:84])

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
        return bytes(header) + b"".join(encode_tags(tags) + bytes(20) for tags in self.entities) + self.environment


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
