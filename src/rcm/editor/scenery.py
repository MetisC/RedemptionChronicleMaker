"""Escenografía: placement dialog for parametric native brush pieces.

The piece is authored as a normal scene object with a `geometry` record;
native collision modes are marked experimental until verified in game.
"""
from PySide6.QtWidgets import (QCheckBox, QComboBox, QCompleter, QDialog,
                               QDialogButtonBox, QDoubleSpinBox, QFormLayout,
                               QLabel, QLineEdit, QScrollArea, QVBoxLayout,
                               QWidget)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
from ..scenery import MODES, PRESETS
from .i18n import tr

MODE_LABELS = {
    'decor': tr('Visible · sin colisión'),
    'solid': tr('Visible · con colisión (experimental)'),
    'barrier': tr('Barrera invisible · experimental'),
    'interactive': tr('Interactiva · responde a clics'),
}


class DecorDialog(QDialog):
    """Preset + size + native material for a parametric box piece.

    With `initial` (a geometry record) the dialog edits the piece: fields are
    prefilled and the preset row shows "(personalizada)" so picking a preset
    still re-templates the piece.
    """

    def __init__(self, parent, level=None, assets=None, initial=None):
        super().__init__(parent)
        self.setObjectName('decor_dialog')
        self.setWindowTitle(tr('Editar decoración') if initial else tr('Nueva decoración'))
        self.payload = None
        self.assets = assets
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.preset = QComboBox(); self.preset.setObjectName('decor_preset')
        for name, mode, size in PRESETS:
            self.preset.addItem(tr(name), (mode, list(size)))
        self.preset.currentIndexChanged.connect(self.apply_preset)
        form.addRow(tr('Pieza'), self.preset)
        self.mode = QComboBox(); self.mode.setObjectName('decor_mode')
        for key in MODES:
            self.mode.addItem(MODE_LABELS[key], key)
        form.addRow(tr('Comportamiento'), self.mode)
        self.size = []
        for axis in 'XYZ':
            spin = QDoubleSpinBox(); spin.setObjectName('decor_size_' + axis.lower())
            spin.setRange(1, 50000); spin.setDecimals(1); spin.setValue(64)
            self.size.append(spin)
            form.addRow(tr('Tamaño ') + axis, spin)
        self.material_names = (sorted(set(level.mesh.materials))
                               if level is not None and getattr(level, 'mesh', None) is not None
                               else ['Prague\\wall1_P'])
        self.material = QComboBox(); self.material.setObjectName('decor_material')
        # The field itself is the search box: typing opens a live-filtered
        # popup (contains, case-insensitive); Enter picks a match there
        # instead of submitting the dialog.
        self.material.setEditable(True)
        self.material.addItems(self.material_names)
        if self.material.lineEdit():
            self.material.lineEdit().setPlaceholderText(tr('Escribe para buscar…'))
        completer = QCompleter(self.material_names, self.material)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.material.setCompleter(completer)
        form.addRow(tr('Material'), self.material)
        self.material_preview = QLabel(); self.material_preview.setObjectName('decor_material_preview')
        self.material_preview.setFixedSize(96, 96)
        self.material_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.material_preview.setFrameShape(QLabel.Shape.StyledPanel)
        form.addRow('', self.material_preview)
        self.material.currentTextChanged.connect(self.update_material_preview)
        self.update_material_preview(self.material.currentText())
        self.uv_mode = QComboBox(); self.uv_mode.setObjectName('decor_uv_mode')
        self.uv_mode.addItem(tr('Repetida (tiled)'), 'tile')
        self.uv_mode.addItem(tr('Ajustada a la cara (expanded)'), 'stretch')
        self.uv_mode.setToolTip(tr('Repetida: la textura se repite según la escala. Ajustada: la textura cubre cada cara entera.'))
        self.uv_mode.currentIndexChanged.connect(lambda _i: self.uv_scale.setEnabled(self.uv_mode.currentData() == 'tile'))
        form.addRow(tr('Textura'), self.uv_mode)
        self.uv_scale = QDoubleSpinBox(); self.uv_scale.setObjectName('decor_uv_scale')
        self.uv_scale.setRange(4, 4096); self.uv_scale.setValue(64)
        self.uv_scale.setToolTip(tr('Unidades del mundo por repetición de textura'))
        form.addRow(tr('Escala de textura'), self.uv_scale)
        layout.addLayout(form)
        note = QLabel(tr('Entidad brush nativa en el NSD; la geometría original no se modifica.'))
        note.setWordWrap(True)
        layout.addWidget(note)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.on_accepted)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        if initial is None:
            self.apply_preset(0)
        else:
            self.preset.insertItem(0, tr('(personalizada)'), None)
            self.preset.setCurrentIndex(0)
            if initial.get('mode', 'decor') in MODES:
                self.mode.setCurrentIndex(list(MODES).index(initial['mode']))
            for spin, value in zip(self.size, list(initial.get('size', [64, 64, 64]))[:3]):
                spin.setValue(float(value))
            if initial.get('material'):
                self.material.setCurrentText(initial['material'])
            self.uv_scale.setValue(float(initial.get('uv_scale', 64)))
            self.uv_mode.setCurrentIndex(1 if initial.get('uv_mode') == 'stretch' else 0)

    def apply_preset(self, index):
        data = self.preset.itemData(index)
        if data is None:
            return
        mode, size = data
        self.mode.setCurrentIndex(list(MODES).index(mode))
        for spin, value in zip(self.size, size):
            spin.setValue(value)

    def update_material_preview(self, name):
        pixmap = None
        tooltip = tr('Sin vista previa')
        if self.assets is not None and name:
            mat = self.assets.material(name.strip())
            if mat.warning is None and mat.rgba:
                image = QImage(mat.rgba, mat.width, mat.height, mat.width * 4,
                               QImage.Format.Format_RGBA8888).copy()
                pixmap = QPixmap.fromImage(image).scaled(
                    96, 96, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
                tooltip = mat.texture or name
            elif mat.warning:
                tooltip = mat.warning
        self.material_preview.setPixmap(pixmap or QPixmap())
        self.material_preview.setToolTip(tooltip)

    def on_accepted(self):
        self.payload = dict(mode=self.mode.currentData(),
                            size=[spin.value() for spin in self.size],
                            material=self.material.currentText().strip(),
                            uv_scale=self.uv_scale.value(),
                            uv_mode=self.uv_mode.currentData())
        self.accept()


def capture_prefab(name, rows):
    """Snapshot absolute objects into a prefab relative to the first item."""
    pivot = rows[0]['transform']['position']
    items = []
    for row in rows:
        transform = row['transform']
        item = dict(name=row.get('name', row['id']),
                    offset=[round(transform['position'][i] - pivot[i], 4) for i in range(3)],
                    orientation=list(transform.get('orientation', [0, 0, 0])))
        if 'geometry' in row:
            item['geometry'] = dict(row['geometry'])
        else:
            item['template'] = row['template']
        items.append(item)
    return dict(name=name, items=items)


def instantiate_prefab(prefab, position):
    """Expand a prefab into normal object rows; ids are assigned by caller."""
    rows = []
    for item in prefab['items']:
        row = dict(name=item['name'],
                   transform=dict(placement='absolute',
                                  position=[position[i] + item['offset'][i] for i in range(3)],
                                  orientation=list(item.get('orientation', [0, 0, 0]))))
        if 'geometry' in item:
            row['geometry'] = dict(item['geometry'])
            row['template'] = MODES[item['geometry'].get('mode', 'decor')]
        else:
            row['template'] = item['template']
        rows.append(row)
    return rows


class PrefabDialog(QDialog):
    """Capture a set of scene objects as a reusable prefab composition."""

    def __init__(self, parent, objects):
        super().__init__(parent)
        self.setObjectName('prefab_dialog')
        self.setWindowTitle(tr('Guardar decorado'))
        self.payload = None
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit(tr('Decorado')); self.name.setObjectName('prefab_name')
        form.addRow(tr('Nombre'), self.name)
        layout.addLayout(form)
        note = QLabel(tr('Elige los objetos que forman el conjunto. El primero marcado hace de pivote; '
                         'se guardan posiciones relativas y cada copia crea objetos normales editables.'))
        note.setWordWrap(True)
        layout.addWidget(note)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setMaximumHeight(260)
        body = QWidget(); box = QVBoxLayout(body)
        self.checks = []
        for i, row in enumerate(objects):
            if row.get('transform', {}).get('placement', 'absolute') != 'absolute':
                continue
            check = QCheckBox(row.get('name', row['id']) + ' · ' + row['id'])
            check.setChecked(True)
            self.checks.append((check, i))
            box.addWidget(check)
        box.addStretch()
        scroll.setWidget(body)
        layout.addWidget(scroll)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.on_accepted)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def on_accepted(self):
        from PySide6.QtWidgets import QMessageBox
        chosen = [i for check, i in self.checks if check.isChecked()]
        if not chosen or not self.name.text().strip():
            QMessageBox.warning(self, tr('Guardar decorado'), tr('Elige un nombre y al menos un objeto.'))
            return
        self.payload = (self.name.text().strip(), chosen)
        self.accept()


class PrefabPickDialog(QDialog):
    """Choose one stored prefab to instantiate at the clicked point."""

    def __init__(self, parent, prefabs):
        super().__init__(parent)
        self.setObjectName('prefab_pick_dialog')
        self.setWindowTitle(tr('Colocar decorado'))
        self.payload = None
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.combo = QComboBox(); self.combo.setObjectName('prefab_choice')
        for i, prefab in enumerate(prefabs):
            self.combo.addItem(prefab.get('name', prefab['id']) + ' · ' + str(len(prefab['items'])), i)
        form.addRow(tr('Decorado'), self.combo)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.on_accepted)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def on_accepted(self):
        self.payload = self.combo.currentData()
        self.accept()
