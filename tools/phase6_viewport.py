"""Visible GL acceptance on our editor's model/controllers, not Redemption."""
from pathlib import Path
import os,sys,time,json
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')];os.environ['QT_QPA_PLATFORM']='windows'
from PySide6.QtWidgets import QApplication
from rcm.paths import Workspace
from rcm.service import Backend,source_text
from rcm.editor.window import MainWindow
app=QApplication([]);backend=Backend(Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption')));win=MainWindow(backend);win.show();reports=[]
def wait(test):
    end=time.monotonic()+60
    while not test() and time.monotonic()<end:app.processEvents();time.sleep(.005)
    assert test(),'GL load timeout'
for project in ['chronicles/system_test/project.yaml','chronicles/large_fixture/project.yaml','chronicles/system_test/project.yaml']:
    path=ROOT/project;before=path.read_bytes();start=time.perf_counter();win.open_path(path);win.center_tabs.setCurrentIndex(0);wait(lambda:not win.spatial.loading and win.spatial.viewport.level is not None)
    viewport=win.spatial.viewport;assert viewport.isValid();load=time.perf_counter()-start
    win.select(('actors',0));win.spatial.transform(('actors',0),{'position':[123.125,-45.5,32.75],'orientation':[0,0,90]});assert win.doc.data['actors'][0]['transform']['position']==[123.125,-45.5,32.75];win.undo_project();assert path.read_bytes()==before
    start=time.perf_counter()
    for _ in range(30):viewport.repaint();app.processEvents()
    frame=(time.perf_counter()-start)/30
    reports.append({'project':project,'load_seconds':load,'repaint_seconds_mean':frame,'real_gl':viewport.isValid(),'triangles':len(viewport.level.mesh.material_ids),'materials':len(viewport.level.materials),'source_unchanged':True,'transform_undo':True,'gpu_memory_measured':False})
    win.doc._saved=source_text(win.doc.snapshot())
wait(lambda:not win.spatial.loading);win.doc=None;win.close();app.processEvents();backend.ws.write('research/phase6/viewport.json',json.dumps(reports,indent=2));print(json.dumps(reports))
