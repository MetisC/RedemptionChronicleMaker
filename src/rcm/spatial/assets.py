"""Read-only NOB resolution and content-addressed, regenerable authoring cache."""
from dataclasses import dataclass
from pathlib import PurePosixPath
import hashlib
import io
import json
import os
import struct
import zipfile
import numpy as np
from PIL import Image
from .geometry import Mesh, Reader, read_nil

CACHE_VERSION = 2

def normalize(path):
    path = path.replace('\\', '/')
    p = PurePosixPath(path)
    if p.is_absolute() or '..' in p.parts or ':' in path:
        raise ValueError('Ruta de recurso insegura')
    return str(p).casefold()

@dataclass
class Material:
    name: str
    rgba: bytes
    width: int
    height: int
    texture: str | None
    transparent: bool = False
    warning: str | None = None

@dataclass
class LevelData:
    name: str
    mesh: Mesh
    materials: list[Material]
    references: list[dict]
    models: dict[str, tuple[Mesh, list[Material]]]
    warnings: list[str]
    cache_hit: bool

class Assets:
    def __init__(self, backend):
        self.backend, self.ws = backend, backend.ws
        self.entries = {}
        for entry in backend.resources['entries']:
            if entry.get('archive'):
                self.entries.setdefault(normalize(entry['path']), []).append(entry)
        self.material_cache, self.model_cache = {}, {}

    def read(self, path, archive=None):
        for key,data in self.backend.project_payload.items():
            if normalize(key)==normalize(path) and archive in (None,'PROJECT'):return data
        entries = self.entries.get(normalize(path), [])
        if archive:
            entries = [e for e in entries if e['archive'] == archive]
        if len(entries) != 1:
            raise ValueError('Recurso ausente o ambiguo: ' + path)
        e = entries[0]
        if e.get('project_owned'):
            return self.backend.project_payload[e['path']]
        if e.get('imported_pack'):
            from ..wtd import read_entry
            return read_entry(self.ws,e)
        if not self.ws.game:
            raise ValueError('Selecciona una instalación para leer recursos originales')
        with zipfile.ZipFile(self.ws.game / e['archive']) as z:
            return z.read(e['path'])

    def material(self, name):
        key = normalize(name)
        if key in self.material_cache:
            return self.material_cache[key]
        warning, texture = None, None
        try:
            path = 'materials/' + name.replace('\\', '/')
            if not path.lower().endswith('.nam'):
                path += '.nam'
            direct = None
            if normalize(path) not in self.entries and '/' not in name.replace('\\', '/'):
                candidate = '3d/materials/' + name + '.tga'
                if normalize(candidate) in self.entries:
                    direct = candidate
                else:
                    matches = [k for k in self.entries if k.endswith('/' + name.casefold() + '.nam')]
                    if len(matches) == 1:
                        path = self.entries[matches[0]][0]['path']
            nam = ('texture ' + PurePosixPath(direct).name) if direct else self.read(path).decode('cp1252')
            props = {}
            for line in nam.splitlines():
                tokens = line.split('//', 1)[0].split('#', 1)[0].split()
                if tokens:
                    props[tokens[0].lower()] = tokens[1:]
            if not props.get('texture'):
                # Original multipass water: static first diffuse pass is useful
                # for authoring; scrolling/reflections deliberately omitted.
                for line in nam.splitlines():
                    tokens = line.split()
                    if len(tokens) >= 3 and tokens[:2] == ['pass', '0']:
                        props['texture'] = [tokens[2]]
                        break
            if not props.get('texture'):
                # Some original solid-color materials intentionally have no bitmap.
                raise ValueError('Material sin textura compatible: ' + name)
            texture = direct or str(PurePosixPath(path).parent / props['texture'][0])
            data = self.read(texture)
            digest = hashlib.sha256(data).hexdigest()
            cache = self.ws.output('cache/textures/' + digest + '.png')
            if cache.exists():
                try:
                    image = Image.open(cache).convert('RGBA')
                    image.load()
                except (OSError, ValueError):
                    image = None
            else:
                image = None
            if image is None:
                image = Image.open(io.BytesIO(data)).convert('RGBA')
                if image.width > 8192 or image.height > 8192:
                    raise ValueError('Textura excede el tamaño admitido')
                cache.parent.mkdir(parents=True, exist_ok=True)
                temporary = cache.with_suffix('.tmp.png')
                image.save(temporary)
                os.replace(temporary, cache)
            transparent = image.getextrema()[3][0] < 255 or any(k in props for k in ('alphablend', 'addblend', 'transparent', 'mask'))
            mat = Material(name, image.tobytes(), image.width, image.height, texture, transparent)
        except (ValueError, OSError, KeyError) as error:
            warning = f'{name}: {error}'
            mat = Material(name, bytes([220, 40, 185, 255, 40, 30, 45, 255, 40, 30, 45, 255, 220, 40, 185, 255]), 2, 2, texture, False, warning)
        self.material_cache[key] = mat
        return mat

    def model(self, name):
        key = normalize(name)
        if key not in self.model_cache:
            name = name if name.lower().endswith('.nod') else name + '.nod'
            data = self.read('3d/models/' + name)
            mesh = read_nod(data)
            self.model_cache[key] = (mesh, [self.material(m) for m in mesh.materials])
        return self.model_cache[key]

    def load(self, name, progress=lambda message: None, templates=()):
        progress('Leyendo level…')
        entry = self.backend.levels[name]['geometry'][0]
        data = self.read(entry['path'], entry['archive'])
        digest = hashlib.sha256(data).hexdigest()
        cache = self.ws.output(f'cache/geometry/{digest}-v{CACHE_VERSION}.npz')
        hit = False
        try:
            with np.load(cache, allow_pickle=False) as f:
                mesh = Mesh(f['vertices'], f['ids'], f['materials'].tolist(), int(f['sectors']), int(f['end']), [],f['triangle_sectors'])
                if (mesh.vertices.ndim != 2 or mesh.vertices.shape[1] != 5
                    or mesh.material_ids.ndim != 1 or mesh.material_ids.dtype.kind not in 'iu'
                    or len(mesh.vertices) != 3 * len(mesh.material_ids) or not len(mesh.vertices)
                    or not np.isfinite(mesh.vertices).all()
                    or np.any(mesh.material_ids < -1) or np.any(mesh.material_ids >= len(mesh.materials))
                    or not all(isinstance(m, str) for m in mesh.materials)
                    or not 0 <= mesh.source_end <= len(data) or not 0 < mesh.sectors <= 10000):
                    raise ValueError('Cache corrupto')
                if mesh.triangle_sectors.shape!=mesh.material_ids.shape or mesh.triangle_sectors.dtype.kind not in 'iu' or np.any(mesh.triangle_sectors<0) or np.any(mesh.triangle_sectors>=mesh.sectors):raise ValueError('Cache de sectores corrupto')
                hit = True
        except (OSError, ValueError, KeyError, IndexError, TypeError, EOFError, zipfile.BadZipFile):
            progress('Reconstruyendo geometría…')
            mesh = read_nil(data)
            cache.parent.mkdir(parents=True, exist_ok=True)
            temp = cache.with_suffix('.tmp.npz')
            np.savez_compressed(temp, vertices=mesh.vertices, ids=mesh.material_ids, materials=np.array(mesh.materials), sectors=mesh.sectors, end=mesh.source_end,triangle_sectors=mesh.triangle_sectors)
            os.replace(temp, cache)
        materials = []
        for i, m in enumerate(mesh.materials):
            progress(f'Cargando texturas {i+1}/{len(mesh.materials)}…')
            materials.append(self.material(m))
        references = []
        # Hints remain explicitly labelled: NOT a complete NSD decode.
        scenes = self.backend.levels[name].get('scenes', [])
        for scene in scenes[:1]:
            hints = self.backend.hints.get(scene.casefold(), {})
            for entity in hints.get('entities', []):
                if entity.get('position'):
                    references.append(dict(entity, origin=scene, read_only=True, confidence='tag-pattern'))
        from ..original_objects import catalogue
        original_props=catalogue(self.backend,name)
        # Story layouts are replaced by RCM. Prefer the actually associated
        # static objects for runtime authoring; retain old hints only if absent.
        if original_props:references=[r for r in original_props if r.get('position') is not None]
        warnings = [m.warning for m in materials if m.warning]
        models = {}
        # Static props belong to the immutable base scenery, not story NPCs.
        # Inline NSD brushes have no NOD template model (e.g. Tenebrae's exit).
        for ref in references:
            try:
                if 'mesh_offset' in ref:
                    from .scene_mesh import read_brush
                    source=self.backend.hints[ref['origin'].casefold()]['source']
                    brush=read_brush(self.read(source['path'],source['archive']),ref['mesh_offset'])
                    ref['preview_model']='@original/'+str(ref['offset'])
                    models[ref['preview_model']]=(brush,[self.material(m) for m in brush.materials])
                elif ref.get('model'):models[ref['template']]=self.model(ref['model'])
            except (ValueError,OSError,KeyError) as error:warnings.append(str(error))
        for row in self.backend.resources['templates']:
            if row['id'] in templates and row.get('model'):
                try:
                    models[row['id']] = self.model(row['model'])
                    warnings.extend(m.warning for m in models[row['id']][1] if m.warning)
                except ValueError as error:
                    warnings.append(str(error))
        progress('Preparando escena…')
        report = dict(level=name, source=entry, sha256=digest, sectors=mesh.sectors, triangles=len(mesh.material_ids), materials=len(materials), textures_loaded=sum(m.warning is None for m in materials), warnings=warnings, cache_hit=hit, reference_confidence='tag-pattern; not full NSD parse')
        self.ws.write('cache/levels/' + name + '.json', json.dumps(report, ensure_ascii=False, indent=2))
        return LevelData(name, mesh, materials, references, models, warnings, hit)

