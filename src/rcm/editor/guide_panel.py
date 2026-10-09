"""Project-local guide with links to the authored entities it explains."""
from PySide6.QtWidgets import QWidget,QVBoxLayout,QTextBrowser

class GuidePanel(QWidget):
    def __init__(self,win):
        super().__init__();self.win=win;self.current=object()
        layout=QVBoxLayout(self);self.text=QTextBrowser();self.text.setObjectName('project_guide');self.text.setOpenLinks(False);self.text.anchorClicked.connect(self.navigate);layout.addWidget(self.text)

    def refresh(self):
        path=self.win.doc.path if self.win.doc else None
        if path==self.current:return
        self.current=path
        guide=path.parent/'README.md' if path else None
        if guide and guide.is_file():self.text.setMarkdown(guide.read_text(encoding='utf8'))
        else:self.text.setMarkdown('## Guía del editor\n\n**3D:** derecho + WASD/QE para volar; izquierdo arrastrado para avanzar y girar; ambos botones para subir/bajar. Alt + izquierdo orbita, Alt + derecho acerca, Alt + central desplaza. F enfoca. Clic derecho abre acciones.\n\n**Escenas:** + Escena crea un layout vacío, duplica el actual o elige otro escenario. NPC, objetos y eventos pertenecen a cada escena.\n\n**Inventario:** selecciona NPC → Editar inventario inicial → + Del catálogo. Aplicar permite deshacer.\n\nAbre el proyecto Tutorial para ver ejemplos y enlaces a sus elementos. La documentación completa se encuentra en docs/ROUND0_GUIDE.md.')

    def navigate(self,url):
        if url.scheme()!='rcm' or not self.win.doc or not hasattr(self.win.doc,'campaign'):return
        parts=[url.host(),*url.path().strip('/').split('/')]
        if len(parts)!=3:return
        scene,kind,ident=parts
        for si,row in enumerate(self.win.doc.campaign['scenes']):
            if row['id']!=scene:continue
            if kind=='scene':self.win.campaign_panel.navigate(('scenes',si));return
            for i,entity in enumerate(row.get(kind,[])):
                if entity['id']==ident:self.win.campaign_panel.navigate(('scenes',si,kind,i));return
