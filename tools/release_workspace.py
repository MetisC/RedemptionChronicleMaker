"""Create and verify a recoverable private workspace archive, excluding Git.

No game directory is read or written. Portable redistribution is a separate build.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'cache/vendor')]
from rcm.paths import Workspace


def verify(path):
    with zipfile.ZipFile(path) as archive:
        manifests=[n for n in archive.namelist() if n.endswith('/RELEASE_WORKSPACE_MANIFEST.json')]
        if len(manifests)!=1:raise ValueError('Missing or ambiguous workspace manifest')
        manifest=json.loads(archive.read(manifests[0]))
        if set(archive.namelist()) != set(manifest['files']) | {manifests[0]}:
            raise ValueError('Archive inventory mismatch')
        for name,record in manifest['files'].items():
            digest=hashlib.sha256();size=0
            with archive.open(name) as stream:
                for block in iter(lambda:stream.read(1024*1024),b''):
                    digest.update(block);size+=len(block)
            if size!=record['size'] or digest.hexdigest()!=record['sha256']:
                raise ValueError('Archive bytes mismatch: '+name)
    return len(manifest['files'])


def create(ws,path):
    path=ws.output(path)
    if path.exists():raise ValueError('Archive already exists; choose a new output name')
    staging=ws.output(str(path)+'.partial')
    if staging.exists():raise ValueError('Incomplete archive exists; inspect it first')
    files={}
    for directory,dirs,names in os.walk(ROOT):
        dirs[:]=sorted(d for d in dirs if d not in {'.git','__pycache__','.mypy_cache','.ruff_cache','.pytest_cache','.agents','.codex'})
        for name in sorted(names):
            file=Path(directory)/name
            if file in {path,staging} or file.suffix in {'.pyc','.pyo'}:continue
            if file.parent==ROOT and file.suffix=='.zip':continue
            if file.relative_to(ROOT).as_posix() in {'research/product_close/workspace_archive.json', 'release_manifest.json', 'SHA256SUMS.txt'}:continue
            ws.output(file)  # rejects links and paths outside the workspace
            files[ROOT.name+'/'+file.relative_to(ROOT).as_posix()]=file
    records={}
    try:
        with zipfile.ZipFile(staging,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as archive:
            for name,file in sorted(files.items()):
                digest=hashlib.sha256();size=0
                with file.open('rb') as source,archive.open(name,'w',force_zip64=True) as target:
                    for block in iter(lambda:source.read(1024*1024),b''):
                        digest.update(block);size+=len(block);target.write(block)
                records[name]=dict(size=size,sha256=digest.hexdigest())
            archive.writestr(ROOT.name+'/RELEASE_WORKSPACE_MANIFEST.json',json.dumps(dict(format=1,files=records,git_included=False),indent=2))
        count=verify(staging);staging.replace(path)
    except Exception:
        # Keep incomplete bytes for diagnosis; never delete an existing archive.
        raise
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    report=dict(archive=str(path),files=count,bytes=path.stat().st_size,sha256=digest.hexdigest(),all_file_hashes_verified=True,git_included=False,native_engine_test=False)
    ws.write('research/product_close/workspace_archive.json',json.dumps(report,indent=2))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='RedemptionChronicleMaker-1.0.0-rc3-workspace.zip');parser.add_argument('--verify',type=Path)
    args=parser.parse_args();ws=Workspace(ROOT)
    print(json.dumps(dict(verified_files=verify(ws.output(args.verify))) if args.verify else create(ws,args.output),indent=2))
