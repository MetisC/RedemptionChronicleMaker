"""Engine-space Z-up math. No GUI or native runtime dependencies."""
import math
from dataclasses import dataclass
import numpy as np

def unit(v):
    v = np.asarray(v, dtype=float)
    return v / max(np.linalg.norm(v), 1e-12)

def rotation(yaw):
    a = math.radians(yaw)
    return np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])

def inside(trigger, position):
    p = np.asarray(position) - np.asarray(trigger['transform']['position'])
    if trigger['shape'] == 'sphere':
        return float(p @ p) <= trigger['radius'] ** 2
    p = rotation(-trigger['transform'].get('orientation', [0, 0, 0])[2]) @ p
    return bool(np.all(np.abs(p) <= np.asarray(trigger['size']) / 2))

def snap(value, step):
    return np.round(np.asarray(value) / step) * step if step > 0 else np.asarray(value)

@dataclass
class Hit:
    distance: float
    position: np.ndarray
    normal: np.ndarray
    triangle: int

class Raycaster:
    """Precomputed triangle bounds + vectorized intersection, not per-frame parsing."""
    def __init__(self, mesh):
        self.tri = mesh.triangles.astype(np.float64)
        self.a = self.tri[:, 0]
        self.e1 = self.tri[:, 1] - self.a
        self.e2 = self.tri[:, 2] - self.a
        self.normals = np.cross(self.e1, self.e2)
        lengths = np.linalg.norm(self.normals, axis=1)
        self.normals /= np.maximum(lengths, 1e-10)[:, None]
        self.low, self.high = self.tri.min(axis=1), self.tri.max(axis=1)

    def cast(self, origin, direction, floor_only=False, max_distance=100000):
        o, d = np.asarray(origin, float), unit(direction)
        inv = np.divide(1., d, out=np.full(3, np.inf), where=np.abs(d) > 1e-12)
        # Parallel axes use an explicit slab test; avoids 0*inf NaNs.
        lo = (self.low - o) * np.where(np.isfinite(inv), inv, 0)
        hi = (self.high - o) * np.where(np.isfinite(inv), inv, 0)
        mn, mx = np.minimum(lo, hi), np.maximum(lo, hi)
        for axis in np.where(np.abs(d) < 1e-12)[0]:
            valid = (o[axis] >= self.low[:, axis]) & (o[axis] <= self.high[:, axis])
            mn[:, axis] = np.where(valid, -np.inf, np.inf)
            mx[:, axis] = np.where(valid, np.inf, -np.inf)
        mask = (np.max(mn, axis=1) <= np.min(mx, axis=1)) & (np.min(mx, axis=1) >= 0)
        if floor_only:
            mask &= np.abs(self.normals[:, 2]) > 0.65
        ix = np.flatnonzero(mask)
        if not len(ix):
            return None
        h = np.cross(np.broadcast_to(d, self.e2[ix].shape), self.e2[ix])
        det = np.einsum('ij,ij->i', self.e1[ix], h)
        invdet = np.divide(1., det, out=np.zeros_like(det), where=np.abs(det) > 1e-9)
        s = o - self.a[ix]
        u = np.einsum('ij,ij->i', s, h) * invdet
        q = np.cross(s, self.e1[ix])
        v = q @ d * invdet
        t = np.einsum('ij,ij->i', self.e2[ix], q) * invdet
        valid = (np.abs(det) > 1e-9) & (u >= -1e-7) & (v >= -1e-7) & (u + v <= 1.0000001) & (t > 1e-5) & (t < max_distance)
        if not valid.any():
            return None
        k = int(np.argmin(np.where(valid, t, np.inf)))
        return Hit(float(t[k]), o + d * t[k], self.normals[ix[k]], int(ix[k]))

    def ground(self, position, above=250, below=2000):
        p = np.array(position, float) + [0, 0, above]
        return self.cast(p, [0, 0, -1], True, above + below)

def ray_box(origin, direction, low, high):
    tmin, tmax = -math.inf, math.inf
    for o, d, a, b in zip(origin, direction, low, high):
        if abs(d) < 1e-9:
            if o < a or o > b:
                return None
        else:
            x, y = (a - o) / d, (b - o) / d
            tmin, tmax = max(tmin, min(x, y)), min(tmax, max(x, y))
    return max(0., tmin) if tmax >= max(0., tmin) else None

def ray_sphere(origin, direction, radius):
    """Ray distance for a sphere centred at zero, including rays starting inside."""
    o, d = np.asarray(origin, float), unit(direction)
    c = float(o @ o) - radius * radius
    if c <= 0:
        return 0.
    b = float(o @ d)
    discriminant = b * b - c
    if discriminant < 0:
        return None
    t = -b - math.sqrt(discriminant)
    return t if t >= 0 else None
