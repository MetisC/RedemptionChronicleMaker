"""Reuse the normal action inspector on a disposable, transactional draft."""
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QComboBox,QPushButton,QScrollArea
from .inspector import Inspector
from .i18n import tr,diagnostic
from ..campaign_document import CampaignDocument


class ActionInspector(Inspector):
    def render(self):self.event_properties()
    def relationships(self):pass


class ClickActions(QWidget):
    def __init__(self,win,root,event_index,error,parent=None):
        super().__init__(parent);self.backend=win.backend;self.doc=CampaignDocument(win.doc.ws,root);self.doc.active=win.doc.active;self.index=event_index;self.error=error
        self.spatial=win.spatial;self.center_tabs=win.center_tabs
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0);bar=QHBoxLayout();layout.addLayout(bar)
        self.actions=QComboBox();self.actions.setObjectName('click_actions');bar.addWidget(self.actions,1)
        for label,callback in [('+',self.add),('−',self.remove)]:
            button=QPushButton(label);button.setMaximumWidth(34);button.clicked.connect(callback);bar.addWidget(button)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);self.scroll.setMinimumHeight(230);layout.addWidget(self.scroll,1)
        self.actions.currentIndexChanged.connect(self.render);self.refresh()
    @property
    def event(self):return self.doc.data['events'][self.index]
    @property
    def selection(self):return ('events',self.index,'actions',max(0,self.actions.currentIndex()))
    def at(self,path):
        value=self.doc.data
        for part in path:value=value[part]
        return value
    def set_value(self,path,value,optional=False):
        row=self.at(path[:-1])
        if optional and value in (None,''):row.pop(path[-1],None)
        else:row[path[-1]]=value
        self.changed()
    def guard(self,callback):
        try:return callback()
        except ValueError as error:self.error.setText(diagnostic(str(error)));return False
    def _title(self):pass
    def changed(self,refresh=False):
        if refresh:self.refresh()
    def refresh(self):
        from ..campaign import ACTIONS
        index=max(self.actions.currentIndex(),0);self.actions.blockSignals(True);self.actions.clear()
        for i,action in enumerate(self.event['actions']):self.actions.addItem(str(i+1)+'. '+tr(ACTIONS[next(iter(action))][0]))
        self.actions.setCurrentIndex(min(index,self.actions.count()-1));self.actions.blockSignals(False);self.render()
    def render(self,*_):
        old=self.scroll.takeWidget()
        if old:old.deleteLater()
        if self.actions.currentIndex()>=0:self.scroll.setWidget(ActionInspector(self))
    def add(self):
        self.event['actions'].append({'show_note':{'title':tr('Nota'),'text':tr('Escribe aquí lo que leerá el jugador.')}});self.refresh();self.actions.setCurrentIndex(self.actions.count()-1)
    def remove(self):
        index=self.actions.currentIndex()
        if index>=0:self.event['actions'].pop(index);self.refresh()
    def commit(self):
        inspector=self.scroll.widget()
        if inspector:
            for field in inspector.findChildren(QWidget):
                callback=getattr(field,'_rcm_commit',None)
                if callback and callback() is False:return False
        return True
