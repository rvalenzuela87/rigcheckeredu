import os

from PySide2.QtWidgets import QWidget, QHBoxLayout
from PySide2.QtCore import Signal, Slot, Property
from PySide2.QtGui import QPixmap

from . import ClickableLabel, EscapableLineEdit


class EditableLabel(QWidget):
    __display_buttons = True
    __edit_mode_status = False

    label = None
    label_edit = None
    accept_button = None
    cancel_button = None

    changeAttempt = Signal([None], [str, str])
    changeDiscarded = Signal()
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

        self.label.clicked.connect(self.enableEditMode)
        self.cancel_button.clicked.connect(self.disableEditMode)
        self.label_edit.escaped.connect(self.disableEditMode)
        self.label_edit.escaped.connect(self.changeDiscarded.emit)

        self.accept_button.clicked.connect(self.acceptChanges)
        self.label_edit.returnPressed.connect(self.acceptChanges)

        for w in [self.label_edit, self.accept_button, self.cancel_button]:
            w.setVisible(False)
            w.setEnabled(False)

        self.layout().addWidget(self.label)
        self.layout().addWidget(self.label_edit)
        self.layout().addWidget(self.accept_button)
        self.layout().addWidget(self.cancel_button)

    def __getDisplayButtons(self):
        return self.__display_buttons

    def __setDisplayButtons(self, display):
        self.__display_buttons = display

    def __getEditModeStatus(self):
        return self.__edit_mode_status

    def __setEditModeStatus(self, enable):
        if enable is True:
            self.enableEditMode()
        else:
            self.disableEditMode()

    @Slot()
    def enableEditMode(self):
        self.label.setEnabled(False)
        self.label_edit.setEnabled(True)

        self.label.setVisible(False)
        self.label_edit.setVisible(True)

        if self.displayButtons is True:
            self.accept_button.setEnabled(True)
            self.cancel_button.setEnabled(True)

            self.accept_button.setVisible(True)
            self.cancel_button.setVisible(True)

        self.label_edit.setFocus()
        self.label_edit.selectAll()
        self.__edit_mode_status = True

    @Slot()
    def disableEditMode(self):
        self.label_edit.deselect()
        self.label_edit.setEnabled(False)
        self.label.setEnabled(True)

        self.label_edit.setVisible(False)

        if self.displayButtons is True:
            self.accept_button.setEnabled(False)
            self.cancel_button.setEnabled(False)

            self.accept_button.setVisible(False)
            self.cancel_button.setVisible(False)

        self.label.setVisible(True)
        self.__edit_mode_status = False

    @Slot()
    def acceptChanges(self):
        previous_value = self.label.text()
        self.label.setText(self.label_edit.text())
        self.disableEditMode()

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
    displayButtons = Property(bool, __getDisplayButtons, __setDisplayButtons)
    editModeOn = Property(bool, __getEditModeStatus, __setEditModeStatus)
