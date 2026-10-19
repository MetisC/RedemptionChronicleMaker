"""Advanced stock constructor binding, with ordinary typed entity references."""
import copy
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QScrollArea,QWidget,QComboBox,QSpinBox,QDoubleSpinBox,QLineEdit,QLabel,QDialogButtonBox,QMessageBox,QListWidget,QPushButton
from .i18n import tr,diagnostic


class NativeScriptDialog(QDialog):
    def __init__(self,win,entity):
        super().__init__(win);self.win=win;self.entity=entity;self.controls=[];self.resize(640,640);self.setWindowTitle(tr('Script nativo · avanzado'))
        from ..native_scripts import available
        from .busy import busy
        with busy(win,tr('Leyendo scripts originales…')):self.scripts=available(win.backend.ws,win.backend.original_resources,win.doc.snapshot())
        layout=QVBoxLayout(self);self.choose=QComboBox();self.choose.setObjectName('native_script_class');self.choose.setEditable(True);self.choose.setInsertPolicy(QComboBox.InsertPolicy.NoInsert);self.choose.addItem(tr('Sin script nativo'),None)
        for name in sorted(self.scripts):self.choose.addItem(name,name)
        layout.addWidget(self.choose)
        note=QLabel(tr('Avanzado: el script original controla sus propios callbacks. Este objeto y sus referencias se crean al cargar la escena; se sustituyen sus acciones simples de creación inicial. Algunos scripts dependen de regiones o datos específicos de la campaña original. Usa Eventos para el comportamiento habitual.'));note.setWordWrap(True);layout.addWidget(note)
        scroll=QScrollArea();scroll.setWidgetResizable(True);self.body=QWidget();self.form=QFormLayout(self.body);scroll.setWidget(self.body);layout.addWidget(scroll,1)
        self.current=entity.get('native_script',{});self.choose.setCurrentIndex(max(0,self.choose.findData(self.current.get('class'))));self.populate();self.choose.currentIndexChanged.connect(self.populate)
        self.frames=list(entity.get('native_frames',[]));layout.addWidget(QLabel(tr('Frames nativos: el frame 0 es la posición inicial. Añade destinos en orden.')))
        self.frame_list=QListWidget();self.frame_list.setObjectName('native_frames');self.frame_list.setMaximumHeight(105);layout.addWidget(self.frame_list)
        bar=QHBoxLayout();layout.addLayout(bar);self.point=QComboBox();self.point.setObjectName('native_frame_point')
        for point in win.doc.data.get('waypoints',[]):self.point.addItem(point['name']+' · '+point['id'],point['id'])
        bar.addWidget(self.point,1);add=QPushButton(tr('Añadir frame'));bar.addWidget(add);remove=QPushButton(tr('Quitar selección'));bar.addWidget(remove)
        def refresh():self.frame_list.clear();self.frame_list.addItems([str(i+1)+' · '+name for i,name in enumerate(self.frames)])
        def append():
            if self.point.currentData() and len(self.frames)<127:self.frames.append(self.point.currentData());refresh()
        def discard():
            if self.frame_list.currentRow()>=0:self.frames.pop(self.frame_list.currentRow());refresh()
        add.clicked.connect(append);remove.clicked.connect(discard);refresh()
        if entity in win.doc.data.get('triggers',[]):
            self.frame_list.setVisible(False);self.point.setEnabled(False);add.setEnabled(False);remove.setEnabled(False)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.apply);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
    def populate(self):
        while self.form.rowCount():self.form.removeRow(0)
        self.controls=[];name=self.choose.currentData()
        if name is None:return
        record=self.scripts[name];values=self.current.get('parameters',[]) if self.current.get('class')==name else []
        for i,parameter in enumerate(record['parameters']):
            kind=parameter['type'];value=values[i]['value'] if i<len(values) else parameter.get('default',0 if kind in ('integer','float') else '')
            if kind in ('actor','thing','region','item'):
                control=QComboBox();control.addItem(tr('Selecciona una entidad…'),None)
                scene=self.win.doc.campaign['scenes'][self.win.doc.active]
                kinds={r['id']:r['kind'] for r in self.win.backend.resources['templates']}
                rows=(scene.get('triggers',[]) if kind=='region' else [r for r in scene['objects'] if kinds.get(r['template']) in ('items','weapons','armour')] if kind=='item' else scene['actors']+([] if kind=='actor' else scene['objects']+[r for r in scene.get('triggers',[]) if r.get('native_region') or r.get('native_script')]))
                for row in rows:control.addItem(row['name']+' · '+row['id'],row['id'])
                control.setCurrentIndex(max(0,control.findData(value)));control.setToolTip(control.currentText());control.currentTextChanged.connect(control.setToolTip)
            elif kind=='integer':control=QSpinBox();control.setRange(-2147483648,2147483647);control.setValue(value)
            elif kind=='float':control=QDoubleSpinBox();control.setRange(-1e7,1e7);control.setDecimals(5);control.setValue(value)
            else:control=QLineEdit(value);control.setMaxLength(255)
            control.setObjectName('native_parameter_'+str(i));self.controls.append((kind,control));self.form.addRow(parameter['label']+' · '+kind,control)
        self.form.addRow(QLabel(record['descriptor']))
    def apply(self):
        try:
            root=self.win.doc.snapshot();scene=root['scenes'][self.win.doc.active];row=next(r for r in scene['actors']+scene.get('objects',[])+scene.get('triggers',[]) if r['id']==self.entity['id']);name=self.choose.currentData()
            if self.choose.currentText()!=self.choose.itemText(self.choose.currentIndex()):raise ValueError(tr('Selecciona un script de la lista'))
            if self.frames:row['native_frames']=list(self.frames)
            else:row.pop('native_frames',None)
            if name is None:row.pop('native_script',None)
            else:
                args=[dict(type=kind,value=control.currentData() if kind in ('thing','actor','region','item') else control.text() if kind=='string' else control.value()) for kind,control in self.controls]
                row['native_script']=dict(class_=name,parameters=args);row['native_script']['class']=row['native_script'].pop('class_')
                for arg in args:
                    if arg['type']=='region':next(t for t in scene['triggers'] if t['id']==arg['value'])['native_region']=True
                native={row['id']}|{arg['value'] for arg in args if arg['type'] in ('thing','actor','region','item')}
                for event in scene['events']:
                    if event['when']=='scene_start' and not event.get('conditions'):event['actions']=[a for a in event['actions'] if a.get('spawn') not in native]
                scene['events'][:]=[e for e in scene['events'] if e['actions']]
                from ..native_scripts import placement
                placement(scene,self.scripts,{r['id']:r['kind'] for r in self.win.backend.resources['templates']})
            if name is None:
                if self.frames:
                    for event in scene['events']:
                        if event['when']=='scene_start' and not event.get('conditions'):event['actions']=[a for a in event['actions'] if a.get('spawn')!=row['id']]
                    scene['events'][:]=[e for e in scene['events'] if e['actions']]
                from ..native_scripts import placement
                placement(scene,self.scripts,{r['id']:r['kind'] for r in self.win.backend.resources['templates']})
            self.win.doc.data=copy.deepcopy(root);self.win.changed(True);self.accept()
        except (ValueError,TypeError,KeyError) as error:QMessageBox.warning(self,tr('Revisa el script'),diagnostic(error))


def edit_native_script(win,entity):
    if win.commit_properties():NativeScriptDialog(win,entity).exec()
