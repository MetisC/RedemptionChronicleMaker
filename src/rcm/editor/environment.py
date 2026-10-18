"""Scene environment intent in the existing Level inspector."""
import copy
from PySide6.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QScrollArea,QWidget,QComboBox,QDoubleSpinBox,QSpinBox,QLabel,QDialogButtonBox,QCheckBox,QMessageBox
from .i18n import tr,diagnostic
from ..environment_fields import validate


class EnvironmentDialog(QDialog):
    def __init__(self,win):
        super().__init__(win);self.win=win;self.level=win.doc.data['level'];self.fields={};self.resize(600,680)
        self.setWindowTitle(tr('Entorno de la escena'))
        layout=QVBoxLayout(self);scroll=QScrollArea();scroll.setWidgetResizable(True);body=QWidget();self.form=QFormLayout(body);scroll.setWidget(body);layout.addWidget(scroll)
        current=self.level.get('environment',{})
        def combo(key,label,choices,value):
            c=QComboBox();c.setObjectName('environment_'+key);c.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon);c.setMinimumContentsLength(12)
            for title,data in choices:c.addItem(title,data)
            index=c.findData(value)
            if index<0:c.addItem(str(value),value);index=c.count()-1
            c.setCurrentIndex(index);c.setToolTip(c.currentText());c.currentTextChanged.connect(c.setToolTip);self.form.addRow(label,c);self.fields[key]=c;return c
        self.combo=combo
        for kind,label,extensions in [('music',tr('Música inicial'),{'.mp3','.wav'}),('ambient',tr('Ambiente inicial'),{'.wav'})]:
            entries=win.backend.resources['entries'];counts={}
            for e in entries:
                if e['extension'].lower() in extensions and len(e['id']+e['extension'])<=31:counts[e['id']]=counts.get(e['id'],0)+1
            choices=[(tr('Heredar del perfil'),None),(tr('Silencio'),'')]+[(name,name) for name,n in sorted(counts.items()) if n==1]
            combo(kind,label,choices,current.get(kind))
            key=kind+'_volume';control=QSpinBox();control.setObjectName('environment_'+key);control.setRange(-1,100);control.setSpecialValueText(tr('Heredar del perfil'));control.setValue(current.get(key,-1));self.fields[key]=control;self.form.addRow(tr('Volumen')+' · '+label,control)
        fog=current.get('fog',{})
        fog_mode=combo('fog_mode',tr('Niebla'),[(tr('Heredar del perfil'),None),(tr('Sin niebla'),'none'),(tr('Lineal'),'linear'),(tr('Exponencial'),'exponential')],fog.get('mode'))
        for i,label in enumerate(['R','G','B']):
            control=QSpinBox();control.setObjectName('environment_color_'+label);control.setRange(0,255);control.setValue(fog.get('color',[64,64,64])[i]);self.fields['color_'+label]=control;self.form.addRow(tr('Color')+' '+label,control)
        for key,label,default in [('start',tr('Distancia 1 / densidad exponencial'),200),('end',tr('Distancia 2'),2000)]:
            c=QDoubleSpinBox();c.setObjectName('environment_fog_'+key);c.setRange(0,1e7);c.setDecimals(5);c.setValue(fog.get(key,default));self.fields[key]=c;self.form.addRow(label,c)
        self.clip=QCheckBox(tr('Cambiar distancia de dibujo (ZClip)'));self.clip.setChecked('zclip' in current);self.form.addRow(self.clip)
        c=QDoubleSpinBox();c.setObjectName('environment_zclip');c.setRange(0,1e7);c.setValue(current.get('zclip',0));self.fields['zclip']=c;self.form.addRow(tr('ZClip · 0 usa el valor del motor'),c)
        def fog_enabled():
            mode=fog_mode.currentData()
            for key in ['color_R','color_G','color_B','start']:self.fields[key].setEnabled(mode in ('linear','exponential'))
            self.fields['end'].setEnabled(mode=='linear')
            if mode=='exponential' and self.fields['start'].value()>1:self.fields['start'].setValue(.001)
        fog_mode.currentIndexChanged.connect(fog_enabled);fog_enabled();self.clip.toggled.connect(c.setEnabled);c.setEnabled(self.clip.isChecked())
        self.sky=QCheckBox(tr('Cambiar cielo'));self.sky.setChecked('sky' in self.level);self.form.addRow(self.sky)
        for key,label,ext in [('model',tr('Modelo de cielo'),'.nod'),('animation',tr('Animación de cielo'),'.nad')]:
            values=sorted({e['id'] for e in win.backend.resources['entries'] if e['extension'].lower()==ext})
            combo('sky_'+key,label,[(tr('Sin cielo'),'')]+[(v,v) for v in values],self.level.get('sky',{}).get(key,''))
        note=QLabel(tr('Las distancias usan unidades del motor. El entorno no modifica geometría ni lightmaps. EAX se hereda: el motor da prioridad a la escena estática original.'));note.setWordWrap(True);self.form.addRow(note)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.apply);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
    def apply(self):
        try:
            values={}
            for key in ('music','ambient'):
                value=self.fields[key].currentData()
                if value is not None:values[key]=value
                volume=self.fields[key+'_volume'].value()
                if volume>=0:values[key+'_volume']=volume
            mode=self.fields['fog_mode'].currentData()
            if mode is not None:values['fog']=dict(mode=mode,color=[self.fields['color_'+k].value() for k in 'RGB'],start=self.fields['start'].value(),end=self.fields['end'].value())
            if self.clip.isChecked():values['zclip']=self.fields['zclip'].value()
            validate(values,self.win.backend.resources)
            candidate=copy.deepcopy(self.win.doc.snapshot());level=candidate['scenes'][self.win.doc.active]['level'] if 'scenes' in candidate else candidate['level']
            if values:level['environment']=values
            else:level.pop('environment',None)
            sky={k:self.fields['sky_'+k].currentData() for k in ('model','animation')}
            if self.sky.isChecked():level['sky']=sky
            else:level.pop('sky',None)
            # Validate the actual level/sky resource contract without requiring
            # unrelated unfinished story drafts to be valid.
            from ..model import parse_project
            scene={'schema':1,'chronicle':{'id':'env_check','name':'Environment'},'level':level,'actors':[],'objects':[],'conversations':[],'events':[]}
            parse_project(__import__('yaml').safe_dump(scene),self.win.backend.levels,self.win.backend.resources,allow_empty=True)
            self.level.clear();self.level.update(level);self.win.changed(True);self.accept()
        except (ValueError,OSError) as error:QMessageBox.warning(self,tr('Revisa el entorno'),diagnostic(error))


def open_environment(win):
    if win.commit_properties():EnvironmentDialog(win).exec()
