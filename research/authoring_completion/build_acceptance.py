"""Compile every bundled acceptance example against real Codex, without launch."""
import hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.document import Document


def main():
    ws=Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption'));backend=Backend(ws);rows=[]
    for name in ('tutorial','mini_chronicle','showcase','dynamic_lab','director_acceptance','strict_acceptance','completion_lab'):
        path=ROOT/'chronicles'/name/'project.yaml';before=path.read_bytes();doc=Document.load(ws,path);report=backend.build(doc.snapshot());pid=doc.snapshot()['chronicle']['id'];archive=ROOT/'build'/pid/(pid+'.nob')
        with zipfile.ZipFile(archive) as package:
            if any(n.lower().endswith('.nil') for n in package.namelist()):raise ValueError('Original geometry must remain a reference')
        if path.read_bytes()!=before:raise ValueError('Source changed during build')
        versions=set(report['class_versions'].values())
        if versions!={'45.3'}:raise ValueError('Wrong native class version')
        row=dict(example=name,id=pid,successful=True,classes=len(report['class_versions']),class_versions=sorted(versions),source_sha256=hashlib.sha256(before).hexdigest(),nob_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),geometry_included=False,native_game_test=False)
        rows.append(row);print(json.dumps(row),flush=True)
    (ROOT/'research/authoring_completion/builds.json').write_text(json.dumps(rows,indent=2),encoding='utf8')


if __name__=='__main__':main()
