"""NIL v27 sectors, derived from native reader 0x4a9170. Never writes NIL."""
from dataclasses import dataclass
import struct
import numpy as np

class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0
    def take(self, size):
        if size < 0 or self.pos + size > len(self.data):
            raise ValueError(f'Geometría truncada en {self.pos:#x} ({size} bytes)')
        result = self.data[self.pos:self.pos + size]
        self.pos += size
        return result
    def unpack(self, fmt):
        values = struct.unpack('<' + fmt, self.take(struct.calcsize('<' + fmt)))
        return values[0] if len(values) == 1 else values
    def count(self, fmt, maximum):
        n = self.unpack(fmt)
        if n > maximum:
            raise ValueError(f'Conteo fuera de rango en {self.pos:#x}: {n}')
        return n

@dataclass
class Mesh:
    vertices: np.ndarray  # expanded triangles: engine xyz (Z up), uv
    material_ids: np.ndarray
    materials: list[str]
    sectors: int
    source_end: int
    warnings: list[str]
    @property
    def triangles(self):
        return self.vertices[:, :3].reshape(-1, 3, 3)
    @property
    def bounds(self):
        return self.vertices[:, :3].min(axis=0), self.vertices[:, :3].max(axis=0)

def read_nil(data):
    r = Reader(data)
    if r.take(8) != b'NIL\x10\x1b\0\0\0':
        raise ValueError('Viewport admite NIL 0x10, versión 27')
    r.take(72)
    r.take(12)
    materials = [r.take(32).split(b'\0', 1)[0].decode('cp1252') for _ in range(r.count('I', 10000))]
    nsectors = r.count('I', 100000)
    vertices, material_ids, warnings = [], [], []
    for si in range(nsectors):
        r.take(16)
        r.take(r.count('B', 255) * 16)
        r.take(r.count('H', 65535) * 16)
        r.take(r.count('H', 65535) * 8)
        points = np.frombuffer(r.take(r.count('H', 16383) * 12), '<f4').reshape(-1, 3)
        corners = r.take(r.count('H', 16383) * 24)
        nsurfaces = r.count('I', 4095)
        groups = []
        for _ in range(r.count('H', 511)):
            ns, material, nlayers, flags, ncorners = r.unpack('HiBIH')
            if nlayers > 4:
                raise ValueError('NIL: demasiadas capas de material')
            r.take(nlayers * 6)
            if not -1 <= material < len(materials):
                raise ValueError(f'NIL: material fuera de índice en sector {si}')
            groups.append((ns, material, ncorners, flags))
        surfaces = [r.unpack('HBi') for _ in range(nsurfaces)]
        if sum(g[0] for g in groups) != nsurfaces:
            raise ValueError(f'NIL: grupos/superficies no coinciden, sector {si}')
        ci, surface_index = 0, 0
        for ns, material, ngcorners, flags in groups:
            before = ci
            for plane, count, lightmap in surfaces[surface_index:surface_index + ns]:
                if count < 3 or ci + count > len(corners) // 24:
                    raise ValueError(f'NIL: polígono inválido en sector {si}')
                polygon = []
                for k in range(count):
                    index = struct.unpack_from('<H', corners, (ci + k) * 24)[0]
                    if index >= len(points):
                        raise ValueError(f'NIL: índice inválido, sector {si}')
                    uv = struct.unpack_from('<2f', corners, (ci + k) * 24 + 8)
                    polygon.append((*points[index], *uv))
                for k in range(1, count - 1):
                    vertices.extend([polygon[0], polygon[k], polygon[k + 1]])
                    material_ids.append(material)
                ci += count
            if ci - before != ngcorners:
                raise ValueError(f'NIL: conteo de corners no coincide, sector {si}')
            surface_index += ns
        if ci * 24 != len(corners):
            raise ValueError('NIL: corners no consumidos')
        r.take(r.count('B', 255) * 96)
        r.take(r.count('H', 65535) * 72)
    array = np.asarray(vertices, dtype=np.float32).reshape(-1, 5)
    if not len(array) or not np.isfinite(array).all():
        raise ValueError('NIL: geometría vacía o no finita')
    return Mesh(array, np.asarray(material_ids, dtype=np.int32), materials, nsectors, r.pos, warnings)
