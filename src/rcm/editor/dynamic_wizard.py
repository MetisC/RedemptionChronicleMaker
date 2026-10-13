"""Small encounter assistant and adapters to existing action authoring controls."""
import copy
from PySide6.QtCore import Qt,QTimer
from PySide6.QtWidgets import (QDialog,QWizard,QWizardPage,QVBoxLayout,QHBoxLayout,QFormLayout,QLabel,QLineEdit,QComboBox,QSpinBox,QDoubleSpinBox,QPushButton,QListWidget,QListWidgetItem,QCheckBox,QGroupBox,QScrollArea,QDialogButtonBox,QMessageBox,QInputDialog)
from .i18n import tr,diagnostic
from .browser import ResourceDialog
from ..dynamic_encounters import MODES
from ..campaign_document import CampaignDocument
from ..service import source_text

DESCRIPTIONS={'ambush':'Un grupo aparece una vez.','waves':'Varios grupos aparecen uno tras otro.','continuous':'Crea nuevos enemigos mientras esté activo.','reinforcements':'Un grupo aparece cuando otro evento lo solicita.','boss':'Ejecuta acciones al bajar la vida del jefe.'}

class ActionsDialog(QDialog):
    """Reuse the ordinary event action inspector against a private draft."""
    def __init__(self,win,source,actions):
        super().__init__(win);self.setWindowTitle(tr('Al ocurrir esto…'));self.resize(660,580)
        self.source=copy.deepcopy(source);self.source['project_format']=10
        self.doc=CampaignDocument(win.backend.ws,self.source);self.doc.active=win.doc.active
        self.scene=self.doc.campaign['scenes'][self.doc.active];self.index=len(self.scene['events'])
        self.scene['events'].append({'id':'actions_draft','when':'scene_start','actions':copy.deepcopy(actions)})
        self.actions=self.scene['events'][-1]['actions'];self.win=win
        layout=QVBoxLayout(self);self.list=QListWidget();self.list.setMaximumHeight(105);layout.addWidget(self.list)
        bar=QHBoxLayout();layout.addLayout(bar)
        for label,fn in [('Añadir acción',self.add),('Quitar acción',self.remove)]:
            b=QPushButton(tr(label));b.clicked.connect(fn);bar.addWidget(b)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);layout.addWidget(self.scroll,1)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
        self.list.currentRowChanged.connect(self.render);self.refresh()
    def refresh(self):
        from ..campaign import ACTIONS
        selected=self.list.currentRow();self.list.blockSignals(True);self.list.clear()
        for a in self.actions:self.list.addItem(tr(ACTIONS.get(next(iter(a)),(next(iter(a)),None))[0]))
        self.list.setCurrentRow(min(max(0,selected),len(self.actions)-1));self.list.blockSignals(False);self.render()
    def add(self):self.actions.append({'reward_xp':1});self.refresh();self.list.setCurrentRow(len(self.actions)-1)
    def remove(self):
        if self.list.currentRow()>=0:self.actions.pop(self.list.currentRow());self.refresh()
    def render(self):
        index=self.list.currentRow();old=self.scroll.takeWidget()
        if old:old.deleteLater()
        if index<0:return
        dialog=self
        class Proxy:
            backend=dialog.win.backend;doc=dialog.doc;selection=('events',dialog.index,'actions',index)
            def at(self,path):
                value=self.doc.data
                for key in path:value=value[key]
                return value
            def guard(self,fn):
                try:return fn()
                except (ValueError,KeyError,TypeError) as error:QMessageBox.warning(dialog,tr('Revisa la acción'),diagnostic(error));return False
            def changed(self,rebuild=False):
                if rebuild:QTimer.singleShot(0,dialog.refresh)
            def _title(self):pass
            def set_value(self,path,value,optional=False):
                parent=self.at(path[:-1])
                if optional and value is None:parent.pop(path[-1],None)
                else:parent[path[-1]]=value
        from .inspector import Inspector
        from .campaign_panel import event_properties
        class ActionInspector(Inspector):
            def render(self):event_properties(self)
            def relationships(self):pass
        self.scroll.setWidget(ActionInspector(Proxy()))
    def accept(self):
        inspector=self.scroll.widget()
        if inspector:
            for control in inspector.findChildren(QLineEdit):
                if getattr(control,'_rcm_pending',False) and not control._rcm_commit():return
        super().accept()

