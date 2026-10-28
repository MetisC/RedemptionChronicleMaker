"""Compare shipped Python code with workspace sources without executing it."""
from pathlib import Path
import argparse,hashlib,json,sys,types
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cache/devtools'),str(ROOT/'cache/vendor'),str(ROOT/'src')]
from PyInstaller.archive.readers import CArchiveReader


def normal(code):
    return code.replace(co_filename='<source>',co_consts=tuple(normal(v) if isinstance(v,types.CodeType) else v for v in code.co_consts))


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--folder',type=Path,default=ROOT/'build/portable/RedemptionChronicleMaker');parser.add_argument('--report',type=Path,default=ROOT/'research/embrace_closure/frozen_sources.json');args=parser.parse_args(argv)
    app=args.folder;exe=app/'RedemptionChronicleMaker.exe'
    archive=CArchiveReader(str(exe)).open_embedded_archive('PYZ.pyz');rows=[]
    for path in sorted((ROOT/'src/rcm').rglob('*.py')):
        parts=list(path.relative_to(ROOT/'src').with_suffix('').parts)
        if parts[-1]=='__init__':parts.pop()
        name='.'.join(parts);embedded=archive.extract(name)
        source=path.read_bytes();compiled=compile(source,str(path),'exec',dont_inherit=True)
        rows.append(dict(module=name,source_sha256=hashlib.sha256(source).hexdigest(),matches=isinstance(embedded,types.CodeType) and normal(compiled)==normal(embedded)))
    translations=(ROOT/'src/rcm/editor/assets/en.json').read_bytes()
    report=dict(successful=all(r['matches'] for r in rows) and translations==(app/'_internal/rcm/editor/assets/en.json').read_bytes(),executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),modules=rows,translations_sha256=hashlib.sha256(translations).hexdigest(),native_engine_test=False)
    args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(dict(successful=report['successful'],modules=len(rows),mismatches=[r['module'] for r in rows if not r['matches']])))
    return 0 if report['successful'] else 1


if __name__=='__main__':raise SystemExit(main())
