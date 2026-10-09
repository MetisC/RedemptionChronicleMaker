import traceback
import time

from PySide6.QtCore import Qt, QTimer, QThread, QObject, Signal
from PySide6.QtGui import QAction, QDesktopServices, QShortcut, QPalette, QColor
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QScrollArea, QDockWidget,
    QTabWidget, QPlainTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QDialog, QFormLayout, QLineEdit, QDialogButtonBox)

from ..document import Document
from ..model import identifier
from .browser import ResourceBrowser, ResourceDialog

ROLE = Qt.ItemDataRole.UserRole
ACTION_LABELS = {"spawn": "Crear", "start_conversation": "Iniciar conversación", "set_flag": "Activar flag", "clear_flag": "Desactivar flag"}
TRIGGER_LABELS = {"scene_start": "Inicia la escena", "actor_clicked": "Hablan con un actor", "conversation_ended": "Termina una conversación", "trigger_enter": "Un jugador entra en el volumen"}


class NewProjectDialog(QDialog):
    def __init__(self, workspace, parent=None):
        super().__init__(parent)
        self.ws = workspace
        self.setWindowTitle("Nueva crónica")
        self.resize(640, 350)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.pid = QLineEdit("new_chronicle")
        self.pid.setObjectName("new_id")
        self.pid.setMaxLength(14)
        self.name = QLineEdit("Mi nueva crónica")
        self.name.setObjectName("new_name")
        self.description = QPlainTextEdit()
        self.description.setObjectName("new_description")
        self.description.setMaximumHeight(90)
        self.directory = QLineEdit(str(workspace.output("chronicles/new_chronicle")))
        self.directory.setObjectName("new_directory")
        self.pid.textChanged.connect(lambda text: self.directory.setText(str(workspace.output("chronicles") / text)))
        path_row = QWidget()
        path_layout = QHBoxLayout(path_row)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.addWidget(self.directory, 1)
        browse = QPushButton("Elegir…")
        browse.clicked.connect(self.choose_directory)
        path_layout.addWidget(browse)
        form.addRow("ID interno", self.pid)
        form.addRow("Nombre", self.name)
        form.addRow("Descripción", self.description)
        form.addRow("Directorio", path_row)
        layout.addLayout(form)
        hint = QLabel("El proyecto y sus builds se guardan dentro del workspace. Después elegirás el escenario.")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Crear proyecto")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        self.buttons.accepted.connect(self.check_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def choose_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Directorio del proyecto", str(self.ws.root / "chronicles"))
        if path:
            self.directory.setText(path)

    def check_accept(self):
        try:
            identifier(self.pid.text(), "ID de crónica", 14)
            self.ws.output(self.directory.text())
            if not self.name.text().strip():
                raise ValueError("Escribe un nombre para la crónica.")
            self.accept()
        except ValueError as error:
            QMessageBox.warning(self, "Revisa el proyecto", str(error))


class BuildWorker(QObject):
    progress = Signal(str)
    succeeded = Signal(object)
    failed = Signal(str, str)
    completed = Signal()

    def __init__(self, backend, source):
        super().__init__()
        self.backend, self.source = backend, source

    def run(self):
        try:
            report = self.backend.build(self.source, progress=self.progress.emit)
            self.succeeded.emit(report)
        except Exception as error:
            self.failed.emit(str(error), traceback.format_exc())
        finally:
            self.completed.emit()


