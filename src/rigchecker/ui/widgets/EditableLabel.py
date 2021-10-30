import os

from PySide2.QtWidgets import QWidget, QHBoxLayout, QStyle
from PySide2.QtCore import Signal, Slot, Property, Qt, QObject
from PySide2.QtGui import QPixmap, QPen, QColor

from . import ClickableLabel, EscapableLineEdit


class RoundedFrameStyle(QStyle):
    green_pen = None
    __style = None
    
    def __init__(self, style, *args, **kwargs):
        super(RoundedFrameStyle, self).__init__(*args, **kwargs)
        self.__style = style

    def __getattribute__(self, item):
        return self.__style.__getattribute__(item)

    def __getattr__(self, item):
        return self.__style.__getattr__(item)

    def drawPrimitive(self, element, option, painter, widget):
        self.green_pen = QPen(QColor("green"))
        self.green_pen.setWidth(4)

        if element == QStyle.PE_FrameLineEdit:
            painter.setPen(self.green_pen)
            painter.drawRoundedRect(widget.rect(), 10, 10)
        else:
            super(RoundedFrameStyle, self).drawPrimitive(element, option, painter, widget)


class EditableLabel(QWidget):
    __display_buttons = True
    __edit_mode_status = False
    __editable = True

    label = None
    label_edit = None
    accept_button = None
    cancel_button = None

    changeAttempt = Signal([None], [str, str])
    changeDiscarded = Signal()
    changed = Signal([None], [str, str])

    def __init__(self, text, *args, **kwargs):
        super(EditableLabel, self).__init__(*args, **kwargs)

        #self.setStyle(RoundedFrameStyle(self.style()))

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0.0, 0.0, 0.0, 0.0)

        self.setLayout(main_layout)

        accept_target_alias_edit_pixmap = QPixmap(
            os.path.join(os.environ["ICONS_DIR"], "checkbox-circle-fill.png")
        )
        cancel_target_alias_edit_pixmap = QPixmap(
            os.path.join(os.environ["ICONS_DIR"], "close-line.png")
        )

        self.label = ClickableLabel.ClickableLabel("", self)
        self.label.underline = self.__editable

        self.label_edit = EscapableLineEdit.EscapableLineEdit(self)

        self.accept_button = ClickableLabel.ClickableLabel("", self)
        self.accept_button.setPixmap(accept_target_alias_edit_pixmap)

        self.cancel_button = ClickableLabel.ClickableLabel("", self)
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

    def isEditable(self):
        return self.__editable

    def setEditable(self, editable):
        self.__editable = editable
        self.label.underline = editable

        if editable is True:
            self.label.setCursor(Qt.PointingHandCursor)
        else:
            self.label.setCursor(Qt.ArrowCursor)

    @Slot()
    def enableEditMode(self):
        editable = self.editable
        display_buttons = self.displayButtons

        self.label.setVisible(not editable)
        self.label.setEnabled(not editable)

        self.label_edit.setEnabled(True and editable)
        self.label_edit.setVisible(True and editable)

        self.accept_button.setEnabled(display_buttons and editable)
        self.cancel_button.setEnabled(display_buttons and editable)

        self.accept_button.setVisible(display_buttons and editable)
        self.cancel_button.setVisible(display_buttons and editable)

        if editable is True:
            self.label_edit.setFocus()
            self.label_edit.selectAll()

        self.__edit_mode_status = True and editable

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
        if self.editModeOn is False:
            return self.label.text()
        else:
            return self.label_edit.text()

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
    editable = Property(bool, isEditable, setEditable)
    displayButtons = Property(bool, __getDisplayButtons, __setDisplayButtons)
    editModeOn = Property(bool, __getEditModeStatus, __setEditModeStatus)
