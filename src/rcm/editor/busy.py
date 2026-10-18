"""Paint synchronous, bounded catalogue work without accepting nested input."""
from contextlib import contextmanager
from PySide6.QtCore import Qt,QEventLoop
from PySide6.QtWidgets import QApplication


@contextmanager
def busy(win,message):
    enabled=win.isEnabled();previous=win.statusBar().currentMessage()
    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor);win.setEnabled(False);win.statusBar().showMessage(message)
    try:
        QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
        yield
    finally:
        win.setEnabled(enabled);win.statusBar().showMessage(previous);QApplication.restoreOverrideCursor()
