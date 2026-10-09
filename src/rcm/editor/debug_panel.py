"""Playtest hub: existing build/deploy/run, observations from disk, never fake state."""
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QCheckBox,QTreeWidget,QTreeWidgetItem,QPlainTextEdit,QInputDialog
from ..debugging import parse_trace

class DebugPanel(QWidget):
    def __init__(self,win):
        super().__init__();self.win=win;self.observed={};layout=QVBoxLayout(self);bar=QHBoxLayout()
        for title,name,cb in [('Build','debug_build',win.build_project),('Deploy','debug_deploy',lambda:win.campaign_panel.deploy()),('Ejecutar','debug_run',lambda:win.campaign_panel.run_game()),('Leer trace','debug_refresh',self.read_trace),('+ Checklist','debug_bookmark',self.bookmark)]:
            b=QPushButton(title);b.setObjectName(name);b.clicked.connect(lambda checked=False,cb=cb:win.guard(cb));bar.addWidget(b)
        layout.addLayout(bar);self.enabled=QCheckBox('Build de desarrollo: instrumentar flags, quests y acciones');self.enabled.setObjectName('debug_instrumentation');self.enabled.toggled.connect(self.toggle);layout.addWidget(self.enabled)
        note=QLabel('Datos leídos de logs reales; no son estado en vivo ni resultados de tests. Quest Watch observa flags de progreso del controlador, no inspecciona el journal.');note.setWordWrap(True);layout.addWidget(note)
        self.tree=QTreeWidget();self.tree.setHeaderLabels(['Tipo','Estado / Mensaje','Tiempo']);self.tree.setObjectName('runtime_trace');self.tree.itemDoubleClicked.connect(self.navigate);layout.addWidget(self.tree,3)
        self.checklist=QPlainTextEdit();self.checklist.setReadOnly(True);layout.addWidget(self.checklist,1)
    def root(self):return self.win.doc.snapshot() if self.win.doc else {}
    def refresh(self):
        root=self.root();self.enabled.blockSignals(True);self.enabled.setEnabled(root.get('project_format') in (5,9));self.enabled.setChecked(root.get('build_options',{}).get('debug',True));self.enabled.blockSignals(False)
        self.checklist.setPlainText('\n\n'.join(p['name']+'\n'+p['instructions'] for p in root.get('playtests',[])))
    def toggle(self,value):
        if self.win.doc and self.root().get('project_format') in (5,9):self.win.doc.campaign.setdefault('build_options',{})['debug']=value;self.win.changed(False)
    def bookmark(self):
        if not self.win.project_resources_panel.upgrade():return
        name,ok=QInputDialog.getText(self,'Checklist de prueba','Nombre')
        if not ok:return
        instructions,ok=QInputDialog.getMultiLineText(self,'Resultado esperado','Pasos y estado esperado')
        if ok:
            rows=self.win.doc.campaign.setdefault('playtests',[]);rows.append(dict(id='test'+str(len(rows)+1),name=name,instructions=instructions));self.win.changed(True)
    def read_trace(self):
        if not self.win.doc or not self.win.backend.ws.game:raise ValueError('Abre proyecto y selecciona instalación')
        root=self.root();ident=root['chronicle']['id'];file=self.win.backend.ws.game/'RCM'/ident/'runtime_trace.log'
        if not file.is_file():raise ValueError('Todavía no existe un trace nativo para esta crónica. Ejecuta una partida')
        mapping=self.win.backend.ws.output('build/'+ident+'/source_map.json');mapping=json.loads(mapping.read_text()) if mapping.exists() else {}
        self.observed=parse_trace(file.read_text(encoding='cp1252',errors='replace')[-256000:],mapping);self.tree.clear()
        for name,val in self.observed['flags'].items():self.tree.addTopLevelItem(QTreeWidgetItem(['Flag',name+' = '+str(val),'Último dato del log']))
        for name,val in self.observed['quests'].items():self.tree.addTopLevelItem(QTreeWidgetItem(['Quest',name+' '+str(val),'Último dato del log']))
        for name,val in self.observed['spawned'].items():self.tree.addTopLevelItem(QTreeWidgetItem(['Spawn',name+' GUID '+str(val),'Identidad observada, no vida actual']))
        for row in self.observed['events']:
            item=QTreeWidgetItem([row['severity'],row['message'],str(row['time'] or '')]);item.setData(0,Qt.ItemDataRole.UserRole,row.get('context'));self.tree.addTopLevelItem(item)
    def navigate(self,item,column):
        ctx=item.data(0,Qt.ItemDataRole.UserRole)
        if not ctx or not hasattr(self.win.doc,'campaign'):return
        if ctx.get('quest'):
            for qi,q in enumerate(self.win.doc.campaign.get('quests',[])):
                if q['id']==ctx['quest']:self.win.campaign_panel.navigate(('quests',qi));return
        for si,s in enumerate(self.win.doc.campaign['scenes']):
            if s['id']==ctx.get('scene'):
                path=('scenes',si)
                for ci,c in enumerate(s['conversations']):
                    if c['id']==ctx.get('conversation'):self.win.campaign_panel.navigate(path+('conversations',ci));return
                for ei,e in enumerate(s['events']):
                    if e['id']==ctx.get('event'):
                        path+=('events',ei)
                        if ctx.get('action') and 0<ctx['action']<=len(e['actions']):path+=('actions',ctx['action']-1)
                        break
                self.win.campaign_panel.navigate(path);return
