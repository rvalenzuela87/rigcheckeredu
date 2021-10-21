import os

from PySide2.QtWidgets import QWidget, QHBoxLayout
from PySide2.QtCore import Signal, Slot, Property
from PySide2.QtGui import QPixmap

from . import ClickableLabel, EscapableLineEdit


class EditableLabel(QWidget):
    label = None
    label_edit = None
    accept_button = None
    cancel_button = None

    changeAttempt = Signal([None], [str, str])
    changeDiscarded = Signal([None], [str])
    changed = Signal([None], [str, str])

    def __init__(self, text, *args, **kwargs):
        super(EditableLabel, self).__init__(*args, **kwargs)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0.0, 0.0, 0.0, 0.0)

        self.setLayout(main_layout)

        accept_target_alias_edit_pixmap = QPixmap(
            os.path.join(os.environ["ICONS_DIR"], "checkbox-circle-fill.png")
        )
        cancel_target_alias_edit_pixmap = QPixmap(
            os.path.join(os.environ["ICONS_DIR"], "close-line.png")
        )

        self.label = ClickableLabel.ClickableLabel(self)
        self.label_edit = EscapableLineEdit.EscapableLineEdit(self)

        self.accept_button = ClickableLabel.ClickableLabel(self)
        self.accept_button.setPixmap(accept_target_alias_edit_pixmap)

        self.cancel_button = ClickableLabel.ClickableLabel(self)
        self.cancel_button.setPixmap(cancel_target_alias_edit_pixmap)

        try:
            self.label.setText(text)
            self.label_edit.setText(text)
        except(IndexError, AttributeError, RuntimeError, Exception):
            pass

        self.label_edit.escapeOnFocusOut = False

        self.label.clicked.connect(self.turnOnEditMode)
        self.cancel_button.clicked.connect(self.turnOffEditMode)
        self.label_edit.escaped.connect(self.turnOffEditMode)

        self.accept_button.clicked.connect(self.acceptChanges)
        self.label_edit.returnPressed.connect(self.acceptChanges)

        for w in [self.label_edit, self.accept_button, self.cancel_button]:
            w.setVisible(False)
            w.setEnabled(False)

        self.layout().addWidget(self.label)
        self.layout().addWidget(self.label_edit)
        self.layout().addWidget(self.accept_button)
        self.layout().addWidget(self.cancel_button)

    @Slot()
    def turnOnEditMode(self):
        self.label.setVisible(False)
        self.label.setEnabled(False)

        self.label_edit.setEnabled(True)
        self.accept_button.setEnabled(True)
        self.cancel_button.setEnabled(True)

        self.label_edit.setVisible(True)
        self.accept_button.setVisible(True)
        self.cancel_button.setVisible(True)

        self.label_edit.setFocus()
        self.label_edit.selectAll()

    @Slot()
    def turnOffEditMode(self):
        self.label_edit.setEnabled(False)
        self.accept_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

        self.label_edit.setVisible(False)
        self.accept_button.setVisible(False)
        self.cancel_button.setVisible(False)

        self.label.setEnabled(True)
        self.label.setVisible(True)

        self.label_edit.deselect()

    @Slot()
    def acceptChanges(self):
        previous_value = self.label.text()
        self.label.setText(self.label_edit.text())
        self.turnOffEditMode()

        self.changed[str, str].emit(previous_value, self.label.text())
        self.changed[None].emit()

    def getText(self):
        return self.label.text()

    def setText(self, text):
        self.label.setText(text)
        self.label_edit.setText(text)

    def setValidator(self, validator):
        self.label_edit.setValidator(validator)

    def setMaxLength(self, max):
        self.label_edit.setMaxLength(max)

    def setMinLength(self, min):
        self.label_edit.setMinLength(min)

    text = Property(str, getText, setText)
