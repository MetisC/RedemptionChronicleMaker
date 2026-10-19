"""Stage generated outputs, publish the manifest last, keep unrelated files."""
from pathlib import Path
import json,shutil,uuid
import re
from .paths import Workspace
from .file_transaction import replace_files

class StagedWorkspace(Workspace):
    def __init__(self,original,chronicle):
        super().__init__(original.root,original.game);self.original=original;self.chronicle=chronicle
        self.stage=original.output('build/.staging/'+uuid.uuid4().hex);self.stage.mkdir(parents=True)
    def output(self,path):
        dest=self.original.output(path);relative=dest.relative_to(self.root)
        if len(relative.parts)>1 and relative.parts[0]=='build' and (relative.parts[1]==self.chronicle or re.fullmatch(re.escape(self.chronicle)+r'_s\d+',relative.parts[1])):
            return self.original.output(self.stage/relative)
        return dest
    def publish(self,report):
        files=sorted(p for p in self.stage.rglob('*') if p.is_file())
        root=Path('build')/self.chronicle
        report['generated_artifacts']=[p.relative_to(self.stage).as_posix() for p in files]
        self.write(root/'build_report.json',json.dumps(report,ensure_ascii=False,indent=2))
        files=sorted(p for p in self.stage.rglob('*') if p.is_file())
        final=root/'build_report.json';files.sort(key=lambda p:p.relative_to(self.stage)==final)
        # Ownership is explicit; publish only staged outputs. Unknown user files survive.
        backup=self.original.output('research/build_backups/'+self.chronicle+'_'+uuid.uuid4().hex+'.zip');backup.parent.mkdir(parents=True,exist_ok=True)
        targets={self.original.output(p.relative_to(self.stage)):p.read_bytes() for p in files}
        replace_files(targets,[],backup,self.root,self.original.output)
        return report
    def close(self):
        target=self.original.output(self.stage)
        if target.parent!=self.original.output('build/.staging'):raise ValueError('Staging fuera del destino')
        shutil.rmtree(target)

def failed_report(ws,source,error):
    """A failed attempt invalidates deployment of a previous artifact for this ID."""
    from .model import identifier
    try:
        ident=identifier(source['chronicle']['id'],'chronicle.id',18)
    except (KeyError,TypeError,ValueError):return
    path=Path('build')/ident/'build_report.json'
    previous={};artifacts=[]
    try:previous=json.loads(ws.output(path).read_text(encoding='utf8'));artifacts=previous.get('generated_artifacts',[])
    except (OSError,ValueError):pass
    record={'chronicle':ident,'status':'failed','reason':str(error),'native_engine_test':False,'generated_artifacts':artifacts,'save_schema_sha256':previous.get('save_schema_sha256')}
    if 'combat_difficulty' in previous:record['combat_difficulty']=previous['combat_difficulty']
    ws.write(path,json.dumps(record,ensure_ascii=False,indent=2))

def clean_build(ws,chronicle):
    from .model import identifier
    identifier(chronicle,'chronicle',18);root=ws.output('build/'+chronicle);path=root/'build_report.json'
    if not path.exists():return []
    report=json.loads(path.read_text(encoding='utf8'));targets=[]
    for name in report.get('generated_artifacts',[]):
        rel=Path(name)
        if rel.is_absolute() or '..' in rel.parts or len(rel.parts)<2 or rel.parts[0]!='build' or not (rel.parts[1]==chronicle or re.fullmatch(re.escape(chronicle)+r'_s\d+',rel.parts[1])):raise ValueError('Manifest clean inseguro')
        p=ws.output(rel)
        if p.is_file():targets.append(p)
    # Resolve every target before deleting anything; no recursive deletion.
    for p in targets:p.unlink()
    return [p.relative_to(ws.root).as_posix() for p in targets]
