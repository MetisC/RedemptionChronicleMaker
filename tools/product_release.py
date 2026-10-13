"""Audit a curated user product, then create a verified Windows ZIP."""
from pathlib import Path
import argparse,hashlib,json,re,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace


def audit(folder):
    from rcm import __version__
    from build_portable import USER_DOCS
    folder=Path(folder);files={};errors=[]
    allowed={'_internal','runtime','examples','docs','THIRD_PARTY_NOTICES','RedemptionChronicleMaker.exe','README.txt','VERSION','CHANGELOG.md','RELEASE_NOTES.md'}
    if {p.name for p in folder.iterdir()}-allowed:errors.append('Unexpected top-level content')
    if (folder/'VERSION').read_text().strip()!=__version__:errors.append('Wrong product version')
    docs={stem+suffix for stem in USER_DOCS for suffix in ('.md','.en.md')}
    if {p.name for p in (folder/'docs').iterdir()}!=docs:errors.append('Uncurated documentation')
    personal=re.compile(rb'H:[\\/]|Repositorios|jdk-21\.0\.11\.10-hotspot|east_demo|C:[\\/]Users[\\/]Usuario',re.I)
    for file in folder.rglob('*'):
        if file.is_symlink():errors.append('Link: '+str(file));continue
        if not file.is_file():continue
        name=file.relative_to(folder).as_posix();parts=name.lower().split('/')
        if any(p in ('research','workspace','tests','tools','pytest','mypy','ruff') for p in parts):errors.append('Development content: '+name)
        if file.name.lower() in ('resource.nob','codex.nob','vampire.exe','classes.zip','manual.pdf') or file.suffix.lower() in ('.lnk','.nil','.nod','.nsd','.nob','.npf','.nsg','.nsw'):errors.append('Original/legacy asset or shortcut: '+name)
        if file.suffix.lower() in ('.md','.txt','.json','.yaml','.yml','.java') and personal.search(file.read_bytes()):errors.append('Personal path: '+name)
        digest=hashlib.sha256()
        with file.open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
        files[name]=dict(size=file.stat().st_size,sha256=digest.hexdigest())
    executable=(folder/'RedemptionChronicleMaker.exe').read_bytes()
    # An arbitrary H:\\ byte triplet in a compressed payload is not a path.
    # Inspect readable strings and real directory prefixes, including UTF-16.
    executable_paths=re.compile(rb'H:[\\/](?:GOG|Repositorios)[\\/]|Repositorios|jdk-21\.0\.11\.10-hotspot|east_demo|C:[\\/]Users[\\/]Usuario',re.I)
    readable=b'\n'.join(re.findall(rb'[\x20-\x7e]{6,}',executable))
    wide=b'\n'.join(s.replace(b'\0',b'') for s in re.findall(rb'(?:[\x20-\x7e]\0){6,}',executable))
    if executable_paths.search(readable+wide):errors.append('Personal path in executable strings')
    return dict(version=__version__,successful=not errors,errors=errors,files=files,native_game_verified=False,clean_machine_verified=False)


def release(folder,output):
    ws=Workspace(ROOT);folder=ws.output(folder);output=ws.output(output);report=audit(folder)
    ws.write('research/product_close/user_release_audit.json',json.dumps(report,indent=2))
    if not report['successful']:raise ValueError(report['errors'])
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name in sorted(report['files']):archive.write(folder/name,'RedemptionChronicleMaker/'+name)
    with zipfile.ZipFile(output) as archive:
        assert len(archive.namelist())==len(report['files'])
        for name,row in report['files'].items():
            assert hashlib.sha256(archive.read('RedemptionChronicleMaker/'+name)).hexdigest()==row['sha256'],name
    manifest=dict(version=report['version'],user_zip=output.name,sha256=hashlib.sha256(output.read_bytes()).hexdigest(),size=output.stat().st_size,files=len(report['files']),all_hashes_verified=True,source_archive_separate=True,native_game_verified=False,clean_machine_verified=False)
    ws.write('release_manifest.json',json.dumps(manifest,indent=2));return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--folder',default='build/portable/RedemptionChronicleMaker');parser.add_argument('--output',default='RedemptionChronicleMaker-1.0.0-rc2-win64.zip');args=parser.parse_args();print(json.dumps(release(args.folder,args.output),indent=2))
