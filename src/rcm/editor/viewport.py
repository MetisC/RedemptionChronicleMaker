from .i18n import tr
"""GPU authoring viewport. Qt owns the GL context; data loading is off-thread."""
import math
import time
import traceback
import numpy as np
from PySide6.QtCore import Qt, QTimer, QThread, QObject, Signal, QPointF
from PySide6.QtGui import (QMatrix4x4, QVector3D, QVector4D, QImage, QPainter, QColor, QPen, QPolygonF, QSurfaceFormat, QCursor)
from PySide6.QtOpenGL import QOpenGLBuffer, QOpenGLShader, QOpenGLShaderProgram, QOpenGLTexture
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox, QDoubleSpinBox, QApplication, QMenu)
from ..spatial.assets import Assets
from ..spatial.math3d import Raycaster, rotation, unit, ray_box, ray_sphere, snap
from ..spatial.relations import affected

GL_FLOAT, GL_TRIANGLES, GL_LINES = 0x1406, 4, 1
GL_DEPTH_TEST, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA = 0xB71, 0xBE2, 0x302, 0x303

class LoadWorker(QObject):
    progress = Signal(str)
    ready = Signal(object, object)
    failed = Signal(str)
    finished = Signal()
    def __init__(self, backend, name, templates, assets=None):
        super().__init__()
        self.backend, self.name, self.templates = backend, name, templates
        self.assets = assets
    def run(self):
        try:
            assets = self.assets or Assets(self.backend)
            level = assets.load(self.name, self.progress.emit, self.templates)
            self.ready.emit(level, assets)
        except Exception:
            self.failed.emit(traceback.format_exc())
        finally:
            self.finished.emit()

class GpuMesh:
    def __init__(self, mesh, materials):
        # A single static VBO sorted by material. Upload once, draw ranges.
        order = np.argsort(mesh.material_ids, kind='stable')
        triangles = mesh.vertices.reshape(-1, 3, 5)[order]
        normals = np.cross(triangles[:, 1, :3] - triangles[:, 0, :3], triangles[:, 2, :3] - triangles[:, 0, :3])
        normals /= np.maximum(np.linalg.norm(normals, axis=1), 1e-10)[:, None]
        array = np.concatenate([triangles, np.repeat(normals[:, None], 3, axis=1)], axis=2).astype(np.float32).reshape(-1, 8)
        self.buffer = QOpenGLBuffer(QOpenGLBuffer.Type.VertexBuffer)
        self.buffer.create()
        self.buffer.bind()
        raw = array.tobytes()
        self.buffer.allocate(raw, len(raw))
        self.buffer.release()
        self.textures, self.ranges = [], []
        ids = mesh.material_ids[order]
        for mid in np.unique(ids):
            indices = np.flatnonzero(ids == mid)
            mat = materials[int(mid)] if 0 <= mid < len(materials) else None
            if mat:
                image = QImage(mat.rgba, mat.width, mat.height, mat.width * 4, QImage.Format.Format_RGBA8888).copy()
            else:
                image = QImage(2, 2, QImage.Format.Format_RGBA8888)
                image.fill(QColor('#be35a0'))
            # PIL canonical top-left image; flipped for engine UVs/OpenGL.
            texture = QOpenGLTexture(image.mirrored(False, True))
            texture.setWrapMode(QOpenGLTexture.WrapMode.Repeat)
            texture.setMinificationFilter(QOpenGLTexture.Filter.LinearMipMapLinear)
            texture.setMagnificationFilter(QOpenGLTexture.Filter.Linear)
            self.textures.append(texture)
            center = triangles[indices, :, :3].mean(axis=(0, 1))
            self.ranges.append((int(indices[0]) * 3, len(indices) * 3, texture, bool(mat and mat.transparent), center))
    def destroy(self):
        for t in self.textures:
            t.destroy()
        self.buffer.destroy()

