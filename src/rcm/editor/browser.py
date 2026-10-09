from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QPushButton, QDialog, QDialogButtonBox)


class ResourceBrowser(QWidget):
    chosen = Signal(str, str)

    def __init__(self, backend, category=None, parent=None):
        super().__init__(parent)
        self.backend = backend
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setObjectName("resource_search")
        self.search.setPlaceholderText("Buscar por nombre o identificador…")
        self.category = QComboBox()
        self.category.setObjectName("resource_category")
        for name, value in [("Levels", "levels"), ("Plantillas de actores", "actors"),
                            ("Objetos", "items"), ("Escenas", ".nsd"), ("Modelos", ".nod"), ("AI", ".nai")]:
            self.category.addItem(name, value)
        row.addWidget(self.search, 1)
        row.addWidget(self.category)
        layout.addLayout(row)
        filters = QHBoxLayout()
        self.family = QComboBox(); self.family.setObjectName('resource_family')
        for label, value in [('Todos los recursos',''),('Objetos','items'),('Props','props'),('Armas','weapons'),('Armaduras','armour'),('Actores','actors')]: self.family.addItem(label,value)
        self.origin = QComboBox(); self.origin.setObjectName('resource_origin')
        for label,value in [('Toda procedencia',''),('Original','Original /'),('Proyecto','Proyecto /')]: self.origin.addItem(label,value)
        self.available = QComboBox(); self.available.setObjectName('resource_available')
        self.available.addItem('Todos',False); self.available.addItem('Sólo seleccionables',True)
        for control in (self.family,self.origin,self.available): filters.addWidget(control); control.currentIndexChanged.connect(self.refresh)
        layout.addLayout(filters)
        self.table = QTableWidget(0, 4)
        self.table.setObjectName("resource_table")
        self.table.setHorizontalHeaderLabels(["Nombre / ID", "Recurso", "Procedencia", "Disponibilidad"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(2, 210)
        self.table.setColumnWidth(3, 165)
        layout.addWidget(self.table, 1)
        self.details = QLabel("Selecciona un recurso para consultar su identificador exacto.")
        self.details.setWordWrap(True)
        layout.addWidget(self.details)
        self.use_button = QPushButton('Usar selección')
        self.use_button.setObjectName('resource_use')
        self.use_button.setEnabled(False)
        self.use_button.clicked.connect(self.choose)
        actions = QHBoxLayout(); actions.addWidget(self.use_button)
        self.inspect_button = QPushButton('Inspeccionar plantilla / AI · solo lectura')
        self.inspect_button.setObjectName('resource_inspect')
        self.inspect_button.clicked.connect(self.inspect_resource)
        actions.addWidget(self.inspect_button)
        self.clone_button=QPushButton('Clonar plantilla al proyecto')
        self.clone_button.setObjectName('resource_clone_project');actions.addWidget(self.clone_button);layout.addLayout(actions)
        self.clone_button.setVisible(category is None)
        def clone():
            selected=self.selected();parent=self.window()
            if selected and hasattr(parent,'project_resources_panel'):parent.guard(lambda:parent.project_resources_panel.clone_original(selected[0]))
        self.clone_button.clicked.connect(clone)
        self.search.textChanged.connect(self.refresh)
        self.category.currentIndexChanged.connect(self.refresh)
        self.table.itemSelectionChanged.connect(self.show_details)
        self.table.cellDoubleClicked.connect(self.choose)
        if category:
            self.category.setCurrentIndex(self.category.findData(category))
            self.category.setEnabled(False)
        self.refresh()

    def refresh(self):
        if not hasattr(self,'table'): return
        kind = self.category.currentData()
        query = self.search.text().strip().casefold()
        rows = []
        if kind == "levels":
            for ident, item in sorted(self.backend.levels.items()):
                title = self.backend.level_label(ident)
                origins = ", ".join(sorted({r["chronicle"] for r in item["references"]}))
                info = f"ID: {ident}\nGeometría: {item['nil']}\nEscenas: {', '.join(item['scenes']) or 'Sin escena asociada'}\nProcedencia: {origins}"
                usable = self.backend.level_usable(ident)
                rows.append((title + " · " + ident, item["nil"], origins, "Disponible" if usable else "Solo catálogo", ident, info, usable))
        elif kind in {"actors", "items"}:
            templates = self.backend.resources["templates"]
            counts = {}
            for t in templates:
                counts[t["id"]] = counts.get(t["id"], 0) + 1
            for item in sorted(templates, key=lambda t: t["id"].casefold()):
                if item["kind"] not in ({"actors"} if kind == "actors" else {"items", "props", "weapons", "armour"}):
                    continue
                if hasattr(self,'allowed_families') and item['kind'] not in self.allowed_families:continue
                origin_text = ('Proyecto / ' if item.get('project_owned') else 'Original / ')+item["archive"] + " / " + item["path"]
                usable = counts[item["id"]] == 1
                info = (f"ID exacto: {item['id']}\nFamilia: {item['kind']}\nProcedencia: {origin_text}"
                        f"\nHereda de: {item.get('parent') or 'Sin padre'}"
                        f"\nModelo: {item.get('model') or 'No declarado directamente'}"
                        f"\nAI: {item.get('ai') or 'No declarada directamente'}")
                rows.append((item["id"], item["kind"], origin_text, "Única" if usable else "Ambigua", item["id"], info, usable))
        else:
            for item in sorted(self.backend.resources["entries"], key=lambda t: t["id"].casefold()):
                if item["extension"].casefold() != kind:
                    continue
                rows.append((item["id"], item["path"], item["archive"], "Consulta", item["id"],
                             f"ID exacto: {item['id']}\n{item['archive']} / {item['path']}", True))
        rows = [r for r in rows if query in " ".join(str(v) for v in r[:6]).casefold()]
        self.family.setEnabled(kind in {'actors','items'}); self.origin.setEnabled(kind in {'actors','items'})
        rows = [r for r in rows if (kind not in {'actors','items'} or (not self.family.currentData() or r[1]==self.family.currentData()) and (not self.origin.currentData() or r[2].startswith(self.origin.currentData()))) and (not self.available.currentData() or r[6])]
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row[:4]):
                cell = QTableWidgetItem(value)
                cell.setToolTip(value)
                if j == 0:
                    cell.setData(Qt.ItemDataRole.UserRole, row[4:])
                if not row[6]:
                    cell.setForeground(Qt.GlobalColor.gray)
                self.table.setItem(i, j, cell)
        self.details.setText(f"{len(rows)} recursos. Selecciona uno para consultar sus detalles.")
        self.use_button.setEnabled(False)

    def selected(self):
        row = self.table.currentRow()
        item = self.table.item(row, 0) if row >= 0 else None
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def inspect_resource(self):
        import json
        from PySide6.QtWidgets import QPlainTextEdit
        selected=self.selected()
        if not selected: return
        kind=self.category.currentData()
        if kind in {'actors','items'}:
            from ..not_inspector import inspect_template
            record=next(t for t in self.backend.resources['templates'] if t['id']==selected[0])
            result=inspect_template(self.backend.ws,record,self.backend.project_payload)
            result['catalogue_inheritance']=record
            text=json.dumps(result,ensure_ascii=False,indent=2)
        elif kind=='.nai':
            record=next(t for t in self.backend.resources['entries'] if t['id']==selected[0] and t['extension'].lower()=='.nai')
            from ..project_resources import original_bytes
            data=self.backend.project_payload[record['path']] if record.get('project_owned') else original_bytes(self.backend.ws,record)
            text=data.decode('cp1252')
        else:return
        dialog=QDialog(self);dialog.setWindowTitle(selected[0]+' · solo lectura');dialog.resize(760,620)
        layout=QVBoxLayout(dialog);view=QPlainTextEdit(text);view.setReadOnly(True);layout.addWidget(view);dialog.exec()

    def show_details(self):
        selected = self.selected()
        self.clone_button.setEnabled(bool(selected and self.category.currentData() in {'actors','items'} and not str(selected[1]).find('Proyecto /')>=0))
        if selected:
            self.details.setText(selected[1])
        self.use_button.setEnabled(bool(selected and selected[2] and self.category.currentData() in {'levels','actors','items'}))

    def choose(self, *unused):
        selected = self.selected()
        if selected and selected[2]:
            self.chosen.emit(self.category.currentData(), selected[0])


class ResourceDialog(QDialog):
    def __init__(self, backend, category, parent=None):
        super().__init__(parent)
        self.setWindowTitle({"levels": "Elegir level base", "actors": "Elegir plantilla de actor", "items": "Elegir plantilla de objeto",'.nai':'Elegir perfil AI'}.get(category,'Elegir recurso'))
        self.resize(950, 600)
        self.selection = None
        layout = QVBoxLayout(self)
        self.browser = ResourceBrowser(backend, category, self)
        self.browser.use_button.hide()
        layout.addWidget(self.browser)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Usar selección")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        layout.addWidget(self.buttons)
        self.browser.chosen.connect(self.selected)
        self.buttons.accepted.connect(self.accept_selection)
        self.buttons.rejected.connect(self.reject)

    def selected(self, kind, ident):
        self.selection = ident
        self.accept()

    def accept_selection(self):
        self.browser.choose()
