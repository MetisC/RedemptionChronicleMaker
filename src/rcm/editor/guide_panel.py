from .i18n import tr, language
"""Project-local guide with links to the authored entities it explains."""
from PySide6.QtWidgets import QWidget,QVBoxLayout,QTextBrowser

class GuidePanel(QWidget):
    def __init__(self,win):
        super().__init__();self.win=win;self.current=object()
        layout=QVBoxLayout(self);self.text=QTextBrowser();self.text.setObjectName('project_guide');self.text.setOpenLinks(False);self.text.anchorClicked.connect(self.navigate);layout.addWidget(self.text)

    def refresh(self):
        path=self.win.doc.path if self.win.doc else None
        key=(path,language())
        if key==self.current:return
        self.current=key
        guide=path.parent/'README.md' if path else None
        localized=path.parent/'README.en.md' if path and language()=='en' else None
        if localized and localized.is_file():guide=localized
        if guide and guide.is_file():self.text.setMarkdown(guide.read_text(encoding='utf8'))
        else:
            from .recipe_wizard import LABELS
            text='## '+tr('Asistentes de crónica')+'\n\n'+tr('Elige una tarea')+'\n\n'
            for kind,label in LABELS.items():
                text+='**'+tr(label)+'** · ['+tr('Haz esto en mi crónica')+'](rcm://wizard/'+kind+'/new) · ['+tr('Muéstramelo en el tutorial')+'](rcm://tutorial/show/'+kind+')\n\n'
            text+=tr('Puedes ver y mover posiciones en Espacio 3D. Los IDs se conservan al editar.')
            self.text.setMarkdown(text)

    def navigate(self,url):
        if url.scheme()!='rcm' or not self.win.doc or not hasattr(self.win.doc,'campaign'):return
        parts=[url.host(),*url.path().strip('/').split('/')]
        if len(parts)<3:return
        scene,kind,ident=parts[:3]
        if scene=='tutorial' and kind=='show':
            if self.win.can_leave():
                self.win.open_path(self.win.backend.ws.output('chronicles/tutorial/project.yaml'))
                self.win.open_project_guide()
            return
        if scene=='wizard':
            from .recipe_wizard import open_wizard
            open_wizard(self.win,kind,ident if ident!='new' else None);return
        if scene=='resources' and kind in ('templates','ai_profiles','textures','scripts'):
            panel=self.win.project_resources_panel;index=panel.kind.findData(kind)
            if index>=0:
                panel.kind.setCurrentIndex(index);panel.refresh()
                rows=self.win.doc.campaign.get('resources',{}).get(kind,[])
                for i,row in enumerate(rows):
                    if row['id']==ident:panel.select(i);self.win.center_tabs.setCurrentWidget(panel);return
            return
        if kind=='quests':
            for i,quest in enumerate(self.win.doc.campaign.get('quests',[])):
                if quest['id']==ident:self.win.campaign_panel.navigate(('quests',i));return
        for si,row in enumerate(self.win.doc.campaign['scenes']):
            if row['id']!=scene:continue
            if kind=='scene':self.win.campaign_panel.navigate(('scenes',si));return
            for i,entity in enumerate(row.get(kind,[])):
                if entity['id']!=ident:continue
                path=('scenes',si,kind,i);value=entity;extra=parts[3:]
                while len(extra)>=2:
                    key,target=extra[:2];extra=extra[2:]
                    if key not in ('nodes','lines','choices','actions','conditions') or not isinstance(value.get(key),list):return
                    rows=value[key]
                    if key=='nodes':index=next((j for j,r in enumerate(rows) if r.get('id')==target),-1)
                    else:index=int(target) if target.isdigit() else -1
                    if not 0<=index<len(rows):return
                    path+=(key,index);value=rows[index]
                if extra:return
                self.win.campaign_panel.navigate(path);return
