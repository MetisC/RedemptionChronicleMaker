"""Run offline format, validation, packaging and generated Java scenario tests."""
from pathlib import Path
import sys
import unittest
import json
import io
import argparse,time
import os
# Historical UI expectations cover the existing Spanish interface. Language
# regressions launch isolated processes and explicitly exercise both choices.
os.environ.setdefault('RCM_EDITOR_LANGUAGE','es')
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8',errors='replace')

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT / "src"),str(ROOT / "cache/vendor")]
parser=argparse.ArgumentParser(description='Offline RCM quality suite')
parser.add_argument('--fast',action='store_true',help='Synthetic fixtures only; no game/catalogue/Java/Qt')
parser.add_argument('--coverage',action='store_true',help='Branch coverage, JSON and HTML report')
parser.add_argument('--pattern',default=None)
args=parser.parse_args()
coverage=None
if args.coverage:
    sys.path.insert(0,str(ROOT/'cache/devtools'))
    from coverage import Coverage
    coverage=Coverage(branch=True,source=[str(ROOT/'src/rcm')],data_file=str(ROOT/'build/tests/.coverage'));coverage.start()
suite=unittest.defaultTestLoader.discover(str(ROOT / "tests"),pattern=args.pattern or ('test_safety_unit.py' if args.fast else 'test_*.py'))
class ProgressBuffer(io.StringIO):
    """Keep the current test visible on disk even if a Qt modal blocks a run."""
    def write(self,value):
        result=super().write(value)
        with (ROOT/'build/tests'/('progress_'+str(os.getpid())+'.log')).open('a',encoding='utf8') as log:
            log.write(value)
        return result
(ROOT/'build/tests').mkdir(parents=True,exist_ok=True)
(ROOT/'build/tests/progress.log').write_text('',encoding='utf8')
output=ProgressBuffer()
started=time.perf_counter()
result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
text=output.getvalue()
dest=ROOT / "build/tests"
dest.mkdir(parents=True,exist_ok=True)
(dest / ("fast_tests.log" if args.fast else "tests.log")).write_text(text,encoding="utf8")
name='fast_test_report.json' if args.fast else 'test_report.json'
(dest / name).write_text(json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped),"successful":result.wasSuccessful(),"elapsed_seconds":time.perf_counter()-started,"category":"synthetic-unit-package" if args.fast else "offline-integration-gui-model-build-format", "native_engine_test":False,"failures_detail":[{'test':str(t),'traceback':trace} for t,trace in result.failures+result.errors]},indent=2),encoding="utf8")
print(text)
if coverage:
    coverage.stop();coverage.save();coverage.json_report(outfile=str(dest/'coverage.json'));coverage.html_report(directory=str(dest/'coverage_html'));coverage.report()
raise SystemExit(0 if result.wasSuccessful() else 1)