class DynamicWizard(QWizard):
    def __init__(self,win,generator_id=None,position=None):
        super().__init__(win);self.win=win;self.open_snapshot=win.doc.snapshot();self.source=copy.deepcopy(self.open_snapshot);self.scene=self.source['scenes'][win.doc.active];self.edit_id=generator_id;self.position=position
        self.setObjectName('dynamic_wizard');self.setWindowTitle(tr('Encuentro dinámico'));self.resize(760,670)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        rows=self.scene.get('generators',[]);self.saved=next((copy.deepcopy(g) for g in rows if g['id']==generator_id),None)
        self.ident=generator_id or self.unique(rows,'dynamic')
        self.waves=[];self.phases=[];self.completion=[];self.completion_index=None;self.group_controls={};self.updating=False
        first=self.page(tr('¿Qué quieres crear?'));form=QFormLayout();first.addLayout(form)
        self.name=QLineEdit(self.saved['name'] if self.saved else tr('Encuentro de enemigos'));self.name.setObjectName('dynamic_name');form.addRow(tr('Nombre'),self.name)
        self.mode=QComboBox();self.mode.setObjectName('dynamic_mode')
        for key,label in MODES.items():self.mode.addItem(tr(label),key)
        form.addRow(tr('Tipo'),self.mode);self.explanation=QLabel();self.explanation.setWordWrap(True);first.addWidget(self.explanation)
        enemies=self.page(tr('¿Qué enemigos aparecen?'));bar=QHBoxLayout();enemies.addLayout(bar)
        self.wave=QComboBox();self.wave.setObjectName('dynamic_wave');bar.addWidget(self.wave,1)
        self.wave_buttons=[]
        for label,fn in [('Añadir oleada',self.add_wave),('Quitar oleada',self.remove_wave)]:
            b=QPushButton(tr(label));b.clicked.connect(fn);bar.addWidget(b);self.wave_buttons.append(b)
        self.enemies=QListWidget();self.enemies.setObjectName('dynamic_enemies');enemies.addWidget(self.enemies,1)
        bar=QHBoxLayout();enemies.addLayout(bar)
        for label,fn in [('Añadir enemigo…',self.add_enemy),('Cambiar enemigo…',self.change_enemy),('Quitar enemigo',self.remove_enemy)]:
            b=QPushButton(tr(label));b.clicked.connect(fn);bar.addWidget(b)
        groupform=QFormLayout();enemies.addLayout(groupform)
        self.quantity=self.spin('dynamic_quantity',1,128,3);self.quantity.setToolTip(tr('En continuo es un lote: crea esta cantidad, uno por intervalo, antes de elegir otro tipo.'));groupform.addRow(tr('Cantidad'),self.quantity)
        self.basic_interval=self.decimal('dynamic_basic_interval',.3,86400,5);groupform.addRow(tr('Crear uno cada (s)'),self.basic_interval)
        self.basic_cap=self.spin('dynamic_basic_cap',1,64,5);groupform.addRow(tr('Máximo enemigos vivos'),self.basic_cap)
        self.enemy_form=groupform
        self.delay=self.decimal('dynamic_delay',0,86400,0);groupform.addRow(tr('Esperar antes de esta oleada (s)'),self.delay)
        self.enemy_advanced,self.enemy_body=self.advanced(tr('Opciones del enemigo'),enemies)
        self.health=QComboBox();self.health.setObjectName('dynamic_health')
        for label,value in [('Original',0),('x0.5',.5),('x1',1),('x1.5',1.5),('x2',2),('x5',5),('Personalizada',-1)]:self.health.addItem(tr(label),value)
        self.enemy_body.addRow(tr('Vida'),self.health);self.custom_health=self.decimal('dynamic_custom_health',1,1000000,100);self.enemy_body.addRow(tr('Vida personalizada'),self.custom_health)
        self.weight=self.spin('dynamic_weight',1,1000,1);self.enemy_body.addRow(tr('Peso de selección'),self.weight)
        self.team=QComboBox();self.team.addItem(tr('Equipo original'),-1)
        for label,value in [('Sin equipo',8),('Peatones',10),('Enemigos',12)]:self.team.addItem(tr(label),value)
        self.enemy_body.addRow(tr('Equipo (override nativo)'),self.team)
        spawn=self.page(tr('¿Dónde y cuándo?'));form=QFormLayout();spawn.addLayout(form)
        self.placement=QComboBox();self.placement.setObjectName('dynamic_placement');self.placement.addItem(tr('Puntos de aparición'),'points');self.placement.addItem(tr('Cerca del jugador (el motor elige)'),'near_player');form.addRow(tr('Aparecen en'),self.placement)
        self.points=QListWidget();self.points.setObjectName('dynamic_points');spawn.addWidget(self.points,1)
        for p in self.scene.get('waypoints',[]):
            item=QListWidgetItem(p['name']);item.setData(Qt.ItemDataRole.UserRole,p['id']);item.setFlags(item.flags()|Qt.ItemFlag.ItemIsUserCheckable);item.setCheckState(Qt.CheckState.Unchecked);item.setToolTip(p['id']);self.points.addItem(item)
        if position is not None:
            key=self.unique(self.scene.get('waypoints',[]),'spawn');self.new_point={'id':key,'name':tr('Punto de aparición'),'transform':{'position':list(position),'orientation':[0,0,0]}}
            item=QListWidgetItem(self.new_point['name']);item.setData(Qt.ItemDataRole.UserRole,key);item.setFlags(item.flags()|Qt.ItemFlag.ItemIsUserCheckable);item.setCheckState(Qt.CheckState.Checked);self.points.addItem(item)
        else:self.new_point=None
        self.start=QComboBox();self.start.setObjectName('dynamic_start')
        for label,key in [('Al entrar en escena','scene_start'),('Al entrar en una zona','trigger_enter'),('Al usar un objeto','object_clicked'),('Al terminar conversación','conversation_ended'),('Al morir un actor','actor_killed'),('Al terminar un encuentro','encounter_complete'),('Después de unos segundos','timer'),('Cuando se cumple una condición','state_changed'),('Desde otro evento','manual')]:self.start.addItem(tr(label),key)
        form.addRow(tr('Empieza'),self.start);self.origin=QComboBox();self.origin.setObjectName('dynamic_origin');form.addRow(tr('Origen'),self.origin)
        self.start_delay=self.decimal('dynamic_start_delay',.15,86400,30);form.addRow(tr('Después de (s)'),self.start_delay)
        self.conditions=[];condition_button=QPushButton(tr('Elegir condición…'));condition_button.setObjectName('dynamic_start_condition');condition_button.clicked.connect(self.choose_start_condition);form.addRow(condition_button)
        final=self.page(tr('Qué ocurre al terminar'));self.summary=QLabel();self.summary.setWordWrap(True);final.addWidget(self.summary)
        self.completion_button=QPushButton(tr('Añadir acciones al terminar…'));self.completion_button.setObjectName('dynamic_completion');self.completion_button.clicked.connect(self.edit_completion);final.addWidget(self.completion_button)
        self.boss=QComboBox();self.boss.setObjectName('dynamic_boss');self.boss.addItem(tr('Generar un jefe'),'')
        for a in self.scene['actors']:self.boss.addItem(a['name'],a['id'])
        self.boss_title=QLabel(tr('Jefe'));final.addWidget(self.boss_title);final.addWidget(self.boss)
        self.phase_list=QListWidget();self.phase_list.setObjectName('dynamic_phases');self.phase_list.setMaximumHeight(150);final.addWidget(self.phase_list)
        phasebar=QHBoxLayout();final.addLayout(phasebar)
        self.phase_buttons=[]
        for label,fn in [('Añadir fase',self.add_phase),('Editar fase…',self.edit_phase),('Quitar fase',self.remove_phase)]:
            b=QPushButton(tr(label));b.clicked.connect(fn);phasebar.addWidget(b);self.phase_buttons.append(b)
        group,advanced=self.advanced(tr('Opciones avanzadas'),final);group.setObjectName('dynamic_advanced')
        self.max_alive=self.spin('dynamic_max_alive',1,64,5);advanced.addRow(tr('Máximo enemigos vivos'),self.max_alive)
        self.interval=self.decimal('dynamic_interval',.3,86400,5);advanced.addRow(tr('Crear uno cada (s)'),self.interval)
        self.max_total=self.spin('dynamic_max_total',0,1000000,0);advanced.addRow(tr('Máximo total (0 = sin límite)'),self.max_total)
        self.target_alive=self.spin('dynamic_target_alive',0,64,0);advanced.addRow(tr('Objetivo de vivos (0 = usar máximo)'),self.target_alive)
        self.persistence=QComboBox();self.persistence.setObjectName('dynamic_persistence')
        for label,key in [('Una vez','once'),('Continuar al volver','resume'),('Reiniciar al volver','reset'),('Repetir tras un tiempo','cooldown')]:self.persistence.addItem(tr(label),key)
        advanced.addRow(tr('Al volver'),self.persistence);self.cooldown=self.decimal('dynamic_cooldown',.3,86400,30);advanced.addRow(tr('Tiempo de repetición (s)'),self.cooldown)
        self.selection=QComboBox();self.selection.addItem(tr('Rotatorio'),'round_robin');self.selection.addItem(tr('Aleatorio ponderado'),'random');advanced.addRow(tr('Tipos en generador continuo'),self.selection)
        self.distribution=QComboBox();self.distribution.addItem(tr('Rotatorio'),'round_robin');self.distribution.addItem(tr('Aleatorio'),'random');advanced.addRow(tr('Distribución de puntos'),self.distribution)
        self.retry=self.spin('dynamic_retry',1,8,3);advanced.addRow(tr('Intentos de aparición'),self.retry)
        self.remove_on_stop=QCheckBox(tr('Retirar sólo sus enemigos al detener'));advanced.addRow(self.remove_on_stop)
        self.visual=QComboBox();self.visual.addItem(tr('Sin representación visual'),'')
        for o in self.scene.get('objects',[]):self.visual.addItem(o['name'],o['id'])
        advanced.addRow(tr('Representación visual'),self.visual)
        self.error=QLabel();self.error.setWordWrap(True);final.addWidget(self.error)
        self.basic_interval.valueChanged.connect(self.interval.setValue);self.interval.valueChanged.connect(self.basic_interval.setValue)
        self.basic_cap.valueChanged.connect(self.max_alive.setValue);self.max_alive.valueChanged.connect(self.basic_cap.setValue)
        self.mode.currentIndexChanged.connect(self.mode_changed);self.wave.currentIndexChanged.connect(self.refresh_enemies);self.enemies.currentRowChanged.connect(self.selected_enemy)
        self.quantity.valueChanged.connect(lambda v:self.set_group('count',v));self.weight.valueChanged.connect(lambda v:self.set_group('weight',v));self.team.currentIndexChanged.connect(lambda:self.set_group('team',self.team.currentData(),-1))
        self.health.currentIndexChanged.connect(self.set_health);self.custom_health.valueChanged.connect(self.set_health);self.delay.valueChanged.connect(self.set_delay);self.start.currentIndexChanged.connect(self.start_changed)
        self.boss.currentIndexChanged.connect(self.refresh_summary)
        if self.saved:self.restore()
        else:self.mode_changed()
        self.start_changed();self.refresh_summary()
        self.phase_list.setToolTip(tr('Se activa al detectar que la vida cruza este umbral mientras el actor sigue válido. Un golpe mortal puede saltarse la fase.'))
        self.interval.setToolTip(tr('Ritmo del generador continuo; las oleadas esperan a que muera el grupo anterior.'))
        self.setButtonText(QWizard.WizardButton.FinishButton,tr('Aplicar' if self.saved else 'Crear'))
    @staticmethod
    def unique(rows,stem):
        i=1
        while any(r['id']==stem+str(i) for r in rows):i+=1
        return stem+str(i)
    def page(self,title):
        page=QWizardPage();page.setTitle(title);scroll=QScrollArea();scroll.setWidgetResizable(True);container=__import__('PySide6.QtWidgets',fromlist=['QWidget']).QWidget();layout=QVBoxLayout(container);scroll.setWidget(container);outer=QVBoxLayout(page);outer.addWidget(scroll);self.addPage(page);return layout
    @staticmethod
    def spin(name,lo,hi,value):
        c=QSpinBox();c.setObjectName(name);c.setRange(lo,hi);c.setValue(value);return c
    @staticmethod
    def decimal(name,lo,hi,value):
        c=QDoubleSpinBox();c.setObjectName(name);c.setRange(lo,hi);c.setDecimals(2);c.setValue(value);return c
    @staticmethod
    def advanced(title,layout):
        group=QGroupBox(title);group.setCheckable(True);group.setChecked(False);outer=QVBoxLayout(group);body=__import__('PySide6.QtWidgets',fromlist=['QWidget']).QWidget();form=QFormLayout(body);outer.addWidget(body);body.hide();group.toggled.connect(body.setVisible);layout.addWidget(group);return group,form
    def mode_changed(self):
        mode=self.mode.currentData();self.explanation.setText(tr(DESCRIPTIONS[mode]));self.mode.setToolTip(tr(DESCRIPTIONS[mode]))
        group={'role':'boss' if mode=='boss' else 'enemy','template':'Rat','count':1 if mode in ('boss','continuous') else 3}
        self.waves=[{'groups':[copy.deepcopy(group)],'delay':0} for _ in range(3 if mode=='waves' else 1)]
        for wave in self.waves[1:]:wave['delay']=2
        self.max_alive.setValue(1 if mode=='boss' else 5);self.interval.setValue(5);self.phases=[{'id':'half','percent':50,'actions':[{'start_generator':self.ident+'_adds'}]},{'id':'quarter','percent':25,'actions':[{'stop_generator':self.ident+'_adds'}]}] if mode=='boss' else []
        self.start.setCurrentIndex(self.start.findData('manual' if mode=='reinforcements' else 'trigger_enter' if self.scene.get('triggers') or self.new_point else 'scene_start'))
        self.refresh_waves();self.refresh_summary()
    def refresh_waves(self):
        old=self.wave.currentIndex();self.wave.blockSignals(True);self.wave.clear()
        for i,w in enumerate(self.waves):self.wave.addItem(tr('Oleada ')+str(i+1),i)
        self.wave.setCurrentIndex(min(max(old,0),len(self.waves)-1));self.wave.blockSignals(False);self.refresh_enemies()
    def refresh_enemies(self):
        self.enemies.blockSignals(True);self.enemies.clear();wi=self.wave.currentIndex()
        if wi>=0:
            for e in self.waves[wi]['groups']:self.enemies.addItem(e['template']+' × '+str(e['count']))
            self.delay.blockSignals(True);self.delay.setValue(self.waves[wi].get('delay',0));self.delay.blockSignals(False)
        self.enemies.blockSignals(False);self.enemies.setCurrentRow(0);self.selected_enemy()
    def group(self):
        wi=self.wave.currentIndex();ei=self.enemies.currentRow()
        return self.waves[wi]['groups'][ei] if wi>=0 and 0<=ei<len(self.waves[wi]['groups']) else None
    def selected_enemy(self,*args):
        group=self.group();self.updating=True
        for control in (self.quantity,self.health,self.custom_health,self.weight,self.team):control.setEnabled(group is not None)
        if group:
            self.quantity.setValue(group['count']);self.weight.setValue(group.get('weight',1));self.team.setCurrentIndex(max(0,self.team.findData(group.get('team',-1))))
            value=-1 if 'health' in group else group.get('health_multiplier',0);index=self.health.findData(value)
            if index<0:self.health.addItem('x'+str(value),value);index=self.health.count()-1
            self.health.setCurrentIndex(index);self.custom_health.setValue(group.get('health',100))
        self.updating=False
    def set_group(self,key,value,omit=None):
        if self.updating or not self.group():return
        if value==omit:self.group().pop(key,None)
        else:self.group()[key]=value
        if key=='count':self.enemies.currentItem().setText(self.group()['template']+' × '+str(value))
    def set_health(self,*args):
        if self.updating or not self.group():return
        group=self.group();group.pop('health',None);group.pop('health_multiplier',None);value=self.health.currentData()
        if value==-1:group['health']=self.custom_health.value()
        elif value:group['health_multiplier']=value
    def set_delay(self,value):
        if self.wave.currentIndex()>=0:self.waves[self.wave.currentIndex()]['delay']=value
    def add_enemy(self):
        dialog=ResourceDialog(self.win.backend,'actors',self);dialog.browser.enemies.setCurrentIndex(1)
        if dialog.exec()==QDialog.DialogCode.Accepted:
            rows=self.waves[self.wave.currentIndex()]['groups'];rows.append({'role':self.unique([{'id':e['role']} for e in rows],'enemy'),'template':dialog.selection,'count':1});self.refresh_enemies();self.enemies.setCurrentRow(len(rows)-1)
    def change_enemy(self):
        if not self.group():return
        dialog=ResourceDialog(self.win.backend,'actors',self);dialog.browser.enemies.setCurrentIndex(1)
        if dialog.exec()==QDialog.DialogCode.Accepted:self.group()['template']=dialog.selection;self.refresh_enemies()
    def remove_enemy(self):
        if self.group():self.waves[self.wave.currentIndex()]['groups'].pop(self.enemies.currentRow());self.refresh_enemies()
    def add_wave(self):
        if self.mode.currentData()!='waves':return
        self.waves.append({'groups':[{'role':'enemy','template':'Rat','count':3}],'delay':2});self.refresh_waves();self.wave.setCurrentIndex(len(self.waves)-1)
    def remove_wave(self):
        if len(self.waves)>1:self.waves.pop(self.wave.currentIndex());self.refresh_waves()
    def start_changed(self):
        kind=self.start.currentData();self.origin.clear();category={'trigger_enter':'triggers','object_clicked':'objects','conversation_ended':'conversations','actor_killed':'actors','encounter_complete':'encounters'}.get(kind)
        if category:
            if kind=='trigger_enter' and self.new_point:self.origin.addItem(tr('Nueva zona junto al punto de aparición'),'@new_zone')
            for r in self.scene.get(category,[]):self.origin.addItem(r.get('name',r['id']),r['id'])
        self.origin.setEnabled(category is not None);self.start_delay.setEnabled(kind=='timer')
    def choose_start_condition(self):
        # Existing flags/quests/actors can be selected without a programming field.
        labels=[tr('Flag activado'),tr('Misión completada'),tr('Sólo queda un enemigo en otro encuentro')]
        choice,ok=QInputDialog.getItem(self,tr('Empieza cuando…'),tr('Condición'),labels,0,False)
        if not ok:return
        if choice==labels[0]:values=[(key,key) for key in self.source.get('state',{}).get('flags',{})]
        elif choice==labels[1]:values=[(q['title'],q['id']) for q in self.source.get('quests',[])]
        else:values=[(g['name'],g['id']) for g in self.scene.get('generators',[]) if g['id']!=self.edit_id]
        if not values:QMessageBox.information(self,tr('Primero crea el origen'),tr('No hay un origen disponible para esta condición.'));return
        label,ok=QInputDialog.getItem(self,tr('Origen'),tr('Selecciona'),[v[0] for v in values],0,False)
        if ok:
            key=next(v[1] for v in values if v[0]==label)
            self.conditions=[{'flag':key,'is_set':True}] if choice==labels[0] else [{'quest':key,'state':'complete'}] if choice==labels[1] else [{'generator_state':{'generator':key,'state':'active'}},{'generator_count':{'generator':key,'counter':'alive','comparison':'<=','value':1}}]
    def config(self):
        g=copy.deepcopy(self.saved or {});g.update(id=self.ident,name=self.name.text().strip(),mode=self.mode.currentData(),waves=copy.deepcopy(self.waves),max_alive=self.max_alive.value(),spawn_points=[self.points.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.points.count()) if self.points.item(i).checkState()==Qt.CheckState.Checked],placement=self.placement.currentData(),interval=self.interval.value(),max_total=self.max_total.value(),target_alive=self.target_alive.value(),persistence=self.persistence.currentData(),cooldown=self.cooldown.value(),selection=self.selection.currentData(),point_selection=self.distribution.currentData(),retry_limit=self.retry.value(),remove_on_stop=self.remove_on_stop.isChecked())
        g.pop('visual',None)
        if self.visual.currentData():g['visual']=self.visual.currentData()
        if g['mode']=='boss':
            g['boss']={'actor':self.boss.currentData()} if self.boss.currentData() else {'role':next((e['role'] for wave in g['waves'] for e in wave['groups'] if e['role']==(self.saved or {}).get('boss',{}).get('role')),next((e['role'] for wave in g['waves'] for e in wave['groups'] if e['count']==1),'boss'))};g['phases']=copy.deepcopy(self.phases)
            if self.boss.currentData():g['waves']=[{'groups':[],'delay':0}]
        else:g.pop('boss',None);g.pop('phases',None)
        return g
    def preview_source(self):
        root=copy.deepcopy(self.source);root['project_format']=10;s=root['scenes'][self.win.doc.active];rows=s.setdefault('generators',[]);g=self.config()
        index=next((i for i,row in enumerate(rows) if row['id']==self.ident),None)
        if index is None:rows.append(g)
        else:rows[index]=g
        if self.new_point:s.setdefault('waypoints',[]).append(copy.deepcopy(self.new_point))
        if self.mode.currentData()=='boss' and any(a.get('start_generator')==self.ident+'_adds' or a.get('stop_generator')==self.ident+'_adds' for p in self.phases for a in p['actions']) and not any(r['id']==self.ident+'_adds' for r in rows):
            rows.append({'id':self.ident+'_adds','name':tr('Refuerzos del jefe'),'mode':'reinforcements','max_alive':2,'spawn_points':g['spawn_points'],'placement':g['placement'],'persistence':'once','waves':[{'groups':[{'role':'adds','template':'Rat','count':2}]}]})
        return root
    def edit_completion(self):
        dialog=ActionsDialog(self.win,self.preview_source(),self.completion)
        if dialog.exec()==QDialog.DialogCode.Accepted:self.completion=copy.deepcopy(dialog.actions);self.refresh_summary()
    def add_phase(self):
        self.phases.append({'id':self.unique(self.phases,'phase'),'percent':50,'actions':[]});self.refresh_summary();self.phase_list.setCurrentRow(len(self.phases)-1);self.edit_phase()
    def remove_phase(self):
        if self.phase_list.currentRow()>=0:self.phases.pop(self.phase_list.currentRow());self.refresh_summary()
    def edit_phase(self):
        index=self.phase_list.currentRow()
        if index<0:return
        phase=self.phases[index];edit=QDialog(self);edit.setWindowTitle(tr('Fase del jefe'));layout=QVBoxLayout(edit);form=QFormLayout();layout.addLayout(form)
        unit=QComboBox();unit.addItem(tr('Porcentaje'),'percent');unit.addItem(tr('Puntos de vida'),'value');unit.setCurrentIndex(0 if 'percent' in phase else 1);form.addRow(tr('Medida'),unit)
        value=self.decimal('phase_threshold',.1,1000000,phase.get('percent',phase.get('value',50)));form.addRow(tr('Cuando la vida baje a'),value)
        once=QCheckBox(tr('Una sola vez'));once.setChecked(phase.get('once',True));form.addRow(once)
        actions=copy.deepcopy(phase['actions']);button=QPushButton(tr('Elegir acciones…'));layout.addWidget(button)
        def choose():
            dialog=ActionsDialog(self.win,self.preview_source(),actions)
            if dialog.exec()==QDialog.DialogCode.Accepted:actions[:]=copy.deepcopy(dialog.actions)
        button.clicked.connect(choose)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(edit.accept);buttons.rejected.connect(edit.reject);layout.addWidget(buttons)
        if edit.exec()==QDialog.DialogCode.Accepted:
            phase.pop('percent',None);phase.pop('value',None);phase[unit.currentData()]=value.value();phase['once']=once.isChecked();phase['actions']=actions;self.refresh_summary()
    def refresh_summary(self,*args):
        if not hasattr(self,'phase_list'):return
        is_boss=self.mode.currentData()=='boss'
        for widget in [self.boss_title,self.boss,self.phase_list,*self.phase_buttons]:widget.setVisible(is_boss)
        for widget in self.wave_buttons:widget.setVisible(self.mode.currentData()=='waves')
        self.enemy_form.setRowVisible(self.basic_interval,self.mode.currentData()=='continuous');self.enemy_form.setRowVisible(self.basic_cap,self.mode.currentData()=='continuous')
        self.phase_list.clear()
        for p in self.phases:self.phase_list.addItem(tr('Al bajar al ')+str(p.get('percent',p.get('value')))+('%' if 'percent' in p else ' HP')+tr(' · ')+str(len(p['actions']))+tr(' acciones'))
        self.summary.setText(tr('El combate termina cuando no quedan enemigos vivos ni oleadas pendientes. Puedes usar las mismas acciones que en cualquier evento. Las fases se detectan por muestreo; un golpe mortal puede saltarse un umbral.'))
    def restore(self):
        g=self.saved
        self.completion_index=next((i for i,e in enumerate(self.scene['events']) if e.get('when')=='generator_complete' and e.get('generator')==self.ident),None)
        if self.completion_index is not None:self.completion=copy.deepcopy(self.scene['events'][self.completion_index]['actions'])
        self.mode.blockSignals(True);self.mode.setCurrentIndex(self.mode.findData(g['mode']));self.mode.blockSignals(False);self.explanation.setText(tr(DESCRIPTIONS[g['mode']]))
        self.waves=copy.deepcopy(g['waves']);self.phases=copy.deepcopy(g.get('phases',[]));self.refresh_waves()
        for control,key,default in [(self.max_alive,'max_alive',5),(self.interval,'interval',5),(self.max_total,'max_total',0),(self.target_alive,'target_alive',0),(self.retry,'retry_limit',3),(self.cooldown,'cooldown',30)]:control.setValue(g.get(key,default))
        for control,key,default in [(self.placement,'placement','points'),(self.persistence,'persistence','once'),(self.selection,'selection','round_robin'),(self.distribution,'point_selection','round_robin'),(self.visual,'visual','')]:control.setCurrentIndex(max(0,control.findData(g.get(key,default))))
        self.boss.setCurrentIndex(max(0,self.boss.findData(g.get('boss',{}).get('actor',''))));self.remove_on_stop.setChecked(g.get('remove_on_stop',False))
        for i in range(self.points.count()):self.points.item(i).setCheckState(Qt.CheckState.Checked if self.points.item(i).data(Qt.ItemDataRole.UserRole) in g.get('spawn_points',[]) else Qt.CheckState.Unchecked)
        self.start.setCurrentIndex(self.start.findData('manual'))
    def accept(self):
        try:
            if self.win.doc.snapshot()!=self.open_snapshot:raise ValueError(tr('El proyecto cambió mientras el asistente estaba abierto. Vuelve a abrirlo.'))
            candidate=self.preview_source();s=candidate['scenes'][self.win.doc.active]
            if self.start.currentData()!='manual':
                kind=self.start.currentData();e={'id':self.unique(s['events'],'dynamic_start'),'when':kind,'once':False,'actions':[{'start_generator':self.ident}]}
                field={'trigger_enter':'trigger','object_clicked':'object','conversation_ended':'conversation','actor_killed':'actor','encounter_complete':'encounter'}.get(kind)
                if field:e[field]=self.origin.currentData()
                if e.get('trigger')=='@new_zone':
                    point=self.new_point['transform'];key=self.unique(s.get('triggers',[]),'combat_zone');s.setdefault('triggers',[]).append({'id':key,'name':tr('Zona del encuentro'),'shape':'sphere','radius':160,'transform':copy.deepcopy(point),'once':False});e['trigger']=key
                if kind=='timer':e['seconds']=self.start_delay.value()
                if kind=='state_changed':e['conditions']=copy.deepcopy(self.conditions)
                s['events'].append(e)
            if self.completion_index is not None:
                if self.completion:s['events'][self.completion_index]['actions']=copy.deepcopy(self.completion)
                else:s['events'].pop(self.completion_index)
            elif self.completion:s['events'].append({'id':self.unique(s['events'],'dynamic_end'),'when':'generator_complete','generator':self.ident,'once':True,'actions':copy.deepcopy(self.completion)})
            errors=[p.message for p in self.win.backend.validate(candidate).problems if p.severity=='ERROR']
            if errors:raise ValueError('\n'.join(errors))
            upgraded=self.open_snapshot.get('project_format',0)<10
            if upgraded:
                from ..project_safety import backup_source
                backup_source(self.win.backend.ws,self.open_snapshot['chronicle']['id'],source_text(self.open_snapshot).encode('utf8'))
            self.win.doc.data=candidate;self.win.history_time=0;self.win.selection=('generators',next(i for i,g in enumerate(s['generators']) if g['id']==self.ident));self.win.changed(True)
            self.win.campaign_panel.path=('scenes',self.win.doc.active,'generators',self.win.selection[1]);self.win.campaign_panel.navigate(self.win.campaign_panel.path)
            if upgraded:self.win.statusBar().showMessage(tr('Encuentro creado. Proyecto actualizado con copia de seguridad.'),6000)
            super().accept()
        except (ValueError,KeyError,TypeError) as error:self.error.setText(diagnostic(error))

def open_dynamic(win,generator_id=None,position=None):
    if win.busy or not win.doc or not win.commit_properties():return
    if not hasattr(win.doc,'campaign'):QMessageBox.information(win,tr('Encuentro dinámico'),tr('Convierte primero este proyecto antiguo en una campaña.'));return
    DynamicWizard(win,generator_id,position).exec()
