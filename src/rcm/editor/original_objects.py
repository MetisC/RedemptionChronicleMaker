from .text_commit import bind_filter
"""Pick scenery and author native hover/click interactions or prop operations."""
import copy
import re
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QLineEdit,QTreeWidget,QTreeWidgetItem,QComboBox,QLabel,QDialogButtonBox,QCheckBox,QPushButton
from .i18n import tr
from ..original_objects import catalogue,selector


def object_label(row):
    material=', '.join(n.replace('\\','/').rsplit('/',1)[-1] for n in row.get('mesh_materials',[]))
    return (material+' · ' if material else '')+row['template']+(' · '+row['script'] if row.get('script') else '')


def click_event_id(scene,target):
    template=target.get('template') or target.get('material','surface').replace('\\','/').rsplit('/',1)[-1]
    stem='click_'+re.sub('[^A-Za-z0-9_]','_',template)[:48]+'_'
    used={e['id'] for e in scene['events']}
    numbers=[int(m.group(1)) for name in used for m in [re.fullmatch(r'click(?:_.*_)?(\d+)',name)] if m]
    number=max([sum(e['when']=='object_clicked' for e in scene['events']),*numbers])+1
    while stem+str(number) in used:number+=1
    return stem+str(number)


class OriginalObjectPicker(QDialog):
    def __init__(self,win,selected=None):
        super().__init__(win);self.setWindowTitle(tr('Elegir objeto original del escenario'));self.resize(830,540);self.selection=None
        layout=QVBoxLayout(self);self.search=QLineEdit();self.search.setPlaceholderText(tr('Buscar objeto, puerta o identificador…'));layout.addWidget(self.search)
        self.tree=QTreeWidget();self.tree.setObjectName('original_object_list');self.tree.setHeaderLabels([tr('Objeto'),tr('Posición'),tr('Cast ID')]);layout.addWidget(self.tree,1)
        self.rows=catalogue(win.backend,win.doc.data['level']['source'])
        for row in self.rows:
            item=QTreeWidgetItem(self.tree,[object_label(row),str(row.get('position',tr('Sin posición'))),row.get('cast_id','')]);item.setData(0,Qt.ItemDataRole.UserRole,selector(row));item.setToolTip(0,object_label(row)+'\n'+row['origin'])
            if selected and selector(row)==selector(selected):self.tree.setCurrentItem(item)
        bind_filter(self.search,lambda:[self.tree.topLevelItem(i).setHidden(self.search.text().casefold() not in ' '.join(self.tree.topLevelItem(i).text(c) for c in range(3)).casefold()) for i in range(self.tree.topLevelItemCount())])
        self.tree.itemDoubleClicked.connect(lambda *_:self.accept())
        locate=QPushButton(tr('Localizar en 3D'));locate.setObjectName('locate_original_object');layout.addWidget(locate)
        def focus():
            item=self.tree.currentItem();viewport=win.spatial.viewport
            if not item or not viewport or not viewport.level or not win.spatial.geometry_matches():return
            chosen=item.data(0,Qt.ItemDataRole.UserRole)
            for i,row in enumerate(viewport.level.references):
                if selector(row)==chosen:
                    win.spatial.select(('original',i));viewport.focus_selection();win.center_tabs.setCurrentWidget(win.spatial);self.reject();return
        locate.clicked.connect(focus);locate.setEnabled(bool(win.spatial.viewport and win.spatial.geometry_matches()))
        note=QLabel(tr('Objetos de la escena estática original. El motor comprueba plantilla, ubicación e identidad antes de actuar. Los muros y superficies fijas no son objetos retirables.'));note.setWordWrap(True);layout.addWidget(note)
        if not self.rows:layout.addWidget(QLabel(tr('Este escenario no ofrece objetos estáticos identificados en el catálogo.')))
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
        self.tree.setColumnWidth(0,260);self.tree.setColumnWidth(1,330)
    def accept(self):
        item=self.tree.currentItem()
        if item:self.selection=copy.deepcopy(item.data(0,Qt.ItemDataRole.UserRole));super().accept()


def choose_target(ins,path,value):
    win=ins.win
    def choose():
        dialog=OriginalObjectPicker(win,value)
        if dialog.exec()!=QDialog.DialogCode.Accepted:return
        updated=dict(dialog.selection,operation=value.get('operation','hide'))
        if updated['operation'] in {'frame','pivot'}:
            updated.update(frame=value.get('frame',1),parameter=value.get('parameter',150),open=value.get('open',True))
        ins.set(path,updated);win.refresh()
    ins.button(tr('Elegir objeto original…'),choose,'choose_original_object')
    ins.note(value.get('template') or tr('Elige un objeto del escenario.'))
    modes=[(tr('Ocultar y dejar paso'),'hide'),(tr('Restaurar aspecto y colisión'),'restore'),(tr('Retirar del mundo'),'remove')]
    modes += [(tr('Mover puerta por frames'),'frame'),(tr('Girar puerta sobre pivote'),'pivot')]
    def operation(op):
        updated=dict(selector(value),operation=op)
        if op in {'frame','pivot'}:updated.update(frame=1,parameter=1 if op=='pivot' else 150,open=True)
        ins.set(path,updated);win.refresh()
    ins.combo(tr('Operación'),modes,value['operation'],operation,'original_operation')
    if value['operation'] in {'frame','pivot'}:
        ins.spin(tr('Frame destino'),value['frame'],lambda v:ins.set(path+('frame',),v),'original_frame',maximum=255)
        ins.spin(tr('Duración' if value['operation']=='pivot' else 'Velocidad'),value['parameter'],lambda v:ins.set(path+('parameter',),v),'original_parameter',True,.001,1000)
        if value['operation']=='pivot':ins.combo(tr('Dirección'),[(tr('Abrir'),True),(tr('Cerrar'),False)],value.get('open',True),lambda v:ins.set(path+('open',),v),'original_open')
    ins.note(tr('Ocultar conserva el objeto y permite restaurarlo. Retirar no lo recrea. El estado de visibilidad se conserva al guardar y volver a la escena; el movimiento de puertas necesita frames originales válidos y prueba en el juego.'))


