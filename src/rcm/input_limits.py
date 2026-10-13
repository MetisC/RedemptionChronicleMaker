"""Bound project inputs before recursive parsers or resource inheritance."""
from typing import Any, Iterable
MAX_BYTES = 2 * 1024 * 1024
CURRENT_PROJECT_FORMAT = 9


def check_project_format(value: Any) -> Any:
    if isinstance(value, dict) and 'project_format' in value:
        version = value['project_format']
        if type(version) is not int:
            raise ValueError('Formato de proyecto inválido.')
        if version > CURRENT_PROJECT_FORMAT:
            raise ValueError('Esta crónica fue creada con una versión más reciente de RCM. Actualiza Redemption Chronicle Maker para abrirla con seguridad.')
    return value


def check_data(value: Any) -> Any:
    pending: list[tuple[Any,int,frozenset[int]]] = [(value, 0, frozenset())]
    count = 0
    while pending:
        item, depth, ancestors = pending.pop()
        count += 1
        if count > 100000 or depth > 32:
            raise ValueError('Proyecto demasiado grande o anidado (máximo 32 niveles)')
        if isinstance(item, (dict, list, tuple)):
            if id(item) in ancestors:
                raise ValueError('Referencias circulares en el proyecto')
            chain = ancestors | {id(item)}
            children: Iterable[Any]
            if isinstance(item, dict):
                if any(not isinstance(k, str) for k in item):
                    raise ValueError('Las claves del proyecto deben ser texto')
                children = item.values()
            else:
                children = item
            pending.extend((child, depth + 1, chain) for child in children)
        elif not isinstance(item, (str, int, float, bool, type(None))):
            raise ValueError('Tipo de dato no admitido en el proyecto')
    return value


def parse_source(source: str | dict) -> Any:
    import yaml
    from .model import UniqueLoader
    if isinstance(source, str):
        if len(source.encode('utf8')) > MAX_BYTES:
            raise ValueError('Proyecto mayor de 2 MiB')
        try:
            source = yaml.load(source, Loader=UniqueLoader)
        except RecursionError as error:
            raise ValueError('YAML demasiado anidado') from error
    return check_project_format(check_data(source))
