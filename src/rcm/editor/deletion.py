"""One deletion flow for the tree, viewport and campaign, with a concrete preview."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QTreeWidget,QTreeWidgetItem,QDialogButtonBox,QPushButton,QMessageBox,QHeaderView
from .i18n import tr,diagnostic
from ..safe_edit import at,deletion_plan,delete_candidate,reference_links


def reference_kind(label):
    labels={'spawn_points':tr('Punto de aparición'),'spawn point':tr('Punto de aparición'),'points':tr('Punto de recorrido'),'start_generator':tr('Inicio del encuentro'),'spawn':tr('Aparición'),'spawn_encounter':tr('Aparición del grupo'),'inventory':tr('Inventario'),'default':tr('Conversación predeterminada'),'trigger':tr('Zona de activación'),'actor':tr('Actor'),'speaker':tr('Interlocutor'),'flag':tr('Flag'),'authoring recipe':tr('Configuración del asistente')}
    from ..campaign import ACTIONS
    return labels.get(label,tr(ACTIONS[label][0]) if label in ACTIONS else tr(label))


def editable_reference(root,path):
    """Navigate to the action/condition or entity, never a scalar reference field."""
    path=tuple(path)
    if path[:2]==('state','flags') and len(path)==3:return path
    while path:
        try:value=at(root,path)
        except (KeyError,IndexError,TypeError):path=path[:-1];continue
        if isinstance(value,dict):return path
        path=path[:-1]
    return ()


class DeleteDialog(QDialog):
    def __init__(self,win,path,plan,error=None):
        super().__init__(win);self.win=win;self.path=path;self.destination=None
        self.setObjectName('delete_references_dialog');self.setWindowTitle(tr('Eliminar elemento'));self.resize(760,520)
        layout=QVBoxLayout(self)
        text=QLabel(tr('Este elemento se usa en otros lugares del proyecto. Puedes revisarlos o eliminarlo junto con sus referencias.'));text.setWordWrap(True);layout.addWidget(text)
        self.references=QTreeWidget();self.references.setObjectName('delete_reference_list');self.references.setHeaderLabels([tr('Se usa en'),tr('Referencia')]);layout.addWidget(self.references,1)
        self.references.header().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        self.references.header().setSectionResizeMode(1,QHeaderView.ResizeMode.ResizeToContents)
        for link in reference_links(win.doc,path):
            item=QTreeWidgetItem(self.references,[win.reference_label(link.source),reference_kind(link.label)])
            item.setData(0,Qt.ItemDataRole.UserRole,editable_reference(win.doc.snapshot(),link.detail));item.setToolTip(0,win.reference_label(link.detail))
        go=QPushButton(tr('Ir a la referencia seleccionada'));go.setObjectName('delete_go_to_reference');go.clicked.connect(lambda:self.go());layout.addWidget(go)
        self.references.itemDoubleClicked.connect(lambda *_:self.go())
        label=QLabel(tr('Al confirmar se eliminará:'));layout.addWidget(label)
        self.preview=QTreeWidget();self.preview.setObjectName('delete_impact_list');self.preview.setHeaderLabels([tr('Elemento / uso')]);layout.addWidget(self.preview,1)
        if plan:
            for p in plan.removed:
                item=QTreeWidgetItem(self.preview,[win.reference_label(p)]);item.setToolTip(0,item.text(0))
            for p in plan.changed:QTreeWidgetItem(self.preview,[tr('Actualizar entrada de la campaña')])
        if error:
            label=QLabel(diagnostic(error));label.setWordWrap(True);layout.addWidget(label)
        label=QLabel(tr('Los eventos que queden sin acciones también se eliminan. No se quitan condiciones para convertirlos en eventos incondicionales. Todo se puede deshacer.'));label.setWordWrap(True);layout.addWidget(label)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
        self.remove=buttons.addButton(tr('Eliminar y quitar referencias'),QDialogButtonBox.ButtonRole.AcceptRole);self.remove.setObjectName('delete_with_references');self.remove.setEnabled(plan is not None);self.remove.clicked.connect(self.accept)
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setDefault(True)
        if self.references.topLevelItemCount():self.references.setCurrentItem(self.references.topLevelItem(0))
    def go(self):
        item=self.references.currentItem()
        if item:self.destination=item.data(0,Qt.ItemDataRole.UserRole);self.reject()


def confirm_delete(win,path):
    """Return a validated snapshot on confirmation; cancel/navigation never mutates."""
    try:
        delete_candidate(win.doc,path,win.backend,remove_spawns=True)
    except ValueError:
        refs=reference_links(win.doc,path)
        try:plan=deletion_plan(win.doc,path,win.backend);error=None
        except ValueError as failure:plan=None;error=str(failure)
        if not refs:
            if plan is None:raise ValueError(error)
            candidate=plan.candidate
        else:
            dialog=DeleteDialog(win,path,plan,error)
            if dialog.exec()==QDialog.DialogCode.Accepted:return plan.candidate
            if dialog.destination:win.navigate_reference(dialog.destination)
            return None
    else:candidate=deletion_plan(win.doc,path,win.backend).candidate
    if QMessageBox.question(win,tr('Eliminar elemento'),tr('¿Eliminar este elemento?')+tr('\nSe retirarán sus acciones de aparición si las tiene. Puedes deshacer la operación.'),QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes:return None
    return candidate
