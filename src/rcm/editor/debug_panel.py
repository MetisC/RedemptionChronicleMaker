from .i18n import tr
"""Playtest hub: existing build/deploy/run, observations from disk, never fake state."""
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QCheckBox,QTreeWidget,QTreeWidgetItem,QPlainTextEdit,QInputDialog
from ..debugging import parse_trace,trace_file,trace_tail

class DebugPanel(QWidget):
    def __init__(self,win):
        super().__init__();self.win=win;self.observed={};layout=QVBoxLayout(self);bar=QHBoxLayout()
        for title,name,cb in [(tr('Construir'),'debug_build',win.build_project),(tr('PROBAR EN REDEMPTION'),'debug_playtest',lambda:win.actions['playtest'].trigger()),(tr('Leer trace'),'debug_refresh',self.read_trace),('+ Checklist','debug_bookmark',self.bookmark)]:
            b=QPushButton(title);b.setObjectName(name);b.clicked.connect(lambda checked=False,cb=cb:win.guard(cb));bar.addWidget(b)
        layout.addLayout(bar);self.enabled=QCheckBox(tr('Registro de pruebas: seguir flags, misiones y acciones'));self.enabled.setObjectName('debug_instrumentation');self.enabled.toggled.connect(self.toggle);layout.addWidget(self.enabled)
        note=QLabel(tr('Datos leídos de logs reales; no son estado en vivo ni resultados de tests. Quest Watch observa flags de progreso del controlador, no inspecciona el journal.'));note.setWordWrap(True);layout.addWidget(note)
        self.tree=QTreeWidget();self.tree.setHeaderLabels([tr('Tipo'),tr('Estado / Mensaje'),tr('Tiempo')]);self.tree.setObjectName('runtime_trace');self.tree.itemDoubleClicked.connect(self.navigate);layout.addWidget(self.tree,3)
        self.checklist=QPlainTextEdit();self.checklist.setReadOnly(True);layout.addWidget(self.checklist,1)
    def root(self):return self.win.doc.snapshot() if self.win.doc else {}
    def refresh(self):
        root=self.root();self.enabled.blockSignals(True);self.enabled.setEnabled(root.get('project_format') in (5,9,10));self.enabled.setChecked(root.get('build_options',{}).get('debug',True));self.enabled.blockSignals(False)
        self.checklist.setPlainText('\n\n'.join(p['name']+'\n'+p['instructions'] for p in root.get('playtests',[])))
    def toggle(self,value):
        if self.win.doc and self.root().get('project_format') in (5,9,10):self.win.doc.campaign.setdefault('build_options',{})['debug']=value;self.win.changed(False)
    def bookmark(self):
        if not self.win.project_resources_panel.upgrade():return
        name,ok=QInputDialog.getText(self,tr('Checklist de prueba'),tr('Nombre'))
        if not ok:return
        instructions,ok=QInputDialog.getMultiLineText(self,tr('Resultado esperado'),tr('Pasos y estado esperado'))
        if ok:
            rows=self.win.doc.campaign.setdefault('playtests',[]);i=1
            while any(row['id']=='test'+str(i) for row in rows):i+=1
            rows.append(dict(id='test'+str(i),name=name,instructions=instructions));self.win.changed(True)
    def read_trace(self):
        if not self.win.doc or not self.win.backend.ws.game:raise ValueError(tr('Abre proyecto y selecciona instalación'))
        root=self.root();ident=root['chronicle']['id'];file=trace_file(self.win.backend.ws,ident)
        if file is None:raise ValueError(tr('Todavía no existe un trace nativo para esta crónica. Ejecuta una partida'))
        mapping=self.win.backend.ws.output('build/'+ident+'/source_map.json');mapping=json.loads(mapping.read_text()) if mapping.exists() else {}
        self.observed=parse_trace(trace_tail(file),mapping);self.tree.clear();self.tree.setToolTip(str(file))
        for name,val in self.observed['flags'].items():self.tree.addTopLevelItem(QTreeWidgetItem(['Flag',name+' = '+str(val),tr('Último dato del log')]))
        for name,val in self.observed['quests'].items():self.tree.addTopLevelItem(QTreeWidgetItem(['Quest',name+' '+str(val),tr('Último dato del log')]))
        for name,val in self.observed['spawned'].items():self.tree.addTopLevelItem(QTreeWidgetItem(['Spawn',name+' GUID '+str(val),tr('Identidad observada, no vida actual')]))
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
                for gi,g in enumerate(s.get('generators',[])):
                    if g['id']==ctx.get('generator'):self.win.campaign_panel.navigate(path+('generators',gi));return
                for ci,c in enumerate(s['conversations']):
                    if c['id']==ctx.get('conversation'):self.win.campaign_panel.navigate(path+('conversations',ci));return
                for ei,e in enumerate(s['events']):
                    if e['id']==ctx.get('event'):
                        path+=('events',ei)
                        if ctx.get('action') and 0<ctx['action']<=len(e['actions']):path+=('actions',ctx['action']-1)
                        break
                self.win.campaign_panel.navigate(path);return
