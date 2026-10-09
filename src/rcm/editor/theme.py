"""Consistent, readable authoring colors for Windows light and dark palettes."""
from PySide6.QtGui import QColor, QPalette


def editor_palette(source):
    palette = QPalette(source)
    dark = source.color(QPalette.ColorRole.Window).lightnessF() < .5
    colors = {
        'Window': '#20242b' if dark else '#f4f6f8',
        'Base': '#252b33' if dark else '#ffffff',
        'AlternateBase': '#303844' if dark else '#edf2f7',
        'Text': '#f0f3f7' if dark else '#182536',
        'WindowText': '#f0f3f7' if dark else '#182536',
        'Button': '#343e4c' if dark else '#e7edf4',
        'ButtonText': '#f0f3f7' if dark else '#182536',
        'ToolTipBase': '#303844' if dark else '#fff8df',
        'ToolTipText': '#f0f3f7' if dark else '#182536',
        'Highlight': '#345e87' if dark else '#2164a3',
        'HighlightedText': '#ffffff',
        'Link': '#8ec9ff' if dark else '#12568f',
    }
    for role, color in colors.items():
        palette.setColor(getattr(QPalette.ColorRole, role), QColor(color))
    for role in (QPalette.ColorRole.Text, QPalette.ColorRole.WindowText, QPalette.ColorRole.ButtonText):
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor('#a1afc0' if dark else '#596a7d'))
    return palette
