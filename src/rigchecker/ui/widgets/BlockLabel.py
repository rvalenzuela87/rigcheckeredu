from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QHBoxLayout, QSizePolicy
from PySide2.QtGui import QPalette, QColor, QBrush, QFontMetrics
from PySide2.QtCore import Qt, Signal, Slot, Property

from . import ClickableLabel


class BlockLabel(QWidget):
    __text_label = None
    __close_button = None

    clicked = Signal()
    doubleClicked = Signal

    def __init__(self, text, *args, **kwargs):
        super(BlockLabel, self).__init__(*args, **kwargs)

        self.__text_label = QLabel("", self)
        self.__text_label.setSizePolicy(
            QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        )
        self.__close_button = ClickableLabel.ClickableLabel("x", self)
        self.__close_button.setSizePolicy(
            QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        )
        self.__close_button.clicked.connect(self.delete)

        m_width = QFontMetrics(self.__text_label.font()).widthChar("m")

        self.setLayout(QHBoxLayout(self))
        self.layout().setContentsMargins(int(m_width * 0.5), int(m_width * 0.25), int(m_width * 0.5), int(m_width * 0.25))
        self.layout().setSpacing(m_width)
        self.layout().setAlignment(Qt.AlignVCenter)

        self.layout().addWidget(self.__text_label)
        self.layout().addWidget(self.__close_button)

        if text is not None:
            self.setText(text)

        palette = self.palette()

        for role in [QPalette.Active, QPalette.Inactive]:
            palette.setBrush(role, QPalette.Window, QBrush(QColor(255, 0, 0)))
            palette.setBrush(role, QPalette.Base, QBrush(QColor(255, 0, 0)))
            palette.setBrush(role, QPalette.Text, QBrush(QColor(255, 255, 255)))

        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def getText(self):
        return self.__text_label.text()

    def setText(self, text):
        self.__text_label.setText(text)

    def getCloseButton(self):
        return self.__close_button

    def isLocked(self):
        return self.closeButton.isEnabled()

    def setLocked(self, locked):
        self.closeButton.setEnabled(not locked)
        self.closeButton.setVisible(not locked)

    @Slot()
    def click(self):
        self.clicked.emit()

    @Slot()
    def doubleClick(self):
        self.doubleClicked.emit()

    @Slot()
    def delete(self):
        self.setVisible(False)
        self.setParent(None)
        self.deleteLater()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

        super(BlockLabel, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        super(BlockLabel, self).mouseDoubleClickEvent(event)

    text = Property(str, getText, setText)
    locked = Property(bool, isLocked, setLocked)
    closeButton = Property(ClickableLabel.ClickableLabel, getCloseButton, None)
