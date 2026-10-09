"""Load/compile the delivered tutorial in the packaged editor, without game UI."""
import argparse
import json
import os
import subprocess
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--executable',type=Path,default=ROOT/'build/portable/RedemptionChronicleMaker/RedemptionChronicleMaker.exe')
    args=parser.parse_args()
    exe=args.executable.resolve();workspace=ROOT/'build/portable/RedemptionChronicleMaker/workspace'
    if not exe.is_relative_to(ROOT.resolve()):raise ValueError('Executable outside workspace')
    env=dict(os.environ,QT_QPA_PLATFORM='offscreen')
    begin=time.monotonic()
    diag=subprocess.run([str(exe),'--workspace',str(workspace),'--cli','diagnostics'],cwd=ROOT,env=env,timeout=60)
    if diag.returncode:raise ValueError('Portable diagnostics failed')
    run=subprocess.run([str(exe),str(workspace/'chronicles/tutorial/project.yaml'),'--workspace',str(workspace),'--safe-mode','--smoke-test'],cwd=ROOT,env=env,timeout=160)
    report=json.loads((workspace/'build/portable_smoke.json').read_text(encoding='utf8'))
    report.update(executable=str(exe),process_exit_code=run.returncode,elapsed_total_seconds=time.monotonic()-begin,native_engine_test=False)
    output=ROOT/'research/round0/guided_tutorial/portable_probe.json'
    output.write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2))
    if run.returncode or not report.get('valid_project') or report.get('build_status')!='compiled-unverified-in-game':raise ValueError('Packaged editor load/compile failed')

if __name__=='__main__':main()
