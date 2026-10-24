"""Stage text locally; commit once on completion, including Save without focus loss."""
from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtWidgets import QPlainTextEdit, QToolButton


class DeferredEdit(QObject):
    def __init__(self, control, callback, owner=None, *, read=None, signal=None):
        super().__init__(control)
        self.control = control
        self.read = read or (control.toPlainText if isinstance(control, QPlainTextEdit) else control.text)
        self.callback = callback
        self.owner = owner
        self.document = getattr(owner, 'doc', None)
        self.baseline = self.read()
        self.committing = False
        control._rcm_pending = False
        control._rcm_commit = self.commit
        control._rcm_reset = self.reset
        (signal if signal is not None else control.textChanged).connect(self.mark)
        if isinstance(control, QPlainTextEdit):
            control.installEventFilter(self)
        else:
            control.editingFinished.connect(self.commit)

    def notify(self):
        # Never serialize/snapshot the project merely to display the dirty marker.
        notify = getattr(self.owner, 'pending_title', None)
        if notify:
            notify()

    def mark(self, *_):
        pending = self.read() != self.baseline
        if pending != self.control._rcm_pending:
            self.control._rcm_pending = pending
            self.notify()

    def reset(self):
        self.baseline = self.read()
        self.control._rcm_pending = False
        self.notify()

    def commit(self):
        if self.committing:
            return False
        if self.document is not None and getattr(self.owner, 'doc', None) is not self.document:
            self.control._rcm_pending = False
            return True
        if not self.control._rcm_pending:
            return True
        value = self.read()
        if value == self.baseline:
            self.control._rcm_pending = False
            return True
        self.committing = True
        try:
            operation = lambda: self.callback(value)
            result = self.owner.guard(operation) if self.owner is not None else operation()
            if result is not False:
                self.baseline = self.read()
            self.control._rcm_pending = self.read() != self.baseline
            self.notify()
            return result is not False
        finally:
            self.committing = False

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut and event.reason() != Qt.FocusReason.PopupFocusReason:
            self.commit()
        return False


def bind_text(control, callback, owner=None):
    control._rcm_edit = DeferredEdit(control, callback, owner)
    return control


def bind_spin(control, owner=None):
    """Keep arrows immediate, but interpret a typed number only on completion."""
    control.setKeyboardTracking(False)
    edit = DeferredEdit(control, lambda value: control.interpretText(), owner,
                        read=control.text, signal=control.lineEdit().textChanged)
    control._rcm_edit = edit
    control.valueChanged.connect(lambda *_: edit.reset())
    return control


def bind_filter(control, callback):
    """Search once on Enter/focus loss, not on every typed character.

    Programmatic filter resets still apply immediately. The native clear button
    is an explicit request too, rather than an unfinished search.
    """
    typing = False

    def user_edit(*_):
        nonlocal typing
        typing = True

    control.textEdited.connect(user_edit)
    bind_text(control, lambda value: callback())
    control.returnPressed.connect(control._rcm_commit)

    def changed(*_):
        nonlocal typing
        if not typing:
            control._rcm_commit()
        typing = False

    control.textChanged.connect(changed)
    for button in control.findChildren(QToolButton):
        button.clicked.connect(control._rcm_commit)
    return control


def commit_edits(panel):
    if panel is None:
        return True
    for control in panel.findChildren(QObject):
        edit = getattr(control, '_rcm_edit', None)
        if edit and not edit.committing and not edit.commit():
            return False
    return True
