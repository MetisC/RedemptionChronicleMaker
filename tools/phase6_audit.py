"""Persist code inventory and suspicious constructs for review, not a PASS stamp."""
from pathlib import Path
import ast,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
inventory=[];findings=[]
for folder in ['src','tools','tests']:
    for path in sorted((ROOT/folder).rglob('*.py')):
        source=path.read_text(encoding='utf8');tree=ast.parse(source);relative=path.relative_to(ROOT).as_posix()
        functions=[node.name for node in ast.walk(tree) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))]
        inventory.append({'path':relative,'sha256':hashlib.sha256(source.encode()).hexdigest(),'lines':len(source.splitlines()),'functions':functions,'classes':[node.name for node in ast.walk(tree) if isinstance(node,ast.ClassDef)]})
        for node in ast.walk(tree):
            reason=None
            if isinstance(node,ast.Pass):reason='pass: inspect whether deliberate recovery or missing behavior'
            if isinstance(node,ast.ExceptHandler) and node.type is None:reason='bare except'
            if isinstance(node,ast.Raise) and 'NotImplemented' in ast.unparse(node):reason='NotImplemented'
            if reason:findings.append({'path':relative,'line':node.lineno,'construct':reason,'source':source.splitlines()[node.lineno-1].strip()})
        for number,line in enumerate(source.splitlines(),1):
            if re.search(r'\b(TODO|FIXME|stub|placeholder|fake)\b',line):findings.append({'path':relative,'line':number,'construct':'keyword; requires contextual review','source':line.strip()})
output=ROOT/'research/phase6';output.mkdir(parents=True,exist_ok=True)
(output/'code_inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf8');(output/'suspicious_constructs.json').write_text(json.dumps(findings,indent=2),encoding='utf8')
print(json.dumps({'python_files':len(inventory),'lines':sum(r['lines'] for r in inventory),'constructs_for_review':len(findings),'automatic_feature_pass':False}))
