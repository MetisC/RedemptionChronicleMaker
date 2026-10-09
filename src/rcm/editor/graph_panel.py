"""Optional, editable graph projection; inspector/list remain the source of edits."""
import json,math
from PySide6.QtCore import Qt,QTimer
from PySide6.QtGui import QColor,QPen,QBrush,QPainter
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QComboBox,QPushButton,QLabel,QGraphicsView,QGraphicsScene,QGraphicsRectItem
from ..story_graph import conversation_graph
from PySide6.QtGui import QPalette

CARD_TEXT = '#142334'

class Card(QGraphicsRectItem):
    def __init__(self,panel,path,x,y,width,height,color):
        super().__init__(x,y,width,height);self.panel=panel;self.path=path
        self.setBrush(QBrush(QColor(color)));self.setPen(QPen(QColor('#71869d')))
    def mousePressEvent(self,event):
        path=self.path
        QTimer.singleShot(0,lambda:self.panel.choose(path))
        super().mousePressEvent(event)

class GraphPanel(QWidget):
    def __init__(self,win):
        super().__init__();self.win=win;self.key=None;layout=QVBoxLayout(self);bar=QHBoxLayout()
        self.kind=QComboBox();self.kind.addItem('Conversaciones','conversations');self.kind.addItem('Eventos · trigger → condiciones → acciones','events');self.kind.setObjectName('graph_kind');bar.addWidget(self.kind)
        self.resource=QComboBox();self.resource.setObjectName('graph_resource');bar.addWidget(self.resource,1)
        for label,key,cb in [('+ Nodo','graph_add_node',win.add_node),('+ Respuesta','graph_add_answer',win.add_answer),('Entrada aquí','graph_set_entry',self.entry),('Ajustar vista','graph_fit',self.fit)]:
            b=QPushButton(label);b.setObjectName(key);b.clicked.connect(lambda checked=False,cb=cb:win.guard(lambda:self.edit(cb)));bar.addWidget(b)
        layout.addLayout(bar);self.notice=QLabel('Selecciona un nodo o respuesta para editarlo en Propiedades. La lista y este gráfico comparten los mismos datos.');self.notice.setWordWrap(True);layout.addWidget(self.notice)
        self.scene=QGraphicsScene(self);self.view=QGraphicsView(self.scene);self.view.setBackgroundBrush(self.palette().brush(QPalette.ColorRole.Base));self.view.setRenderHint(QPainter.RenderHint.Antialiasing);self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag);self.view.setObjectName('story_graph');layout.addWidget(self.view,1)
        self.kind.currentIndexChanged.connect(self.changed_kind);self.resource.currentIndexChanged.connect(self.changed_resource)
        self.timer=QTimer(self);self.timer.setInterval(250);self.timer.timeout.connect(self.refresh);self.timer.start()
    def changed_kind(self):self.key=None;self.refresh()
    def changed_resource(self):
        i=self.resource.currentData()
        if i is not None:self.win.select((self.kind.currentData(),i));self.key=None;self.refresh()
    def choose(self,path):
        if not self.win.commit_properties():return
        self.win.select(path);self.key=None
    def edit(self,cb):
        if not self.win.doc or not self.win.commit_properties():return
        i=self.resource.currentData()
        if i is None:return
        if self.win.selection[:2]!=(self.kind.currentData(),i):self.win.select((self.kind.currentData(),i))
        cb();self.key=None;self.refresh()
    def entry(self):
        if self.kind.currentData()!='conversations':return
        conv=self.win.graph_conversation()
        if conv is not None:conv['entry']=conv['nodes'][self.win.selected_node_index(conv)]['id'];self.win.changed(True)
    def card(self,path,x,y,text,color='#e7eef7',width=285,height=120):
        card=Card(self,path,x,y,width,height,color);self.scene.addItem(card)
        item=self.scene.addText(text);item.setDefaultTextColor(QColor(CARD_TEXT));item.setTextWidth(width-18);item.setPos(x+9,y+5);item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
    def line(self,x,y,x2,y2,label=''):
        dark=self.palette().color(QPalette.ColorRole.Base).lightnessF()<.5
        pen=QPen(QColor('#a5bfdc' if dark else '#445c79'),2);self.scene.addLine(x,y,x2,y2,pen)
        angle=math.atan2(y2-y,x2-x)
        for delta in [-.45,.45]:self.scene.addLine(x2,y2,x2-10*math.cos(angle+delta),y2-10*math.sin(angle+delta),pen)
        if label:t=self.scene.addText(label);t.setDefaultTextColor(self.palette().color(QPalette.ColorRole.Text));t.setPos((x+x2)/2,(y+y2)/2)
    def fit(self):self.view.fitInView(self.scene.itemsBoundingRect().adjusted(-30,-30,30,30),Qt.AspectRatioMode.KeepAspectRatio)
    def refresh(self):
        if not self.isVisible():return
        rows=self.win.doc.data.get(self.kind.currentData(),[]) if self.win.doc else []
        key=json.dumps([rows,self.win.selection,self.kind.currentData(),self.resource.currentData()],sort_keys=True,ensure_ascii=False)
        if key==self.key:return
        i=self.resource.currentData();self.resource.blockSignals(True);self.resource.clear()
        for index,row in enumerate(rows):self.resource.addItem(row.get('id','Evento '+str(index+1)),index)
        if self.win.selection[0]==self.kind.currentData() and len(self.win.selection)>1:i=self.win.selection[1]
        self.resource.setCurrentIndex(max(0,self.resource.findData(i)));self.resource.blockSignals(False)
        self.scene.clear();i=self.resource.currentData();self.key=key
        if i is None:return
        prefix=(self.kind.currentData(),i);row=rows[i]
        if self.kind.currentData()=='conversations':
            graph=conversation_graph(row,prefix);positions={n['id']:(index%3*385,index//3*310) for index,n in enumerate(graph['nodes'])}
            for e in graph['edges']:
                if e['target'] in positions:
                    x,y=positions[e['source']];u,v=positions[e['target']];self.line(x+285,y+50,u,v+50)
            for n in graph['nodes']:
                x,y=positions[n['id']];status=('ENTRADA ' if n['entry'] else '')+('INACCESIBLE ' if n['unreachable'] else '')+('SIN SALIDA ' if n['dead'] else '')+('CICLO ' if n['cycle'] else '')
                text=n['id']+' · '+status+'\n'+'\n'.join(l.get('speaker','')+': '+l.get('text','')[:100] for l in n['lines'][:2])
                self.card(n['path'],x,y,text,'#f7d9d9' if n['dead'] else '#fff0cf' if n['unreachable'] else '#d9f0e6' if n['entry'] else '#e7eef7')
                answers=[a for a in graph['edges'] if a['source']==n['id']]
                for j,a in enumerate(answers):
                    target='→ '+str(a['target']) if a['target'] is not None else 'RETURN '+str(a['result'])
                    self.card(a['path'],x,y+125+j*36,a['label'][:30]+' '+target,'#ffffff',285,34)
            self.notice.setText('Speaker y líneas en Propiedades; selecciona respuestas para editar GOTO / RETURN / flags. Entry verde; inaccesible ámbar; sin salida rojo. Ciclos informativos. Destinos ausentes: '+str(graph['missing']))
        else:
            self.card(prefix,0,0,'CUANDO '+str(row.get('when'))+'\n'+str({k:v for k,v in row.items() if k not in {'actions','conditions'}}),'#d9f0e6')
            sequence=[('conditions',j,'SI '+str(c)) for j,c in enumerate(row.get('conditions',[]))]+[('actions',j,'HACER '+str(a)) for j,a in enumerate(row.get('actions',[]))]
            for index,(kind,j,text) in enumerate(sequence):
                self.line(142,120+index*160,142,160+index*160);self.card(prefix+(kind,j),0,160+index*160,text,'#fff0cf' if kind=='conditions' else '#e7eef7')
            self.notice.setText('Cadena del mismo evento: selecciona trigger, condición o acción para editarlo en Propiedades. Orden de ejecución conservado.')
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-30,-30,30,30))