class ViewportHelpers(QWidget):
    """Composite authoring markers above GL without inheriting its render state."""
    def __init__(self, viewport):
        super().__init__(viewport)
        self.viewport = viewport
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAutoFillBackground(False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.viewport.paint_helpers(painter)
        painter.end()

class Viewport(QOpenGLWidget):
    selected = Signal(tuple)
    transformed = Signal(tuple, object)
    placed = Signal(object)
    message = Signal(str)
    gesture_started = Signal()
    gesture_finished = Signal()
    operation_cancelled = Signal()
    mode_requested = Signal(str)
    menu_requested = Signal(object)
    def __init__(self, parent=None):
        super().__init__(parent)
        fmt = QSurfaceFormat()
        fmt.setVersion(2, 1)
        fmt.setDepthBufferSize(24)
        fmt.setSamples(4)
        self.setFormat(fmt)
        self.setObjectName('spatial_viewport')
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.level = None
        self.original_rays={}
        self.data = None
        self.selection = ()
        self.context_surface = None
        self.hidden = {('original',)}
        self.show_relations = True
        self.paths = []
        self.mode = 'move'
        self.grid = 0.
        self.angle_step = 0.
        self.snap_surface = True
        self.walk = False
        self.placing = None
        self.pos = np.array([1000., 800., 260.])
        self.yaw, self.pitch, self.speed = -90., -12., 350.
        self.keys = set()
        self.drag = None
        self.looking = False
        self.orbiting = False
        self.last_mouse = None
        self.warp_target = None
        self.nav_buttons = Qt.MouseButton.NoButton
        self.right_origin = None
        self.right_dragged = False
        self.left_pending = None
        self.left_origin = None
        self.orbit_center = None
        self.fov = 60.
        self.gpu = None
        self.model_gpu = {}
        self.upload = False
        self.error = ''
        self.program = None
        self.frames = []
        self.frame_count = 0
        self.frame_times = []
        self.tick_time = time.perf_counter()
        self.helpers = ViewportHelpers(self)
        self.helpers.setGeometry(self.rect())
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

    def initializeGL(self):
        try:
            self.gl = self.context().functions()
            self.gl.initializeOpenGLFunctions()
            self.program = QOpenGLShaderProgram(self)
            vertex = '''#version 120
                attribute vec3 position; attribute vec2 texcoord; attribute vec3 normal;
                uniform mat4 mvp; uniform mat4 model;
                varying vec2 uv; varying float light;
                void main(){ gl_Position=mvp*vec4(position,1.0); uv=texcoord;
                  vec3 n=normalize((model*vec4(normal,0.0)).xyz);
                  light=0.60+0.40*abs(dot(n,normalize(vec3(0.35,0.55,1.0)))); }
            '''
            fragment = '''#version 120
                uniform sampler2D image; uniform vec4 tint;
                varying vec2 uv; varying float light;
                void main(){ vec4 c=texture2D(image,uv); if(c.a<0.30) discard;
                  gl_FragColor=vec4(c.rgb*light*tint.rgb,c.a*tint.a); }
            '''
            if not self.program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Vertex, vertex) or not self.program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Fragment, fragment) or not self.program.link():
                raise RuntimeError(self.program.log())
            self.context().aboutToBeDestroyed.connect(self.cleanup)
            self.upload = self.level is not None
        except Exception as e:
            self.error = str(e)
            self.message.emit(tr('No se pudo iniciar OpenGL: ') + self.error)

    def cleanup(self):
        self.makeCurrent()
        if self.gpu:
            self.gpu.destroy()
            self.gpu = None
        for gpu in self.model_gpu.values():
            gpu.destroy()
        self.model_gpu.clear()
        self.doneCurrent()

    def set_level(self, level):
        changed = self.level is None or self.level.name != level.name
        self.level = level
        self.original_rays={}
        if changed:
            self.raycaster = Raycaster(level.mesh)
            self.upload = True
        self.error = ''
        self.update()
        if changed:
            self.focus_selection()

    def sync(self, data, path):
        self.data, self.selection = data, tuple(path)
        if self.level:
            import hashlib,json
            clicks=[e for e in data.get('objects',[]) if 'interaction' in e]
            signature=(id(self.level),tuple((e['id'],hashlib.sha256(json.dumps(e['interaction'],sort_keys=True).encode()).hexdigest()) for e in clicks))
            if signature!=getattr(self,'click_signature',None):
                self.click_signature=signature
                for key in list(self.level.models):
                    if key.startswith('@click/'):del self.level.models[key]
                from ..click_interactions import validate
                from ..spatial.geometry import Mesh
                for e in clicks:
                    try:
                        value=validate(e['interaction']);mesh=Mesh(np.asarray(value['vertices'],dtype=np.float32),np.asarray(value['material_ids'],dtype=np.int32),value['materials'],0,0,[])
                        parent=self.parent();assets=getattr(parent,'assets',None)
                        if assets:materials=[assets.material(m) for m in mesh.materials]
                        else:
                            from ..spatial.assets import Material
                            materials=[Material(m,bytes([130,170,200,255]),1,1,None) for m in mesh.materials]
                        self.level.models[self.model_key(e)]=(mesh,materials)
                    except (ValueError,TypeError,KeyError):pass # Semantic drafts remain inspectable; validation blocks build.
                self.original_rays={};self.upload=True
        self.update()

    def entities(self):
        if not self.data:
            return []
        out = []
        for kind in ('actors', 'objects', 'triggers', 'entries', 'waypoints'):
            if (kind,) in self.hidden:
                continue
            for i, e in enumerate(self.data.get(kind, [])):
                path = (kind, i)
                if path not in self.hidden:
                    out.append((path, e, False))
        if self.level and ('original',) not in self.hidden:
            for i, e in enumerate(self.level.references):
                if ('original', i) not in self.hidden:
                    out.append((('original', i), e, True))
        elif self.level and self.selection[:1]==('original',) and len(self.selection)>1 and self.selection[1]<len(self.level.references):
            out.append((self.selection[:2],self.level.references[self.selection[1]],True))
        return out

    @staticmethod
    def model_key(e):return '@click/'+e['id'] if 'interaction' in e else e.get('preview_model',e.get('template'))

    @staticmethod
    def object_rotation(ori):
        pitch,roll,yaw=np.radians(ori);c,s=math.cos,math.sin
        return rotation(math.degrees(yaw))@np.array([[1,0,0],[0,c(pitch),-s(pitch)],[0,s(pitch),c(pitch)]])@np.array([[c(roll),0,s(roll)],[0,1,0],[-s(roll),0,c(roll)]])

    def pick_at(self,x,y):
        if not self.level:return None
        o,d=self.screen_ray(x,y);nearest=self.raycaster.cast(o,d);distance=nearest.distance+5 if nearest else math.inf;chosen=None
        candidates=[row for row in self.entities() if not row[2]]
        if ('geometry',) not in self.hidden:
            candidates += [(('original',i),e,True) for i,e in enumerate(self.level.references) if ('original',i) not in self.hidden and (self.model_key(e) in self.level.models or ('original',) not in self.hidden)]
        for path,e,ro in candidates:
            pos=self.position(path,e);low,high=self.entity_bounds(path,e);ori=e.get('orientation',[0,0,0]) if ro else e['transform'].get('orientation',[0,0,0]);inv=self.object_rotation(ori).T;origin=inv@(o-pos);direction=inv@d
            if (ro or 'interaction' in e) and self.model_key(e) in self.level.models:
                key=self.model_key(e)
                if key not in self.original_rays:self.original_rays[key]=Raycaster(self.level.models[key][0])
                hit=self.original_rays[key].cast(origin,direction,max_distance=min(distance,nearest.distance+.05) if nearest else distance);t=hit.distance if hit else None
            else:t=ray_sphere(o-pos,d,e['radius']) if path[0]=='triggers' and e['shape']=='sphere' else ray_box(origin,direction,low,high)
            if t is not None and t<distance:distance=t;chosen=path
        return chosen

    def position(self, path, e):
        if path[0] == 'original':
            return np.array(e['position'], float)
        if e['transform'].get('placement', 'absolute') != 'near_player':
            # An editable semantic draft may still lack its absolute position.
            # Validation blocks its build; showing a marker must not crash Qt.
            return np.array(e['transform'].get('position', [0, 0, 0]), float)
        # Runtime-dependent entity remains symbolic: preview is never serialized.
        anchor = self.level.references[0]['position'] if self.level and self.level.references else [0, 0, 0]
        hit = self.raycaster.ground(anchor) if self.level else None
        return (hit.position if hit else np.array(anchor)) + [70 * path[1], 0, 0]

    def entity_bounds(self, path, e):
        if path[0] == 'triggers':
            extent = np.array(e.get('size', [2 * e.get('radius', 60)] * 3)) / 2
            return -extent, extent
        if self.level and self.model_key(e) in self.level.models:
            return self.level.models[self.model_key(e)][0].bounds
        return np.array([-16., -16., 0.]), np.array([16., 16., 110. if path[0] == 'actors' else 32.])

    def matrices(self):
        projection = QMatrix4x4()
        projection.perspective(self.fov, max(1, self.width()) / max(1, self.height()), 2., 60000.)
        view = QMatrix4x4()
        forward = self.forward()
        y = math.radians(self.yaw)
        right = np.array([math.sin(y), -math.cos(y), 0.])
        up = np.cross(right, forward)
        # lookAt(pos, pos + unit_forward) subtracts float32 world coordinates.
        # Near a vertical angle the tiny horizontal component was quantized,
        # causing visible jumps. Build the orthonormal basis in float64 first.
        for row, axis in enumerate((right, up, -forward)):
            view.setRow(row, QVector4D(*axis, -float(axis @ self.pos)))
        return projection * view

    def forward(self):
        y, p = math.radians(self.yaw), math.radians(self.pitch)
        return np.array([math.cos(y) * math.cos(p), math.sin(y) * math.cos(p), math.sin(p)])

    def project(self, position):
        v = self.matrices().map(QVector4D(*position, 1.))
        if v.w() <= 0 or v.z() / v.w() > 1:
            return None
        return QPointF((v.x() / v.w() + 1) * self.width() / 2, (1 - v.y() / v.w()) * self.height() / 2)

    def screen_ray(self, x, y):
        inv, okay = self.matrices().inverted()
        def point(z):
            q = inv.map(QVector4D(2 * x / self.width() - 1, 1 - 2 * y / self.height(), z, 1))
            return np.array([q.x(), q.y(), q.z()]) / q.w()
        return self.pos.copy(), unit(point(1) - point(-1))

    def draw_mesh(self, gpu, model, tint=QVector4D(1, 1, 1, 1)):
        p = self.program
        p.bind()
        p.setUniformValue('mvp', self.matrices() * model)
        p.setUniformValue('model', model)
        p.setUniformValue('tint', tint)
        p.setUniformValue('image', 0)
        gpu.buffer.bind()
        for name, offset, size in [('position', 0, 3), ('texcoord', 12, 2), ('normal', 20, 3)]:
            p.enableAttributeArray(name)
            p.setAttributeBuffer(name, GL_FLOAT, offset, size, 32)
        opaque = [r for r in gpu.ranges if not r[3]]
        transparent = [r for r in gpu.ranges if r[3]]
        def distance(r):
            center = model.map(QVector3D(*r[4]))
            return np.linalg.norm(np.array([center.x(), center.y(), center.z()]) - self.pos)
        transparent.sort(key=distance, reverse=True)
        for start, count, tex, alpha, _ in opaque + transparent:
            if alpha:
                self.gl.glEnable(GL_BLEND)
                self.gl.glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                self.gl.glDepthMask(False)
            tex.bind(0)
            self.gl.glDrawArrays(GL_TRIANGLES, start, count)
            tex.release()
        self.gl.glDepthMask(True)
        self.gl.glDisable(GL_BLEND)
        for name in ('position', 'texcoord', 'normal'):
            p.disableAttributeArray(name)
        gpu.buffer.release()
        p.release()

    def paintGL(self):
        started = time.perf_counter()
        if self.program and self.level and not self.error:
            try:
                if self.upload:
                    if self.gpu:
                        self.gpu.destroy()
                    for gpu in self.model_gpu.values():
                        gpu.destroy()
                    self.gpu = GpuMesh(self.level.mesh, self.level.materials)
                    self.model_gpu = {name: GpuMesh(*model) for name, model in self.level.models.items()}
                    self.upload = False
                else:
                    for name,model in self.level.models.items():
                        if name not in self.model_gpu:
                            self.model_gpu[name] = GpuMesh(*model)
                self.gl.glClearColor(0.14, 0.18, 0.23, 1.)
                self.gl.glClear(0x4000 | 0x0100)
                self.gl.glEnable(GL_DEPTH_TEST)
                self.gl.glDisable(GL_BLEND)
                if ('geometry',) not in self.hidden:
                    self.draw_mesh(self.gpu, QMatrix4x4())
                linked = affected(self.data, self.selection[:2]) if self.show_relations and self.data else set()
                rendered=[row for row in self.entities() if not row[2]]
                if ('geometry',) not in self.hidden:rendered += [(('original',i),e,True) for i,e in enumerate(self.level.references) if ('original',i) not in self.hidden]
                for path, e, ro in rendered:
                    if path[0] != 'triggers' and self.model_key(e) in self.model_gpu:
                        m = QMatrix4x4()
                        m.translate(QVector3D(*self.position(path, e)))
                        ori = e.get('orientation',[0,0,0]) if ro else e['transform'].get('orientation', [0, 0, 0])
                        m.rotate(ori[2], 0, 0, 1)
                        m.rotate(ori[0], 1, 0, 0)
                        m.rotate(ori[1], 0, 1, 0)
                        tint = QVector4D(1, 1., 0.65, 1) if path == self.selection[:2] else QVector4D(0.65, 1., 0.85, 1) if path in linked else QVector4D(1, 1, 1, 1)
                        self.draw_mesh(self.model_gpu[self.model_key(e)], m, tint)
            except Exception:
                self.error = traceback.format_exc()
                self.message.emit(self.error)
        self.frame_count += 1
        self.frame_times.append(time.perf_counter() - started)
        self.frame_times = self.frame_times[-120:]

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.helpers.setGeometry(self.rect())

    def update(self, *args):
        super().update(*args)
        if hasattr(self, 'helpers'):
            self.helpers.update()

    def paint_helpers(self, painter):
        if self.error:
            painter.setPen(QColor('#ef8e8e'))
            painter.drawText(self.rect().adjusted(15, 15, -15, -15), Qt.TextFlag.TextWordWrap, 'OpenGL: ' + self.error[-600:])
        elif not self.level:
            painter.setPen(QColor('#a7bdcf'))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, tr('Selecciona un level y abre el espacio 3D'))
        else:
            self.overlays(painter)

    def box_corners(self, low, high):
        return [np.array([x, y, z]) for z in (low[2], high[2]) for y in (low[1], high[1]) for x in (low[0], high[0])]

    def overlays(self, painter):
        preview=getattr(self,'director_preview',[])
        painter.setPen(QPen(QColor('#ffd064'),2))
        for i,point in enumerate(preview):
            painter.setPen(QPen(QColor('#ffffff' if i==getattr(self,'director_selected',-1) else '#ffd064'),3 if i==getattr(self,'director_selected',-1) else 2))
            position=np.asarray(point['position']);screen=self.project(position)
            if not screen:continue
            painter.drawEllipse(screen,5,5);painter.drawText(screen+QPointF(7,-7),str(i+1))
            pitch,roll,yaw=np.radians(point['orientation']);forward=np.array([-math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(pitch),math.sin(pitch)])
            tip=self.project(position+forward*70)
            if tip:painter.drawLine(screen,tip)
            if i:
                previous=self.project(preview[i-1]['position'])
                if previous:painter.drawLine(previous,screen)
        if self.context_surface is not None:
            surface=self.context_surface;xyz=np.asarray(surface['interaction']['vertices'])[:,:3];center=np.asarray(surface['position'])
            corners=[self.project(center+p) for p in self.box_corners(xyz.min(0),xyz.max(0))]
            painter.setPen(QPen(QColor('#ffd064'),2.))
            for i,j in [(0,1),(0,2),(1,3),(2,3),(4,5),(4,6),(5,7),(6,7),(0,4),(1,5),(2,6),(3,7)]:
                if corners[i] and corners[j]:painter.drawLine(corners[i],corners[j])
        linked = affected(self.data, self.selection[:2]) if self.show_relations and self.data else set()
        selected_pos = None
        if self.data:
            points={p['id']:p for p in self.data.get('waypoints',[])}
            painter.setPen(QPen(QColor('#eea5fc'),2))
            for route in self.paths:
                keys=route['points']+([route['points'][0]] if route.get('loop') and route['points'] else [])
                for a,b in zip(keys,keys[1:]):
                    if a in points and b in points:
                        pa=self.project(np.array(points[a]['transform']['position'])+[0,0,10]);pb=self.project(np.array(points[b]['transform']['position'])+[0,0,10])
                        if pa and pb:painter.drawLine(pa,pb)
        for path, e, ro in self.entities():
            pos = self.position(path, e)
            pt = self.project(pos + [0, 0, 30])
            if pt is None:
                continue
            selected = path == self.selection[:2]
            color = QColor('#ffd064' if selected else '#72edc5' if path in linked else '#a0a6b1' if ro else '#48cde0' if path[0] == 'triggers' else '#94e6a6' if path[0] == 'entries' else '#eea5fc' if path[0] == 'waypoints' else '#98c5f9')
            # Entity helpers are authoring overlays; models remain depth tested.
            low, high = self.entity_bounds(path, e)
            ori = e.get('orientation', [0, 0, 0]) if ro else e['transform'].get('orientation', [0, 0, 0])
            rot = self.object_rotation(ori)
            points = [self.project(pos + rot @ c) for c in self.box_corners(low, high)]
            painter.setPen(QPen(color, 2. if selected else 1.))
            if path[0] == 'triggers' and e.get('shape') == 'sphere':
                for plane in range(3):
                    ring = []
                    for i in range(49):
                        c = np.zeros(3)
                        c[(plane+1)%3] = math.cos(i * math.pi / 24) * e['radius']
                        c[(plane+2)%3] = math.sin(i * math.pi / 24) * e['radius']
                        q = self.project(pos + c)
                        if q:
                            ring.append(q)
                    if len(ring) == 49:
                        painter.drawPolyline(QPolygonF(ring))
            else:
                if path[0] == 'triggers' and all(points):
                    fill = QColor(color)
                    fill.setAlpha(26)
                    painter.setBrush(fill)
                    for indices in [(0,1,3,2), (4,5,7,6), (0,1,5,4), (2,3,7,6)]:
                        painter.drawPolygon(QPolygonF([points[k] for k in indices]))
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                if selected or ro or path[0] == 'triggers' or e.get('template') not in self.model_gpu:
                    for i, j in [(0,1),(0,2),(1,3),(2,3),(4,5),(4,6),(5,7),(6,7),(0,4),(1,5),(2,6),(3,7)]:
                        if points[i] and points[j]:
                            painter.drawLine(points[i], points[j])
            yaw = math.radians(ori[2])
            tip = self.project(pos + [math.cos(yaw)*60, math.sin(yaw)*60, 4])
            base = self.project(pos + [0,0,4])
            if not ro and path[0] != 'triggers' and base and tip:
                painter.drawLine(base, tip)
            if selected or path in linked:
                label = e.get('name', e.get('template', 'Original'))
                if ro:
                    label += tr(' · original, sólo lectura')
                if not ro and e['transform'].get('placement') == 'near_player':
                    label += tr(' · posición relativa al jugador (vista aproximada)')
                painter.drawText(pt + QPointF(12, -15), label)
            if selected:
                selected_pos = pos
        if selected_pos is not None:
            if self.show_relations:
                start = self.project(selected_pos + [0,0,50])
                painter.setPen(QPen(QColor('#71d9b4'), 1, Qt.PenStyle.DashLine))
                for path,e,ro in self.entities():
                    if path in linked and path != self.selection[:2] and start:
                        end = self.project(self.position(path,e)+[0,0,50])
                        if end:
                            painter.drawLine(start,end)
            if self.selection[0] != 'original':
                self.draw_gizmo(painter, selected_pos)
        if self.data and self.selection and self.selection[0]=='generators':
            related=[(p,e) for p,e,ro in self.entities() if p in linked]
            if related:
                center=np.mean([self.position(p,e) for p,e in related],axis=0)+[0,0,35];start=self.project(center)
                painter.setPen(QPen(QColor('#71d9b4'),1,Qt.PenStyle.DashLine))
                for number,(p,e) in enumerate(related):
                    end=self.project(self.position(p,e)+[0,0,35])
                    if start and end:painter.drawLine(start,end)
                    if end and p[0]=='waypoints':painter.drawText(end+QPointF(5,-5),str(number+1))
        painter.setPen(QColor('#d9e5ef'))
        painter.fillRect(0, self.height()-33, self.width(), 33, QColor(20, 27, 34, 215))
        hint = tr('Click en el suelo para colocar · Esc cancela') if self.placing else tr('RMB + WASD mirar/mover · Q/E altura · Shift rápido · Alt+LMB orbitar · F enfocar · Supr eliminar')
        painter.drawText(12, self.height()-12, hint)
        painter.drawText(12, 23, (f'{self.level.name}' + '  |  ' + f'{len(self.level.mesh.material_ids):,}' + tr(' triángulos  |  velocidad ') + f'{self.speed:.0f}' + '  |  ')+ (tr('Suelo') if self.walk else tr('Volar')))

    def gizmo_segments(self, pos):
        origin = self.project(pos)
        if origin is None:
            return []
        scale = max(35., np.linalg.norm(pos - self.pos) * .14)
        basis = np.eye(3)
        if self.mode == 'scale' and self.data and self.selection[0] == 'triggers':
            entity = self.data['triggers'][self.selection[1]]
            basis = rotation(entity['transform'].get('orientation', [0,0,0])[2]).T
        return [(axis, origin, self.project(pos + basis[axis]*scale), scale) for axis in range(3)]

    def draw_gizmo(self, painter, pos):
        self.gizmo = self.gizmo_segments(pos)
        if self.mode == 'rotate':
            painter.setPen(QPen(QColor('#ffd064'), 3))
            ring = [self.project(pos + np.array([math.cos(i*math.pi/24),math.sin(i*math.pi/24),0])*max(45, np.linalg.norm(pos-self.pos)*.14)) for i in range(49)]
            self.rotation_ring = [p for p in ring if p]
            if len(self.rotation_ring)==49:
                painter.drawPolyline(QPolygonF(self.rotation_ring))
            return
        for axis,start,end,scale in self.gizmo:
            if end:
                painter.setPen(QPen(QColor(['#fa6565','#75db89','#72aafc'][axis]),4))
                painter.drawLine(start,end)
                painter.drawText(end+QPointF(5,-5),['X','Y','Z'][axis])

    def focus_selection(self):
        if not self.level:
            return
        found = next(((p,e) for p,e,ro in self.entities() if p==self.selection[:2]),None)
        related = affected(self.data, self.selection[:2]) if self.data else set()
        positions = [self.position(p,e) for p,e,ro in self.entities() if p in related]
        target = self.position(*found) if found else np.mean(positions,axis=0) if positions else np.array(self.level.references[0]['position'] if self.level.references else (self.level.mesh.bounds[0]+self.level.mesh.bounds[1])/2)
        self.pos = target + [230., -320., 180.]
        if found and found[0][0]=='original':
            low,high=self.entity_bounds(*found);center=target+self.object_rotation(found[1].get('orientation',[0,0,0]))@((low+high)/2);radius=max(40.,np.linalg.norm(high-low)/2);distance=max(220.,radius*2.4)
            # Frame base scenery from an unobstructed point inside the level.
            # A fixed world-space offset can put the camera beyond an outer wall.
            for angle in range(0,360,30):
                direction=np.array([math.cos(math.radians(angle)),math.sin(math.radians(angle)),0.]);eye=center+direction*distance+[0,0,radius*.3];delta=center-eye
                if self.raycaster.ground(eye,80,1200) and not self.raycaster.cast(eye,delta,max_distance=np.linalg.norm(delta)-.5):self.pos=eye;target=center-[0,0,55];break
        direction = target + [0,0,55] - self.pos
        self.yaw = math.degrees(math.atan2(direction[1],direction[0]))
        self.pitch = math.degrees(math.atan2(direction[2],np.linalg.norm(direction[:2])))
        self.update()

    def tick(self):
        now=time.perf_counter();dt=min(.06,now-self.tick_time);self.tick_time=now
        if not self.isVisible() or not self.keys or not self.looking:
            return
        forward=self.forward();right=unit(np.cross(forward,[0,0,1]))
        if self.walk:
            forward=unit(forward*[1,1,0])
        delta=np.zeros(3)
        for key,vec in [(Qt.Key.Key_W,forward),(Qt.Key.Key_S,-forward),(Qt.Key.Key_D,right),(Qt.Key.Key_A,-right),(Qt.Key.Key_E,np.array([0,0,1])),(Qt.Key.Key_Q,np.array([0,0,-1]))]:
            if key in self.keys:
                delta+=vec
        self.pos+=unit(delta)*dt*self.speed*(3 if Qt.Key.Key_Shift in self.keys else 1)
        if Qt.Key.Key_Z in self.keys: self.fov=min(110.,self.fov+dt*30)
        if Qt.Key.Key_C in self.keys: self.fov=max(20.,self.fov-dt*30)
        if self.walk and self.level:
            ground=self.raycaster.ground(self.pos-[0,0,110],120,220)
            if ground:
                self.pos[2]=ground.position[2]+110
        self.update()

    def keyPressEvent(self,event):
        key=self.navigation_key(event)
        if event.key()==Qt.Key.Key_F:
            self.focus_selection()
        elif event.key()==Qt.Key.Key_Escape:
            self.gesture_finished.emit();self.operation_cancelled.emit()
            self.placing=None;self.drag=None;self.looking=False;self.warp_target=None;self.releaseMouse();self.unsetCursor();self.message.emit(tr('Operación cancelada'))
        elif key in (Qt.Key.Key_1,Qt.Key.Key_2,Qt.Key.Key_3):
            self.mode_requested.emit({Qt.Key.Key_1:'move',Qt.Key.Key_2:'rotate',Qt.Key.Key_3:'scale'}[key])
        else:
            self.keys.add(key)
            if self.looking:self.right_dragged=True
    @staticmethod
    def navigation_key(event):
        aliases={Qt.Key.Key_Up:Qt.Key.Key_W,Qt.Key.Key_Down:Qt.Key.Key_S,Qt.Key.Key_Left:Qt.Key.Key_A,Qt.Key.Key_Right:Qt.Key.Key_D,Qt.Key.Key_PageUp:Qt.Key.Key_E,Qt.Key.Key_PageDown:Qt.Key.Key_Q}
        if event.modifiers() & Qt.KeyboardModifier.KeypadModifier:
            aliases.update({Qt.Key.Key_8:Qt.Key.Key_W,Qt.Key.Key_2:Qt.Key.Key_S,Qt.Key.Key_4:Qt.Key.Key_A,Qt.Key.Key_6:Qt.Key.Key_D,Qt.Key.Key_9:Qt.Key.Key_E,Qt.Key.Key_7:Qt.Key.Key_Q,Qt.Key.Key_1:Qt.Key.Key_Z,Qt.Key.Key_3:Qt.Key.Key_C})
        return aliases.get(event.key(),event.key())
    def keyReleaseEvent(self,event):
        if not event.isAutoRepeat():
            self.keys.discard(self.navigation_key(event))
    def focusOutEvent(self,event):
        if self.drag:self.gesture_finished.emit();self.drag=None
        self.keys.clear();self.looking=False;self.orbiting=False;self.warp_target=None;self.releaseMouse();self.unsetCursor()
        self.right_origin=None;self.right_dragged=False;self.left_pending=None;self.left_origin=None;self.nav_buttons=Qt.MouseButton.NoButton;self.fov=60.
        super().focusOutEvent(event)
    def wheelEvent(self,event):
        if self.looking:
            self.speed=max(20.,min(6000.,self.speed*(1.25 if event.angleDelta().y()>0 else .8)))
        else:
            self.pos+=self.forward()*self.speed*.3*(1 if event.angleDelta().y()>0 else -1)
        self.update()
    @staticmethod
    def line_distance(pt,a,b):
        v=np.array([b.x()-a.x(),b.y()-a.y()]);w=np.array([pt.x()-a.x(),pt.y()-a.y()]);t=np.clip((w@v)/max(1e-6,v@v),0,1)
        return np.linalg.norm(w-t*v)

    def mousePressEvent(self,event):
        self.setFocus()
        self.last_mouse=event.position()
        self.nav_buttons=event.buttons()
        if event.button()==Qt.MouseButton.RightButton:
            if self.drag:self.gesture_finished.emit()
            self.right_origin=event.position();self.right_dragged=False;self.left_pending=None;self.drag=None
            self.warp_target=None;self.looking=True;self.grabMouse();self.setCursor(Qt.CursorShape.BlankCursor);return
        if event.button()==Qt.MouseButton.MiddleButton:
            if self.drag:self.gesture_finished.emit()
            self.drag=None;self.left_pending=None;return
        if event.buttons() & Qt.MouseButton.RightButton:return
        if event.button()!=Qt.MouseButton.LeftButton or not self.level:
            return
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            self.orbit_center=self.pos+self.forward()*500
            self.orbiting=True;return
        if self.placing:
            o,d=self.screen_ray(event.position().x(),event.position().y());hit=self.raycaster.cast(o,d)
            if hit and abs(hit.normal[2])>.65:
                pos=hit.position
                if self.grid:
                    pos=snap(pos,self.grid);floor=self.raycaster.ground(pos,20,40);pos=floor.position if floor else hit.position
                self.placed.emit(pos.tolist());self.placing=None
            else:
                self.message.emit(tr('Selecciona una superficie de suelo válida'))
            return
        selected=next(((p,e) for p,e,ro in self.entities() if p==self.selection[:2] and not ro),None)
        if selected:
            path,e=selected;pos=self.position(path,e)
            if self.mode=='rotate' and (path[0]!='triggers' or e['shape']=='box'):
                ring=getattr(self,'rotation_ring',[])
                if any(self.line_distance(event.position(),a,b)<10 for a,b in zip(ring,ring[1:])):
                    self.gesture_started.emit()
                    self.drag=(path,'rotate',None,event.position(),pos.copy(),e['transform'].get('orientation',[0,0,0])[:],e.get('size',[1,1,1])[:],e.get('radius',60));return
            elif self.mode=='move' or (self.mode=='scale' and path[0]=='triggers'):
                for axis,start,end,scale in self.gizmo_segments(pos):
                    if end and self.line_distance(event.position(),start,end)<10:
                        self.gesture_started.emit()
                        self.drag=(path,self.mode,axis,event.position(),pos.copy(),e['transform'].get('orientation',[0,0,0])[:],e.get('size',[120,120,120])[:],e.get('radius',60));return
        chosen=self.pick_at(event.position().x(),event.position().y())
        self.left_pending=chosen;self.left_origin=event.position()

    def mouseMoveEvent(self,event):
        if self.last_mouse is None:
            self.last_mouse=event.position();return
        delta=event.position()-self.last_mouse
        buttons=event.buttons()
        alt=bool(event.modifiers() & Qt.KeyboardModifier.AltModifier)
        right=unit(np.cross(self.forward(),[0,0,1]));up=unit(np.cross(right,self.forward()))
        if self.right_origin is not None and (event.position()-self.right_origin).manhattanLength()>4:self.right_dragged=True
        if buttons & Qt.MouseButton.MiddleButton:
            self.pos+=(-right*delta.x()+up*delta.y())*self.speed*.004
        elif buttons & Qt.MouseButton.RightButton and buttons & Qt.MouseButton.LeftButton:
            self.pos[2]-=delta.y()*self.speed*.004
            self.right_dragged=True
        elif alt and buttons & Qt.MouseButton.RightButton:
            self.pos+=self.forward()*(-delta.y()+delta.x())*self.speed*.004
        elif self.looking:
            if self.warp_target is not None:
                # The OS may have queued old positions before the recenter.
                # Neither those nor the synthetic recenter are mouse movement.
                if (event.position()-self.warp_target).manhattanLength()<2:
                    self.last_mouse=self.warp_target;self.warp_target=None
                    return
                # Some Windows drivers coalesce the synthetic center event.
                # Accept the next real event relative to the anchor, rather
                # than waiting forever; discard queued events at old positions.
                live=QPointF(self.mapFromGlobal(QCursor.pos()))
                if (event.position()-live).manhattanLength()>2:
                    return
                self.last_mouse=self.warp_target;self.warp_target=None
                delta=event.position()-self.last_mouse
            self.yaw=(self.yaw-delta.x()*.22)%360;self.pitch=max(-88,min(88,self.pitch-delta.y()*.22))
            # Warp within the widget, so free look does not stop at screen edges.
            if event.position().x()<20 or event.position().x()>self.width()-20 or event.position().y()<20 or event.position().y()>self.height()-20:
                center=self.rect().center();self.warp_target=QPointF(center);QCursor.setPos(self.mapToGlobal(center));self.last_mouse=QPointF(center);self.update();return
        elif self.orbiting:
            selected=next(((p,e) for p,e,ro in self.entities() if p==self.selection[:2]),None)
            if selected or self.orbit_center is not None:
                center=self.position(*selected)+[0,0,50] if selected else self.orbit_center;v=self.pos-center
                radius=max(1.,float(np.linalg.norm(v)))
                azimuth=math.atan2(v[1],v[0])-math.radians(delta.x()*.3)
                elevation=max(math.radians(-88),min(math.radians(88),math.atan2(v[2],np.linalg.norm(v[:2]))+math.radians(delta.y()*.3)))
                self.pos=center+radius*np.array([math.cos(azimuth)*math.cos(elevation),math.sin(azimuth)*math.cos(elevation),math.sin(elevation)])
                d=center-self.pos;self.yaw=math.degrees(math.atan2(d[1],d[0]));self.pitch=math.degrees(math.atan2(d[2],np.linalg.norm(d[:2])))
        elif self.drag:
            path,mode,axis,start,pos,ori,size,radius=self.drag
            change={}
            if mode=='rotate':
                yaw=ori[2]+(event.position().x()-start.x())*.5
                if self.angle_step:
                    yaw=float(snap([yaw],self.angle_step)[0])
                change['orientation']=[ori[0],ori[1],yaw%360]
            else:
                segments=self.gizmo_segments(pos);a,b=segments[axis][1:3]
                if not b:
                    return
                screen=np.array([b.x()-a.x(),b.y()-a.y()]);movement=np.array([event.position().x()-start.x(),event.position().y()-start.y()]);amount=float(movement@screen/max(1e-6,screen@screen))*segments[axis][3]
                if mode=='move':
                    moved=pos.copy();moved[axis]+=amount;moved=snap(moved,self.grid)
                    if self.snap_surface and axis!=2:
                        hit=self.raycaster.ground(moved,100,220)
                        if hit:
                            moved[2]=hit.position[2]
                            if path[0]=='triggers':
                                entity=self.data[path[0]][path[1]]
                                moved[2]+=entity['size'][2]/2 if entity['shape']=='box' else entity['radius']
                    change['position']=moved.tolist()
                else:
                    entity=self.data[path[0]][path[1]]
                    if entity['shape']=='sphere':
                        change['radius']=max(1.,radius+amount)
                    else:
                        resized=list(size);resized[axis]=max(1.,size[axis]+amount*2);change['size']=resized
            self.transformed.emit(path,change)
        elif buttons & Qt.MouseButton.LeftButton:
            if self.left_origin is not None and (event.position()-self.left_origin).manhattanLength()<4:return
            self.left_pending=None
            self.yaw=(self.yaw-delta.x()*.22)%360
            self.pos-=unit(self.forward()*[1,1,0])*delta.y()*self.speed*.004
        self.last_mouse=event.position();self.update()

    def mouseReleaseEvent(self,event):
        if self.drag:self.gesture_finished.emit()
        if event.button()==Qt.MouseButton.LeftButton and self.left_pending is not None:
            self.selected.emit(self.left_pending)
        if event.button()==Qt.MouseButton.RightButton:
            show_menu=self.right_origin is not None and not self.right_dragged
            self.looking=False;self.warp_target=None;self.right_origin=None;self.fov=60.;self.releaseMouse();self.unsetCursor()
            if show_menu:self.menu_requested.emit(event.globalPosition().toPoint())
        self.nav_buttons=event.buttons();self.left_pending=None;self.left_origin=None;self.orbiting=False;self.drag=None

