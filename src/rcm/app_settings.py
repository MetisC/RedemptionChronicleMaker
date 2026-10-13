"""Small, versioned application preferences; no chronicle content or telemetry."""
from pathlib import Path
import copy
import json
import os
import tempfile
import time


def system_language():
    from PySide6.QtCore import QLocale
    return 'es' if QLocale.system().name().lower().startswith('es') else 'en'


def settings_directory():
    from PySide6.QtCore import QStandardPaths
    # GenericDataLocation is LocalAppData on Windows, independent of Qt app name.
    return Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.GenericDataLocation)) / 'RedemptionChronicleMaker'


def default_workspace():
    from PySide6.QtCore import QStandardPaths
    return Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)) / 'Redemption Chronicle Maker'


class AppSettings:
    def __init__(self, directory=None):
        self.directory = Path(directory) if directory else settings_directory()
        self.path = self.directory / 'settings.json'
        self.warning = None
        self.exists = self.path.is_file()
        self.data = dict(schema=1, language=system_language(), appearance='system',
                         recent_projects=[], show_playtest_hint=True, safe_mode=False,
                         autosave_seconds=30, reopen_last=False)
        if self.exists:
            try:
                loaded = json.loads(self.path.read_text(encoding='utf-8-sig'))
                self.validate(loaded)
                self.data.update(loaded)
            except (OSError, ValueError, TypeError):
                # Preserve malformed data before publishing defaults, including future schemas.
                backup = self.path.with_name('settings.corrupt.' + str(time.time_ns()) + '.json')
                backup.write_bytes(self.path.read_bytes())
                self.warning = 'Las preferencias no se pudieron leer. Se conserva una copia y se usan valores seguros.'
                self.exists = False

    @staticmethod
    def validate(data):
        if not isinstance(data, dict) or data.get('schema') != 1:
            raise ValueError('Unsupported application settings')
        if data.get('language', 'en') not in ('en', 'es') or data.get('appearance', 'system') not in ('system', 'light', 'dark'):
            raise ValueError('Invalid preferences')
        for key in ('game_installation', 'workspace', 'window_geometry', 'window_state'):
            if key in data and not isinstance(data[key], str):raise ValueError('Invalid preference: ' + key)
        if not isinstance(data.get('recent_projects', []), list):raise ValueError('Invalid recent projects')
        for item in data.get('recent_projects', []):
            if not isinstance(item, dict) or not all(isinstance(item.get(k), str) for k in ('path', 'name', 'opened')):
                raise ValueError('Invalid recent project')
        for key in ('safe_mode', 'show_playtest_hint', 'reopen_last', 'setup_complete'):
            if key in data and type(data[key]) is not bool:raise ValueError('Invalid preference: ' + key)
        if type(data.get('autosave_seconds',30)) is not int or not 0 <= data.get('autosave_seconds',30) <= 600:
            raise ValueError('Invalid autosave interval')
        if 'splitter_sizes' in data and (not isinstance(data['splitter_sizes'],list) or any(type(n) is not int or n < 0 for n in data['splitter_sizes'])):
            raise ValueError('Invalid splitter sizes')
        if 'last_tab' in data and (type(data['last_tab']) is not int or not 0 <= data['last_tab'] <= 20):raise ValueError('Invalid tab')
        if not isinstance(data.get('last_resource_filters',{}),dict):raise ValueError('Invalid resource filters')
        for row in data.get('last_resource_filters',{}).values():
            if not isinstance(row,dict):raise ValueError('Invalid resource filters')
        for key in ('resource_recent','resource_favorites'):
            if not isinstance(data.get(key,[]),list) or any(not isinstance(r,dict) or not all(isinstance(r.get(k),str) for k in ('kind','id')) for r in data.get(key,[])):
                raise ValueError('Invalid resources preference')

    def save(self):
        self.validate(self.data)
        self.directory.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix='settings.', suffix='.tmp', dir=self.directory)
        try:
            with os.fdopen(fd, 'w', encoding='utf8') as stream:
                json.dump(self.data, stream, ensure_ascii=False, indent=2)
                stream.flush(); os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if Path(temporary).exists():Path(temporary).unlink()
        self.exists = True

    def migrate(self, workspace):
        """Only fill unset preferences; legacy files remain untouched."""
        for name, fields in [('game_settings.json', {'installation':'game_installation'}),
                             ('editor_settings.json', {'language':'language'})]:
            path = Path(workspace) / 'cache' / name
            try:legacy = json.loads(path.read_text(encoding='utf-8-sig'))
            except (OSError, ValueError):continue
            if not isinstance(legacy, dict):continue
            for old, new in fields.items():
                if old in legacy and (new not in self.data or not self.exists and new == 'language'):
                    candidate = copy.deepcopy(self.data); candidate[new] = legacy[old]
                    try:self.validate(candidate)
                    except ValueError:continue
                    self.data = candidate
        self.data.setdefault('workspace', str(Path(workspace).resolve()))

    def recent(self, path, name):
        from datetime import datetime, timezone
        path = str(Path(path).resolve())
        rows = [r for r in self.data['recent_projects'] if r['path'].casefold() != path.casefold()]
        self.data['recent_projects'] = [dict(path=path, name=name, opened=datetime.now(timezone.utc).isoformat()), *rows][:12]
        self.save()

    def remove_recent(self, path):
        self.data['recent_projects'] = [r for r in self.data['recent_projects'] if r['path'] != str(path)]
        self.save()
