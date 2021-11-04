from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.QtCore import Qt, Signal, Slot, Property, QRectF, QSize, QRect, QMargins, QEvent, QObject
from PySide2.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QFontMetrics


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


class MayaGroupBox(QWidget):
    __title = ""
    __titleMargins = None
    __titleAlignment = Qt.AlignCenter
    __layoutMargins = None
    __flat = False
    __borderSize = 2
    __borderRadius = 5
    __outlineColor = None
    __fillColor = None
    __textColor = None
    __antiAliasing = True
    __contentWidget = None

    # Signals
    clicked = Signal([None], [QWidget])

    def __init__(self, title, *args, **kwargs):
        super(MayaGroupBox, self).__init__(*args, **kwargs)

        self.__title = title
        self.__titleMargins = QMargins(10, 10, 10, 10)
        self.__outlineColor = QColor(100, 100, 100)
        self.__fillColor = QColor(72, 72, 72)
        self.__textColor = QColor(200, 200, 200)

        #self.setAutoFillBackground(True)

        super(MayaGroupBox, self).setContentsMargins(QMargins(0, self.__calcTitleHeight(), 0, 0))
        super(MayaGroupBox, self).setMouseTracking(True)

        content_layout = QVBoxLayout(self)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.__contentWidget = QWidget(self)

        content_layout.addWidget(self.__contentWidget)
        super(MayaGroupBox, self).setLayout(content_layout)

    def __calcTitleHeight(self):
        title_height = self.titleMargins.top() + QFontMetrics(self.font()).boundingRect(self.title).height() + self.titleMargins.bottom()

        return title_height

    def titleRect(self):
        widget_rect = self.rect()

        return QRect(widget_rect.x(), widget_rect.y(), widget_rect.width(), self.__calcTitleHeight())

    def layout(self):
        return self.__contentWidget.layout()

    def contentLayout(self):
        return self.__contentWidget.layout()

    def getTitle(self):
        return self.__title

    def getTitleMargins(self):
        return self.__titleMargins

    def getTitleAlignment(self):
        return self.__titleAlignment

    def isFlat(self):
        return self.__flat

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

    def setContentLayout(self, layout):
        self.__contentWidget.setLayout(layout)

    def setLayout(self, layout):
        self.__contentWidget.setLayout(layout)

    def setAlignment(self, align):
        pass

    def setTitle(self, title):
        self.__title = title

    def setTitleMargins(self, *args):
        try:
            left, top, right, bot = args

            self.__titleMargins = QMargins(left, top, right, bot)
        except(TypeError, IndexError):
            # Assume the method received a single argument of type QMargins
            try:
                margins = args[0]
                assert type(margins) is QMargins
            except(RuntimeError, IndexError, TypeError, AssertionError):
                pass
            else:
                self.__titleMargins = margins

    def setTitleAlignment(self, align):
        self.__titleAlignment = align

    def setFlat(self, flat):
        self.__flat = flat
        self.__contentWidget.setVisible(not flat)

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
        """
        Shows or hides the content section.

        @return: None
        """

        self.setFlat(not self.flat)

    def paintEvent(self, event):
        if self.rect().contains(event.rect(), True):
            # This means the region to render is, probably, an inner section of the widget, therefore there is no
            # need to repaint the whole widget
            return super(MayaGroupBox, self).paintEvent(event)

        # Assume the widget needs to repaint itself and not only a region inside it

        # Start painting the title section
        contents_rect = QRectF(self.rect())
        contents_clip_rect = QRectF(contents_rect)

        title_rect = QRectF(contents_rect)
        title_rect.setHeight(self.__calcTitleHeight())
        title_clip_rect = QRectF(title_rect)

        # Slightly shrink dimensions to account for borderSize if anti aliasing is set to false
        if self.antiAlias is False:
            left_adjust = (self.borderSize - (self.borderSize % 2)) / 2
            right_adjust = (left_adjust + (self.borderSize % 2)) * -1

            title_rect.adjust(left_adjust, left_adjust, right_adjust, right_adjust)
            contents_rect.adjust(left_adjust, left_adjust, right_adjust, right_adjust)
        else:
            # When antialiasing is on, the border width will be distributed, equally, outside and inside the
            # rectangle. Therefore, adjust the rectangle accordingly so the borders get painted inside the
            # calculated geometry
            half_border_size = float(self.borderSize) * 0.5
            title_rect.adjust(half_border_size, half_border_size, half_border_size * -1.0, half_border_size * -1.0)
            contents_rect.adjust(half_border_size, half_border_size, half_border_size * -1.0, half_border_size * -1.0)

        # Start painting the contents border
        contents_border_path = QPainterPath()
        contents_border_path.addRoundedRect(contents_rect, self.borderRadius, self.borderRadius)

        contents_clip_path = QPainterPath()
        contents_clip_path.addRoundedRect(contents_clip_rect, self.borderRadius, self.borderRadius)

        contents_border_painter = QPainter(self)

        if self.antiAlias is True:
            contents_border_painter.setRenderHint(QPainter.Antialiasing)

        contents_border_painter.setClipPath(contents_clip_path)

        if self.borderSize > 0:
            contents_border_pen = QPen(self.outlineColor, self.borderSize)
            contents_border_painter.strokePath(contents_border_path, contents_border_pen)

        # Create the title rounded border path
        title_border_path = QPainterPath()
        title_border_path.addRoundedRect(title_rect, self.borderRadius, self.borderRadius)

        title_clip_path = QPainterPath()
        title_clip_path.addRoundedRect(title_clip_rect, self.borderRadius, self.borderRadius)

        # Set painter colors to given values.
        title_border_brush = QBrush(self.fillColor)

        # Create the painter
        title_painter = QPainter(self)

        if self.antiAlias is True:
            title_painter.setRenderHint(QPainter.Antialiasing)

        title_painter.setClipPath(title_clip_path)

        # Fill shape, draw the border and center the text.
        title_painter.fillPath(title_border_path, title_border_brush)

        if self.borderSize > 0:
            title_border_pen = QPen(self.outlineColor, self.borderSize)
            title_painter.strokePath(title_border_path, title_border_pen)

        # Adjust the title rectangle to consider the title margins
        title_align = self.titleAlignment
        title_metrics = QFontMetrics(self.font())
        title_width = title_metrics.width(self.title)
        title_bound_rect = title_metrics.boundingRect(self.title)
        title_contents_rect = QRectF(title_clip_rect)
        title_contents_rect.adjust(
            self.titleMargins.left(), self.titleMargins.top(),
            self.titleMargins.right() * -1, self.titleMargins.bottom() * -1
        )
        text_drawing_rect = QRect(
            title_contents_rect.x() + title_contents_rect.width() * 0.5 - title_width * 0.5,
            title_contents_rect.y() + title_contents_rect.height() * 0.5 - title_bound_rect.height() * 0.5,
            title_width, title_bound_rect.height()
        )

        if title_align == Qt.AlignTop or title_align == Qt.AlignLeft | Qt.AlignTop or title_align == Qt.AlignRight | Qt.AlignTop:
            text_drawing_rect.moveTop(title_contents_rect.y())
        elif title_align == Qt.AlignBottom or title_align == Qt.AlignLeft | Qt.AlignBottom or title_align == Qt.AlignRight | Qt.AlignBottom:
            text_drawing_rect.moveTop(title_contents_rect.y() + title_contents_rect.height() - title_bound_rect.height())

        if title_align == Qt.AlignLeft or title_align == Qt.AlignLeft | Qt.AlignVCenter or title_align == Qt.AlignLeft | Qt.AlignTop or title_align == Qt.AlignLeft | Qt.AlignBottom:
            text_drawing_rect.moveLeft(title_contents_rect.x())
        elif title_align == Qt.AlignRight or title_align == Qt.AlignRight | Qt.AlignVCenter or title_align == Qt.AlignRight | Qt.AlignTop or title_align == Qt.AlignRight | Qt.AlignBottom:
            text_drawing_rect.moveLeft(title_contents_rect.x() + title_contents_rect.width() - title_bound_rect.width())

        if self.borderSize > 0:
            title_text_pen = QPen(self.textColor, self.borderSize)
        else:
            title_text_pen = QPen(self.textColor, 2)

        title_painter.setPen(title_text_pen)
        title_painter.drawText(text_drawing_rect, self.titleAlignment, self.title)

    def sizeHint(self):
        """
        There is no need to reimplementing this method since the contents margins are being modified to consider the
        widget's title region

        @return: QSize
        """

        return super(MayaGroupBox, self).sizeHint()
        size_hint = super(MayaGroupBox, self).sizeHint()
        title_height = self.__calcTitleHeight()
        #contents_rect = self.layout().contentsRect()
        #layout_margins = self.layout().contentsMargins()

        return QSize(size_hint.width(), (title_height + size_hint.height()))

    def minimumSize(self):
        return super(MayaGroupBox, self).minimumSize()
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

    def mouseMoveEvent(self, event):
        if self.titleRect().contains(event.pos()) is True:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

        super(MayaGroupBox, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.titleRect().contains(event.pos()) is True:
            self.toggleContent()

        super(MayaGroupBox, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        super(MayaGroupBox, self).mouseDoubleClickEvent(event)

    title = Property(str, getTitle, setTitle)
    titleMargins = Property(QMargins, getTitleMargins, setTitleMargins)
    titleAlignment = Property(int, getTitleAlignment, setTitleAlignment)
    flat = Property(bool, isFlat, setFlat)

    textColor = Property(QColor, getTextColor, setTextColor)
    fillColor = Property(QColor, getFillColor, setFillColor)
    outlineColor = Property(QColor, getOutlineColor, setOutlineColor)
    borderSize = Property(int, getBorderSize, setBorderSize)
    borderRadius = Property(int, getBorderRadius, setBorderRadius)
    antiAlias = Property(bool, isAntiAliased, setAntiAliasing)

