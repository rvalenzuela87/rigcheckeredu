from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide2.QtCore import Qt, Signal, Slot, Property
from PySide2.QtGui import QPalette, QBrush, QColor

from . import BlockLabel
reload(BlockLabel)


class MayaGroupBoxTitle(QWidget):
    clicked = Signal()
    doubleClicked = Signal()

    def __init__(self, title, *args, **kwargs):
        super(MayaGroupBoxTitle, self).__init__(*args, **kwargs)

        self.setLayout(QHBoxLayout(self))
        self.layout().setAlignment(Qt.AlignLeft)
        self.layout().setContentsMargins(10, 5, 10, 5)

        self.layout().addWidget(QLabel(title, self))

        palette = self.palette()

        for role in [QPalette.Active, QPalette.Inactive]:
            palette.setBrush(role, QPalette.Window, QBrush(QColor(93, 93, 93)))
            palette.setBrush(role, QPalette.Base, QBrush(QColor(93, 93, 93)))
            palette.setBrush(role, QPalette.Text, QBrush(QColor(127, 127, 127)))

        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setCursor(Qt.PointingHandCursor)

    def setAlignment(self, align):
        self.layout().setAlignment(align)

    @Slot()
    def click(self):
        self.clicked.emit()

    @Slot()
    def doubleClick(self):
        self.doubleClicked.emit()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

        super(MayaGroupBoxTitle, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        super(MayaGroupBoxTitle, self).mouseDoubleClickEvent(event)


class MayaGroupBox(QWidget):
    __title_widget = None
    __content_area_widget = None

    def __init__(self, title, *args, **kwargs):
        super(MayaGroupBox, self).__init__(*args, **kwargs)

        self.setLayout(QVBoxLayout(self))
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.__title_widget = MayaGroupBoxTitle(title, self)
        self.__title_widget.clicked.connect(self.toggleContent)

        self.__content_area_widget = QWidget(self)

        palette = self.__content_area_widget.palette()

        for role in [QPalette.Active, QPalette.Inactive]:
            palette.setBrush(role, QPalette.Window, QBrush(QColor(72, 72, 72)))
            palette.setBrush(role, QPalette.Base, QBrush(QColor(72, 72, 72)))
            palette.setBrush(role, QPalette.Text, QBrush(QColor(127, 127, 127)))

        self.__content_area_widget.setPalette(palette)
        self.__content_area_widget.setAutoFillBackground(True)

        self.layout().addWidget(self.__title_widget)
        self.layout().addWidget(self.__content_area_widget)

    def contentLayout(self):
        return self.__content_area_widget.layout()

    def setContentLayout(self, layout):
        self.__content_area_widget.setLayout(layout)

    def setAlignment(self, align):
        self.__title_widget.setAlignment(align)

    def getTitle(self):
        return self.__title_widget.text()

    def setTitle(self, title):
        self.__title_widget.setText(title)

    def isFlat(self):
        return not self.__content_area_widget.isVisible()

    def setFlat(self, flat):
        self.__content_area_widget.setVisible(not flat)

    @Slot()
    def toggleContent(self):
        self.__content_area_widget.setVisible(not self.__content_area_widget.isVisible())

    title = Property(str, getTitle, setTitle)
    flat = Property(bool, isFlat, setFlat)

