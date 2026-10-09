"""Local fresh-workspace packaged-editor test; explicitly not an independent VM."""
from pathlib import Path
import argparse,os,json,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--executable',type=Path,default=ROOT/'build/portable/RedemptionChronicleMaker/RedemptionChronicleMaker.exe');parser.add_argument('--report',type=Path,default=ROOT/'research/phase9/portable_probe.json');args=parser.parse_args()
exe=args.executable
workspace=ROOT/'build'/('phase9_portable_probe_'+str(time.time_ns()))
environment=dict(os.environ);environment['PATH']=str(Path(os.environ.get('SystemRoot','C:/Windows'))/'System32')
command=[str(exe),str(workspace/'chronicles/tutorial/project.yaml'),'--workspace',str(workspace),'--game',r'H:\GOG\Vampire The Masquerade - Redemption','--smoke-test']
result=subprocess.run(command,cwd=ROOT,env=environment,capture_output=True,text=True,timeout=180)
path=workspace/'build/portable_smoke.json';report=json.loads(path.read_text()) if path.exists() else {}
report.update(exit_code=result.returncode,workspace=str(workspace),global_python_jdk_path=False,clean_machine_test=False,native_engine_test=False,executable=str(exe))
report_path=ROOT/args.report;report_path.parent.mkdir(parents=True,exist_ok=True)
report_path.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if result.returncode or not report.get('valid_project') or not report.get('real_gl'):raise SystemExit(1)
