"""Bounded rolling source backups and safe full-project duplication."""
from pathlib import Path
import hashlib
import json
import stat
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


def project_deletion_target(ws, source):
    """Only dedicated project folders can be removed recursively.

    Standalone YAML files keep their surrounding folder and shared assets.
    Validate the whole tree before any deletion, including Windows junctions.
    """
    from .product import example_root
    path = ws.output(source)
    if not path.is_file() or path.suffix.lower() not in {'.yaml', '.yml'}:
        raise ValueError('No se encuentra el archivo de la crónica.')
    relative = path.relative_to(ws.root)
    reserved = {'src', 'docs', 'tools', 'tests', 'cache', 'build', 'research', 'backups', 'rcm'}
    if any(part.startswith('.') for part in relative.parts) or relative.parts[0].lower() in reserved:
        raise ValueError('Esta ubicación contiene archivos del programa y no se puede eliminar desde aquí.')
    target = path.parent if path.name == 'project.yaml' else path
    if target.is_dir() and (target == ws.root or target == ws.root/'chronicles' or target == ws.root/'user_workspaces'):
        raise ValueError('La crónica debe estar en una carpeta propia para eliminarla.')
    masters = ('tutorial', 'mini_chronicle', 'showcase', 'dynamic_lab', 'director_acceptance', 'strict_acceptance', 'completion_lab')
    if any(path.is_relative_to((example_root()/name).resolve()) for name in masters):
        raise ValueError('Este es un ejemplo original del programa. Crea una copia para editarlo o eliminarlo.')
    for parent in path.parent.parents:
        if parent == ws.root:break
        if (parent/'project.yaml').is_file():
            raise ValueError('Esta carpeta pertenece a otra crónica. No se ha eliminado nada.')

    def inspect(entry):
        info = entry.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError('La crónica contiene enlaces. No se ha eliminado nada.')
        if entry.is_file() and info.st_nlink != 1:
            raise ValueError('La crónica contiene enlaces. No se ha eliminado nada.')
        if entry.is_dir():
            if entry.name == '.git':
                raise ValueError('Esta carpeta contiene un repositorio. No se ha eliminado nada.')
            for child in entry.iterdir():inspect(child)
        elif entry != path and entry.suffix.lower() in {'.yaml', '.yml'}:
            raise ValueError('La carpeta contiene otros archivos YAML. Separa las crónicas antes de eliminarla.')

    # ws.output resolves paths, so inspect raw ancestors too (Python 3.10
    # does not expose Path.is_junction).
    raw = ws.root/Path(source)
    for ancestor in [raw, *raw.parents]:
        info = ancestor.lstat()
        if getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError('La crónica contiene enlaces. No se ha eliminado nada.')
        if ancestor == ws.root:break
    inspect(target)
    if target.is_file():
        recovery = ws.output(str(path)+'.autosave')
        if recovery.exists():inspect(recovery)
    return target


def delete_project(ws, source):
    """Delete the confirmed local project, never deployments or saved games."""
    path = ws.output(source)
    target = project_deletion_target(ws, source)
    lock = ProjectLock(path)
    if not lock.acquire():
        raise ValueError('Esta crónica está abierta en otro editor. Cierra esa ventana antes de eliminarla.')
    try:
        project_deletion_target(ws, source)  # Recheck after acquiring ownership.
        if target.is_dir():
            # Keep the lock until the source/assets are gone. QLockFile removes
            # its own file on release; another editor cannot load a deleted source.
            entries = sorted(target.rglob('*'), key=lambda p:len(p.parts), reverse=True)
            for entry in entries:
                if entry == lock.path:continue
                if entry.is_dir():entry.rmdir()
                else:entry.unlink()
        else:
            recovery = ws.output(str(path)+'.autosave')
            if recovery.exists():recovery.unlink()
            path.unlink()
    finally:
        lock.release()
    if target.is_dir():target.rmdir()
    prefs = getattr(ws, 'app_settings', None)
    if prefs:prefs.remove_recent(path)
    return target
