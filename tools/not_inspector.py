from pathlib import Path
import sys,json,argparse
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.not_inspector import inspect_not
p=argparse.ArgumentParser(description='Inspector NOT propio, solo lectura');p.add_argument('file',type=Path);p.add_argument('--template');p.add_argument('--output',type=Path);a=p.parse_args()
data=inspect_not(a.file.read_bytes())
if a.template:data['templates']=[t for t in data['templates'] if t['name'].casefold()==a.template.casefold()]
result=json.dumps(data,ensure_ascii=False,indent=2)
if a.output:
    from rcm.paths import Workspace
    Workspace(ROOT).write(a.output,result)
else:print(result)
