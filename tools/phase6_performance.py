"""Local baseline: CPU authoring operations, build and bounded repeated loads."""
from pathlib import Path
import gc,hashlib,json,platform,sys,time,tracemalloc
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.document import Document
from rcm.service import Backend
from rcm.campaign_relations import graph
from rcm.packages import create_package
ws=Workspace(ROOT);backend=Backend(ws);results={};tracemalloc.start()
for name in ['system_test','golden','large_fixture']:
    path=ws.output('chronicles/'+name+'/project.yaml');t=time.perf_counter();doc=Document.load(ws,path);root=doc.snapshot();load=time.perf_counter()-t
    t=time.perf_counter();doc.save('build/performance/'+name+'/project.yaml');save=time.perf_counter()-t
    t=time.perf_counter();validation=backend.validate(root);assert validation.valid,[p.message for p in validation.problems];validate=time.perf_counter()-t
    t=time.perf_counter();links=graph(root);refs=time.perf_counter()-t
    t=time.perf_counter();search=[r for r in links if 'actor' in str(r).casefold()];search_time=time.perf_counter()-t
    tracemalloc.stop();t=time.perf_counter();report=backend.build(root);build=time.perf_counter()-t
    archive=ws.output('build/'+report['chronicle']+'/'+report['chronicle']+'.rcmpack');create_package(ws,report['chronicle'],archive)
    distribution=ws.output('build/'+report['chronicle']+'/'+report['chronicle']+'_distribution.zip')
    results[name]={'load_seconds':load,'save_seconds':save,'validation_seconds':validate,'references_seconds':refs,'reference_count':len(links),'search_links_seconds':search_time,'search_hits':len(search),'build_seconds':build,'distribution_bytes':distribution.stat().st_size,'distribution_sha256':hashlib.sha256(distribution.read_bytes()).hexdigest(),'source_unchanged':path.read_text(encoding='utf8').strip()==__import__('rcm.service',fromlist=['source_text']).source_text(root).strip(),'native_engine_test':False}
    tracemalloc.start()
gc.collect();start=tracemalloc.get_traced_memory()[0]
for _ in range(30):
    d=Document.load(ws,'chronicles/large_fixture/project.yaml');graph(d.snapshot());del d
gc.collect();end,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
result={'platform':platform.platform(),'python':platform.python_version(),'projects':results,'repeated_loads':{'iterations':30,'retained_python_bytes_delta':end-start,'traced_peak_bytes':peak,'gpu_memory_measured':False,'proves_no_leaks':False}}
ws.write('research/phase6/performance.json',json.dumps(result,indent=2));print(json.dumps(result))
