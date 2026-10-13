from .i18n import tr, diagnostic
from pathlib import Path
import traceback
import time

from PySide6.QtCore import Qt, QTimer, QThread, QObject, Signal, Slot
from PySide6.QtGui import QAction, QShortcut, QPalette, QColor
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QScrollArea, QDockWidget,
    QTabWidget, QPlainTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMenu,QComboBox)

from ..document import Document
from ..model import identifier
from .browser import ResourceBrowser, ResourceDialog

ROLE = Qt.ItemDataRole.UserRole
ACTION_LABELS = {"spawn": tr("Crear"), "start_conversation": tr("Iniciar conversación"), "set_flag": tr("Activar flag"), "clear_flag": tr("Desactivar flag")}
TRIGGER_LABELS = {"scene_start": tr("Inicia la escena"), "actor_clicked": tr("Hablan con un actor"), "conversation_ended": tr("Termina una conversación"), "trigger_enter": tr("Un jugador entra en el volumen")}


class NewProjectDialog(QDialog):
    def __init__(self, workspace, parent=None):
        super().__init__(parent)
        self.ws = workspace
        self.setWindowTitle(tr("Nueva crónica"))
        self.resize(640, 350)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.pid = QLineEdit("new_chronicle")
        self.pid.setObjectName("new_id")
        self.pid.setMaxLength(14)
        self.name = QLineEdit(tr("Mi nueva crónica"))
        self.name.setObjectName("new_name")
        self.description = QPlainTextEdit()
        self.description.setObjectName("new_description")
        self.description.setMaximumHeight(90)
        self.directory = QLineEdit(str(workspace.output("chronicles/new_chronicle")))
        self.directory.setObjectName("new_directory")
        self._auto_directory=self.directory.text()
        def update_directory(text):
            path=str(workspace.output('chronicles')/text)
            if self.directory.text()==self._auto_directory:self.directory.setText(path)
            self._auto_directory=path
        self.pid.textChanged.connect(update_directory)
        path_row = QWidget()
        path_layout = QHBoxLayout(path_row)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.addWidget(self.directory, 1)
        browse = QPushButton(tr("Elegir…"))
        browse.clicked.connect(self.choose_directory)
        path_layout.addWidget(browse)
        form.addRow(tr("ID interno"), self.pid)
        form.addRow(tr("Nombre"), self.name)
        form.addRow(tr("Descripción"), self.description)
        form.addRow(tr("Directorio"), path_row)
        layout.addLayout(form)
        hint = QLabel(tr("El proyecto y sus builds se guardan dentro del workspace. Después elegirás el escenario."))
        hint.setWordWrap(True)
        layout.addWidget(hint)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText(tr("Crear proyecto"))
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancelar"))
        self.buttons.accepted.connect(self.check_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        # Normal creation asks for a name and a usable scenario first. Internal
        # ID and folder remain available for existing workflows and automation.
        from ..product import project_id
        def derive(value):
            if hasattr(self,'advanced') and self.advanced.isChecked():return
            self.pid.setText(project_id(value,self.ws.root))
        self.name.textChanged.connect(derive)
        self.level=QComboBox();self.level.setObjectName('new_level');self.level.addItem(tr('Elige un escenario…'),'')
        self.level.setEditable(True);self.level.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        if parent and hasattr(parent,'backend'):
            for ident in sorted(parent.backend.levels):
                if parent.backend.level_usable(ident):self.level.addItem(parent.backend.level_label(ident)+' · '+ident,ident)
        form.insertRow(0,tr('Escenario inicial'),self.level)
        # Keep advanced fields out of the primary path without discarding them.
        self.advanced=__import__('PySide6.QtWidgets',fromlist=['QCheckBox']).QCheckBox(tr('Opciones avanzadas'))
        form.addRow(self.advanced)
        for field in (self.pid,path_row):form.setRowVisible(field,False)
        self.advanced.toggled.connect(lambda checked:(form.setRowVisible(self.pid,checked),form.setRowVisible(path_row,checked)))
        hint.setText(tr('Elige el escenario antes de crear. Después coloca la entrada, añade un NPC y escribe su conversación.'))

    def choose_directory(self):
        path = QFileDialog.getExistingDirectory(self, tr("Directorio del proyecto"), str(self.ws.root / "chronicles"))
        if path:
            self.directory.setText(path)

    def check_accept(self):
        try:
            identifier(self.pid.text(), tr("ID de crónica"), 14)
            self.ws.output(self.directory.text())
            if not self.name.text().strip():
                raise ValueError(tr("Escribe un nombre para la crónica."))
            if not self.level.currentData():raise ValueError(tr('Elige un escenario inicial disponible.'))
            self.accept()
        except ValueError as error:
            QMessageBox.warning(self, tr("Revisa el proyecto"), diagnostic(error))


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
        self.center_tabs.addTab(self.campaign_panel, tr('Campaña / Misiones'))
        from .resource_panel import ProjectResourcesPanel
        self.project_resources_panel=ProjectResourcesPanel(self)
        self.center_tabs.addTab(self.project_resources_panel,tr('Recursos propios'))
        from .debug_panel import DebugPanel
        self.debug_panel=DebugPanel(self);self.center_tabs.addTab(self.debug_panel,tr('Prueba / Depuración'))
        from .graph_panel import GraphPanel
        self.graph_panel=GraphPanel(self);self.center_tabs.addTab(self.graph_panel,tr('Gráfico de historia'))
        from .guide_panel import GuidePanel
        self.guide_panel=GuidePanel(self);self.center_tabs.addTab(self.guide_panel,tr('Tutorial / Ayuda'))
        for widget, callback in [(self.nav, self.delete_selected), (self.content, self.delete_selected),
                                 (self.graph_panel.view, self.delete_selected),
                                 (self.campaign_panel.tree, self.campaign_panel.delete)]:
            self.register_delete_shortcut(widget, callback)
        campaign_menu = self.menuBar().addMenu(tr('Campaña'))
        self.campaign_menu=campaign_menu
        campaign_menu.addAction(tr('Crear campaña de varios mapas'), lambda: self.guard(self.campaign_panel.convert))
        campaign_menu.addAction(tr('Buscar en toda la crónica'), self.campaign_panel.focus_search, 'Ctrl+Shift+F')
        campaign_menu.addAction(tr('Comprobar integridad'), self.validate_from_ui)
        self.actions['redo'].setShortcuts(['Ctrl+Y', 'Ctrl+Shift+Z'])
        self.validation_timer = QTimer(self)
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.validate_project)
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setInterval(30000)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start()
        self.refresh()
        from .product_ui import install
        install(self)

    def choose_language(self, code):
        from .i18n import save_language, language
        try:
            save_language(self.backend.ws, code)
        except (ValueError, OSError) as error:
            self.language_actions[self.preferred_language].setChecked(True)
            QMessageBox.warning(self, tr('Revisa la operación'), diagnostic(error))
            return False
        self.preferred_language=code
        self.language_menu.setTitle(tr('Idioma (al reiniciar)') if code != language() else tr('Idioma'))
        if code != language():
            QMessageBox.information(self, tr('Idioma del editor'), tr('La preferencia se ha guardado. Cierra y vuelve a abrir el editor para aplicar el idioma. Tus proyectos no se traducen ni se modifican.'))
        return True

    def _actions(self):
        self.actions = {}
        toolbar = self.addToolBar(tr("Proyecto"))
        toolbar.setMovable(False)
        for key, label, shortcut, callback in [
            ("new", tr("Nueva crónica"), "Ctrl+N", self.new_project),
            ("open", tr("Abrir"), "Ctrl+O", self.open_project),
            ("save", tr("Guardar"), "Ctrl+S", self.save_project),
            ("save_as", tr("Guardar como…"), "Ctrl+Shift+S", self.save_as),
            ("validate", tr("Validar"), "Ctrl+Shift+V", self.validate_from_ui),
            ("build", tr('Construir'), "Ctrl+B", self.build_project)]:
            action = QAction(label, self)
            action.setShortcut(shortcut)
            action.setObjectName("action_" + key)
            action.triggered.connect(lambda checked=False, cb=callback: self.guard(cb))
            self.actions[key] = action
            if key != "save_as":
                toolbar.addAction(action)
        from .i18n import LANGUAGES, language
        from PySide6.QtGui import QActionGroup
        self.language_menu = QMenu(tr('Idioma'), self)
        self.language_menu.setObjectName('language_menu')
        self.language_group = QActionGroup(self)
        self.language_group.setExclusive(True)
        self.language_actions = {}
        self.preferred_language = language()
        for code, label in LANGUAGES.items():
            action = self.language_menu.addAction(label)
            action.setObjectName('language_' + code)
            action.setCheckable(True)
            action.setChecked(code == language())
            self.language_group.addAction(action)
            action.triggered.connect(lambda checked=False, code=code: self.choose_language(code))
            self.language_actions[code] = action
        file_menu = self.menuBar().addMenu(tr("Archivo"))
        self.file_menu=file_menu
        for key in ["new", "open", "save", "save_as"]:
            file_menu.addAction(self.actions[key])
        edit_menu = self.menuBar().addMenu(tr("Editar"))
        self.edit_menu=edit_menu
        for key, label, shortcut, callback in [('undo',tr('Deshacer'),'Ctrl+Z',self.undo_project),('redo',tr('Rehacer'),'Ctrl+Y',self.redo_project)]:
            action = QAction(label,self)
            action.setShortcut(shortcut)
            action.triggered.connect(lambda checked=False,cb=callback:self.guard(cb))
            self.actions[key] = action
            edit_menu.addAction(action)
        edit_menu = self.menuBar().addMenu(tr('Crónica'))
        self.chronicle_menu=edit_menu
        edit_menu.addAction(tr("Elegir level base…"), self.choose_level)
        edit_menu.addAction(tr("Añadir actor"), self.add_actor)
        edit_menu.addAction(tr("Nueva conversación"), self.add_conversation)
        edit_menu.addAction(tr("Nuevo evento"), self.add_event)
        edit_menu.addAction(tr("Nuevo flag"), self.add_flag)
        edit_menu.addAction(tr('Asistentes de crónica…'),lambda:self.guard(self.show_recipe))
        self.recipe_menu=edit_menu.addMenu(tr('Editar asistente'))
        def refresh_recipes():
            self.recipe_menu.clear()
            from ..recipes import recipes,missing
            if self.doc and hasattr(self.doc,'campaign'):
                for recipe in recipes(self.doc.campaign):
                    label=recipe['id']+(' · '+tr('Configuración incompleta') if missing(self.doc.campaign,recipe) else '')
                    self.recipe_menu.addAction(label,lambda checked=False,ident=recipe['id']:self.guard(lambda:self.show_recipe(recipe_id=ident)))
        self.recipe_menu.aboutToShow.connect(refresh_recipes)
        build_menu = self.menuBar().addMenu(tr('Construir'))
        self.build_menu=build_menu
        build_menu.addAction(self.actions["validate"])
        build_menu.addAction(self.actions["build"])
        help_menu = self.menuBar().addMenu(tr("Ayuda"))
        self.help_menu=help_menu
        help_menu.addAction(tr('Tutorial del proyecto'),self.open_project_guide)
        help_menu.addAction(tr("Guía del editor"), lambda:self.guard(self.open_editor_guide))
        from .package_panel import menu
        menu(self)
        help_menu.addAction(tr('Informe de diagnóstico'),lambda:self.guard(lambda:__import__('rcm.diagnostics',fromlist=['diagnostic_report']).diagnostic_report(self.backend.ws)))
        self.menuBar().addMenu(self.language_menu)

    def show_recipe(self,kind=None,recipe_id=None):
        from .recipe_wizard import open_wizard
        open_wizard(self,kind,recipe_id)

    def open_editor_guide(self):
        from .i18n import language
        import sys
        root=Path(sys.executable).parent if getattr(sys,'frozen',False) else self.backend.ws.root
        name='EDITOR_GUIDE.en.md' if language()=='en' else 'EDITOR_GUIDE.md'
        guide=root/'docs'/name
        self.guide_panel.text.setMarkdown(guide.read_text(encoding='utf8'))
        self.center_tabs.setCurrentWidget(self.guide_panel)

    def open_project_guide(self):
        self.guide_panel.current=object()
        self.guide_panel.refresh()
        self.center_tabs.setCurrentWidget(self.guide_panel)

    def _layout(self):
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)
        self.nav = QTreeWidget()
        self.nav.setHeaderLabel(tr("PROYECTO"))
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
        for key, label, callback in [("actor", tr("+ Actor"), self.add_actor), ("conversation", tr("+ Conversación"), self.add_conversation),
            ("event", tr("+ Evento"), self.add_event), ("flag", "+ Flag", self.add_flag),
            ("node", tr("+ Nodo"), self.add_node), ("line", tr("+ Línea"), self.add_line), ("answer", tr("+ Respuesta"), self.add_answer),
            ("condition", tr("+ Condición"), self.add_condition), ("action", tr("+ Acción"), self.add_event_action),
            ("up", tr("Subir"), lambda: self.move_selected(-1)), ("down", tr("Bajar"), lambda: self.move_selected(1)),
            ("delete", tr("Eliminar"), self.delete_selected)]:
            button = QPushButton(label)
            button.setObjectName("add_" + key if key not in {"up", "down", "delete"} else key)
            button.clicked.connect(lambda checked=False, cb=callback: self.guard(cb))
            self.buttons[key] = button
            self.button_row.addWidget(button)
        self.button_row.addStretch()
        header_layout.addWidget(self.story_buttons)
        self.content = QTreeWidget()
        self.content.setObjectName("content_tree")
        self.content.setHeaderLabels([tr("Elemento"), tr("Contenido")])
        self.content.setAlternatingRowColors(True)
        self.content.setColumnWidth(0, 220)
        self.content.header().setStretchLastSection(True)
        self.content.itemSelectionChanged.connect(self.content_selected)
        self.center_tabs = QTabWidget()
        self.center_tabs.setObjectName('editor_modes')
        from .viewport import SpatialPanel
        self.spatial = SpatialPanel(self)
        self.center_tabs.addTab(self.spatial, tr('Espacio 3D'))
        story = QWidget()
        story_layout = QVBoxLayout(story)
        story_layout.setContentsMargins(0, 0, 0, 0)
        story_layout.addWidget(self.story_header)
        story_layout.addWidget(self.content, 1)
        self.browser = ResourceBrowser(self.backend)
        self.browser.chosen.connect(self.resource_chosen)
        story_layout.addWidget(self.browser, 1)
        self.center_tabs.addTab(story, tr('Historia / Recursos'))
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
        dock = QDockWidget(tr('Problemas / Construcción'), self)
        self.build_dock=dock
        dock.setObjectName("build_dock")
        tabs = QTabWidget()
        self.problem_table = QTableWidget(0, 2)
        self.problem_table.setObjectName("problems_table")
        self.problem_table.setHorizontalHeaderLabels([tr("Estado"), tr("Descripción")])
        self.problem_table.verticalHeader().hide()
        self.problem_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.problem_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.problem_table.cellDoubleClicked.connect(self.problem_selected)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setObjectName("build_log")
        tabs.addTab(self.problem_table, tr('Problemas'))
        tabs.addTab(self.log, tr('Construcción / Registro'))
        self.reference_tree = QTreeWidget()
        self.reference_tree.setHeaderLabels([tr('Relación'), tr('Elemento')])
        self.reference_tree.setObjectName('references_tree')
        self.reference_tree.itemDoubleClicked.connect(lambda item, column: self.navigate_reference(item.data(0, ROLE)))
        tabs.addTab(self.reference_tree, tr('Referencias'))
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
                        item.setText(0, value.get("name", value.get("id", (tr('Evento ') + f'{path[1] + 1}'))))
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
            return tr("Escenario"), value.get("source") or tr("Elige un level original")
        if path[0] == "state" and len(path) == 3:
            return path[2], str(value)
        if path[0] == "conversations" and len(path) > 2:
            conv = self.doc.data["conversations"][path[1]]
            if path[-1] == "prompt":
                return tr("Línea inicial"), value
            if path[-2] == "nodes":
                return value["id"] + (tr(" · entrada") if value["id"] == conv.get("entry") else ""), ""
            if path[-2] == "lines":
                return tr("Línea · ") + value.get("speaker", conv["speaker"]), value["text"]
            if path[-2] == "choices":
                prefix = "→ " if "nodes" in conv else ""
                return prefix + str(value.get("goto", "RETURN " + str(value.get("result", "?")))), value["text"]
        if path[0] == "events" and len(path) > 2:
            if path[-2] == "conditions":
                detail = value.get("flag", "") + (tr(" activado") if value.get("is_set") else tr(" desactivado"))
                return (tr('SI ') + f'{path[-1] + 1}'), detail
            if path[-2] == "actions":
                if isinstance(value.get('show_note'),dict):return (tr('HACER ') + f'{path[-1] + 1}'), tr('Mostrar nota · ')+value['show_note'].get('title',tr('Sin título'))
                return (tr('HACER ') + f'{path[-1] + 1}'), tr(" · ").join((f'{ACTION_LABELS.get(k, k)}' + tr(': ') + f'{v}') for k, v in value.items())
        if len(path) == 2 and path[0] in {"actors", "objects", "conversations", "events", "triggers", "entries", "waypoints"}:
            label = value.get("name", value.get("id", (tr('Evento ') + f'{path[1] + 1}')))
            detail = value.get("template", value.get("speaker", TRIGGER_LABELS.get(value.get("when"), value.get("when", ""))))
            return label, detail
        labels = {"actors": tr("Actores"), "objects": tr("Objetos"), "conversations": tr("Conversaciones"), "events": tr("Eventos"), "triggers": "Triggers"}
        return labels.get(path[0], tr("Elemento")), str(len(value)) if isinstance(value, list) else ""

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
        name = self.doc.data.get("chronicle", {}).get("name", tr("Proyecto")) if self.doc else tr("Sin proyecto")
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
        add(tr("Crónica"), ("chronicle",))
        add(tr("Level base"), ("level",))
        add(tr('Geometría original · sólo lectura'), ('geometry',))
        original = add(tr('Referencias originales · sólo lectura'), ('original',))
        if self.spatial.viewport and self.spatial.viewport.level:
            for i, e in enumerate(self.spatial.viewport.level.references):
                add(e['template'] + tr(' · ') + str(e.get('sector', '?')), ('original', i), original)
        for key, label in [("actors", tr("Actores")), ("objects", tr("Objetos")), ("entries", tr("Entradas")), ("waypoints", tr('Puntos de recorrido')), ("triggers", tr('Zonas de activación')), ("conversations", tr("Conversaciones")), ("events", tr("Eventos"))]:
            parent = add(label, (key,))
            if self.doc:
                for i, item in enumerate(self.doc.data.get(key, [])):
                    add(item.get("name", item.get("id", (tr('Evento ') + f'{i + 1}'))), (key, i), parent)
            parent.setExpanded(True)
        parent = add(tr('Flags de crónica'), ("state", "flags"))
        if self.doc:
            for alias in self.doc.data.get("state", {}).get("flags", {}):
                add(alias, ("state", "flags", alias), parent)
        parent.setExpanded(True)
        add(tr("Recursos originales"), ("resources",))
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
        if hasattr(self,'product_stack'):
            from .product_ui import refresh_status
            refresh_status(self)

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
            self.statusBar().showMessage(tr('Esta crónica usa la entrada original del mapa; no tiene un inicio propio colocado.'),8000);return
        root=self.doc.campaign
        si=next(i for i,row in enumerate(root['scenes']) if row['id']==root['entry'])
        scene=root['scenes'][si]
        ei=next((i for i,row in enumerate(scene.get('entries',[])) if row['id']==scene.get('default_entry')),-1)
        if ei<0:
            self.statusBar().showMessage(tr('La escena inicial usa la entrada original 0. Crea una entrada y elígela como llegada por defecto para colocar un inicio propio.'),10000);return
        if not self.commit_properties():return
        self.doc.active=si;self.selection=('entries',ei);self.refresh();self.select(('entries',ei));self.center_tabs.setCurrentIndex(0)
        viewport=self.spatial.viewport
        if viewport and self.spatial.geometry_matches():viewport.focus_selection()
        else:self.spatial.pending_start_focus=True
        self.statusBar().showMessage(tr('Inicio del jugador: ')+scene['entries'][ei]['name']+tr(' · edita XYZ/orientación o arrastra el marcador en 3D.'),10000)

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
        if self.selection[0] in {'conversations', 'events', 'state', 'resources'} and self.center_tabs.currentWidget() is not getattr(self,'graph_panel',None):
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
        titles = {"chronicle": tr("Tu crónica"), "level": tr("Escenario base"), "actors": tr("Actores"), "objects": tr("Objetos"),
                  "conversations": tr("Conversaciones"), "events": tr("Eventos"), "state": "Chronicle Flags", "resources": tr("Recursos originales")}
        self.heading.setText(titles.get(path[0], tr("Proyecto")))
        self.subtitle.setText(tr("Crea una crónica o abre un proyecto para empezar.") if not self.doc else tr("Selecciona un elemento y edita sus propiedades a la derecha."))
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
                    self.subtitle.setText(tr("Conversación de Fase 1. Añadir un nodo la convierte al modelo ramificado conservando sus respuestas."))
            elif path[0] == "events" and len(path) > 1:
                event = data["events"][path[1]]
                self.heading.setText(event.get("id", (tr('Evento ') + f'{path[1] + 1}')))
                self.subtitle.setText(tr("Deben cumplirse todas las condiciones. Los cambios de estado preceden al inicio de conversaciones y a la creación diferida de actores."))
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
                self.subtitle.setText(tr("Define el escenario, añade personajes y escribe tu historia. Valida antes de compilar."))
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
            QMessageBox.warning(self, tr("Revisa la operación"), diagnostic(error) if isinstance(error, (ValueError, OSError)) else tr("No se pudo realizar la operación. Revisa los datos del proyecto."))
            return False

    def can_leave(self):
        if self.busy:
            QMessageBox.information(self, tr("Build en curso"), tr("Espera a que termine la compilación."))
            return False
        if self.doc and (self.doc.modified or self.pending_properties()):
            choice = QMessageBox.question(self, tr("Cambios sin guardar"), tr("¿Guardar los cambios antes de continuar?"),
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
        document = CampaignDocument.new(self.backend.ws, dialog.pid.text(), dialog.name.text(), dialog.directory.text(), dialog.description.toPlainText())
        if dialog.level.currentData():
            scene=document.campaign['scenes'][0];scene['level']['source']=dialog.level.currentData()
            # No guessed player coordinates: initial native location remains until
            # the creator places a named entry using Start in the existing viewport.
        document.path.parent.mkdir(parents=True,exist_ok=True)
        from ..project_safety import ProjectLock
        lock=ProjectLock(document.path)
        if not lock.acquire():raise ValueError(tr('Esta crónica está abierta en otro editor. Cierra esa ventana antes de editarla aquí.'))
        previous=getattr(self,'project_lock',None)
        if previous:previous.release()
        self.project_lock=lock;self.doc=document
        document.save()
        prefs=getattr(self.backend.ws,'app_settings',None)
        if prefs:prefs.recent(document.path,document.data['chronicle']['name'])
        self.selection = ("chronicle",)
        self.refresh()
        self.validate_project()

    def open_project(self):
        if not self.can_leave():
            return
        path, _ = QFileDialog.getOpenFileName(self, tr("Abrir crónica"), str(self.backend.ws.root / "chronicles"), tr("Proyectos YAML (*.yaml *.yml)"))
        if path:
            self.guard(lambda: self.open_path(path))

    def open_path(self, path):
        document = Document.load(self.backend.ws, path)
        from ..project_safety import ProjectLock
        existing=getattr(self,'project_lock',None)
        if not existing or existing.path.parent!=document.path.parent:
            lock=ProjectLock(document.path)
            if not lock.acquire():raise ValueError(tr('Esta crónica está abierta en otro editor. Cierra esa ventana antes de editarla aquí.'))
        else:lock=existing
        if document.recovery_path.exists():
            from datetime import datetime
            choice=QMessageBox(self);choice.setWindowTitle(tr('Recuperación disponible'));choice.setText(tr('Proyecto guardado: ')+datetime.fromtimestamp(document.path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')+'\n'+tr('Recuperación: ')+datetime.fromtimestamp(document.recovery_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'))
            recover=choice.addButton(tr('Recuperar'),QMessageBox.ButtonRole.AcceptRole);ignore=choice.addButton(tr('Ignorar por ahora'),QMessageBox.ButtonRole.RejectRole);discard=choice.addButton(tr('Descartar recuperación'),QMessageBox.ButtonRole.DestructiveRole);choice.setDefaultButton(ignore);choice.exec()
            if choice.clickedButton()==recover:document.recover()
            elif choice.clickedButton()==discard:self.backend.ws.output(document.recovery_path).unlink()
        self.doc = document
        if existing and existing is not lock:existing.release()
        self.project_lock=lock
        prefs=getattr(self.backend.ws,'app_settings',None)
        if prefs:prefs.recent(document.path,document.data['chronicle']['name'])
        self.selection = ("chronicle",)
        self.refresh()
        self.validate_project()

    def save_project(self):
        if not self.doc or not self.commit_properties():
            return False
        def save():
            from ..project_safety import ExternalChange
            try:self.doc.save()
            except ExternalChange:
                choice=QMessageBox(self);choice.setWindowTitle(tr('Archivo modificado fuera de RCM'));choice.setText(tr('El archivo cambió fuera del editor. Elige cómo conservar tu trabajo.'))
                reload=choice.addButton(tr('Recargar'),QMessageBox.ButtonRole.ActionRole);copy=choice.addButton(tr('Guardar una copia'),QMessageBox.ButtonRole.ActionRole);overwrite=choice.addButton(tr('Sobrescribir'),QMessageBox.ButtonRole.DestructiveRole);cancel=choice.addButton(tr('Cancelar'),QMessageBox.ButtonRole.RejectRole);choice.setDefaultButton(cancel);choice.exec()
                if choice.clickedButton()==reload:self.open_path(self.doc.path);return False
                if choice.clickedButton()==copy:
                    from .product_ui import duplicate_project
                    duplicate_project(self);return False
                if choice.clickedButton()!=overwrite:return False
                self.doc.save(force=True)
            self._title()
            prefs=getattr(self.backend.ws,'app_settings',None)
            if prefs:prefs.recent(self.doc.path,self.doc.data['chronicle']['name'])
            self.statusBar().showMessage(tr("Proyecto guardado"), 4000)
            return True
        return self.guard(save)

    def save_as(self):
        if not self.doc or not self.commit_properties():
            return
        path, _ = QFileDialog.getSaveFileName(self, tr("Guardar crónica como"), str(self.doc.path), tr("Proyectos YAML (*.yaml)"))
        if path:
            self.guard(lambda: self.doc.save(path))
            self._title()

    def autosave(self):
        if self.doc and self.doc.modified and not self.busy:
            try:
                self.doc.autosave()
                self.statusBar().showMessage(tr("Copia de recuperación actualizada"), 2000)
            except (OSError, ValueError) as error:
                self.log.appendPlainText(tr("No se pudo guardar recuperación: ") + diagnostic(error))

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
            self.statusBar().showMessage(tr("Crea o abre un proyecto para usar el recurso."), 4000)
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
            raise ValueError(tr('Elige una plantilla de actor única del catálogo.'))
        data = self.doc.data
        ident = self.doc.unique_id("actors", "actor")
        actor = {"id": ident, "name": tr("Nuevo personaje"), "template": template,
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
            rows.append(dict(id=ident,name=tr('Nueva entrada') if kind=='entries' else tr('Nuevo waypoint'),transform=dict(placement='absolute',position=list(position),orientation=[0,0,0])))
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
        menu.addAction(tr('Buscar referencias'), lambda: self.find_references(tuple(item.data(0, ROLE))))
        menu.exec(self.nav.mapToGlobal(position))

    def reference_label(self, path):
        try:
            if hasattr(self.doc, 'campaign') and path[0] in {'scenes', 'quests','authoring'}:
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
            if path[0] not in {'state', 'scenes', 'quests','authoring'}: path = ('scenes', self.doc.active) + path
            links = graph(self.doc.campaign)
            incoming, outgoing = [x for x in links if x.target == path], [x for x in links if x.source == path]
        else:
            incoming, outgoing = references(self.doc.data, path)
        self.reference_tree.clear()
        for label, links, attr in [(tr('USED BY / Referenciado por'), incoming, 'source'), (tr('AFFECTS / Referencia a'), outgoing, 'target')]:
            parent = QTreeWidgetItem(self.reference_tree, [label, ''])
            for link in links:
                target = getattr(link, attr)
                item = QTreeWidgetItem(parent, [link.label, self.reference_label(target)])
                item.setData(0, ROLE, link.detail if attr == 'source' and link.source[0] in {'events', 'conversations'} else target)
            parent.setExpanded(True)
        self.bottom_tabs.setCurrentIndex(2)

    def navigate_reference(self, path):
        if path:
            if path[0]=='authoring':
                self.show_recipe(recipe_id=self.doc.campaign['authoring']['recipes'][path[2]]['id']);return
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
                "nodes": [{"id": "opening", "lines": [{"speaker": speaker, "text": tr("Escribe el diálogo.")}],
                           "choices": [{"text": tr("Continuar."), "result": 1}, {"text": tr("Me voy."), "result": 2}]}]}
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
        conv["nodes"].append({"id": "node"+str(i), "lines": [{"speaker": conv["speaker"], "text": tr("Escribe el diálogo.")}],
                              "choices": [{"text": tr("Terminar."), "result": self.next_result(conv)}]})
        self.selection = self.selection[:2] + ("nodes", len(conv["nodes"])-1)
        self.changed(True)

    def add_line(self):
        conv = self.graph_conversation()
        if conv is None:
            return
        ni = self.selected_node_index(conv)
        lines = conv["nodes"][ni]["lines"]
        lines.append({"speaker": conv["speaker"], "text": tr("Nueva línea.")})
        self.selection = self.selection[:2] + ("nodes", ni, "lines", len(lines)-1)
        self.changed(True)

    def add_answer(self):
        conv = self.graph_conversation()
        if conv is None:
            return
        ni = self.selected_node_index(conv)
        answers = conv["nodes"][ni]["choices"]
        answers.append({"text": tr("Nueva respuesta."), "result": self.next_result(conv)})
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
        if event['when']=='object_clicked':
            action={'show_note':{'title':tr('Nota'),'text':tr('Escribe aquí lo que leerá el jugador.')}}
        elif event["when"] == "actor_clicked":
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
            QMessageBox.warning(self, "Flags", tr("Se han agotado los índices admitidos por el backend actual."))
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
            QMessageBox.warning(self,tr('Elemento referenciado'),diagnostic(error));return
        extra = tr("\nTambién se retirarán sus acciones de aparición.") if p[0] in {'actors', 'objects'} else ""
        if QMessageBox.question(self, tr("Eliminar elemento"), tr("¿Eliminar este elemento?") + extra + tr("\nPuedes deshacer esta operación."),
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
        self.product_valid=validation.valid
        self.problem_table.setRowCount(len(validation.problems))
        dark = self.palette().color(QPalette.ColorRole.Base).lightnessF() < .5
        severity_colors = {'ERROR': '#ff8c96' if dark else '#a40016', 'WARNING': '#f1c56c' if dark else '#825300', 'INFO': '#91c7ff' if dark else '#17527d'}
        for i, problem in enumerate(validation.problems):
            level = QTableWidgetItem(problem.severity)
            level.setData(ROLE, problem.path)
            level.setForeground(QColor(severity_colors.get(problem.severity, severity_colors['INFO'])))
            self.problem_table.setItem(i, 0, level)
            cell = QTableWidgetItem(diagnostic(problem.message))
            cell.setToolTip(diagnostic(problem.message))
            self.problem_table.setItem(i, 1, cell)
        self.statusBar().showMessage(tr("Proyecto válido") if validation.valid else tr("Hay errores por corregir"))
        counts={level:sum(p.severity==level for p in validation.problems) for level in ('ERROR','WARNING')}
        self.bottom_tabs.setTabText(0,tr('Problemas')+' ('+str(counts['ERROR'])+' / '+str(counts['WARNING'])+')')
        if hasattr(self,'product_stack'):
            from .product_ui import refresh_status
            refresh_status(self)
        return validation

    def validate_from_ui(self):
        if self.doc and self.commit_properties():
            return self.validate_project()

    def problem_selected(self, row, column):
        path = self.problem_table.item(row, 0).data(ROLE)
        if path and path[0]=='authoring':self.navigate_reference(path);return
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
            failed_report(self.backend.ws,self.doc.snapshot(),tr('Validación fallida desde el editor'))
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
        self.worker.progress.connect(self.append_build_progress)
        self.worker.succeeded.connect(self.build_succeeded)
        self.worker.failed.connect(self.build_failed)
        self.worker.completed.connect(self.thread.quit)
        self.worker.completed.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.build_finished)
        self.thread.start()

    @Slot(str)
    def append_build_progress(self, message):
        self.log.appendPlainText(diagnostic(message))
        self.statusBar().showMessage(diagnostic(message))

    def build_succeeded(self, report):
        self.last_build = report
        path = self.backend.ws.root / "build" / report["chronicle"]
        self.log.appendPlainText((tr('Crónica construida correctamente.')+'\n' + f'{path}' + tr('\nPreparado para probar en Redemption; este build no instala ni ejecuta el juego.')))
        if report.get('save_warning'):self.log.appendPlainText(diagnostic(report['save_warning']))
        self.build_completed.emit(report)

    def build_failed(self, message, details):
        try:self.backend.ws.write("build/editor/build_error.log", details)
        except (OSError,ValueError):pass
        self.log.appendPlainText(tr("Build falló: ") + diagnostic(message) + tr("\nDetalle disponible en build/editor/build_error.log"))
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
            self.statusBar().showMessage(tr('Terminando la carga del escenario antes de cerrar…'))
            QTimer.singleShot(150, self.close)
            event.ignore()
            return
        if self.can_leave():
            from .product_ui import save_ui
            save_ui(self)
            self.autosave_timer.stop()
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self,event):
        urls=event.mimeData().urls()
        if len(urls)==1 and urls[0].isLocalFile() and Path(urls[0].toLocalFile()).suffix.casefold() in ('.yaml','.yml','.rcmproject','.rcmpack'):
            event.acceptProposedAction()

    def dropEvent(self,event):
        path=Path(event.mimeData().urls()[0].toLocalFile())
        def accept():
            if path.suffix.casefold() in ('.yaml','.yml'):
                if not self.can_leave():return
                self.open_path(self.backend.ws.output(path))
            elif path.suffix.casefold()=='.rcmproject':
                if not self.can_leave():return
                from ..packages import read_archive,verify_manifest,import_project
                from ..product import project_id
                meta=verify_manifest(read_archive(path),'project');ident=project_id(meta['name'],self.backend.ws.root)
                doc=import_project(self.backend.ws,path,'chronicles/'+ident);self.open_path(doc.path)
            elif path.suffix.casefold()=='.rcmpack':
                from .package_panel import install_package
                install_package(self,path)
        self.guard(accept);event.acceptProposedAction()
