"""Retire visible historical examples, retaining originals and regression fixtures."""
from pathlib import Path
import hashlib,json,os,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
KEEP={'tutorial','mini_chronicle'}

def checked(path):
    if not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Fuera del workspace')
    for p in [path,*path.parents]:
        if p==ROOT:break
        if p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()) or (p.is_file() and p.stat().st_nlink!=1):raise ValueError('Enlace: '+str(p))
    return path

def retire(folder,dest,archive):
    checked(folder);checked(dest);checked(archive)
    paths=[p for p in folder.iterdir() if p.name not in KEEP]
    files=[f for p in paths for f in ([p] if p.is_file() else p.rglob('*')) if f.is_file()]
    for p in [*paths,*files]:checked(p)
    for p in paths:
        if (dest/p.name).exists():raise ValueError('Archivo de respaldo ya existe: '+p.name)
    archive.parent.mkdir(parents=True,exist_ok=True);hashes={}
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files:
            key=p.relative_to(folder).as_posix();data=p.read_bytes();z.writestr(key,data);hashes[key]=hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(archive) as z:
        if any(hashlib.sha256(z.read(k)).hexdigest()!=v for k,v in hashes.items()):raise ValueError('Respaldo no verificado')
    dest.mkdir(parents=True,exist_ok=True)
    for p in paths:os.replace(p,dest/p.name)
    return hashes

def main():
    names=[p.name for p in (ROOT/'chronicles').iterdir() if p.name not in KEEP]
    source=retire(ROOT/'chronicles',ROOT/'tests/fixtures/chronicles',ROOT/'research/round0/retired_source_projects.zip')
    replacements={'chronicles/'+name: 'tests/fixtures/chronicles/'+name for name in names}
    # Historical evidence/docs remain untouched. Executable regression sources
    # and their owned Java paths now address the dedicated fixture directory.
    for folder in ['tests','tools']:
        for p in (ROOT/folder).rglob('*'):
            if p.suffix not in {'.py','.yaml','.yml'} or '__pycache__' in p.parts or p==Path(__file__):continue
            s=p.read_text(encoding='utf8');old=s
            for before,after in replacements.items():s=s.replace(before,after)
            if s!=old:p.write_text(s,encoding='utf8')
    portable=ROOT/'build/portable/RedemptionChronicleMaker/workspace/chronicles'
    user=retire(portable,ROOT/'research/round0/retired_user_projects',ROOT/'research/round0/retired_user_projects.zip') if portable.exists() else {}
    for name in KEEP:
        target=checked(portable/name)
        if target.exists():raise ValueError('El proyecto nuevo ya existe; se conserva')
        shutil.copytree(ROOT/'chronicles'/name,target)
    (ROOT/'research/round0/archive_report.json').write_text(json.dumps(dict(source_backup=source,user_backup=user,visible_projects=sorted(KEEP),original_game_modified=False),indent=2),encoding='utf8')
    print('Historical sources retained as fixtures; user projects archived; two visible examples')

if __name__=='__main__':main()
