from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide2.QtCore import Qt, Signal, Slot, Property, QRectF, QSize, QRect, QMargins
from PySide2.QtGui import QPalette, QBrush, QColor, QPainter, QPainterPath, QPen, QFontMetrics

from . import BlockLabel


class RoundedBox(QWidget):
    __borderSize = 1.0
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

    def paintEvent(self, event):
        if self.contentsRect().contains(event.rect(), True):
            return super(RoundedBox, self).paintEvent(event)

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
        rect.adjust(self.borderSize * 0.5, self.borderSize * 0.5, -self.borderSize * 0.5, -self.borderSize * 0.5)

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


class MayaGroupBoxBck(QWidget):
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


class MayaGroupBox(QWidget):
    __title = ""
    __flat = True
    __borderSize = 1.0
    __borderRadius = 5
    __outlineColor = None
    __fillColor = None
    __textColor = None
    __antiAliasing = True

    def __init__(self, title, *args, **kwargs):
        super(MayaGroupBox, self).__init__(*args, **kwargs)

        self.__title = title
        self.__outlineColor = QColor(100, 100, 100)
        self.__outlineColor = QColor("red")
        self.__fillColor = QColor(72, 72, 72)
        self.__fillColor = QColor("transparent")

        #self.setAutoFillBackground(True)

        self.setContentsMargins(QMargins(0, 0, 0, 0))

    def __calcTitleHeight(self):
        title_height = 5.0 + QFontMetrics(self.font()).boundingRect(self.title).height() + 5.0
        print("Title height: {}".format(title_height))
        return title_height

    def contentLayout(self):
        return self.layout()

    def setContentLayout(self, layout):
        self.setLayout(layout)

    def setAlignment(self, align):
        pass

    def getTitle(self):
        return self.__title

    def setTitle(self, title):
        self.__title = title

    def isFlat(self):
        return self.__flat

    def setFlat(self, flat):
        self.__flat = flat

    def getFillColor(self):
        return self.__fillColor

    def getOutlineColor(self):
        return self.__outlineColor

    def getTextColor(self):
        return self.__textColor

    def getBorderSize(self):
        return self.__borderSize

    def getBorderRadius(self):
        return self.__borderRadius

    def isAntiAliased(self):
        return self.__antiAliasing

    def setFillColor(self, fillColor):
        self.__fillColor = fillColor

    def setOutlineColor(self, outlineColor):
        self.__outlineColor = outlineColor

    def setTextColor(self, textColor):
        self.__textColor = textColor

    def setBorderSize(self, borderSize):
        self.__borderSize = borderSize

    def setBorderRadius(self, radius):
        self.__borderRadius = radius

    def setAntiAliasing(self, antiAlias):
        self.__antiAliasing = antiAlias

    @Slot()
    def toggleContent(self):
        pass

    def paintEvent(self, event):
        print("From paint event")
        if self.contentsRect().contains(event.rect(), True):
            #return super(MayaGroupBox, self).paintEvent(event)
            pass

        # Assume the widget needs to repaint itself and not only a region inside it

        # Start painting the title section
        title_rect = QRectF(event.rect())
        title_rect.setHeight(self.__calcTitleHeight())

        contents_rect = QRectF(event.rect())

        # Slightly shrink dimensions to account for borderSize if anti aliasing is set to false
        if self.antiAlias is False:
            left_adjust = (self.borderSize - (self.borderSize % 2)) / 2
            right_adjust = (left_adjust + (self.borderSize % 2)) * -1

            title_rect.adjust(left_adjust, left_adjust, right_adjust, right_adjust)
            contents_rect.adjust(left_adjust, left_adjust, right_adjust, right_adjust)

        # Create the path
        path = QPainterPath()
        path.addRoundedRect(title_rect, self.borderRadius, self.borderRadius)

        # Set painter colors to given values.
        pen = QPen(self.outlineColor, self.borderSize)
        brush = QBrush(self.fillColor)

        # Create the painter
        painter = QPainter(self)

        if self.antiAlias is True:
            painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.setClipPath(path)

        # Fill shape, draw the border and center the text.
        painter.fillPath(path, painter.brush())
        painter.strokePath(path, painter.pen())
        painter.drawText(title_rect, Qt.AlignCenter, self.title)

        # Start painting the contents border

        border_path = QPainterPath()
        border_path.addRoundedRect(contents_rect, self.borderRadius, self.borderRadius)

        border_pen = QPen(self.outlineColor, self.borderSize)

        border_painter = QPainter(self)

        if self.antiAlias is True:
            border_painter.setRenderHint(QPainter.Antialiasing)

        border_painter.setPen(border_pen)
        border_painter.setClipPath(border_path)

        border_painter.strokePath(border_path, border_painter.pen())

    def sizeHint(self):
        size_hint = super(MayaGroupBox, self).sizeHint()
        title_height = self.__calcTitleHeight()
        #contents_rect = self.layout().contentsRect()
        #layout_margins = self.layout().contentsMargins()

        return QSize(size_hint.width(), (title_height + size_hint.height()))

    def minimumSize(self):
        min_size = super(MayaGroupBox, self).minimumSize()

        return QSize(min_size.width(), (self.__calcTitleHeight() + min_size.height()))

    def contentsMargins(self):
        return super(MayaGroupBox, self).contentsMargins()
        margins = super(MayaGroupBox, self).contentsMargins()
        margins.setTop(margins.top() + self.__calcTitleHeight())

        print("Contents margins: {}".format(margins))
        return margins

    def setContentsMargins(self, margins):
        margins.setTop(margins.top() + self.__calcTitleHeight())

        super(MayaGroupBox, self).setContentsMargins(margins)

    def contentsRect(self):
        return super(MayaGroupBox, self).contentsRect()
        cont_rect = super(MayaGroupBox, self).contentsRect()
        print("Prev rect: {}".format(cont_rect))
        #cont_rect.moveTop(self.__calcTitleHeight())
        #cont_rect.setHeight(cont_rect.height() + self.__calcTitleHeight())
        cont_rect.adjust(0, self.__calcTitleHeight(), 0, 0)
        print("New rect: {}".format(cont_rect))

        return cont_rect

    def geometry(self):
        print("From geo")
        geo = super(MayaGroupBox, self).geometry()

        return geo

    title = Property(str, getTitle, setTitle)
    flat = Property(bool, isFlat, setFlat)

    textColor = Property(QColor, getTextColor, setTextColor)
    fillColor = Property(QColor, getFillColor, setFillColor)
    outlineColor = Property(QColor, getOutlineColor, setOutlineColor)
    borderSize = Property(int, getBorderSize, setBorderSize)
    borderRadius = Property(int, getBorderRadius, setBorderRadius)
    antiAlias = Property(bool, isAntiAliased, setAntiAliasing)

