from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide2.QtCore import Qt, Signal, Slot, Property, QRectF
from PySide2.QtGui import QPalette, QBrush, QColor, QPainter, QPainterPath, QPen

from . import BlockLabel
reload(BlockLabel)


class RoundedBox(QWidget):
    __borderSize = 1
    __outlineColor = None
    __fillColor = None
    __textColor = None

    def __init__(self, *args, **kwargs):
        super(RoundedBox, self).__init__(*args, **kwargs)

        self.__outlineColor = QColor(100, 100, 100)
        self.__fillColor = QColor(72, 72, 72)

        self.setAutoFillBackground(True)

    def getFillColor(self):
        return self.__fillColor

    def getOutlineColor(self):
        return self.__outlineColor

    def getTextColor(self):
        return self.__textColor

    def getBorderSize(self):
        return self.__borderSize

    def setFillColor(self, fillColor):
        self.__fillColor = fillColor

    def setOutlineColor(self, outlineColor):
        self.__outlineColor = outlineColor

    def setTextColor(self, textColor):
        self.__textColor = textColor

    def setBorderSize(self, borderSize):
        self.__borderSize = borderSize

    def paintEventBck(self, event):
        # Create the painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Create the path
        path = QPainterPath()
        # Set painter colors to given values.
        pen = QPen(self.outlineColor, self.borderSize)
        painter.setPen(pen)
        brush = QBrush(self.fillColor)
        painter.setBrush(brush)

        rect = QRectF(event.rect())
        # Slightly shrink dimensions to account for borderSize.
        rect.adjust(self.borderSize / 2, self.borderSize / 2, -self.borderSize / 2, -self.borderSize / 2)

        # Add the rect to path.
        path.addRoundedRect(rect, 5, 5)
        painter.setClipPath(path)

        # Fill shape, draw the border and center the text.
        painter.fillPath(path, painter.brush())
        painter.strokePath(path, painter.pen())
        #painter.drawText(rect, Qt.AlignCenter, self.title)

    textColor = Property(QColor, getTextColor, setTextColor)
    fillColor = Property(QColor, getFillColor, setFillColor)
    outlineColor = Property(QColor, getOutlineColor, setOutlineColor)
    borderSize = Property(int, getBorderSize, setBorderSize)


class MayaGroupBoxTitle(RoundedBox):
    __title_label = None

    # Signals
    clicked = Signal()
    doubleClicked = Signal()

    def __init__(self, title, *args, **kwargs):
        super(MayaGroupBoxTitle, self).__init__(*args, **kwargs)

        self.setLayout(QHBoxLayout(self))

        self.layout().setAlignment(Qt.AlignLeft)
        self.layout().setContentsMargins(10, 5, 10, 5)

        self.__title_label = QLabel(title, self)

        self.layout().addWidget(self.__title_label)

        palette = self.palette()

        palette.setBrush(QPalette.Active, QPalette.Window, QBrush(self.fillColor))
        palette.setBrush(QPalette.Active, QPalette.Base, QBrush(self.fillColor))
        palette.setBrush(QPalette.Active, QPalette.Text, QBrush(QColor(127, 127, 127)))

        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setCursor(Qt.PointingHandCursor)

        self.fillColor = QColor(100, 100, 100)
        self.textColor = QColor(127, 127, 127)

    def setAlignment(self, align):
        self.layout().setAlignment(align)

    def getTitle(self):
        return self.__title_label.text()

    def setTitle(self, title):
        self.__title_label.setText(title)

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

    title = Property(str, getTitle, setTitle)


class MayaGroupBoxContent(RoundedBox):
    def __init__(self, *args, **kwargs):
        super(MayaGroupBoxContent, self).__init__(*args, **kwargs)

        self.fillColor = QColor(72, 72, 72)
        self.textColor = QColor(127, 127, 127)

        palette = self.palette()

        for role in [QPalette.Active, QPalette.Inactive]:
            palette.setBrush(role, QPalette.Window, QBrush(QColor(72, 72, 72)))
            palette.setBrush(role, QPalette.Base, QBrush(QColor(72, 72, 72)))
            palette.setBrush(role, QPalette.Text, QBrush(QColor(127, 127, 127)))

        self.setPalette(palette)
        self.setAutoFillBackground(True)


class MayaGroupBox(QWidget):
    __title_widget = None
    __content_area_widget = None

    def __init__(self, title, *args, **kwargs):
        super(MayaGroupBox, self).__init__(*args, **kwargs)

        self.setLayout(QVBoxLayout(self))
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(2)

        self.__title_widget = MayaGroupBoxTitle(title, self)
        self.__title_widget.clicked.connect(self.toggleContent)

        '''self.__content_area_widget = QWidget(self)

        palette = self.__content_area_widget.palette()

        for role in [QPalette.Active, QPalette.Inactive]:
            palette.setBrush(role, QPalette.Window, QBrush(QColor(72, 72, 72)))
            palette.setBrush(role, QPalette.Base, QBrush(QColor(72, 72, 72)))
            palette.setBrush(role, QPalette.Text, QBrush(QColor(127, 127, 127)))

        self.__content_area_widget.setPalette(palette)
        self.__content_area_widget.setAutoFillBackground(True)'''
        self.__content_area_widget = MayaGroupBoxContent(self)

        self.layout().addWidget(self.__title_widget)
        self.layout().addWidget(self.__content_area_widget)

    def contentLayout(self):
        return self.__content_area_widget.layout()

    def setContentLayout(self, layout):
        self.__content_area_widget.setLayout(layout)

    def setAlignment(self, align):
        self.__title_widget.setAlignment(align)

    def getTitle(self):
        return self.__title_widget.title

    def setTitle(self, title):
        self.__title_widget.title = title

    def isFlat(self):
        return not self.__content_area_widget.isVisible()

    def setFlat(self, flat):
        self.__content_area_widget.setVisible(not flat)

    @Slot()
    def toggleContent(self):
        self.__content_area_widget.setVisible(not self.__content_area_widget.isVisible())

    title = Property(str, getTitle, setTitle)
    flat = Property(bool, isFlat, setFlat)