class PassageDialog(QDialog):
    """Native hover/click binding; cancelling never edits the live document."""
    def __init__(self,win,target):
        from .click_actions import ClickActions
        super().__init__(win);self.win=win;self.fixed=bool(target.get('fixed_surface'));self.target=selector(target);self.source=copy.deepcopy(target)
        self.setWindowTitle(tr('Interacción al hacer clic'));self.resize(700,670)
        layout=QVBoxLayout(self);form=QFormLayout();layout.addLayout(form)
        form.addRow(tr('Superficie') if self.fixed else tr('Objeto'),QLabel(target.get('material','') if self.fixed else object_label(target)))
        default=tr('Salida') if self.fixed else win.backend.strings.get(target.get('description_key'),target.get('template',''))
        self.label=QLineEdit(target.get('name') or default);self.label.setObjectName('click_label');form.addRow(tr('Texto al pasar el ratón'),self.label)
        self.when=QComboBox();self.when.addItem(tr('Al hacer clic'),'object_clicked')
        if not self.fixed:self.when.addItem(tr('Al entrar en la escena'),'scene_start')
        form.addRow(tr('Cuándo'),self.when)
        self.operation=QComboBox();self.operation.addItem(tr('Sólo ejecutar las acciones'),'none')
        if not self.fixed:
            for label,op in [('Ocultar y dejar paso','hide'),('Retirar del mundo','remove'),('Restaurar aspecto y colisión','restore'),('Abrir puerta (frame 1)','frame_open'),('Cerrar puerta (frame 0)','frame_close')]:self.operation.addItem(tr(label),op)
        self.operation.setEnabled(not self.fixed);form.addRow(tr('Operación sobre el original'),self.operation)
        self.once=QCheckBox(tr('Una sola vez'));form.addRow(self.once)
        note=QLabel(tr('El texto aparece al señalar la superficie. Las acciones se ejecutan al pulsarla, nunca al acercarte. Puedes combinar acciones y añadir condiciones después en el evento. Un viaje debe terminar en otra escena.'));note.setWordWrap(True);layout.addWidget(note)
        self.error=QLabel();self.error.setWordWrap(True)
        root=win.doc.snapshot();scene=root['scenes'][win.doc.active]
        def ident(kind,stem):
            used={r['id'] for r in scene.get(kind,[])};i=1
            while stem+str(i) in used:i+=1
            return stem+str(i)
        self.object_id=ident('objects','click');self.event_index=len(scene['events'])
        scene['events'].append(dict(id=click_event_id(scene,target),when='object_clicked',object=self.object_id,once=False,actions=[{'show_note':{'title':tr('Nota'),'text':tr('Escribe aquí lo que leerá el jugador.')}}]))
        self.actions=ClickActions(win,root,self.event_index,self.error,self);layout.addWidget(self.actions,1);layout.addWidget(self.error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
    def accept(self):
        from .i18n import diagnostic
        from ..click_interactions import target_mesh,validate
        if not self.actions.commit():return
        root=self.actions.doc.snapshot();scene=root['scenes'][self.win.doc.active];event=scene['events'][self.event_index]
        event.update(when=self.when.currentData(),once=self.once.isChecked())
        event['actions']=copy.deepcopy(self.actions.event['actions'])
        if event['when']=='object_clicked':
            try:
                if self.fixed:
                    mesh=copy.deepcopy(self.source.get('interaction'));validate(mesh);position=self.source['position'];orientation=[0,0,0]
                else:position,orientation,mesh=target_mesh(self.win.backend,self.source)
                name=self.label.text().strip()
                from ..model import text
                text(name,'Texto al pasar el ratón')
            except (ValueError,TypeError,KeyError) as error:self.error.setText(diagnostic(str(error)));return
            scene.setdefault('objects',[]).append(dict(id=self.object_id,name=name,template='tracker_thing',transform=dict(position=position,orientation=orientation,placement='absolute'),interaction=mesh))
        else:event.pop('object',None)
        op=self.operation.currentData()
        if op!='none':
            action=dict(self.target,operation=op)
            if op in ('frame_open','frame_close'):action.update(operation='frame',frame=1 if op=='frame_open' else 0,parameter=150)
            event['actions'].insert(0,{'control_original':action})
        errors=[p.message for p in self.win.backend.validate(root).problems if p.severity=='ERROR']
        if errors:self.error.setText(diagnostic('\n'.join(errors)));return
        self.win.doc.data=root;self.win.history_time=0;self.win.selection=('events',self.event_index);self.win.changed(True);super().accept()


def use_selected(win,target=None,picker=False):
    if not win.doc or win.busy or not win.commit_properties():return
    if not hasattr(win.doc,'campaign') or win.doc.campaign.get('project_format') not in (9,10):raise ValueError(tr('Convierte primero el proyecto en una campaña moderna.'))
    if target is not None:value=target
    elif not picker and win.selection[0]=='original' and len(win.selection)==2:
        value=win.at(win.selection)
        if value.get('level')!=win.doc.data['level']['source']:raise ValueError(tr('Selecciona un objeto de la escena estática original.'))
    else:
        picker=OriginalObjectPicker(win)
        if picker.exec()!=QDialog.DialogCode.Accepted:return
        value=picker.selection
    PassageDialog(win,value).exec()