class SpatialPanel(QWidget):
    def __init__(self,window):
        super().__init__()
        self.win=window;self.loading=False;self.loaded_name=None;self.assets=None;self.pending_resource=None;self.request_name=None;self.requested_templates=set()
        self.document = None
        self.gesture_active=False;self.gesture_changed=False;self.gesture_inspect=False
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0)
        toolbar=QHBoxLayout()
        self.mode_buttons = {}
        for label,mode in [(tr('Mover'),'move'),(tr('Girar'),'rotate'),(tr('Tamaño'),'scale')]:
            b=QPushButton(label);b.setCheckable(True);b.setChecked(mode=='move');self.mode_buttons[mode]=b;b.setObjectName('gizmo_'+mode);b.clicked.connect(lambda checked=False,m=mode:self.set_mode(m));toolbar.addWidget(b)
        b=QPushButton(tr('Enfocar'));b.clicked.connect(lambda:self.viewport.focus_selection() if self.viewport else None);toolbar.addWidget(b)
        b=QPushButton(tr('Inicio'));b.setObjectName('focus_player_start');b.setToolTip(tr('Ver el punto de aparición del jugador al comenzar la crónica'));b.clicked.connect(lambda:self.win.guard(self.win.focus_player_start));toolbar.addWidget(b)
        b=QPushButton(tr('+ Actor'));b.setObjectName('place_actor');b.clicked.connect(lambda:self.win.guard(self.win.add_actor));toolbar.addWidget(b)
        b=QPushButton(tr('+ Zona de activación'));b.setObjectName('place_trigger');b.clicked.connect(self.add_trigger);toolbar.addWidget(b)
        b=QPushButton(tr('Eliminar'));b.setObjectName('spatial_delete');b.clicked.connect(lambda:self.win.guard(self.win.delete_selected));toolbar.addWidget(b)
        b=QPushButton(tr('Referencias'));b.clicked.connect(lambda:self.win.find_references());toolbar.addWidget(b)
        layout.addLayout(toolbar)
        options=QHBoxLayout()
        self.ground=QCheckBox(tr('Suelo'));self.ground.setToolTip(tr('Altura de cámara sobre suelo; no sustituye colisión del motor'));options.addWidget(self.ground)
        self.surface=QCheckBox(tr('Snap suelo'));self.surface.setChecked(True);options.addWidget(self.surface)
        self.grid=QDoubleSpinBox();self.grid.setRange(0,512);self.grid.setSpecialValueText(tr('Libre'));self.grid.setPrefix('Grid ');options.addWidget(self.grid)
        self.angle=QDoubleSpinBox();self.angle.setRange(0,90);self.angle.setValue(0);self.angle.setSpecialValueText(tr('Libre'));self.angle.setSuffix('°');self.angle.setToolTip(tr('Giro libre con 0; elige un ángulo para activar el ajuste por pasos.'));options.addWidget(self.angle)
        self.links=QCheckBox(tr('Relaciones'));self.links.setChecked(True);options.addWidget(self.links)
        options.addStretch();layout.addLayout(options)
        self.status=QLabel(tr('Carga pendiente'));self.status.setWordWrap(True);layout.addWidget(self.status)
        self.viewport=None
        if QApplication.platformName() != 'offscreen' and not getattr(window.backend,'safe_mode',False):
            self.viewport=Viewport(self);layout.addWidget(self.viewport,1)
            self.win.register_delete_shortcut(self.viewport,self.win.delete_selected)
            self.viewport.selected.connect(self.select)
            self.viewport.transformed.connect(self.transform)
            self.viewport.placed.connect(self.place)
            self.viewport.message.connect(self.status.setText)
            self.viewport.gesture_started.connect(self.start_gesture)
            self.viewport.gesture_finished.connect(self.finish_gesture)
            self.viewport.operation_cancelled.connect(self.cancel_place)
            self.viewport.mode_requested.connect(self.set_mode)
            self.viewport.menu_requested.connect(self.context_menu)
            self.ground.toggled.connect(lambda v:setattr(self.viewport,'walk',v))
            self.surface.toggled.connect(lambda v:setattr(self.viewport,'snap_surface',v))
            self.grid.valueChanged.connect(lambda v:setattr(self.viewport,'grid',v))
            self.angle.valueChanged.connect(lambda v:setattr(self.viewport,'angle_step',v))
            self.links.toggled.connect(self.relationships)
        else:
            layout.addWidget(QLabel(tr('OpenGL requiere una ventana real; backend y edición de datos siguen disponibles.')),1)

    def context_menu(self,position):
        menu=QMenu(self);menu.setObjectName('viewport_context_menu')
        local=self.viewport.mapFromGlobal(position);path=self.viewport.pick_at(local.x(),local.y()) if self.win.doc and self.geometry_matches() else None;target=None;surface=None
        if path:
            self.select(path)
            if path[0]=='original':target=self.viewport.level.references[path[1]]
        elif self.viewport.level and self.win.doc and self.geometry_matches():
            o,d=self.viewport.screen_ray(local.x(),local.y());hit=self.viewport.raycaster.cast(o,d)
            if hit:
                mid=self.viewport.level.mesh.material_ids[hit.triangle];material=self.viewport.level.mesh.materials[mid] if mid>=0 else ''
                normal=hit.normal if hit.normal@d<0 else -hit.normal
                from ..click_interactions import surface as click_surface
                try:
                    center,mesh=click_surface(self.viewport.level.mesh,hit.triangle,normal)
                    surface=dict(level=self.win.doc.data['level']['source'],position=center,material=material,fixed_surface=True,interaction=mesh)
                except ValueError as error:self.status.setText(str(error))
        for label,cb in [(tr('Enfocar selección · F'),self.viewport.focus_selection),(tr('Mover · 1'),lambda:self.set_mode('move')),(tr('Girar · 2'),lambda:self.set_mode('rotate')),(tr('Tamaño · 3'),lambda:self.set_mode('scale')),(tr('+ Actor…'),self.win.add_actor),(tr('+ Objeto…'),self.add_object),('+ Trigger',self.add_trigger),(tr('+ Entrada'),lambda:self.win.campaign_panel.add_marker('entries')),('+ Waypoint',lambda:self.win.campaign_panel.add_marker('waypoints')),(tr('Ajustar al suelo'),self.snap_selected),(tr('Buscar referencias'),self.win.find_references),(tr('Eliminar · Supr'),self.win.delete_selected)]:
            action=menu.addAction(label);action.triggered.connect(lambda checked=False,cb=cb:self.win.guard(cb))
        self.win.add_conversation_action(menu,path or self.win.selection)
        from .dynamic_wizard import open_dynamic
        from .original_objects import use_selected,object_label
        label=tr('Objeto original / crear paso…')
        if target:label+=' · '+object_label(target)
        elif surface:label=tr('Superficie / interacción al hacer clic…')+' · '+surface['material']
        original=menu.addAction(label);original.setObjectName('use_original');original.triggered.connect(lambda:self.win.guard(lambda:use_selected(self.win,target=surface or target,picker=target is None)));original.setEnabled(self.win.doc is not None)
        if path and path[0]=='objects' and 'interaction' in self.win.at(path):
            def edit_click():
                ident=self.win.at(path)['id'];index=next((i for i,e in enumerate(self.win.doc.data['events']) if e['when']=='object_clicked' and e.get('object')==ident),None)
                if index is not None:self.win.select(('events',index))
            original.setText(tr('Editar acciones al hacer clic…'));original.triggered.disconnect();original.triggered.connect(edit_click)
        def encounter_here():
            local=self.viewport.mapFromGlobal(position);o,d=self.viewport.screen_ray(local.x(),local.y());hit=self.viewport.raycaster.cast(o,d) if self.viewport.level else None
            if not hit or abs(hit.normal[2])<=.65:raise ValueError(tr('Selecciona una superficie de suelo válida'))
            open_dynamic(self.win,position=hit.position.tolist())
        action=menu.addAction(tr('Encuentro dinámico aquí…'));action.setObjectName('dynamic_here');action.triggered.connect(lambda:self.win.guard(encounter_here));action.setEnabled(self.win.doc is not None and self.viewport.level is not None)
        self.viewport.context_surface=surface;self.viewport.update()
        try:menu.exec(position)
        finally:self.viewport.context_surface=None;self.viewport.update()

    def add_object(self):
        from .browser import ResourceDialog
        from PySide6.QtWidgets import QDialog
        dialog=ResourceDialog(self.win.backend,'items',self)
        if dialog.exec()==QDialog.DialogCode.Accepted:self.begin_place('objects',dialog.selection)

    def set_mode(self,mode):
        for key,button in self.mode_buttons.items():
            button.setChecked(key==mode)
        if self.viewport:
            self.viewport.mode=mode;self.viewport.update()
            if mode=='scale' and self.win.selection[0]!='triggers':
                self.status.setText(tr('Tamaño sólo se aplica a volúmenes; los actores conservan su escala original.'))
    def start_gesture(self):
        self.finish_gesture()
        self.gesture_active=True;self.gesture_changed=False;self.gesture_inspect=False
        self.win.validation_timer.stop()
        self.win.history_time = 0
    def finish_gesture(self):
        changed=self.gesture_changed;inspect=self.gesture_inspect
        self.gesture_active=False;self.gesture_changed=False;self.gesture_inspect=False
        if changed and self.win.doc:
            self.win.changed()
            # Each mouse gesture is a single undo operation, including long drags.
            self.win.history_time=0
            if inspect:self.win.inspect()
    def cancel_place(self):
        self.pending_resource=None
        if self.viewport:self.viewport.placing=None;self.viewport.unsetCursor()
    def relationships(self,value):
        self.viewport.show_relations=value;self.viewport.update()
    def sync(self):
        if self.viewport and self.win.doc:
            scene_key=getattr(self.win.doc, 'active', None)
            source=self.win.doc.data['level'].get('source')
            if self.document is not self.win.doc or getattr(self,'scene_key',None)!=scene_key or getattr(self,'source_name',None)!=source:
                self.gesture_active=False;self.gesture_changed=False;self.gesture_inspect=False
                self.viewport.placing = None
                self.viewport.drag = None
                self.pending_resource = None
                self.viewport.hidden={('original',)}
            self.scene_key=scene_key
            self.source_name=source
            self.document = self.win.doc
            self.viewport.paths=self.win.doc.campaign['scenes'][self.win.doc.active].get('paths',[]) if hasattr(self.win.doc,'campaign') else []
            self.viewport.sync(self.win.doc.data,self.win.selection)

    def geometry_matches(self):
        return self.viewport is None or (self.viewport.level is not None and self.win.doc is not None and self.viewport.level.name == self.win.doc.data['level'].get('source'))
    def load_identity(self):
        return (id(self.win.doc),getattr(self.win.doc,'active',None),self.win.doc.data['level'].get('source')) if self.win.doc else None
    def ensure_loaded(self):
        if not self.win.doc or not self.viewport:
            return
        name=self.win.doc.data['level'].get('source')
        if name not in self.win.backend.levels:
            return
        self.request_name=name
        templates={a.get('template') for k in ('actors','objects') for a in self.win.doc.data.get(k,[])}
        models=tuple(sorted((t['id'],t.get('model') or '') for t in self.win.backend.resources['templates'] if t['id'] in templates))
        if self.loading or (name==self.loaded_name and templates<=self.requested_templates and models==getattr(self,'requested_models',None)):
            return
        self.loading=True;self.status.setText(tr('Leyendo escenario…'))
        self.loading_identity=self.load_identity()
        self.requested_templates=templates
        self.requested_models=models
        self.thread=QThread(self);self.worker=LoadWorker(self.win.backend,name,templates,self.assets);self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run);self.worker.progress.connect(self.status.setText);self.worker.ready.connect(self.loaded);self.worker.failed.connect(self.failed)
        self.worker.finished.connect(self.thread.quit);self.worker.finished.connect(self.worker.deleteLater);self.thread.finished.connect(self.finished);self.thread.start()
    def finished(self):
        self.loading=False
        self.thread.deleteLater()
        if self.win.doc and self.request_name is not None and self.request_name==self.win.doc.data['level'].get('source'):
            # failed load is retried explicitly with the button, not in a loop
            QTimer.singleShot(0,self.ensure_loaded)
    def loaded(self,level,assets):
        if not self.win.doc or level.name!=self.win.doc.data['level'].get('source') or getattr(self,'loading_identity',self.load_identity())!=self.load_identity():
            return
        self.assets=assets;self.loaded_name=level.name;self.viewport.set_level(level);self.sync()
        if getattr(self,'pending_start_focus',False):self.pending_start_focus=False;self.viewport.focus_selection()
        self.status.setText((f'{level.name}' + tr(' · ') + f'{sum((m.warning is None for m in level.materials))}' + '/' + f'{len(level.materials)}' + tr(' materiales con textura · geometría original de sólo lectura')))
        for warning in level.warnings:
            self.win.log.appendPlainText('Viewport warning: '+warning)
        self.win.refresh()
        self.arm_place()
    def failed(self,error):
        if getattr(self,'loading_identity',self.load_identity())!=self.load_identity():return
        self.status.setText(tr('No se pudo cargar el level; consulta Build / Log.'));self.win.log.appendPlainText(error)
        self.request_name=None
        self.cancel_place()
    def select(self,path):
        if not self.win.commit_properties():
            return
        self.win.select(path)
        item=self.win.nav_items.get(path)
        if item:
            self.win.nav.blockSignals(True);self.win.nav.setCurrentItem(item);self.win.nav.blockSignals(False)
    def transform(self,path,change):
        if self.win.busy or path[0]=='original' or not self.win.doc:
            return
        if not self.geometry_matches():
            self.status.setText(tr('Espera a que cargue el escenario seleccionado antes de editar su posición.'))
            return
        entity=self.win.at(path)
        was_relative = entity['transform'].get('placement')=='near_player'
        if 'position' in change:
            entity['transform']['placement']='absolute';entity['transform']['position']=[float(v) for v in change['position']]
        if 'orientation' in change:
            entity['transform']['orientation']=[float(v) for v in change['orientation']]
        for key in ('size','radius'):
            if key in change and path[0]=='triggers':
                entity[key]=[float(v) for v in change[key]] if key=='size' else float(change[key])
        if self.gesture_active:
            self.gesture_changed=True;self.gesture_inspect |= was_relative
            self.viewport.update()
        else:self.win.changed()
        if was_relative and not self.gesture_active:
            self.win.inspect()
        else:
            panel=self.win.properties.widget()
            values={}
            if path[0] in {'actors','objects','entries','waypoints'}:
                for i,axis in enumerate('xyz'):
                    values['position_'+axis]=entity['transform'].get('position',[0,0,0])[i]
                    values['orientation_'+str(i)]=entity['transform']['orientation'][i]
            elif path[0]=='triggers':
                for i,axis in enumerate('XYZ'):
                    values['trigger_position_'+axis]=entity['transform']['position'][i]
                    if 'size' in entity:
                        values['trigger_size_'+axis]=entity['size'][i]
                values['trigger_yaw']=entity['transform']['orientation'][2]
                values['trigger_radius']=entity.get('radius',60)
            for name,value in values.items():
                control=panel.findChild(QDoubleSpinBox,name)
                if control:
                    control.blockSignals(True);control.setValue(value);control.blockSignals(False)
    def begin_place(self,kind,template=''):
        if not self.win.doc or self.win.busy:
            return
        self.win.center_tabs.setCurrentIndex(0);self.sync()
        if not self.viewport:return
        self.pending_resource=(kind,template);self.ensure_loaded();self.viewport.setFocus()
        if not self.arm_place():self.status.setText(tr('Cargando escenario; tu selección se conserva. Esc cancela.'))
    def arm_place(self):
        if not self.pending_resource or not self.viewport or not self.geometry_matches():return False
        self.viewport.placing=self.pending_resource;self.viewport.setCursor(Qt.CursorShape.CrossCursor)
        self.status.setText(tr('Haz click en el suelo para colocar. Esc cancela.'))
        return True
    def add_trigger(self):
        self.begin_place('triggers')
    def place(self,position):
        if not self.geometry_matches():
            self.status.setText(tr('Espera a que cargue el escenario seleccionado y vuelve a elegir el recurso.'))
            return
        if not self.pending_resource:
            return
        kind,template=self.pending_resource;self.pending_resource=None
        if kind=='triggers':
            data=self.win.doc.data;ident=self.win.doc.unique_id('triggers','trigger');index=len(data.setdefault('triggers',[]))
            data['triggers'].append(dict(id=ident,name=tr('Nuevo trigger'),shape='box',transform=dict(position=[position[0],position[1],position[2]+60],orientation=[0,0,0]),size=[160,160,120],once=True))
            self.win.selection=('triggers',index);self.win.changed(True)
        else:
            self.win.add_spatial_entity(kind,template,position)
        self.viewport.unsetCursor();self.status.setText(tr('Entidad colocada. Mover · 1 / Girar · 2 / F enfocar'))

    def snap_selected(self):
        if not self.viewport or not self.viewport.level:
            return
        p=self.win.selection[:2]
        if len(p)!=2 or p[0] not in ('actors','objects','triggers','entries','waypoints'):
            return
        e=self.win.at(p);pos=self.viewport.position(p,e);hit=self.viewport.raycaster.ground(pos,250,4000)
        if hit:
            moved=hit.position.copy()
            if p[0]=='triggers':
                moved[2]+=e.get('size',[0,0,2*e.get('radius',60)])[2]/2
            self.transform(p,{'position':moved.tolist()})

