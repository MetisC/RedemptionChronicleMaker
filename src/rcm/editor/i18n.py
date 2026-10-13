"""Explicit UI translations. Authored project data is never passed here wholesale."""
import json
import os
import re
import time
from pathlib import Path
from functools import lru_cache

LANGUAGES = {'en': 'English', 'es': 'Español'}
_language = os.environ.get('RCM_EDITOR_LANGUAGE', 'en')
if _language not in LANGUAGES:
    _language = 'en'


def language():
    return _language


def configure(ws):
    global _language
    preferences=getattr(ws,'app_settings',None)
    if preferences:
        _language=preferences.data['language']
        return _language
    path = ws.output('cache/editor_settings.json')
    try:
        data = json.loads(path.read_text(encoding='utf8')) if path.exists() else {}
        value = data.get('language', 'en') if isinstance(data, dict) else 'en'
    except (ValueError, OSError):
        value = 'en'
    _language = value if isinstance(value, str) and value in LANGUAGES else 'en'
    return _language


def save_language(ws, value):
    """Persist only preferences, atomically, without changing project or game settings."""
    if not isinstance(value, str) or value not in LANGUAGES:
        raise ValueError('Unsupported editor language')
    preferences=getattr(ws,'app_settings',None)
    if preferences:
        preferences.data['language']=value;preferences.save();return
    path = ws.output('cache/editor_settings.json')
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding='utf8'))
            if not isinstance(data, dict):
                raise ValueError('Invalid preferences')
        except (ValueError, OSError):
            ws.write('research/editor/preferences_' + str(time.time_ns()) + '.json', path.read_bytes())
            data = {}
    data['language'] = value
    temporary = ws.write('cache/editor_settings.json.tmp', json.dumps(data, ensure_ascii=False, indent=2))
    # Verify the final path again just before replacing it.
    temporary.replace(ws.output('cache/editor_settings.json'))


@lru_cache(maxsize=1)
def catalogue():
    return json.loads((Path(__file__).parent / 'assets/en.json').read_text(encoding='utf8'))


@lru_cache(maxsize=1)
def patterns():
    result = []
    for source, target in catalogue().items():
        parts = re.split(r'(\{\d+\})', source)
        if len(parts) == 1:
            continue
        regex = ''.join('(.*?)' if re.fullmatch(r'\{\d+\}', p) else re.escape(p) for p in parts)
        indices = [int(p[1:-1]) for p in parts if re.fullmatch(r'\{\d+\}', p)]
        result.append((re.compile(regex, re.S), target, indices))
    result.sort(key=lambda row:len(row[0].pattern),reverse=True)
    return result


@lru_cache(maxsize=4096)
def _translate(text, code):
    if code == 'es':
        return text
    found = catalogue().get(text)
    if found is not None:
        return found
    for pattern, target, indices in patterns():
        match = pattern.fullmatch(text)
        if match:
            fields = {str(i): v for i, v in zip(indices, match.groups())}
            return re.sub(r'\{(\d+)\}', lambda m: fields[m[1]], target)
    return text


def tr(text):
    return _translate(str(text), _language)


@lru_cache(maxsize=1)
def prefixes():
    return sorted((s for s in catalogue() if s and '{' not in s),key=len,reverse=True)


def diagnostic(text):
    """Translate known diagnostic sentences; leave unknown details/paths verbatim."""
    text = str(text)
    if language() == 'es':
        return text
    direct = tr(text)
    if direct != text:
        return direct
    lines = []
    for line in text.splitlines(keepends=True):
        ending = '\n' if line.endswith('\n') else ''
        body = line.rstrip('\n')
        translated = tr(body)
        if translated == body:
            for source in prefixes():
                if body.startswith(source + ':') or len(source)>5 and source.endswith(' ') and body.startswith(source):
                    translated = catalogue()[source] + body[len(source):]
                    break
        if translated==body and ': ' in body:
            prefix, rest=body.split(': ',1)
            # A scene/field ID is context, not something to translate.
            translated=prefix+': '+diagnostic(rest)
        lines.append(translated + ending)
    return ''.join(lines)


def install_qt(app):
    from PySide6.QtCore import QTranslator, QLibraryInfo, QLocale, Qt
    from PySide6.QtWidgets import QApplication
    if hasattr(app, '_rcm_translator'):
        app.removeTranslator(app._rcm_translator)
        del app._rcm_translator
    QLocale.setDefault(QLocale('es_ES' if language() == 'es' else 'en_US'))
    # Native OS file dialogs follow Windows' language, not the editor's choice.
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)
    if language() == 'es':
        translator = QTranslator(app)
        folder = Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))
        import sys
        bundled = Path(getattr(sys, '_MEIPASS', folder)) / 'translations'
        if translator.load('qtbase_es', str(bundled)) or translator.load('qtbase_es', str(folder)):
            app.installTranslator(translator)
            app._rcm_translator = translator
