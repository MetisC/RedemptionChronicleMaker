"""Optional activation-zone controls, committed through the normal document."""
import copy
from PySide6.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QCheckBox,QComboBox,QSpinBox,QDoubleSpinBox,QDialogButtonBox,QLabel
from .i18n import tr,diagnostic


def edit_zone(win,trigger,kind):
    key=kind+'_zone';value=dict(resource='',volume=75,min_distance=128,max_distance=512) if kind=='sound' else dict(entity='',color=[1,1,1],intensity=1,radius=300,style='constant');value.update(copy.deepcopy(trigger.get(key,{})))
    dialog=QDialog(win);dialog.resize(570,520);dialog.setWindowTitle(tr('Zona sonora' if kind=='sound' else 'Zona de luz dinámica'));layout=QVBoxLayout(dialog);form=QFormLayout();layout.addLayout(form)
    enabled=QCheckBox(tr('Activar esta zona'));enabled.setObjectName('zone_enabled');enabled.setChecked(key in trigger);form.addRow(enabled);fields={}
    def combo(label,name,options,current):
        c=QComboBox();c.setObjectName('zone_'+name)
        for title,data in options:c.addItem(title,data)
        c.setCurrentIndex(c.findData(current));form.addRow(tr(label),c);fields[name]=c
    def number(label,name,low,high,floating=False):
        c=QDoubleSpinBox() if floating else QSpinBox();c.setObjectName('zone_'+name);c.setRange(low,high);c.setValue(value[name]);form.addRow(tr(label),c);fields[name]=c
    if kind=='sound':
        combo('Sonido','resource',[(r['id'],r['id']) for r in win.backend.resources['entries'] if r['extension'].lower()=='.wav'],value['resource']);number('Volumen','volume',0,100);number('Radio interior','min_distance',0,100000,True);number('Radio exterior','max_distance',1,100000,True)
    else:
        from ..dynamic_targets import choices
        scene=win.doc.campaign['scenes'][win.doc.active]
        combo('Entidad','entity',[(r['name'],r['id']) for r in win.doc.data['actors']+win.doc.data['objects']]+choices(scene),value['entity'])
        from ..world_effects import STYLES
        combo('Estilo','style',[(s,s) for s in STYLES],value['style']);number('Intensidad','intensity',0,1000,True);number('Radio','radius',.01,100000,True)
        for i,label in enumerate(('Rojo','Verde','Azul')):
            value['color'+str(i)]=value['color'][i];number(label,'color'+str(i),0,1,True)
    flag=QComboBox();flag.setObjectName('zone_flag');flag.addItem(tr('Siempre activa'),None)
    for alias in win.doc.data.get('state',{}).get('flags',{}):flag.addItem(alias,alias)
    flag.setCurrentIndex(max(0,flag.findData(trigger.get('zone_flag',{}).get('flag'))));form.addRow(tr('Activación por flag'),flag)
    flag_value=QCheckBox(tr('Cuando el flag está activado'));flag_value.setObjectName('zone_flag_value');flag_value.setChecked(trigger.get('zone_flag',{}).get('is_set',True));flag_value.setEnabled(flag.currentData() is not None);flag.currentIndexChanged.connect(lambda:flag_value.setEnabled(flag.currentData() is not None));form.addRow(flag_value)
    note=QLabel(tr('Usa el volumen del trigger para activar un sonido situado o una luz puntual. Es una alternativa de activación; no reproduce el recorte por sectores de las cajas originales.'));note.setWordWrap(True);layout.addWidget(note)
    error=QLabel();error.setWordWrap(True);layout.addWidget(error)
    buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);layout.addWidget(buttons);buttons.rejected.connect(dialog.reject)
    def accept():
        try:
            candidate=copy.deepcopy(trigger)
            if enabled.isChecked():
                result={name:(field.currentData() if isinstance(field,QComboBox) else field.value()) for name,field in fields.items()}
                if kind=='light':result['color']=[result.pop('color'+str(i)) for i in range(3)]
                candidate[key]=result
            else:candidate.pop(key,None)
            if flag.currentData() is not None and any(k in candidate for k in ('sound_zone','light_zone')):candidate['zone_flag']={'flag':flag.currentData(),'is_set':flag_value.isChecked()}
            else:candidate.pop('zone_flag',None)
            from ..scene_zones import validate
            from ..dynamic_targets import candidates
            scene=win.doc.campaign['scenes'][win.doc.active];test=dict(scene,triggers=[candidate if r['id']==trigger['id'] else r for r in scene['triggers']]);validate(test,{**{r['id']:r for r in scene['actors']},**candidates(scene)},{r['id']:r for r in scene.get('objects',[])},win.backend.resources,win.doc.data.get('state',{}).get('flags',{}))
            trigger.clear();trigger.update(candidate);win.history_time=0;win.changed(True);dialog.accept()
        except ValueError as exc:error.setText(diagnostic(exc))
    buttons.accepted.connect(accept);dialog.exec()
