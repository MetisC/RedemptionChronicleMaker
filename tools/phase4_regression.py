"""Regression: open old projects in a real viewport; rebuild without source changes."""
from pathlib import Path
import sys,os,time,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')];os.environ['QT_QPA_PLATFORM']='windows'
from PySide6.QtWidgets import QApplication
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.editor.window import MainWindow
app=QApplication([]);b=Backend(Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption')));w=MainWindow(b);w.show();reports=[]
def pump():app.processEvents();time.sleep(.005)
def wait(test,timeout=90):
 end=time.monotonic()+timeout
 while not test() and time.monotonic()<end:pump()
 assert test(),'viewport timeout'
for relative in ['tests/fixtures/chronicles/east_demo.yaml','tests/fixtures/chronicles/editor_acceptance/project.yaml','tests/fixtures/chronicles/editor_playtest/project.yaml','tests/fixtures/chronicles/phase3_demo/project.yaml','tests/fixtures/chronicles/phase4_demo/project.yaml']:
 path=ROOT/relative;before=path.read_bytes();w.open_path(path);w.center_tabs.setCurrentIndex(0);wait(lambda:not w.spatial.loading and w.spatial.viewport.level is not None)
 v=w.spatial.viewport;assert v.isValid();assert before==path.read_bytes();report=b.build(before.decode('utf8'));bundle=ROOT/'build'/report['chronicle']/(report['chronicle']+'_distribution.zip');sha=hashlib.sha256(bundle.read_bytes()).hexdigest()
 if report['chronicle']=='editor_demo':assert sha=='90b41cb0b203510fafadde9f08bef5afe484aaefcb2cc8aaafbc636b88ca86ab'
 assert before==path.read_bytes();reports.append({'project':relative,'sha256':sha,'source_unchanged':True,'real_gl':v.isValid(),'triangles':len(v.level.mesh.material_ids),'materials':len(v.level.materials),'class_versions':report['class_versions']})
 w.doc._saved=__import__('rcm.service',fromlist=['source_text']).source_text(w.doc.snapshot())
wait(lambda:not w.spatial.loading);w.close();(ROOT/'research/phase4/final_regression.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports))
