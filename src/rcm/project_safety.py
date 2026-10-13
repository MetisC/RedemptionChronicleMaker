"""Bounded rolling source backups and safe full-project duplication."""
from pathlib import Path
import hashlib
import json
import time


class ExternalChange(ValueError):
    pass


def disk_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if path and Path(path).is_file() else None


def before_save(doc, target, content, force=False):
    target = doc.ws.output(target)
    known = getattr(doc,'_disk_hash',None)
    if target==doc.path and getattr(doc,'_expects_new_file',False) and target.exists() and not force:
        raise ExternalChange('Otro editor ha creado este archivo. Guarda tu proyecto como copia para conservar ambos.')
    if target == getattr(doc,'_disk_path',None) and known is not None and disk_hash(target) != known and not force:
        raise ExternalChange('El archivo fue modificado fuera de RCM. Recarga o guarda una copia antes de sobrescribirlo.')
    if target.is_file() and target.read_bytes() != content.encode('utf8'):
        backup_source(doc.ws,doc.snapshot()['chronicle']['id'],target.read_bytes())


def backup_source(ws, ident, data, limit=20):
    from .model import identifier
    identifier(ident,'chronicle',18)
    directory = ws.output('backups/'+ident)
    directory.mkdir(parents=True,exist_ok=True)
    rows = sorted(directory.glob('*.yaml'))
    if rows and rows[-1].read_bytes() == data:return rows[-1]
    path = ws.write(directory/(str(time.time_ns())+'.yaml'),data)
    for old in sorted(directory.glob('*.yaml'))[:-limit]:ws.output(old).unlink()
    return path


def restore_backup(doc, backup):
    from .document import Document
    candidate=Document.load(doc.ws,backup)
    if candidate.snapshot()['chronicle']['id']!=doc.snapshot()['chronicle']['id']:raise ValueError('Esta copia pertenece a otra crónica')
    if doc.path.is_file():backup_source(doc.ws,doc.snapshot()['chronicle']['id'],doc.path.read_bytes())
    backup_source(doc.ws,doc.snapshot()['chronicle']['id'],__import__('rcm.service',fromlist=['source_text']).source_text(doc.snapshot()).encode('utf8'))
    doc.data=candidate.snapshot()
    return doc.save(force=True)


def duplicate_project(ws, source, directory, name, ident, readme_directory=None):
    from .packages import export_project,import_project
    archive=ws.output('cache/project_copy_'+str(time.time_ns())+'.rcmproject')
    try:
        export_project(ws,source,archive)
        doc=import_project(ws,archive,directory)
        doc.snapshot()  # Draft shape already validated by the importer.
        root=doc.campaign if hasattr(doc,'campaign') else doc.data
        root['chronicle'].update(id=ident,name=name)
        doc.save()
        if readme_directory:
            for filename in ('README.md','README.en.md'):
                p=ws.output(Path(readme_directory)/filename)
                if p.is_file():ws.write(Path(directory)/filename,p.read_bytes())
        return doc
    finally:
        if archive.is_file():archive.unlink()


class ProjectLock:
    """QLockFile checks PID/process identity and stale locks on Windows."""
    def __init__(self, path):
        from PySide6.QtCore import QLockFile
        self.path = Path(path).with_name('.rcm_project.lock')
        self.lock=QLockFile(str(self.path));self.lock.setStaleLockTime(0)
    def acquire(self):return self.lock.tryLock(0)
    def release(self):self.lock.unlock()
    def details(self):
        ok,pid,host,app=self.lock.getLockInfo()
        return json.dumps(dict(valid=ok,pid=pid,host=host,application=app))
