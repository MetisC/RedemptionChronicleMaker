"""Render our Qt forms and measure content space; not a native game/UI test."""
import json
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
os.environ['QT_QPA_PLATFORM']='offscreen'
from PySide6.QtWidgets import QApplication,QPushButton,QListWidget
from PySide6.QtGui import QFont,QColor,QFontDatabase
from PySide6.QtTest import QTest
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.document import Document
from rcm.editor.window import MainWindow
from rcm.editor.graph_panel import Card,CARD_TEXT


def luminance(color):
    c=QColor(color)
    values=[c.redF(),c.greenF(),c.blueF()]
    values=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(v*w for v,w in zip(values,[.2126,.7152,.0722]))


def main():
    app=QApplication([]);app.setStyle('Fusion')
    font_id=QFontDatabase.addApplicationFont(str(Path(os.environ.get('SystemRoot',r'C:\Windows'))/'Fonts/segoeui.ttf'))
    families=QFontDatabase.applicationFontFamilies(font_id)
    if not families:raise ValueError('No se pudo cargar la fuente del ensayo visual')
    app.setFont(QFont(families[0],10))
    backend=Backend(Workspace(ROOT));backend.safe_mode=True
    out=ROOT/'research/round0/stability_usability';out.mkdir(parents=True,exist_ok=True)
    records=[]
    for points,size in [(10,(1100,720)),(10,(1430,900)),(15,(1430,900))]:
        app.setFont(QFont(families[0],points))
        win=MainWindow(backend);win.autosave_timer.stop();win.setFont(QFont(families[0],points))
        win.doc=Document.load(backend.ws,'chronicles/tutorial/project.yaml');win.refresh();win.resize(*size);win.show()
        win.campaign_panel.navigate(('scenes',0,'paths',0));QTest.qWait(120)
        panel=win.campaign_panel;listing=panel.findChild(QListWidget,'path_points')
        prefix=f'{size[0]}_{size[1]}_font{points}'
        win.grab().save(str(out/(prefix+'_route.png')))
        clipped=[b.text() for b in panel.findChildren(QPushButton) if b.isVisible() and b.fontMetrics().horizontalAdvance(b.text())+14>b.width()]
        records.append(dict(requested_size=size,actual_size=[win.width(),win.height()],font_points=points,effective_font_points=listing.font().pointSizeF(),route_form_height=panel.scroll.height(),route_rows_visible=listing.viewport().visibleRegion().boundingRect().height()/max(1,listing.sizeHintForRow(0)),route_list_height=listing.height(),buttons_with_possible_text_clipping=clipped))
        if points==10 and size[0]==1430:
            ci=next(i for i,c in enumerate(win.doc.data['conversations']) if c['id']=='lab')
            ni=next(i for i,n in enumerate(win.doc.data['conversations'][ci]['nodes']) if n['id']=='gesture10')
            win.select(('conversations',ci,'nodes',ni));app.processEvents();win.grab().save(str(out/'animation_node.png'))
            win.campaign_panel.navigate(('scenes',0,'sequences',0));app.processEvents();win.grab().save(str(out/'cinema_form.png'))
            win.select(('conversations',ci));win.center_tabs.setCurrentWidget(win.graph_panel);app.processEvents();win.graph_panel.refresh();win.graph_panel.fit();app.processEvents();win.grab().save(str(out/'story_graph.png'))
            text=luminance(CARD_TEXT)
            ratios=[(max(text,luminance(c.brush().color()))+.05)/(min(text,luminance(c.brush().color()))+.05) for c in win.graph_panel.scene.items() if isinstance(c,Card)]
            records[-1]['minimum_card_text_contrast']=min(ratios)
            win.center_tabs.setCurrentWidget(win.guide_panel);win.guide_panel.refresh();app.processEvents();win.grab().save(str(out/'tutorial_help.png'))
        win.doc=None;win.close();app.processEvents()
    report=dict(forms=records,font=families[0],render='Qt offscreen / Fusion',safe_mode=True,real_gl=False,native_engine_test=False,physical_dpi_test=False,notes='Font sizes simulate large text; they are not a physical Windows DPI or mouse test.')
    (out/'form_probe.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=='__main__':main()
