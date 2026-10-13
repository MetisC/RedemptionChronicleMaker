from .i18n import tr
"""Optional, editable graph projection; inspector/list remain the source of edits."""
import json,math
from PySide6.QtCore import Qt,QTimer
from PySide6.QtGui import QColor,QPen,QBrush,QPainter,QTextDocument,QFontMetrics
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QComboBox,QPushButton,QLabel,QGraphicsView,QGraphicsScene,QGraphicsRectItem
from ..story_graph import conversation_graph
from ..campaign import ACTIONS,WHEN
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
        self.kind=QComboBox();self.kind.addItem(tr('Conversaciones'),'conversations');self.kind.addItem(tr('Eventos · trigger → condiciones → acciones'),'events');self.kind.setObjectName('graph_kind');bar.addWidget(self.kind)
        self.kind.addItem(tr('Encuentros dinámicos'),'generators')
        self.resource=QComboBox();self.resource.setObjectName('graph_resource');bar.addWidget(self.resource,1)
        for label,key,cb in [(tr('+ Nodo'),'graph_add_node',win.add_node),(tr('+ Respuesta'),'graph_add_answer',win.add_answer),(tr('Entrada aquí'),'graph_set_entry',self.entry),(tr('Ajustar vista'),'graph_fit',self.fit)]:
            b=QPushButton(label);b.setObjectName(key);b.clicked.connect(lambda checked=False,cb=cb:win.guard(lambda:self.edit(cb)));bar.addWidget(b)
        layout.addLayout(bar);self.notice=QLabel(tr('Selecciona un nodo o respuesta para editarlo en Propiedades. La lista y este gráfico comparten los mismos datos.'));self.notice.setWordWrap(True);layout.addWidget(self.notice)
        self.scene=QGraphicsScene(self);self.view=QGraphicsView(self.scene);self.view.setBackgroundBrush(self.palette().brush(QPalette.ColorRole.Base));self.view.setRenderHint(QPainter.RenderHint.Antialiasing);self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag);self.view.setObjectName('story_graph');layout.addWidget(self.view,1)
        self.kind.currentIndexChanged.connect(self.changed_kind);self.resource.currentIndexChanged.connect(self.changed_resource)
        self.timer=QTimer(self);self.timer.setInterval(250);self.timer.timeout.connect(self.refresh);self.timer.start()
    def changed_kind(self):
        if not self.win.commit_properties():
            self.kind.blockSignals(True);self.kind.setCurrentIndex(getattr(self,'previous_kind',0));self.kind.blockSignals(False);return
        self.previous_kind=self.kind.currentIndex();self.key=None;self.refresh()
    def changed_resource(self):
        i=self.resource.currentData()
        if not self.win.commit_properties():
            previous=self.win.selection[1] if self.win.selection[0]==self.kind.currentData() and len(self.win.selection)>1 else None
            self.resource.blockSignals(True);self.resource.setCurrentIndex(self.resource.findData(previous));self.resource.blockSignals(False);return
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
        item=self.scene.addText(text,self.view.font());item.setDefaultTextColor(QColor(CARD_TEXT));item.setTextWidth(width-18);item.setPos(x+9,y+5);item.setAcceptedMouseButtons(Qt.MouseButton.NoButton);card.setToolTip(text)
        return card
    def text_height(self,text,width=285):
        doc=QTextDocument();doc.setDefaultFont(self.view.font());doc.setPlainText(text);doc.setTextWidth(width-18)
        return max(120,math.ceil(doc.size().height())+12)
    def line(self,x,y,x2,y2,label=''):
        dark=self.palette().color(QPalette.ColorRole.Base).lightnessF()<.5
        pen=QPen(QColor('#a5bfdc' if dark else '#445c79'),2);self.scene.addLine(x,y,x2,y2,pen)
        angle=math.atan2(y2-y,x2-x)
        for delta in [-.45,.45]:self.scene.addLine(x2,y2,x2-10*math.cos(angle+delta),y2-10*math.sin(angle+delta),pen)
        if label:t=self.scene.addText(label);t.setDefaultTextColor(self.palette().color(QPalette.ColorRole.Text));t.setPos((x+x2)/2,(y+y2)/2)
    def fit(self):
        bounds=self.scene.itemsBoundingRect().adjusted(-30,-30,30,30)
        self.view.fitInView(bounds,Qt.AspectRatioMode.KeepAspectRatio)
        if self.view.transform().m11()>1:self.view.resetTransform();self.view.centerOn(bounds.center())
    def refresh(self):
        if not self.isVisible():return
        for key in ('graph_add_node','graph_add_answer','graph_set_entry'):
            self.findChild(QPushButton,key).setVisible(self.kind.currentData()!='generators')
        rows=self.win.doc.data.get(self.kind.currentData(),[]) if self.win.doc else []
        key=json.dumps([rows,self.win.selection,self.kind.currentData(),self.resource.currentData()],sort_keys=True,ensure_ascii=False)
        if key==self.key:return
        i=self.resource.currentData();self.resource.blockSignals(True);self.resource.clear()
        for index,row in enumerate(rows):self.resource.addItem(row.get('id',tr('Evento ')+str(index+1)),index)
        if self.win.selection[0]==self.kind.currentData() and len(self.win.selection)>1:i=self.win.selection[1]
        self.resource.setCurrentIndex(max(0,self.resource.findData(i)));self.resource.blockSignals(False)
        self.scene.clear();i=self.resource.currentData();self.key=key
        if i is None:return
        prefix=(self.kind.currentData(),i);row=rows[i]
        if self.kind.currentData()=='conversations':
            graph=conversation_graph(row,prefix);positions={};top=0;heights={};texts={}
            answer_height=max(34,QFontMetrics(self.view.font()).height()+18)
            answer_step=answer_height+2
            for n in graph['nodes']:
                status=(tr('Inicio ') if n['entry'] else '')+(tr('INACCESIBLE ') if n['unreachable'] else '')+(tr('SIN SALIDA ') if n['dead'] else '')+(tr('CICLO ') if n['cycle'] else '')
                text=n['id']+tr(' · ')+status+'\n'+'\n'.join(l.get('speaker','')+tr(': ')+l.get('text','')[:100] for l in n['lines'][:2])
                texts[n['id']]=text
                heights[n['id']]=self.text_height(text)
            for start in range(0,len(graph['nodes']),3):
                group=graph['nodes'][start:start+3]
                height=0
                for col,n in enumerate(group):
                    positions[n['id']]=(col*385,top)
                    count=sum(a['source']==n['id'] for a in graph['edges'])
                    height=max(height,heights[n['id']]+5+count*answer_step)
                top+=max(190,height)+50
            for e in graph['edges']:
                if e['target'] in positions:
                    x,y=positions[e['source']];u,v=positions[e['target']];self.line(x+285,y+50,u,v+50)
            for n in graph['nodes']:
                x,y=positions[n['id']]
                text=texts[n['id']]
                card=self.card(n['path'],x,y,text,'#f7d9d9' if n['dead'] else '#fff0cf' if n['unreachable'] else '#d9f0e6' if n['entry'] else '#e7eef7',height=heights[n['id']])
                card.setToolTip(n['id']+'\n'+'\n'.join(l.get('speaker','')+': '+l.get('text','') for l in n['lines']))
                answers=[a for a in graph['edges'] if a['source']==n['id']]
                for j,a in enumerate(answers):
                    target=tr('Ir a ')+str(a['target']) if a['target'] is not None else tr('Terminar · resultado ')+str(a['result'])
                    full=a['label']+' '+target
                    short=QFontMetrics(self.view.font()).elidedText(full.replace('\n',' '),Qt.TextElideMode.ElideRight,261)
                    card=self.card(a['path'],x,y+heights[n['id']]+5+j*answer_step,short,'#ffffff',285,answer_height);card.setToolTip(full)
            self.notice.setText(tr('Selecciona un nodo o respuesta para editarlo en Propiedades. Inicio verde; inaccesible ámbar; sin salida rojo. Destinos ausentes: ')+str(graph['missing']))
        elif self.kind.currentData()=='generators':
            from ..dynamic_encounters import MODES
            starts=[e for e in self.win.doc.data['events'] if any(a.get('start_generator')==row['id'] for a in e['actions'])]
            text='\n'.join(tr(WHEN.get(e['when'],e['when'])) for e in starts) or tr('Desde otro evento')
            self.card(prefix,0,0,text,'#d9f0e6');self.line(142,120,142,160)
            self.card(prefix,0,160,row['name']+'\n'+tr(MODES[row['mode']]),'#e7eef7');y=280
            for wi,wave in enumerate(row['waves']):
                self.line(142,y,142,y+35);y+=35
                text=tr('Oleada ')+str(wi+1)+'\n'+', '.join(e['template']+' × '+str(e['count']) for e in wave['groups']);height=self.text_height(text)
                self.card(prefix,0,y,text,'#fff0cf',height=height);y+=height
            for event in self.win.doc.data['events']:
                if event.get('generator')==row['id']:
                    ei=self.win.doc.data['events'].index(event);self.line(142,y,142,y+35);y+=35
                    text=tr(WHEN.get(event['when'],event['when']))+'\n'+'\n'.join(tr(ACTIONS[next(iter(a))][0]) for a in event['actions'])
                    height=self.text_height(text);self.card(('events',ei),0,y,text,'#d9f0e6',height=height);y+=height
            for phase in row.get('phases',[]):
                self.line(142,y,142,y+35);y+=35
                text=tr('Fase del jefe')+' '+phase['id']+' · '+str(phase.get('percent',phase.get('value')))+('%' if 'percent' in phase else ' HP')+'\n'+'\n'.join(tr(ACTIONS[next(iter(a))][0]) for a in phase['actions'])
                height=self.text_height(text);self.card(prefix,0,y,text,'#fff0cf',height=height);y+=height
            self.notice.setText(tr('Activación → encuentro → oleadas → acciones. Los enemigos creados durante la partida no se dibujan como nodos.'))
        else:
            text=tr('CUANDO ')+tr(WHEN.get(row.get('when'),str(row.get('when'))))+'\n'+str({k:v for k,v in row.items() if k not in {'when','actions','conditions'}})
            height=self.text_height(text);self.card(prefix,0,0,text,'#d9f0e6',height=height);top=height
            sequence=[('conditions',j,tr('SI ')+str(c),str(c)) for j,c in enumerate(row.get('conditions',[]))]
            for j,action in enumerate(row.get('actions',[])):
                key=next(iter(action));value=action[key]
                summary=value.get('title','') if key=='show_note' and isinstance(value,dict) else str(value)
                sequence.append(('actions',j,tr(ACTIONS.get(key,(key,None))[0])+'\n'+summary,str(action)))
            for kind,j,text,full in sequence:
                self.line(142,top,142,top+40);top+=40;height=self.text_height(text)
                card=self.card(prefix+(kind,j),0,top,text,'#fff0cf' if kind=='conditions' else '#e7eef7',height=height);card.setToolTip(full);top+=height
            self.notice.setText(tr('Cadena del mismo evento: selecciona trigger, condición o acción para editarlo en Propiedades. Orden de ejecución conservado.'))
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-30,-30,30,30))
