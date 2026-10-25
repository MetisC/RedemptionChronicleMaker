"""Parametric decorative brushes on native NSD tracker_thing entities.

Each authored record becomes a real brush entity in the generated NSD, the
same body layout original doors and props carry (NSD v8 brush reader
0x4c3e50). The mode selects the stock tracker_thing variant that owns the
native flag contract; RCM never rewrites those flags in game code.

decor       tracker_thing_null      visible, no collision claim
solid       tracker_thing_nohilite  visible, collide=3 BBOX (experimental)
barrier     tracker_thing_blocker   invisible, collide + VISBLOCK/CAMERABLOCK/BLOCKSELECT (experimental)
interactive tracker_thing           visible, collide, click via CaptureThing

Vertices are local to the entity transform: X/Y centred, Z spans 0..height
so a ground-snapped origin leaves the piece resting on the floor. Only the
six-plane box subset is written; Scene.encode already enforces the bounded
collision tail. NIL geometry is never modified.
"""
import math
import re

from .model import mapping, sequence

MATERIAL_NAME = re.compile(r'^[A-Za-z0-9_./\\ -]{1,31}$')

# mode -> original NOT template carrying the native flag/collision contract.
MODES = {
    'decor': 'tracker_thing_null',
    'solid': 'tracker_thing_nohilite',
    'barrier': 'tracker_thing_blocker',
    'interactive': 'tracker_thing',
}

# Editor placement presets (label, mode, size). Sizes are full extents.
PRESETS = (
    ('Caja', 'decor', [64, 64, 64]),
    ('Panel', 'decor', [96, 8, 96]),
    ('Pared', 'solid', [256, 16, 256]),
    ('Columna', 'decor', [32, 32, 192]),
    ('Plataforma', 'solid', [192, 192, 24]),
    ('Barrera invisible', 'barrier', [128, 16, 128]),
)


def validate_geometry(value):
    """Authoring-level checks; raises ValueError with a readable message."""
    geometry = mapping(value, {'shape', 'size', 'material', 'uv_scale', 'mode'},
                       {'shape', 'size', 'material'}, 'geometry')
    if geometry['shape'] != 'box':
        raise ValueError('Escenografía: forma no soportada (sólo box)')
    size = sequence(geometry['size'], 'geometry.size')
    if len(size) != 3 or any(type(v) not in (int, float) or not math.isfinite(v) or not 1 <= v <= 50000 for v in size):
        raise ValueError('Escenografía: size requiere 3 dimensiones finitas entre 1 y 50000')
    material = geometry['material']
    if not isinstance(material, str) or not MATERIAL_NAME.fullmatch(material):
        raise ValueError('Escenografía: material nativo inválido (1..31 caracteres, ruta NAM)')
    if 'uv_scale' in geometry:
        scale = geometry['uv_scale']
        if type(scale) not in (int, float) or not math.isfinite(scale) or not 4 <= scale <= 4096:
            raise ValueError('Escenografía: uv_scale requiere un valor entre 4 y 4096')
    else:
        geometry['uv_scale'] = 64
    mode = geometry.get('mode', 'decor')
    if mode not in MODES:
        raise ValueError('Escenografía: modo inválido')
    geometry['mode'] = mode
    return geometry


def spec(geometry, sector):
    """Brush dict in the click_interactions value shape (local vertices)."""
    g = validate_geometry(dict(geometry))
    w, d, h = g['size'][0] / 2, g['size'][1] / 2, g['size'][2]
    us = float(g['uv_scale'])

    # Quad corners are ordered so triangles (0,1,2),(0,2,3) keep outward normals.
    # uv = the two in-plane world coords / uv_scale, matching original
    # world-scale brush UVs (research/scenography: door example ~1 repeat/64u).
    faces = [
        ([(-w, -d, h), (w, -d, h), (w, d, h), (-w, d, h)], (0, 1)),   # top    +z
        ([(-w, -d, 0), (-w, d, 0), (w, d, 0), (w, -d, 0)], (0, 1)),   # bottom -z
        ([(w, -d, 0), (w, d, 0), (w, d, h), (w, -d, h)], (1, 2)),     # +x
        ([(-w, d, 0), (-w, -d, 0), (-w, -d, h), (-w, d, h)], (1, 2)), # -x
        ([(w, d, 0), (-w, d, 0), (-w, d, h), (w, d, h)], (0, 2)),     # +y
        ([(-w, -d, 0), (w, -d, 0), (w, -d, h), (-w, -d, h)], (0, 2)), # -y
    ]
    vertices = []
    for corners, axes in faces:
        quad = [[p[0], p[1], p[2], p[axes[0]] / us, p[axes[1]] / us] for p in corners]
        for tri in ((0, 1, 2), (0, 2, 3)):
            vertices.extend(quad[i] for i in tri)
    return dict(materials=[g['material']], vertices=vertices,
                material_ids=[0] * 12, sector=sector)
