import os
from PySide2 import QtWidgets, QtCore, QtGui
from Rigging_Tool_App.System import UIConstants
from Rigging_Tool_App.UI.Widgets import ClickableLabel, EscapableLineEdit


class EditableLabel(QtWidgets.QWidget):
    label = None
    label_edit = None
    accept_button = None
    cancel_button = None

    change_attempt = QtCore.Signal([None], [str, str])
    change_discarded = QtCore.Signal([None], [str])
    changed = QtCore.Signal([None], [str, str])

    def __init__(self, *args, **kwargs):
        try:
            parent = args[1]
        except IndexError:
            # Assume parent is the first argument
            try:
                parent = args[0]
            except IndexError:
                parent = None

        try:
            assert type(parent) is QtWidgets.QWidget or issubclass(type(parent), QtWidgets.QWidget)
        except AssertionError:
            parent = None

        super(EditableLabel, self).__init__(parent)

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0.0, 0.0, 0.0, 0.0)

        self.setLayout(main_layout)

        accept_target_alias_edit_pixmap = QtGui.QPixmap(
            os.path.join(UIConstants.ICONS_DIRECTORY, "checkbox-circle-fill.png")
        )
        cancel_target_alias_edit_pixmap = QtGui.QPixmap(
            os.path.join(UIConstants.ICONS_DIRECTORY, "close-line.png")
        )

        self.label = ClickableLabel.ClickableLabel(self)
        self.label_edit = EscapableLineEdit.EscapableLineEdit(self)
        self.accept_button = ClickableLabel.ClickableLabel(self)
        self.accept_button.setPixmap(accept_target_alias_edit_pixmap)
        self.cancel_button = ClickableLabel.ClickableLabel(self)
        self.cancel_button.setPixmap(cancel_target_alias_edit_pixmap)

        try:
            self.label.setText(args[0])
            self.label_edit.setText(args[0])
        except(IndexError, AttributeError, RuntimeError, Exception):
            pass

        self.label_edit.escape_on_focus_out = False

        self.label.clicked.connect(self.turnOnEditMode)
        self.cancel_button.clicked.connect(self.turnOffEditMode)
        self.label_edit.escaped.connect(self.turnOffEditMode)

        self.accept_button.clicked.connect(self.emitChangeAttempt)
        self.label_edit.returnPressed.connect(self.accept_button.clicked.emit)

        for w in [self.label_edit, self.accept_button, self.cancel_button]:
            w.setVisible(False)
            w.setEnabled(False)

        self.layout().addWidget(self.label)
        self.layout().addWidget(self.label_edit)
        self.layout().addWidget(self.accept_button)
        self.layout().addWidget(self.cancel_button)

    @QtCore.Slot()
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

    @QtCore.Slot()
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

    @QtCore.Slot()
    def emitChangeAttempt(self):
        try:
            assert len(self.label_edit.text()) > 0
        except AssertionError:
            # Field is empty
            self.change_discarded[str].emit("Field is empty")
            self.change_discarded[None].emit()
        else:
            try:
                assert float(self.label_edit.text()) <= 1.0 and float(self.label_edit.text() >= 0.0)
            except AssertionError:
                # Value is not valid
                pass
            else:
                self.change_attempt[str, str].emit(self.label.text(), self.label_edit.text())
                self.change_attempt[None].emit()

    @QtCore.Slot()
    def acceptChanges(self):
        previous_value = self.label.text()
        self.label.setText(self.label_edit.text())
        self.turnOffEditMode()

        self.changed[str, str].emit(previous_value, self.label.text())
        self.changed[None].emit()

    def text(self):
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