class MainWindow(QMainWindow):
    build_completed = Signal(object)
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.doc = None
        self.selection = ("chronicle",)
        self.busy = False
        self.last_build = None
        self.history_document = None
        self.history = []
        self.redo_history = []
        self.history_time = 0
        self.history_path = None
        self.delete_shortcuts = []
        self.resize(1430, 900)
        self.setMinimumSize(1100, 720)
        self.setObjectName("chronicle_editor")
        from .identity import application_icon
        self.setWindowIcon(application_icon())
        from .theme import editor_palette
        self.setPalette(editor_palette(self.palette()))
        colors = {name: self.palette().color(getattr(QPalette.ColorRole, name)).name() for name in ['Base', 'AlternateBase', 'Text', 'Highlight', 'HighlightedText']}
        self.setStyleSheet("QTreeWidget, QTableWidget { background-color: " + colors['Base'] + "; alternate-background-color: " + colors['AlternateBase'] + "; color: " + colors['Text'] + "; selection-background-color: " + colors['Highlight'] + "; selection-color: " + colors['HighlightedText'] + "; } QPushButton { min-height: 20px; padding: 1px 7px; } QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { min-height: 21px; } QToolBar { spacing: 4px; padding: 3px; }")
        self._actions()
        self._layout()
        from .campaign_panel import CampaignPanel
        self.campaign_panel = CampaignPanel(self)
        self.center_tabs.addTab(self.campaign_panel, 'Campaña / Quests')
        from .resource_panel import ProjectResourcesPanel
        self.project_resources_panel=ProjectResourcesPanel(self)
        self.center_tabs.addTab(self.project_resources_panel,'Templates / AI propios')
        from .debug_panel import DebugPanel
        self.debug_panel=DebugPanel(self);self.center_tabs.addTab(self.debug_panel,'Playtest / Debug')
        from .graph_panel import GraphPanel
        self.graph_panel=GraphPanel(self);self.center_tabs.addTab(self.graph_panel,'Gráfico de historia')
        from .guide_panel import GuidePanel
        self.guide_panel=GuidePanel(self);self.center_tabs.addTab(self.guide_panel,'Tutorial / Ayuda')
        for widget, callback in [(self.nav, self.delete_selected), (self.content, self.delete_selected),
                                 (self.graph_panel.view, self.delete_selected),
                                 (self.campaign_panel.tree, self.campaign_panel.delete)]:
            self.register_delete_shortcut(widget, callback)
        campaign_menu = self.menuBar().addMenu('Campaña')
        campaign_menu.addAction('Crear campaña de varios mapas', lambda: self.guard(self.campaign_panel.convert))
        campaign_menu.addAction('Buscar en toda la crónica', self.campaign_panel.focus_search, 'Ctrl+Shift+F')
        campaign_menu.addAction('Comprobar integridad', self.validate_from_ui)
        self.actions['redo'].setShortcuts(['Ctrl+Y', 'Ctrl+Shift+Z'])
        self.validation_timer = QTimer(self)
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.validate_project)
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setInterval(30000)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start()
        self.refresh()

    def _actions(self):
        self.actions = {}
        toolbar = self.addToolBar("Proyecto")
        toolbar.setMovable(False)
        for key, label, shortcut, callback in [
            ("new", "Nueva crónica", "Ctrl+N", self.new_project),
            ("open", "Abrir", "Ctrl+O", self.open_project),
            ("save", "Guardar", "Ctrl+S", self.save_project),
            ("save_as", "Guardar como…", "Ctrl+Shift+S", self.save_as),
            ("validate", "Validar", "Ctrl+Shift+V", self.validate_from_ui),
            ("build", "BUILD CHRONICLE", "F5", self.build_project)]:
            action = QAction(label, self)
            action.setShortcut(shortcut)
            action.setObjectName("action_" + key)
            action.triggered.connect(lambda checked=False, cb=callback: self.guard(cb))
            self.actions[key] = action
            if key != "save_as":
                toolbar.addAction(action)
        file_menu = self.menuBar().addMenu("Archivo")
        for key in ["new", "open", "save", "save_as"]:
            file_menu.addAction(self.actions[key])
        edit_menu = self.menuBar().addMenu("Crónica")
        for key, label, shortcut, callback in [('undo','Deshacer','Ctrl+Z',self.undo_project),('redo','Rehacer','Ctrl+Y',self.redo_project)]:
            action = QAction(label,self)
            action.setShortcut(shortcut)
            action.triggered.connect(lambda checked=False,cb=callback:self.guard(cb))
            self.actions[key] = action
            edit_menu.addAction(action)
        edit_menu.addAction("Elegir level base…", self.choose_level)
        edit_menu.addAction("Añadir actor", self.add_actor)
        edit_menu.addAction("Nueva conversación", self.add_conversation)
        edit_menu.addAction("Nuevo evento", self.add_event)
        edit_menu.addAction("Nuevo flag", self.add_flag)
        build_menu = self.menuBar().addMenu("Build")
        build_menu.addAction(self.actions["validate"])
        build_menu.addAction(self.actions["build"])
        help_menu = self.menuBar().addMenu("Ayuda")
        help_menu.addAction('Tutorial del proyecto',lambda:self.center_tabs.setCurrentWidget(self.guide_panel))
        help_menu.addAction("Guía del editor", lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.backend.ws.root / "docs/EDITOR_GUIDE.md"))))
        from .package_panel import menu
        menu(self)
        help_menu.addAction('Informe de diagnóstico',lambda:self.guard(lambda:__import__('rcm.diagnostics',fromlist=['diagnostic_report']).diagnostic_report(self.backend.ws)))

    def _layout(self):
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)
        self.nav = QTreeWidget()
        self.nav.setHeaderLabel("PROYECTO")
        self.nav.setObjectName("project_tree")
        self.nav.setMinimumWidth(200)
        self.splitter.addWidget(self.nav)
        center = QWidget()
        center_layout = QVBoxLayout(center)
        self.heading = QLabel("Redemption Chronicle Maker")
        self.heading.setStyleSheet("font-size: 21px; font-weight: 600; padding: 8px 0;")
        self.subtitle = QLabel()
        self.subtitle.setWordWrap(True)
        # Mode tabs always occupy the same row. Story-specific controls belong
        # to their page, so selecting actors cannot push every tab downwards.
        self.story_header = QWidget()
        header_layout = QVBoxLayout(self.story_header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(self.heading)
        header_layout.addWidget(self.subtitle)
        self.button_row = QHBoxLayout()
        self.story_buttons = QWidget()
        self.story_buttons.setLayout(self.button_row)
        self.buttons = {}
        for key, label, callback in [("actor", "+ Actor", self.add_actor), ("conversation", "+ Conversación", self.add_conversation),
            ("event", "+ Evento", self.add_event), ("flag", "+ Flag", self.add_flag),
            ("node", "+ Nodo", self.add_node), ("line", "+ Línea", self.add_line), ("answer", "+ Respuesta", self.add_answer),
            ("condition", "+ Condición", self.add_condition), ("action", "+ Acción", self.add_event_action),
            ("up", "Subir", lambda: self.move_selected(-1)), ("down", "Bajar", lambda: self.move_selected(1)),
            ("delete", "Eliminar", self.delete_selected)]:
            button = QPushButton(label)
            button.setObjectName("add_" + key if key not in {"up", "down", "delete"} else key)
            button.clicked.connect(lambda checked=False, cb=callback: self.guard(cb))
            self.buttons[key] = button
            self.button_row.addWidget(button)
        self.button_row.addStretch()
        header_layout.addWidget(self.story_buttons)
        self.content = QTreeWidget()
        self.content.setObjectName("content_tree")
        self.content.setHeaderLabels(["Elemento", "Contenido"])
        self.content.setAlternatingRowColors(True)
        self.content.setColumnWidth(0, 220)
        self.content.header().setStretchLastSection(True)
        self.content.itemSelectionChanged.connect(self.content_selected)
        self.center_tabs = QTabWidget()
        self.center_tabs.setObjectName('editor_modes')
        from .viewport import SpatialPanel
        self.spatial = SpatialPanel(self)
        self.center_tabs.addTab(self.spatial, 'Espacio 3D')
        story = QWidget()
        story_layout = QVBoxLayout(story)
        story_layout.setContentsMargins(0, 0, 0, 0)
        story_layout.addWidget(self.story_header)
        story_layout.addWidget(self.content, 1)
        self.browser = ResourceBrowser(self.backend)
        self.browser.chosen.connect(self.resource_chosen)
        story_layout.addWidget(self.browser, 1)
        self.center_tabs.addTab(story, 'Historia / Recursos')
        # Existing offscreen tests exercise editing, without requesting a GL context.
        from PySide6.QtWidgets import QApplication
        self.center_tabs.setCurrentIndex(1 if QApplication.platformName() == 'offscreen' else 0)
        self.center_tabs.currentChanged.connect(self.mode_changed)
        center_layout.addWidget(self.center_tabs, 1)
        self.splitter.addWidget(center)
        self.properties = QScrollArea()
        self.properties.setWidgetResizable(True)
        self.properties.setMinimumWidth(340)
        self.properties.setObjectName("properties_panel")
        self.splitter.addWidget(self.properties)
        self.splitter.setSizes([220, 740, 410])
        self.nav.itemSelectionChanged.connect(self.nav_selected)
        self.nav.itemClicked.connect(lambda *unused: self.nav_selected())
        self.nav.itemChanged.connect(self.visibility_changed)
        self.nav.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.nav.customContextMenuRequested.connect(self.context_references)
        dock = QDockWidget("Problems / Build", self)
        dock.setObjectName("build_dock")
        tabs = QTabWidget()
        self.problem_table = QTableWidget(0, 2)
        self.problem_table.setObjectName("problems_table")
        self.problem_table.setHorizontalHeaderLabels(["Estado", "Descripción"])
        self.problem_table.verticalHeader().hide()
        self.problem_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.problem_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.problem_table.cellDoubleClicked.connect(self.problem_selected)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setObjectName("build_log")
        tabs.addTab(self.problem_table, "Problems")
        tabs.addTab(self.log, "Build / Log")
        self.reference_tree = QTreeWidget()
        self.reference_tree.setHeaderLabels(['Relación', 'Elemento'])
        self.reference_tree.setObjectName('references_tree')
        self.reference_tree.itemDoubleClicked.connect(lambda item, column: self.navigate_reference(item.data(0, ROLE)))
        tabs.addTab(self.reference_tree, 'Referencias')
        self.bottom_tabs = tabs
        dock.setWidget(tabs)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
        dock.setMinimumHeight(130)
        self.resizeDocks([dock], [170], Qt.Orientation.Vertical)

    def at(self, path):
        if path and path[0] == 'original' and len(path) == 2 and self.spatial.viewport and self.spatial.viewport.level:
            return self.spatial.viewport.level.references[path[1]]
        value = self.doc.data
        for key in path:
            value = value[key]
        return value

    def mode_changed(self, index):
        self.update_buttons()
        if index == 0:
            self.spatial.ensure_loaded()

    def set_value(self, path, value, optional=False):
        parent = self.at(path[:-1])
        if optional and value in (None, ""):
            parent.pop(path[-1], None)
        else:
            parent[path[-1]] = value
        self.changed()

    def changed(self, refresh=False):
        self.remember_change(refresh)
        self.spatial.sync()
        if self.center_tabs.currentIndex() == 0:
            self.spatial.ensure_loaded()
        self._title()
        self.validation_timer.start(250)
        if refresh:
            self.refresh()
        else:
            for path, item in self.nav_items.items():
                if len(path) > 1 and path[0] in {"actors", "objects", "conversations", "events", "triggers", "entries", "waypoints"}:
                    try:
                        value = self.at(path)
                        item.setText(0, value.get("name", value.get("id", f"Evento {path[1]+1}")))
                        item.setToolTip(0,item.text(0))
                    except (KeyError, IndexError):
                        pass
            for path, item in self.content_items.items():
                try:
                    label, detail = self.content_fields(path)
                    item.setText(0, label)
                    item.setText(1, detail)
                    item.setToolTip(0,label);item.setToolTip(1,detail)
                except (KeyError, IndexError):
                    pass

    def content_fields(self, path):
        value = self.at(path)
        if path == ("level",):
            return "Escenario", value.get("source") or "Elige un level original"
        if path[0] == "state" and len(path) == 3:
            return path[2], str(value)
        if path[0] == "conversations" and len(path) > 2:
            conv = self.doc.data["conversations"][path[1]]
            if path[-1] == "prompt":
                return "Línea inicial", value
            if path[-2] == "nodes":
                return value["id"] + (" · entrada" if value["id"] == conv.get("entry") else ""), ""
            if path[-2] == "lines":
                return "Línea · " + value.get("speaker", conv["speaker"]), value["text"]
            if path[-2] == "choices":
                prefix = "→ " if "nodes" in conv else ""
                return prefix + str(value.get("goto", "RETURN " + str(value.get("result", "?")))), value["text"]
        if path[0] == "events" and len(path) > 2:
            if path[-2] == "conditions":
                detail = value.get("flag", "") + (" activado" if value.get("is_set") else " desactivado")
                return f"SI {path[-1]+1}", detail
            if path[-2] == "actions":
                return f"HACER {path[-1]+1}", " · ".join(f"{ACTION_LABELS.get(k, k)}: {v}" for k, v in value.items())
        if len(path) == 2 and path[0] in {"actors", "objects", "conversations", "events", "triggers", "entries", "waypoints"}:
            label = value.get("name", value.get("id", f"Evento {path[1]+1}"))
            detail = value.get("template", value.get("speaker", TRIGGER_LABELS.get(value.get("when"), value.get("when", ""))))
            return label, detail
        labels = {"actors": "Actores", "objects": "Objetos", "conversations": "Conversaciones", "events": "Eventos", "triggers": "Triggers"}
        return labels.get(path[0], "Elemento"), str(len(value)) if isinstance(value, list) else ""

    def pending_properties(self):
        panel = self.properties.widget()
        controls = panel.findChildren(QLineEdit) if panel else []
        controls += self.campaign_panel.findChildren(QLineEdit)
        controls += self.project_resources_panel.findChildren(QLineEdit)
        controls += self.project_resources_panel.findChildren(QPlainTextEdit)
        return [control for control in controls if getattr(control, '_rcm_pending', False)]

    def commit_properties(self):
        for control in self.pending_properties():
            if not control._rcm_commit():
                return False
        return True

    def _title(self):
        name = self.doc.data.get("chronicle", {}).get("name", "Proyecto") if self.doc else "Sin proyecto"
        self.setWindowTitle(("* " if self.doc and (self.doc.modified or self.pending_properties()) else "") + name + " — Redemption Chronicle Maker")

    def refresh(self):
        if self.doc:
            try:self.backend.sync_resources(self.doc.snapshot())
            except (ValueError,OSError,KeyError,TypeError):self.backend.resources=self.backend.original_resources;self.backend.project_payload={};self.backend._resources_key=None
        else:self.backend.resources=self.backend.original_resources;self.backend.project_payload={};self.backend._resources_key=None
        if self.doc is not self.history_document:
            self.history_document = self.doc
            self.history = [self.doc.snapshot()] if self.doc else []
            self.redo_history = []
        self.update_history_actions()
        self.mode_changed(self.center_tabs.currentIndex())
        self.nav.blockSignals(True)
        self.nav.clear()
        self.nav_items = {}
        def add(label, path, parent=None):
            item = QTreeWidgetItem(parent or self.nav, [label])
            item.setToolTip(0,label)
            item.setData(0, ROLE, path)
            self.nav_items[path] = item
            if path[0] in {'actors', 'objects', 'triggers', 'entries', 'waypoints', 'original', 'geometry'}:
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(0, Qt.CheckState.Unchecked if self.spatial.viewport and path in self.spatial.viewport.hidden else Qt.CheckState.Checked)
            return item
        add("Crónica", ("chronicle",))
        add("Level base", ("level",))
        add('Geometría original · sólo lectura', ('geometry',))
        original = add('Referencias originales · sólo lectura', ('original',))
        if self.spatial.viewport and self.spatial.viewport.level:
            for i, e in enumerate(self.spatial.viewport.level.references):
                add(e['template'] + ' · ' + str(e.get('sector', '?')), ('original', i), original)
        for key, label in [("actors", "Actores"), ("objects", "Objetos"), ("entries", "Entradas"), ("waypoints", "Waypoints"), ("triggers", "Triggers"), ("conversations", "Conversaciones"), ("events", "Eventos")]:
            parent = add(label, (key,))
            if self.doc:
                for i, item in enumerate(self.doc.data.get(key, [])):
                    add(item.get("name", item.get("id", f"Evento {i+1}")), (key, i), parent)
            parent.setExpanded(True)
        parent = add("Chronicle Flags", ("state", "flags"))
        if self.doc:
            for alias in self.doc.data.get("state", {}).get("flags", {}):
                add(alias, ("state", "flags", alias), parent)
        parent.setExpanded(True)
        add("Recursos originales", ("resources",))
        nav_path = self.selection[:2] if self.selection[0] in {"actors", "objects", "conversations", "events", "triggers", "entries", "waypoints", "original"} else self.selection
        self.nav.setCurrentItem(self.nav_items.get(nav_path, self.nav_items[("chronicle",)]))
        self.nav.blockSignals(False)
        for key in ["save", "save_as", "validate", "build"]:
            self.actions[key].setEnabled(self.doc is not None and not self.busy)
        self._title()
        self.render_content()
        self.guide_panel.refresh()
        self.inspect()
        self.spatial.sync()
        self.campaign_panel.refresh()
        self.project_resources_panel.refresh()
        self.debug_panel.refresh()
        if self.center_tabs.currentIndex() == 0:
            self.spatial.ensure_loaded()

    def update_history_actions(self):
        self.actions['undo'].setEnabled(not self.busy and len(self.history)>1)
        self.actions['redo'].setEnabled(not self.busy and bool(self.redo_history))

    def remember_change(self, discrete=False):
        if not self.doc or self.doc is not self.history_document:
            return
        snapshot = self.doc.snapshot()
        if self.history and snapshot == self.history[-1]:
            return
        now = time.monotonic()
        if not discrete and len(self.history)>1 and self.history_path==self.selection and now-self.history_time<.4:
            self.history[-1] = snapshot
        else:
            self.history.append(snapshot)
            self.history = self.history[-40:]
        # Creation/deletion/rename snapshots must not be merged with a later
        # numeric edit merely because it occurs on the same selected entity.
        self.history_time, self.history_path = (0 if discrete else now), self.selection
        self.redo_history.clear()
        self.update_history_actions()

    def undo_project(self):
        if not self.busy and self.doc and self.commit_properties() and len(self.history)>1:
            self.redo_history.append(self.history.pop())
            import copy
            self.doc.data = copy.deepcopy(self.history[-1])
            self.selection = ('chronicle',)
            self.history_time = 0
            self.refresh()
            self.validate_project()

    def redo_project(self):
        if not self.busy and self.doc and self.redo_history:
            import copy
            snapshot = self.redo_history.pop()
            self.history.append(snapshot)
            self.doc.data = copy.deepcopy(snapshot)
            self.selection = ('chronicle',)
            self.history_time = 0
            self.refresh()
            self.validate_project()

    def nav_selected(self):
        item = self.nav.currentItem()
        if item:
            self.select(tuple(item.data(0, ROLE)))

    def content_selected(self):
        item = self.content.currentItem()
        if item and item.data(0, ROLE):
            self.select(tuple(item.data(0, ROLE)), False)

    def focus_player_start(self):
        if not self.doc or not hasattr(self.doc,'campaign'):
            self.statusBar().showMessage('Esta crónica usa la entrada original del mapa; no tiene un inicio propio colocado.',8000);return
        root=self.doc.campaign
        si=next(i for i,row in enumerate(root['scenes']) if row['id']==root['entry'])
        scene=root['scenes'][si]
        ei=next((i for i,row in enumerate(scene.get('entries',[])) if row['id']==scene.get('default_entry')),-1)
        if ei<0:
            self.statusBar().showMessage('La escena inicial usa la entrada original 0. Crea una entrada y elígela como llegada por defecto para colocar un inicio propio.',10000);return
        if not self.commit_properties():return
        self.doc.active=si;self.selection=('entries',ei);self.refresh();self.select(('entries',ei));self.center_tabs.setCurrentIndex(0)
        viewport=self.spatial.viewport
        if viewport and self.spatial.geometry_matches():viewport.focus_selection()
        else:self.spatial.pending_start_focus=True
        self.statusBar().showMessage('Inicio del jugador: '+scene['entries'][ei]['name']+' · edita XYZ/orientación o arrastra el marcador en 3D.',10000)

    def select(self, path, render=True):
        self.selection = tuple(path)
        nav_path = self.selection[:2] if self.selection[0] in {'actors','objects','triggers','entries','waypoints','events','conversations','original'} else self.selection
        item = self.nav_items.get(nav_path)
        if item:
            self.nav.blockSignals(True)
            self.nav.setCurrentItem(item)
            self.nav.blockSignals(False)
        if render:
            self.render_content()
        else:
            self.update_buttons()
        self.inspect()
        if self.selection[0] in {'conversations', 'events', 'state', 'resources'}:
            self.center_tabs.setCurrentIndex(1)
        self.spatial.sync()

    def render_content(self):
        path = self.selection
        resources = path[0] == "resources"
        self.browser.setVisible(resources)
        self.content.setVisible(not resources)
        self.content.blockSignals(True)
        self.content.clear()
        self.content_items = {}
        titles = {"chronicle": "Tu crónica", "level": "Escenario base", "actors": "Actores", "objects": "Objetos",
                  "conversations": "Conversaciones", "events": "Eventos", "state": "Chronicle Flags", "resources": "Recursos originales"}
        self.heading.setText(titles.get(path[0], "Proyecto"))
        self.subtitle.setText("Crea una crónica o abre un proyecto para empezar." if not self.doc else "Selecciona un elemento y edita sus propiedades a la derecha.")
        def add(target, parent=None):
            label, detail = self.content_fields(target)
            item = QTreeWidgetItem(parent or self.content, [label, detail])
            item.setToolTip(0,label); item.setToolTip(1,detail)
            item.setData(0, ROLE, target)
            self.content_items[target] = item
            return item
        if self.doc:
            data = self.doc.data
            if path[0] == "conversations" and len(path) > 1:
                conv = data["conversations"][path[1]]
                self.heading.setText(conv["id"])
                if "nodes" in conv:
                    for ni, node in enumerate(conv["nodes"]):
                        node_path = ("conversations", path[1], "nodes", ni)
                        parent = add(node_path)
                        for li in range(len(node["lines"])):
                            add(node_path + ("lines", li), parent)
                        for ai in range(len(node["choices"])):
                            add(node_path + ("choices", ai), parent)
                        parent.setExpanded(True)
                else:
                    add(("conversations", path[1], "prompt"))
                    for ai in range(len(conv["choices"])):
                        add(("conversations", path[1], "choices", ai))
                    self.subtitle.setText("Conversación de Fase 1. Añadir un nodo la convierte al modelo ramificado conservando sus respuestas.")
            elif path[0] == "events" and len(path) > 1:
                event = data["events"][path[1]]
                self.heading.setText(event.get("id", f"Evento {path[1]+1}"))
                self.subtitle.setText("Deben cumplirse todas las condiciones. Los cambios de estado preceden al inicio de conversaciones y a la creación diferida de actores.")
                for key in ["conditions", "actions"]:
                    for i in range(len(event.get(key, []))):
                        add(("events", path[1], key, i))
            elif path[0] in {"actors", "objects", "conversations", "events", "triggers", "entries", "waypoints"}:
                for i in range(len(data.get(path[0], []))):
                    add((path[0], i))
            elif path[0] == "state":
                for alias in data.get("state", {}).get("flags", {}):
                    add(("state", "flags", alias))
            elif path[0] in {"chronicle", "level"}:
                add(("level",))
                for key in ["actors", "conversations", "events"]:
                    add((key,))
                self.subtitle.setText("Define el escenario, añade personajes y escribe tu historia. Valida antes de compilar.")
            selected = self.content_items.get(path)
            if selected:
                self.content.setCurrentItem(selected)
        self.content.blockSignals(False)
        self.update_buttons()

    def update_buttons(self):
        p = self.selection
        shown = set()
        if self.doc and p[0] != "resources":
            if p[0] in {"chronicle", "level"}:
                shown = {"actor", "conversation", "event", "flag"}
            elif p[0] in {"actors", "objects"}:
                shown = {"actor"}
            elif p[0] == "conversations":
                shown = {"conversation"} if len(p) == 1 else {"node", "line", "answer"}
            elif p[0] == "events":
                shown = {"event"} if len(p) == 1 else {"condition", "action"}
            elif p[0] == "state":
                shown = {"flag"}
            if (p[0] in {"actors", "objects", "conversations", "events", "triggers", "entries", "waypoints"} and len(p) > 1) or (p[0] == "state" and len(p) == 3):
                shown.add("delete")
            if (len(p) >= 4 or p[0] == "events" and len(p) == 2) and isinstance(p[-1], int):
                shown.update(("up", "down"))
        if self.center_tabs.currentIndex()==2: shown=set()
        for key, button in self.buttons.items():
            button.setVisible(key in shown)
            button.setEnabled(not self.busy)

    def inspect(self):
        from .inspector import Inspector
        old = self.properties.takeWidget()
        if old:
            old.deleteLater()
        self.properties.setWidget(Inspector(self))

    def guard(self, operation):
        try:
            return operation()
        except Exception as error:
            try:self.backend.ws.write("build/editor/last_error.log", traceback.format_exc())
            except (OSError,ValueError):pass  # Still show the original failure if the disk is unavailable.
            QMessageBox.warning(self, "Revisa la operación", str(error) if isinstance(error, (ValueError, OSError)) else "No se pudo realizar la operación. Revisa los datos del proyecto.")
            return False

    def can_leave(self):
        if self.busy:
            QMessageBox.information(self, "Build en curso", "Espera a que termine la compilación.")
            return False
        if self.doc and (self.doc.modified or self.pending_properties()):
            choice = QMessageBox.question(self, "Cambios sin guardar", "¿Guardar los cambios antes de continuar?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save)
            if choice == QMessageBox.StandardButton.Cancel:
                return False
            if choice == QMessageBox.StandardButton.Save:
                return bool(self.save_project())
            if choice == QMessageBox.StandardButton.Discard:
                for control in self.pending_properties():
                    control._rcm_pending = False
                self.inspect()
        return True

    def new_project(self):
        if not self.can_leave():
            return
        dialog = NewProjectDialog(self.backend.ws, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.guard(lambda: self.create_project(dialog))

    def create_project(self, dialog):
        from ..campaign_document import CampaignDocument
        self.doc = CampaignDocument.new(self.backend.ws, dialog.pid.text(), dialog.name.text(), dialog.directory.text(), dialog.description.toPlainText())
        self.selection = ("chronicle",)
        self.refresh()
        self.validate_project()

    def open_project(self):
        if not self.can_leave():
            return
        path, _ = QFileDialog.getOpenFileName(self, "Abrir crónica", str(self.backend.ws.root / "chronicles"), "Proyectos YAML (*.yaml *.yml)")
        if path:
            self.guard(lambda: self.open_path(path))

    def open_path(self, path):
        document = Document.load(self.backend.ws, path)
        if document.recovery_path.exists():
            choice = QMessageBox.question(self, "Recuperación disponible", "Hay una copia de recuperación. ¿Quieres recuperar sus cambios?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if choice == QMessageBox.StandardButton.Yes:
                document.recover()
        self.doc = document
        self.selection = ("chronicle",)
        self.refresh()
        self.validate_project()

    def save_project(self):
        if not self.doc or not self.commit_properties():
            return False
        def save():
            self.doc.save()
            self._title()
            self.statusBar().showMessage("Proyecto guardado", 4000)
            return True
        return self.guard(save)

    def save_as(self):
        if not self.doc or not self.commit_properties():
            return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar crónica como", str(self.doc.path), "Proyectos YAML (*.yaml)")
        if path:
            self.guard(lambda: self.doc.save(path))
            self._title()

    def autosave(self):
        if self.doc and self.doc.modified and not self.busy:
            try:
                self.doc.autosave()
                self.statusBar().showMessage("Copia de recuperación actualizada", 2000)
            except (OSError, ValueError) as error:
                self.log.appendPlainText("No se pudo guardar recuperación: " + str(error))

    def choose_level(self):
        if not self.doc or self.busy:
            return
        dialog = ResourceDialog(self.backend, "levels", self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.doc.data["level"]["source"] = dialog.selection
            self.doc.data['level'].pop('environment_scene', None)
            self.selection = ("level",)
            self.changed(True)

    def choose_template(self, path):
        dialog = ResourceDialog(self.backend, "actors" if path[0] == "actors" else "items", self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.set_value(path + ("template",), dialog.selection)
            self.inspect()

    def resource_chosen(self, kind, ident):
        if not self.doc:
            self.statusBar().showMessage("Crea o abre un proyecto para usar el recurso.", 4000)
            return
        if kind == "levels":
            self.doc.data["level"]["source"] = ident
            self.doc.data['level'].pop('environment_scene', None)
            self.selection = ("level",)
            self.changed(True)
        elif kind == "actors":
            self.spatial.begin_place('actors', ident) if self.spatial.viewport else self.add_actor(template=ident)
        elif kind == 'items' and self.spatial.viewport:
            candidates = [t for t in self.backend.resources['templates'] if t['id'] == ident and t['kind'] in {'items', 'props', 'weapons', 'armour'}]
            if len(candidates) == 1:
                self.spatial.begin_place('objects', ident)

    def add_actor(self, checked=False, template=""):
        if not self.doc or self.busy:
            return
        if not template:
            dialog = ResourceDialog(self.backend, 'actors', self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            template = dialog.selection
            if not template:
                return
            if self.spatial.viewport and self.center_tabs.currentIndex() == 0:
                self.spatial.begin_place('actors', template)
                return
        matches = [r for r in self.backend.resources['templates'] if r['id'] == template and r['kind'] == 'actors']
        if len(matches) != 1:
            raise ValueError('Elige una plantilla de actor única del catálogo.')
        data = self.doc.data
        ident = self.doc.unique_id("actors", "actor")
        actor = {"id": ident, "name": "Nuevo personaje", "template": template,
                 "transform": {"placement": "near_player", "orientation": [0, 0, 0]}}
        data["actors"].append(actor)
        event = next((e for e in data["events"] if e["when"] == "scene_start" and not e.get("conditions")), None)
        if event is None:
            event = {"id": self.doc.unique_id("events", "event"), "when": "scene_start", "actions": []}
            data["events"].append(event)
        event["actions"].append({"spawn": ident})
        self.selection = ("actors", len(data["actors"])-1)
        self.changed(True)

    def add_spatial_entity(self, kind, template, position):
        data = self.doc.data
        if kind in ('entries','waypoints'):
            ident=self.doc.unique_id(kind,'entry' if kind=='entries' else 'point')
            rows=data.setdefault(kind,[])
            rows.append(dict(id=ident,name='Nueva entrada' if kind=='entries' else 'Nuevo waypoint',transform=dict(placement='absolute',position=list(position),orientation=[0,0,0])))
            if kind=='entries':self.doc.campaign['scenes'][self.doc.active].setdefault('default_entry',ident)
            self.selection=(kind,len(rows)-1);self.changed(True);return
        ident = self.doc.unique_id(kind, 'actor' if kind == 'actors' else 'object')
        data.setdefault(kind, []).append(dict(id=ident, name=template, template=template,
            transform=dict(placement='absolute', position=position, orientation=[0, 0, 0])))
        event = next((e for e in data['events'] if e['when'] == 'scene_start' and not e.get('conditions')), None)
        if event is None:
            event = dict(id=self.doc.unique_id('events', 'event'), when='scene_start', actions=[])
            data['events'].append(event)
        event['actions'].append({'spawn': ident})
        self.selection = (kind, len(data[kind])-1)
        # Models are optional. Their loading happens on demand in a worker,
        # never in a frame or while moving an entity.
        self.changed(True)
        if self.spatial.viewport and template not in self.spatial.viewport.level.models:
            self.spatial.loaded_name = None
            self.spatial.ensure_loaded()

    def visibility_changed(self, item, column):
        path = item.data(0, ROLE)
        viewport = self.spatial.viewport
        if viewport and path and path[0] in {'actors', 'objects', 'triggers', 'entries', 'waypoints', 'original', 'geometry'}:
            if item.checkState(0) == Qt.CheckState.Unchecked:
                viewport.hidden.add(tuple(path))
            else:
                viewport.hidden.discard(tuple(path))
            viewport.update()

    def context_references(self, position):
        item = self.nav.itemAt(position)
        if not item:
            return
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.addAction('Find References / Buscar referencias', lambda: self.find_references(tuple(item.data(0, ROLE))))
        menu.exec(self.nav.mapToGlobal(position))

    def reference_label(self, path):
        try:
            if hasattr(self.doc, 'campaign') and path[0] in {'scenes', 'quests'}:
                value = self.doc.campaign
                for key in path: value = value[key]
                return value.get('title', value.get('name', value.get('id', str(path))))
            value = self.at(path)
            return value.get('name', value.get('id', str(path))) if isinstance(value, dict) else str(path[-1])
        except (KeyError, IndexError):
            return str(path)

    def find_references(self, path=None):
        if not self.doc:
            return
        from ..spatial.relations import references
        path = tuple(path or self.selection)
        if path[0] in {'actors','objects','triggers','entries','waypoints','conversations','events'}:
            path = path[:2]
        if hasattr(self.doc, 'campaign'):
            from ..campaign_relations import graph
            if path[0] not in {'state', 'scenes', 'quests'}: path = ('scenes', self.doc.active) + path
            links = graph(self.doc.campaign)
            incoming, outgoing = [x for x in links if x.target == path], [x for x in links if x.source == path]
        else:
            incoming, outgoing = references(self.doc.data, path)
        self.reference_tree.clear()
        for label, links, attr in [('USED BY / Referenciado por', incoming, 'source'), ('AFFECTS / Referencia a', outgoing, 'target')]:
            parent = QTreeWidgetItem(self.reference_tree, [label, ''])
            for link in links:
                target = getattr(link, attr)
                item = QTreeWidgetItem(parent, [link.label, self.reference_label(target)])
                item.setData(0, ROLE, link.detail if attr == 'source' and link.source[0] in {'events', 'conversations'} else target)
            parent.setExpanded(True)
        self.bottom_tabs.setCurrentIndex(2)

    def navigate_reference(self, path):
        if path:
            if path[0] in {'scenes', 'quests'}:
                self.campaign_panel.navigate(path)
                return
            # Detailed reference paths end at records, never scalar fields.
            if path[-1] in {'speaker', 'trigger', 'actor', 'conversation'}:
                path = path[:-1]
            self.select(tuple(path))

    def add_conversation(self):
        if not self.doc or self.busy:
            return
        actors = self.doc.data["actors"]
        speaker = actors[0]["id"] if actors else ""
        if self.selection[0]=='actors' and len(self.selection)>1 and self.selection[1]<len(actors):speaker=actors[self.selection[1]]['id']
        conv = {"id": self.doc.unique_id("conversations", "conv"), "speaker": speaker, "entry": "opening",
                "nodes": [{"id": "opening", "lines": [{"speaker": speaker, "text": "Escribe el diálogo."}],
                           "choices": [{"text": "Continuar.", "result": 1}, {"text": "Me voy.", "result": 2}]}]}
        if hasattr(self.doc,'campaign') and self.doc.campaign.get('project_format')==9:
            from ..camera_presets import DEFAULT_DIALOGUE_CAMERA
            conv['camera']=DEFAULT_DIALOGUE_CAMERA
        self.doc.data["conversations"].append(conv)
        self.selection = ("conversations", len(self.doc.data["conversations"])-1)
        self.changed(True)

    def graph_conversation(self):
        if not self.doc or self.selection[0] != "conversations" or len(self.selection) < 2:
            return None
        conv = self.doc.data["conversations"][self.selection[1]]
        if "nodes" not in conv:
            conv["entry"] = "opening"
            conv["nodes"] = [{"id": "opening", "lines": [{"speaker": conv["speaker"], "text": conv.pop("prompt")}], "choices": conv.pop("choices")}]
        return conv

    def selected_node_index(self, conv):
        p = self.selection
        return p[3] if len(p) >= 4 and p[2] == "nodes" else next((i for i, n in enumerate(conv["nodes"]) if n["id"] == conv["entry"]), 0)

    def next_result(self, conv):
        values = {a.get("result") for n in conv["nodes"] for a in n["choices"]}
        result = 1
        while result in values:
            result += 1
        return result

    def add_node(self):
        conv = self.graph_conversation()
        if conv is None:
            return
        ids = {n["id"] for n in conv["nodes"]}
        i = 1
        while "node" + str(i) in ids:
            i += 1
        conv["nodes"].append({"id": "node"+str(i), "lines": [{"speaker": conv["speaker"], "text": "Escribe el diálogo."}],
                              "choices": [{"text": "Terminar.", "result": self.next_result(conv)}]})
        self.selection = self.selection[:2] + ("nodes", len(conv["nodes"])-1)
        self.changed(True)

    def add_line(self):
        conv = self.graph_conversation()
        if conv is None:
            return
        ni = self.selected_node_index(conv)
        lines = conv["nodes"][ni]["lines"]
        lines.append({"speaker": conv["speaker"], "text": "Nueva línea."})
        self.selection = self.selection[:2] + ("nodes", ni, "lines", len(lines)-1)
        self.changed(True)

    def add_answer(self):
        conv = self.graph_conversation()
        if conv is None:
            return
        ni = self.selected_node_index(conv)
        answers = conv["nodes"][ni]["choices"]
        answers.append({"text": "Nueva respuesta.", "result": self.next_result(conv)})
        self.selection = self.selection[:2] + ("nodes", ni, "choices", len(answers)-1)
        self.changed(True)

    def add_event(self):
        if not self.doc or self.busy:
            return
        self.doc.data["events"].append({"id": self.doc.unique_id("events", "event"), "when": "scene_start", "actions": []})
        self.selection = ("events", len(self.doc.data["events"])-1)
        self.changed(True)

    def add_condition(self):
        if not self.doc or self.selection[0] != "events" or len(self.selection) < 2:
            return
        flags = self.doc.data.get("state", {}).get("flags", {})
        conditions = self.at(self.selection[:2]).setdefault("conditions", [])
        conditions.append({"flag": next(iter(flags), ""), "is_set": True})
        self.selection = self.selection[:2] + ("conditions", len(conditions)-1)
        self.changed(True)

    def add_event_action(self):
        if not self.doc or self.selection[0] != "events" or len(self.selection) < 2:
            return
        event = self.at(self.selection[:2])
        if event["when"] == "actor_clicked":
            action = {"start_conversation": next((c["id"] for c in self.doc.data["conversations"] if c["speaker"] == event.get("actor")), "")}
        elif event["when"] == "conversation_ended":
            action = {"set_flag": next(iter(self.doc.data.get("state", {}).get("flags", {})), "")}
        else:
            spawned = {a.get("spawn") for e in self.doc.data["events"] for a in e["actions"]}
            action = {"spawn": next((a["id"] for a in self.doc.data["actors"] if a["id"] not in spawned), "")}
        event["actions"].append(action)
        self.selection = self.selection[:2] + ("actions", len(event["actions"])-1)
        self.changed(True)

    def add_flag(self):
        if not self.doc or self.busy:
            return
        flags = self.doc.data.setdefault("state", {}).setdefault("flags", {})
        i = 1
        while "flag"+str(i) in flags:
            i += 1
        available = next((v for v in range(256) if v not in flags.values()), None)
        if available is None:
            QMessageBox.warning(self, "Flags", "Se han agotado los índices admitidos por el backend actual.")
            return
        alias = "flag"+str(i)
        flags[alias] = available
        self.selection = ("state", "flags", alias)
        self.changed(True)

    def register_delete_shortcut(self, widget, callback):
        shortcut = QShortcut('Delete', widget)
        shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        shortcut.setAutoRepeat(False)
        shortcut.activated.connect(lambda: self.guard(callback))
        self.delete_shortcuts.append(shortcut)

    def delete_selected(self):
        if not self.doc or self.busy:
            return
        p = self.selection
        if p[0] in {'original', 'geometry', 'level', 'chronicle'}:
            return
        if len(p) < 2 or p in {("state", "flags")}:
            return
        if not self.commit_properties():return
        from ..safe_edit import delete_candidate
        path=('scenes',self.doc.active)+p if hasattr(self.doc,'campaign') and p[0]!='state' else p
        try:candidate=delete_candidate(self.doc,path,self.backend,remove_spawns=True)
        except ValueError as error:
            QMessageBox.warning(self,'Elemento referenciado',str(error));return
        extra = "\nTambién se retirarán sus acciones de aparición." if p[0] in {'actors', 'objects'} else ""
        if QMessageBox.question(self, "Eliminar elemento", "¿Eliminar este elemento?" + extra + "\nPuedes deshacer esta operación.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        self.doc.data=candidate
        self.selection = p[:2] if len(p) > 2 and p[0] in {"conversations", "events"} else (("state", "flags") if p[0] == "state" else p[:1])
        self.changed(True)

    def move_selected(self, delta):
        p = self.selection
        if not self.doc or not isinstance(p[-1], int) or (len(p) < 4 and not (p[0] == "events" and len(p) == 2)):
            return
        items = self.at(p[:-1])
        target = p[-1] + delta
        if 0 <= target < len(items):
            items[p[-1]], items[target] = items[target], items[p[-1]]
            self.selection = p[:-1] + (target,)
            self.changed(True)

    def validate_project(self):
        if not self.doc:
            return None
        validation = self.backend.validate(self.doc.snapshot())
        self.problem_table.setRowCount(len(validation.problems))
        dark = self.palette().color(QPalette.ColorRole.Base).lightnessF() < .5
        severity_colors = {'ERROR': '#ff8c96' if dark else '#a40016', 'WARNING': '#f1c56c' if dark else '#825300', 'INFO': '#91c7ff' if dark else '#17527d'}
        for i, problem in enumerate(validation.problems):
            level = QTableWidgetItem(problem.severity)
            level.setData(ROLE, problem.path)
            level.setForeground(QColor(severity_colors.get(problem.severity, severity_colors['INFO'])))
            self.problem_table.setItem(i, 0, level)
            self.problem_table.setItem(i, 1, QTableWidgetItem(problem.message))
        self.statusBar().showMessage("Proyecto válido" if validation.valid else "Hay errores por corregir")
        return validation

    def validate_from_ui(self):
        if self.doc and self.commit_properties():
            return self.validate_project()

    def problem_selected(self, row, column):
        path = self.problem_table.item(row, 0).data(ROLE)
        if path and path[0] in {'scenes','quests'}:
            self.campaign_panel.navigate(path)
            return
        if path:
            self.select(tuple(path))

    def build_project(self):
        if not self.doc or self.busy or not self.commit_properties():
            return
        validation = self.validate_project()
        if not validation.valid:
            from ..build_transaction import failed_report
            failed_report(self.backend.ws,self.doc.snapshot(),'Validación fallida desde el editor')
            self.last_build=None
            self.bottom_tabs.setCurrentIndex(0)
            return
        if not self.save_project():
            return
        self.busy = True
        self.splitter.setEnabled(False)
        for action in self.actions.values():
            action.setEnabled(False)
        self.log.clear()
        self.bottom_tabs.setCurrentIndex(1)
        self.thread = QThread(self)
        self.worker = BuildWorker(self.backend, self.doc.snapshot())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.log.appendPlainText)
        self.worker.succeeded.connect(self.build_succeeded)
        self.worker.failed.connect(self.build_failed)
        self.worker.completed.connect(self.thread.quit)
        self.worker.completed.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.build_finished)
        self.thread.start()

    def build_succeeded(self, report):
        self.last_build = report
        path = self.backend.ws.root / "build" / report["chronicle"]
        self.log.appendPlainText(f"Build successful\n{path}\nPreparado para probar en Redemption; este build no instala ni ejecuta el juego.")
        if report.get('save_warning'):self.log.appendPlainText(report['save_warning'])
        self.build_completed.emit(report)

    def build_failed(self, message, diagnostic):
        try:self.backend.ws.write("build/editor/build_error.log", diagnostic)
        except (OSError,ValueError):pass
        self.log.appendPlainText("Build falló: " + message + "\nDetalle disponible en build/editor/build_error.log")
        self.build_completed.emit({"status": "failed", "reason": message})

    def build_finished(self):
        self.busy = False
        self.splitter.setEnabled(True)
        for action in self.actions.values():
            action.setEnabled(True)
        self.thread.deleteLater()
        self.refresh()

    def closeEvent(self, event):
        if self.spatial.loading:
            self.statusBar().showMessage('Terminando la carga del escenario antes de cerrar…')
            QTimer.singleShot(150, self.close)
            event.ignore()
            return
        if self.can_leave():
            self.autosave_timer.stop()
            event.accept()
        else:
            event.ignore()
