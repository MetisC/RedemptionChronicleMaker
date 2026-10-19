"""Optional, user-supplied WTD content and ordinary actor trait editing."""
import copy
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QFileDialog,QMessageBox,QApplication,QComboBox,QSpinBox,QTreeWidget,QTreeWidgetItem,QDialogButtonBox,QHeaderView
from PySide6.QtCore import Qt
from .i18n import tr,diagnostic


def summary(backend):
    from ..wtd import manifest
    record=manifest(backend.ws)
    if not record:return tr('Sin contenido WTD importado.')
    c=record['counts']
    return tr('Contenido disponible: {0} clanes, {1} disciplinas, {2} plantillas y {3} escenario.').format(c['clans'],c['disciplines'],c['templates'],c.get('levels',0))


def import_widget(win,layout):
    row=QHBoxLayout();button=QPushButton(tr('Importar contenido de mod «Within The Darkness»…'));button.setObjectName('settings_import_wtd');row.addWidget(button);layout.addLayout(row)
    status=QLabel(summary(win.backend));status.setObjectName('settings_wtd_status');status.setWordWrap(True);layout.addWidget(status)
    note=QLabel(tr('Elige tu NOB. Se importan recursos utilizables y Penthouse; la interfaz y la crónica demo quedan fuera. El mod no se incluye con el programa.'));note.setWordWrap(True);layout.addWidget(note)
    def run():
        if not win.commit_properties():return
        source,_=QFileDialog.getOpenFileName(win,tr('Importar Within The Darkness'),'',tr('Archivo NOB (*.nob)'))
        if not source:return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            from ..wtd import import_content
            import_content(win.backend,source)
            win.refresh();win.browser.refresh();status.setText(summary(win.backend))
        except (ValueError,OSError,KeyError) as error:QMessageBox.warning(win,tr('No se pudo importar'),diagnostic(error))
        finally:QApplication.restoreOverrideCursor()
    button.clicked.connect(run)


class TraitsDialog(QDialog):
    def __init__(self,win,actor):
        super().__init__(win);self.win=win;self.actor_id=actor['id'];self.setWindowTitle(tr('Clan y disciplinas'));self.resize(680,470)
        self.setObjectName('actor_traits_dialog');layout=QVBoxLayout(self);layout.addWidget(QLabel(tr('Sin cambios conserva la configuración de la plantilla.')))
        from ..actor_traits import catalogue
        data=catalogue(win.backend.resources);current=actor.get('traits',{})
        self.clan=QComboBox();self.clan.setObjectName('actor_clan');self.clan.addItem(tr('Heredar de la plantilla'),None)
        for r in data['clans']:self.clan.addItem(r['id']+(' · WTD' if r['imported'] else ''),r['id'])
        self.clan.setCurrentIndex(max(0,self.clan.findData(current.get('clan'))));layout.addWidget(self.clan)
        row=QHBoxLayout();self.discipline=QComboBox();self.discipline.setObjectName('actor_discipline')
        for r in data['disciplines']:self.discipline.addItem(r['id']+(' · WTD' if r['imported'] else ''),r['id'])
        row.addWidget(self.discipline,1);self.level=QSpinBox();self.level.setRange(0,5);self.level.setValue(1);self.level.setObjectName('actor_discipline_level');row.addWidget(QLabel(tr('Nivel')));row.addWidget(self.level)
        add=QPushButton(tr('Añadir / cambiar'));add.setObjectName('add_actor_discipline');row.addWidget(add);layout.addLayout(row)
        self.tree=QTreeWidget();self.tree.setHeaderLabels([tr('Disciplina'),tr('Nivel')]);self.tree.setObjectName('actor_disciplines');self.tree.header().setStretchLastSection(False);self.tree.header().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch);self.tree.header().setSectionResizeMode(1,QHeaderView.ResizeMode.ResizeToContents);layout.addWidget(self.tree,1)
        self.powers=copy.deepcopy(current.get('disciplines',{}));add.clicked.connect(self.add);remove=QPushButton(tr('Quitar selección'));remove.clicked.connect(self.remove);layout.addWidget(remove);self.render()
        self.error=QLabel();self.error.setWordWrap(True);layout.addWidget(self.error)
        self.buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);self.buttons.accepted.connect(self.accept);self.buttons.rejected.connect(self.reject);layout.addWidget(self.buttons)
    def render(self):
        self.tree.clear()
        for name,level in self.powers.items():
            item=QTreeWidgetItem(self.tree,[name,str(level)]);item.setToolTip(0,name)
    def add(self):self.powers[self.discipline.currentData()]=self.level.value();self.render()
    def remove(self):
        item=self.tree.currentItem()
        if item:self.powers.pop(item.text(0),None);self.render()
    def accept(self):
        candidate=self.win.doc.snapshot();actor=next(a for a in candidate['scenes'][self.win.doc.active]['actors'] if a['id']==self.actor_id)
        traits={}
        if self.clan.currentData():traits['clan']=self.clan.currentData()
        if self.powers:traits['disciplines']=self.powers
        if traits:actor['traits']=traits
        else:actor.pop('traits',None)
        errors=[p.message for p in self.win.backend.validate(candidate).problems if p.severity=='ERROR']
        if errors:self.error.setText(diagnostic('\n'.join(errors)));return
        if candidate!=self.win.doc.snapshot():self.win.doc.data=candidate;self.win.history_time=0;self.win.changed(True)
        super().accept()
