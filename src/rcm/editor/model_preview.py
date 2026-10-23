"""Read-only, asynchronous previews of the actual NOD mesh and its textures.

Software rasterization also works without an OpenGL context (remote desktops).
No actor is instantiated and no project data is changed by browsing models.
"""
import math
import numpy as np
from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from ..spatial.assets import Assets
from .i18n import tr

DEFAULT_YAW = 210.


def render_model(mesh, materials, yaw=DEFAULT_YAW, size=320):
    """Orthographic turntable, Z up; sample original UVs with a depth buffer."""
    vertices = np.asarray(mesh.vertices, dtype=float)
    if not len(vertices) or not np.isfinite(vertices).all():
        raise ValueError('Empty or invalid model')
    angle = math.radians(yaw)
    right = np.array([math.cos(angle), math.sin(angle), 0.])
    forward = np.array([-math.sin(angle), math.cos(angle), -.22])
    forward /= np.linalg.norm(forward)
    up = np.cross(right, forward)
    points = vertices[:, :3] @ np.array([right, up, forward]).T
    low, high = points.min(axis=0), points.max(axis=0)
    scale = (size - 28) / max(float(np.max(high[:2] - low[:2])), 1.)
    points[:, :2] = (points[:, :2] - (low[:2] + high[:2]) / 2) * scale
    points[:, 0] += size / 2
    points[:, 1] = size / 2 - points[:, 1]
    pixels = np.full((size, size, 4), [35, 41, 50, 255], dtype=np.uint8)
    depth = np.full((size, size), np.inf)
    textures = [np.frombuffer(m.rgba, dtype=np.uint8).reshape(m.height, m.width, 4) for m in materials]
    for index, tri in enumerate(points.reshape(-1, 3, 3)):
        minimum = np.maximum(0, np.floor(tri[:, :2].min(axis=0)).astype(int))
        maximum = np.minimum(size - 1, np.ceil(tri[:, :2].max(axis=0)).astype(int))
        if np.any(minimum > maximum):
            continue
        a, b, c = tri
        divisor = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
        if abs(divisor) < 1e-8:
            continue
        x, y = np.meshgrid(np.arange(minimum[0], maximum[0]+1)+.5,
                           np.arange(minimum[1], maximum[1]+1)+.5)
        w0 = ((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/divisor
        w1 = ((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/divisor
        w2 = 1-w0-w1
        z = w0*a[2]+w1*b[2]+w2*c[2]
        area = np.s_[minimum[1]:maximum[1]+1, minimum[0]:maximum[0]+1]
        mask = (w0 >= 0) & (w1 >= 0) & (w2 >= 0) & (z < depth[area])
        if not np.any(mask):
            continue
        mid = int(mesh.material_ids[index])
        if 0 <= mid < len(textures):
            texture = textures[mid]
            uv = vertices[index*3:index*3+3, 3:5]
            u = w0*uv[0, 0]+w1*uv[1, 0]+w2*uv[2, 0]
            v = w0*uv[0, 1]+w1*uv[1, 1]+w2*uv[2, 1]
            # Engine UVs start at the bottom; decoded PIL images start at the top.
            color = texture[texture.shape[0]-1-np.floor(v*texture.shape[0]).astype(int) % texture.shape[0],
                            np.floor(u*texture.shape[1]).astype(int) % texture.shape[1]]
            mask &= color[:, :, 3] > 127
        else:
            color = np.full((*mask.shape, 4), [180, 190, 205, 255], dtype=np.uint8)
        pixels[area][mask] = color[mask]
        depth[area][mask] = z[mask]
    return QImage(pixels.data, size, size, size*4, QImage.Format.Format_RGBA8888).copy()


class PreviewSignals(QObject):
    ready = Signal(int, str, object, str)


class PreviewJob(QRunnable):
    def __init__(self, backend, token, model, yaw):
        super().__init__()
        self.backend, self.token, self.model, self.yaw = backend, token, model, yaw
        self.signals = PreviewSignals()

    def run(self):
        try:
            mesh, materials = Assets(self.backend).model(self.model)
            image, error = render_model(mesh, materials, self.yaw), ''
        except Exception as exc:
            image, error = None, str(exc)
        self.signals.ready.emit(self.token, self.model, image, error)


class PreviewImage(QLabel):
    """Fit the whole model even when resource details reduce the available height."""
    def __init__(self, text):
        super().__init__(text)
        self.frame = None
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)

    def clear(self):
        self.frame = None
        super().clear()

    def setText(self, text):
        self.frame = None
        super().setText(text)

    def set_frame(self, image):
        self.frame = image
        self.fit()

    def fit(self):
        if self.frame is not None:
            self.setPixmap(QPixmap.fromImage(self.frame).scaled(self.contentsRect().size(),
                           Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit()


class ModelPreview(QWidget):
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend, self.model, self.token, self.yaw = backend, '', 0, DEFAULT_YAW
        self.cache = {}
        self.running = False
        self.source_resources = None
        self.source_payload = None
        self.source_game = None
        self.setObjectName('resource_model_preview')
        self.setMinimumWidth(230)
        layout = QVBoxLayout(self)
        self.image = PreviewImage(tr('Selecciona un actor u objeto para ver su modelo.'))
        self.image.setObjectName('resource_preview_image')
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image.setWordWrap(True)
        self.image.setMinimumSize(220, 220)
        layout.addWidget(self.image, 1)
        self.caption = QLabel(); self.caption.setWordWrap(True); layout.addWidget(self.caption)
        row = QHBoxLayout()
        for label, delta in [('↶', -45), ('↷', 45)]:
            button = QPushButton(label); button.setToolTip(tr('Girar previsualización'))
            button.clicked.connect(lambda checked=False, delta=delta: self.turn(delta)); row.addWidget(button)
        layout.addLayout(row)
        self.timer = QTimer(self); self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.load)

    def select(self, kind, ident):
        model = ''
        if kind in {'actors', 'items'}:
            matches = [t for t in self.backend.resources['templates'] if t['id'] == ident]
            if len(matches) == 1:
                model = matches[0].get('model') or ''
        elif kind == '.nod' and ident:
            model = ident
        payload = getattr(self.backend, 'project_payload', None)
        game = getattr(getattr(self.backend, 'ws', None), 'game', None)
        source_changed = (self.source_resources is not self.backend.resources or
                          self.source_payload is not payload or self.source_game != game)
        if model == self.model and not source_changed:
            return
        if source_changed:
            self.cache.clear()
        self.source_resources, self.source_payload, self.source_game = self.backend.resources, payload, game
        self.token += 1; self.timer.stop(); self.model = model; self.yaw = DEFAULT_YAW
        self.caption.setText(model+'\n'+tr('Modelo estático · no reproduce animaciones.') if model else '')
        self.image.clear()
        self.image.setToolTip('')
        self.image.setText(tr('Cargando modelo…') if model else tr('Sin modelo para previsualizar.'))
        if model:
            self.timer.start(120)

    def turn(self, delta):
        if self.model:
            self.yaw = (self.yaw + delta) % 360
            self.token += 1; self.timer.start(80)

    def load(self):
        if not self.model or self.running:
            return
        key = (self.model, self.yaw)
        if key in self.cache:
            self.show_result(self.token, self.model, self.cache[key], '')
            return
        job = PreviewJob(self.backend, self.token, self.model, self.yaw)
        self.running = True
        job.signals.ready.connect(self.completed)
        QThreadPool.globalInstance().start(job)

    def completed(self, token, model, image, error):
        self.running = False
        self.show_result(token, model, image, error)
        if token != self.token and self.model and self.isVisible():
            self.timer.start(80)

    def show_result(self, token, model, image, error):
        if token != self.token or model != self.model:
            return
        if error:
            self.image.setText(tr('No se pudo previsualizar el modelo.'))
            self.image.setToolTip(error)
            return
        if len(self.cache) >= 16:
            self.cache.pop(next(iter(self.cache)))
        self.cache[(model, self.yaw)] = image
        self.image.setToolTip(tr('Vista del modelo original; las animaciones se ejecutan en el juego.'))
        self.image.set_frame(image)

    def hideEvent(self, event):
        self.timer.stop(); self.token += 1
        super().hideEvent(event)

    def showEvent(self, event):
        if self.model:
            self.timer.start(120)
        super().showEvent(event)
