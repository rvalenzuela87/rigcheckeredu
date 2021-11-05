from PySide2.QtWidgets import QLabel
from PySide2.QtGui import QColor, QPainter, QPainterPath, QBrush, QPen, QFontMetrics, QVector2D
from PySide2.QtCore import Qt, Signal, Slot, Property, QMargins, QRect, QPoint, QSize


class BlockLabel(QLabel):
    __margins = None
    __locked = False
    __alignment = Qt.AlignCenter
    __borderSize = 1.0
    __borderRadius = 5
    __fillColor = None
    __outlineColor = None
    __textColor = None
    __antiAliasing = True
    __closeButtonAtRightEdge = True

    # Signals
    clicked = Signal()
    doubleClicked = Signal

    def __init__(self, *args, **kwargs):
        super(BlockLabel, self).__init__(*args, **kwargs)

        m_width = QFontMetrics(self.font()).widthChar("m")
        x_height = QFontMetrics(self.font()).xHeight()

        if m_width % 2 > 0:
            m_width -= m_width % 2

        if x_height % 2 > 0:
            x_height -= x_height % 2

        contents_margins = QMargins(m_width / 2, x_height / 2, m_width / 2, x_height / 2)

        if self.__locked is False:
            if self.__closeButtonAtRightEdge is True:
                contents_margins.setRight(contents_margins.right() + self.__closeButtonRect().width() + contents_margins.right())
            else:
                contents_margins.setLeft(contents_margins.left() + self.__closeButtonRect().width() + contents_margins.left())

        self.__textColor = QColor(200, 200, 200)
        self.__outlineColor = QColor(100, 100, 100)
        self.__fillColor = QColor(72, 72, 72)
        self.__borderSize = 2

        self.setMargins(contents_margins)

        super(BlockLabel, self).setMouseTracking(True)

    def __closeButtonRect(self):
        block_rect = self.rect()
        m_width = QFontMetrics(self.font()).width("m")
        button_width = QFontMetrics(self.font()).width("M")

        if self.__closeButtonAtRightEdge is True:
            button_x = block_rect.width() - button_width - m_width * 0.5
        else:
            button_x = m_width * 0.5

        button_y = block_rect.height() * 0.5 - button_width * 0.5

        if button_x < 0:
            button_x = 0

        if button_y < 0:
            button_y = 0

        return QRect(button_x, button_y, button_width, button_width)

    def getText(self):
        return self.text()

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

    def isLocked(self):
        return self.__locked

    def getAlignment(self):
        return self.__alignment

    def getCloseButtonAlignment(self):
        return self.__closeButtonAtRightEdge

    def getMargins(self):
        return self.contentsMargins()

    def getLeftMargin(self):
        return self.margins.left()

    def getRightMargin(self):
        return self.margins.right()

    def getTopMargin(self):
        return self.margin.top()

    def getBottomMargin(self):
        return self.margin.bottom()

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

    def setAlignment(self, align):
        self.__alignment = align

    def setCloseButtonAlignment(self, align):
        self.__closeButtonAtRightEdge = align

    def setMargins(self, margins):
        self.__margins = margins
        self.setContentsMargins(margins)

    def setLeftMargin(self, left):
        self.margins.setLeft(left)

    def setRightMargin(self, right):
        self.margins.setRight(right)

    def setTopMargin(self, top):
        self.margins.setTop(top)

    def setBottomMargin(self, bottom):
        self.margin.setBottom(bottom)

    def setLocked(self, locked):
        self.__locked = locked
        contents_margins = QMargins(self.margins)
        close_button_rect = self.__closeButtonRect()

        if locked is False:
            if self.__closeButtonAtRightEdge is True:
                if contents_margins.right() < close_button_rect.width():
                    contents_margins.setRight(QFontMetrics(self.font()).widthChar("m") + close_button_rect.width())
            else:
                if contents_margins.left() < close_button_rect.width():
                    contents_margins.setLeft(QFontMetrics(self.font()).widthChar("m") + close_button_rect.width())
        else:
            if self.__closeButtonAtRightEdge is True:
                if contents_margins.right() > close_button_rect.width():
                    contents_margins.setRight(QFontMetrics(self.font()).widthChar("m") / 2)
            else:
                if contents_margins.left() > close_button_rect.width():
                    contents_margins.setLeft(QFontMetrics(self.font()).widthChar("m") / 2)

        self.setMargins(contents_margins)

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

    def sizeHint(self):
        text_metrics = QFontMetrics(self.font())
        text_width = text_metrics.width(self.text())
        text_height = text_metrics.boundingRect(self.text()).height()
        margins = self.margins
        border_size = self.borderSize

        return QSize(
            margins.left() + text_width + margins.right(),
            margins.top() + text_height + margins.bottom()
        )

    def mouseMoveEvent(self, event):
        if self.locked is False:
            if self.__closeButtonRect().contains(event.pos()) is True:
                self.setCursor(Qt.PointingHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

        super(BlockLabel, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.locked is False and self.__closeButtonRect().contains(event.pos()) is True:
                self.delete()
            else:
                self.clicked.emit()

    def mouseDoubleClickEvent(self, event):
        super(BlockLabel, self).mouseDoubleClickEvent(event)

    def paintEvent(self, event):
        # Start painting the title section
        block_rect = QRect(self.rect())
        clip_rect = QRect(block_rect)

        # Slightly shrink dimensions to account for borderSize if anti aliasing is set to false
        if self.borderSize > 1:
            if self.antiAlias is False:
                left_adjust = (self.borderSize - (self.borderSize % 2)) / 2
                right_adjust = (left_adjust + (self.borderSize % 2)) * -1

                block_rect.adjust(left_adjust, left_adjust, right_adjust, right_adjust)
            else:
                # When antialiasing is on, the border width will be distributed, equally, outside and inside the
                # rectangle. Therefore, adjust the rectangle accordingly so the borders get painted inside the
                # calculated geometry
                half_border_size = float(self.borderSize) * 0.5
                block_rect.adjust(half_border_size, half_border_size, half_border_size * -1.0, half_border_size * -1.0)

        # Create two paths. The first one will be used when painting the widget's border and fill color. The
        # second path will be used for the painter's clip mask
        block_border_path = QPainterPath()
        block_border_path.addRoundedRect(block_rect, 0, 0)

        clip_path = QPainterPath()
        clip_path.addRoundedRect(clip_rect, self.borderRadius, self.borderRadius)

        # Create a painter and a brush to fill the first path
        block_painter = QPainter(self)

        if self.antiAlias is True:
            block_painter.setRenderHint(QPainter.Antialiasing)

        block_fill_brush = QBrush(self.fillColor)

        block_painter.setClipPath(clip_path)
        block_painter.fillPath(block_border_path, block_fill_brush)

        # Only draw a border if the border size property is greater than 1. Otherwise, skip this step
        if self.borderSize > 1:
            block_border_path = QPainterPath()
            block_border_path.addRoundedRect(block_rect, self.borderRadius, self.borderRadius)

            block_outline_pen = QPen(self.outlineColor, self.borderSize)
            block_painter.strokePath(block_border_path, block_outline_pen)

        # Adjust the rectangle to account for the text margins before drawing the label
        text_align = self.alignment
        text_metrics = QFontMetrics(self.font())
        text_bound_rect =  text_metrics.boundingRect(self.text())
        contents_rect = self.contentsRect()
        text_drawing_rect = QRect(
            contents_rect.x() + contents_rect.width() * 0.5 - text_metrics.width(self.text()) * 0.5,
            contents_rect.y() + contents_rect.height() * 0.5 - text_bound_rect.height() * 0.5,
            text_metrics.width(self.text()), text_bound_rect.height()
        )

        if text_align == Qt.AlignTop or text_align == Qt.AlignLeft | Qt.AlignTop or text_align == Qt.AlignRight | Qt.AlignTop:
            text_drawing_rect.moveTop(contents_rect.y())
        elif text_align == Qt.AlignBottom or text_align == Qt.AlignLeft | Qt.AlignBottom or text_align == Qt.AlignRight | Qt.AlignBottom:
            text_drawing_rect.moveTop(contents_rect.y() + contents_rect.height() - text_bound_rect.height())

        if text_align == Qt.AlignLeft or text_align == Qt.AlignLeft | Qt.AlignVCenter or text_align == Qt.AlignLeft | Qt.AlignTop or text_align == Qt.AlignLeft | Qt.AlignBottom:
            text_drawing_rect.moveLeft(contents_rect.x())
        elif text_align == Qt.AlignRight or text_align == Qt.AlignRight | Qt.AlignVCenter or text_align == Qt.AlignRight | Qt.AlignTop or text_align == Qt.AlignRight | Qt.AlignBottom:
            text_drawing_rect.moveLeft(contents_rect.x() + contents_rect.width() - text_bound_rect.width())

        # If the value held in the borderSize property is greater than 1 use this value for the text pen.
        # Otherwise, use 2.
        if self.borderSize > 1:
            block_text_pen = QPen(self.textColor, self.borderSize)
        else:
            block_text_pen = QPen(self.textColor, 2)

        block_painter.setPen(block_text_pen)
        block_painter.drawText(text_drawing_rect, self.alignment, self.text())

        # Draw the close button region if the label is unlocked
        if self.locked is False:
            close_button_rect = self.__closeButtonRect()
            close_button_clip_rect = QRect(close_button_rect)

            if self.antiAlias is False:
                pass
            else:
                if self.borderSize > 1:
                    half_border_size = float(self.borderSize) * 0.5
                else:
                    half_border_size = 1

                close_button_rect.adjust(
                    half_border_size, half_border_size,
                    half_border_size * -1.0, half_border_size * -1.0
                )

            close_button_path = QPainterPath()
            close_button_clip_path = QPainterPath()

            close_button_path.addRoundedRect(
                close_button_rect, close_button_rect.width() * 0.5, close_button_rect.width() * 0.5
            )
            close_button_clip_path.addRoundedRect(
                close_button_clip_rect, close_button_clip_rect.width() * 0.5, close_button_clip_rect.width() * 0.5
            )

            block_painter.setBrush(block_fill_brush)
            block_painter.setClipPath(close_button_clip_path)

            block_painter.fillPath(close_button_path, block_painter.brush())

            if self.borderSize > 1:
                close_button_border_pen = QPen(self.outlineColor, self.borderSize)
            else:
                close_button_border_pen = QPen(self.outlineColor, 2)

            block_painter.setPen(close_button_border_pen)
            block_painter.strokePath(close_button_path, close_button_border_pen)

            top_left_vector = QVector2D(close_button_rect.topLeft() - close_button_rect.center())
            bot_right_vector = top_left_vector * -1

            top_left_point = close_button_rect.center() + QPoint(top_left_vector.x(), top_left_vector.y())
            bot_right_point = close_button_rect.center() + QPoint(bot_right_vector.x(), bot_right_vector.y())
            top_right_point = close_button_rect.center() + QPoint(top_left_vector.x() * -1, top_left_vector.y())
            bot_left_point = close_button_rect.center() + QPoint(bot_right_vector.x() * -1, bot_right_vector.y())

            block_painter.drawLine(close_button_clip_rect.topLeft(), close_button_clip_rect.bottomRight())
            block_painter.drawLine(close_button_clip_rect.topRight(), close_button_clip_rect.bottomLeft())

    locked = Property(bool, isLocked, setLocked)
    margins = Property(QMargins, getMargins, setMargins)
    leftMargin = Property(int, getLeftMargin, setLeftMargin)
    rightMargin = Property(int, getRightMargin, setRightMargin)
    topMargin = Property(int, getTopMargin, setTopMargin)
    bottomMargin = Property(int, getBottomMargin, setBottomMargin)

    alignment = Property(int, getAlignment, setAlignment)
    closeButtonAlignment = Property(int, getCloseButtonAlignment, setCloseButtonAlignment)
    textColor = Property(QColor, getTextColor, setTextColor)
    fillColor = Property(QColor, getFillColor, setFillColor)
    outlineColor = Property(QColor, getOutlineColor, setOutlineColor)
    borderSize = Property(int, getBorderSize, setBorderSize)
    borderRadius = Property(int, getBorderRadius, setBorderRadius)
    antiAlias = Property(bool, isAntiAliased, setAntiAliasing)
