"""CI-ready local gate. Full mode needs scanned assets and a JVM, never game UI."""
from pathlib import Path
import argparse,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--fast',action='store_true');args=parser.parse_args()
env=dict(os.environ,PYTHONPATH=os.pathsep.join([str(ROOT/'cache/devtools'),str(ROOT/'cache/vendor'),str(ROOT/'src')]))
commands=[['-m','ruff','check','src','tools','tests'],['-m','mypy','--follow-imports=skip','--check-untyped-defs','--cache-dir','build/tests/mypy_cache','src/rcm/paths.py','src/rcm/input_limits.py','src/rcm/file_transaction.py'],['tools/test.py',*(['--fast'] if args.fast else ['--coverage'])]]
records=[]
for cmd in commands:
    run=subprocess.run([sys.executable,*cmd],cwd=ROOT,env=env,capture_output=True,text=True);records.append({'command':cmd,'returncode':run.returncode,'output':run.stdout+run.stderr});print((run.stdout+run.stderr)[-5000:])
dest=ROOT/'build/tests';dest.mkdir(parents=True,exist_ok=True);(dest/'quality_report.json').write_text(json.dumps({'successful':all(r['returncode']==0 for r in records),'checks':records,'native_engine_test':False},indent=2),encoding='utf8')
raise SystemExit(0 if all(r['returncode']==0 for r in records) else 1)