def read_nod(data):
    """NOD v7 static bind mesh; bones preserved only as opaque transforms.

    Native 0x4c35d0/0x4c3ba0: bounds24, joints66, shape names32,
    vertices40, optional LOD links2, triangle indices6, material groups28.
    No animation or skeleton edits; vertex positions already in bind space.
    """
    r = Reader(data)
    if r.unpack('I') != 7:
        raise ValueError('Sólo NOD versión 7 en viewport')
    materials = [r.take(32).split(b'\0', 1)[0].decode('cp1252') for _ in range(r.count('I', 1000))]
    bones, names, nverts, ntris, ngroups, flags = r.unpack('HHIIHI')
    if max(nverts, ntris) > 2000000:
        raise ValueError('Modelo demasiado grande')
    r.take(24 + bones * 66 + names * 32)
    raw = r.take(nverts * 40)
    points = np.frombuffer(raw, dtype='<f4').reshape(-1, 10)
    if flags & 1:
        r.take(nverts * 2)
    triangles = np.frombuffer(r.take(ntris * 6), '<u2').reshape(-1, 3)
    vertices, ids = [], []
    vi = ti = 0
    for _ in range(ngroups):
        group = r.take(28)
        material = struct.unpack_from('<i', group)[0]
        nt, nv = struct.unpack_from('<HH', group, 16)
        if not -1 <= material < len(materials) or vi + nv > nverts or ti + nt > ntris:
            raise ValueError('Grupo de modelo fuera de rango')
        indices = triangles[ti:ti + nt].astype(np.int64) + vi
        if nt and int(indices.max()) >= vi + nv:
            raise ValueError('Índice de modelo fuera de su grupo')
        vertices.extend(points[indices.reshape(-1)][:, [0, 1, 2, 6, 7]])
        ids.extend([material] * nt)
        vi += nv
        ti += nt
    if ti != ntris or vi != nverts or r.pos != len(data):
        raise ValueError('Modelo contiene bloques no interpretados')
    array = np.array(vertices, dtype=np.float32).reshape(-1, 5)
    if not len(array) or not np.isfinite(array).all():
        raise ValueError('Modelo no finito o vacío')
    return Mesh(array, np.array(ids, dtype=np.int32), materials, 0, r.pos, [])
