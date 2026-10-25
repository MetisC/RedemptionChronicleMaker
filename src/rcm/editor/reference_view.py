"""Group reference rows without discarding the individual editable uses."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidgetItem
from .i18n import tr
from ..safe_edit import at


def grouped_links(links):
    groups = {}
    for link in links:
        key = (link.source, link.target, link.label)
        uses = groups.setdefault(key, [])
        if link not in uses:
            uses.append(link)
    return list(groups.values())


def usage_label(root, link):
    """Describe the precise authoring location, preserving user-authored text."""
    from .deletion import reference_kind
    path = tuple(link.detail)
    labels = {'nodes': tr('Nodo'), 'lines': tr('Línea'),
              'choices': tr('Respuesta'), 'actions': tr('Acción'),
              'conditions': tr('Condición'), 'inventory': tr('Inventario')}
    parts = []
    for index, key in enumerate(path[:-1]):
        if key not in labels or type(path[index + 1]) is not int:
            continue
        number = path[index + 1]
        row = at(root, path[:index + 2])
        name = row.get('id') if isinstance(row, dict) else None
        parts.append(labels[key] + ' ' + (str(name) if name else str(number + 1)))
        if isinstance(row, dict) and key in ('lines', 'choices') and row.get('text'):
            parts.append(row['text'])
    parts.append(reference_kind(link.label))
    return tr(' · ').join(parts)


def add_reference_groups(parent, win, links, attr):
    """A single summary row per relationship, expandable to every exact use."""
    from .deletion import editable_reference, reference_kind
    root = win.doc.snapshot()
    items = []
    for uses in grouped_links(links):
        link = uses[0]
        target = getattr(link, attr)
        kind = reference_kind(link.label)
        if len(uses) > 1:
            kind += ' (' + str(len(uses)) + ' ' + tr('usos') + ')'
        item = QTreeWidgetItem(parent, [kind, win.reference_label(target)])
        destination = (target if attr == 'target' or len(uses) > 1
                       else editable_reference(root, link.detail))
        item.setData(0, Qt.ItemDataRole.UserRole, destination)
        details = [usage_label(root, use) for use in uses]
        tooltip = win.reference_label(target) + '\n' + '\n'.join(details)
        item.setToolTip(0, tooltip)
        item.setToolTip(1, tooltip)
        if len(uses) > 1:
            for use, description in zip(uses, details):
                child = QTreeWidgetItem(item, [description, win.reference_label(use.source)])
                child.setData(0, Qt.ItemDataRole.UserRole, editable_reference(root, use.detail))
                child.setToolTip(0, description)
                child.setToolTip(1, win.reference_label(use.source))
        items.append(item)
    return items
