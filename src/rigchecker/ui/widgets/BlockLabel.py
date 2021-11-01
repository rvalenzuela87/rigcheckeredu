from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QHBoxLayout, QSizePolicy
from PySide2.QtGui import QPalette, QColor, QFontMetrics, QPainter, QPainterPath, QBrush, QPen, QFontMetrics, QVector2D
from PySide2.QtCore import Qt, Signal, Slot, Property, QMargins, QRect, QPoint

from . import ClickableLabel


class BlockLabelBck(QWidget):
    __text_label = None
    __close_button = None

    clicked = Signal()
    doubleClicked = Signal

    def __init__(self, text, *args, **kwargs):
        super(BlockLabel, self).__init__(*args, **kwargs)
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        )

        self.__text_label = QLabel("", self)
        self.__text_label.setSizePolicy(
            QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
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
        self.closeButton.setVisible(not locked)
        self.closeButton.setEnabled(not locked)

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


class BlockLabel(QLabel):
    __margins = None
    __locked = False
    __alignment = Qt.AlignLeft
    __borderSize = 1.0
    __borderRadius = 5
    __fillColor = None
    __outlineColor = None
    __textColor = None
    __antiAliasing = True

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
            contents_margins.setRight(contents_margins.right() + self.__closeButtonRect().width() + contents_margins.right())

        self.__textColor = QColor(255, 255, 255)
        self.__outlineColor = QColor(255, 255, 255)
        self.__fillColor = QColor(255, 0, 0)
        self.__borderSize = 2
        self.__margins = contents_margins

        super(BlockLabel, self).setContentsMargins(
            self.__margins.left(), self.__margins.top(),
            self.__margins.right(), self.__margins.bottom()
        )

        super(BlockLabel, self).setMouseTracking(True)

    def __closeButtonRect(self):
        m_width = QFontMetrics(self.font()).widthChar("m")
        block_rect = self.rect()
        close_button_width = m_width * 1.5

        return QRect(
            block_rect.width() - self.borderSize - close_button_width - m_width * 0.5,
            (block_rect.height() * 0.5) - (close_button_width * 0.5),
            close_button_width, close_button_width
        )

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

    def getMargins(self):
        return self.__margins

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

    def setMargins(self, margins):
        self.__margins = margins

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
        contents_margins = self.contentsMargins()
        close_button_rect = self.__closeButtonRect()

        if locked is False:
            if contents_margins.right() < close_button_rect.width():
                contents_margins.setRight(QFontMetrics(self.font()).widthChar("m") + close_button_rect.width())
        else:
            if contents_margins.right() > close_button_rect.width():
                contents_margins.setRight(QFontMetrics(self.font()).widthChar("m") / 2)

        self.setContentsMargins(contents_margins)

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

        # Slightly shrink dimensions to account for borderSize if anti aliasing is set to false
        if self.antiAlias is False:
            left_adjust = (self.borderSize - (self.borderSize % 2)) / 2
            right_adjust = (left_adjust + (self.borderSize % 2)) * -1

            block_rect.adjust(left_adjust, left_adjust, right_adjust, right_adjust)

        # Start painting the contents border
        block_border_path = QPainterPath()
        block_border_path.addRoundedRect(block_rect, self.borderRadius, self.borderRadius)

        block_painter = QPainter(self)

        if self.antiAlias is True:
            block_painter.setRenderHint(QPainter.Antialiasing)

        block_outline_pen = QPen(self.outlineColor, self.borderSize)
        block_text_pen = QPen(self.textColor, self.borderSize)
        block_fill_brush = QBrush(self.fillColor)

        block_painter.setPen(block_outline_pen)
        block_painter.setBrush(block_fill_brush)
        block_painter.setClipPath(block_border_path)

        block_painter.fillPath(block_border_path, block_fill_brush)
        block_painter.strokePath(block_border_path, block_outline_pen)

        # Adjust the rectangle to account for the text margins before drawing the label
        text_margins = self.margins

        '''try:
            block_rect.adjust(
                text_margins.left(), text_margins.top(),
                0, 0
            )
        except AttributeError:
            pass
        '''
        try:
            block_rect.moveTo(
                text_margins.left(),
                (block_rect.height() * 0.5) - (QFontMetrics(self.font()).boundingRect(self.text()).height() * 0.5)
            )
        except AttributeError:
            pass

        block_painter.setPen(block_text_pen)

        block_painter.drawText(block_rect, self.alignment, self.text())

        # Draw the close button region if the label is unlocked
        if self.locked is False:
            close_button_rect = self.__closeButtonRect()

            close_button_path = QPainterPath()
            close_button_path.addRoundedRect(
                close_button_rect, close_button_rect.width() * 0.5, close_button_rect.width() * 0.5
            )

            block_painter.setPen(block_outline_pen)
            block_painter.setBrush(QColor(0, 255, 0))
            block_painter.setClipPath(close_button_path)

            block_painter.fillPath(close_button_path, block_painter.brush())
            block_painter.strokePath(close_button_path, block_outline_pen)

            #close_button_rect.adjust(self.borderSize, self.borderSize, -self.borderSize, -self.borderSize)

            top_left_vector = QVector2D(close_button_rect.topLeft() - close_button_rect.center())
            bot_right_vector = top_left_vector * -1

            top_left_point = close_button_rect.center() + QPoint(top_left_vector.x(), top_left_vector.y())
            bot_right_point = close_button_rect.center() + QPoint(bot_right_vector.x(), bot_right_vector.y())
            top_right_point = close_button_rect.center() + QPoint(top_left_vector.x() * -1, top_left_vector.y())
            bot_left_point = close_button_rect.center() + QPoint(bot_right_vector.x() * -1, bot_right_vector.y())

            block_painter.drawLine(close_button_rect.topLeft(), close_button_rect.bottomRight())
            block_painter.drawLine(close_button_rect.topRight(), close_button_rect.bottomLeft())

    locked = Property(bool, isLocked, setLocked)
    margins = Property(QMargins, getMargins, setMargins)
    leftMargin = Property(int, getLeftMargin, setLeftMargin)
    rightMargin = Property(int, getRightMargin, setRightMargin)
    topMargin = Property(int, getTopMargin, setTopMargin)
    bottomMargin = Property(int, getBottomMargin, setBottomMargin)

    alignment = Property(int, getAlignment, setAlignment)
    textColor = Property(QColor, getTextColor, setTextColor)
    fillColor = Property(QColor, getFillColor, setFillColor)
    outlineColor = Property(QColor, getOutlineColor, setOutlineColor)
    borderSize = Property(int, getBorderSize, setBorderSize)
    borderRadius = Property(int, getBorderRadius, setBorderRadius)
    antiAlias = Property(bool, isAntiAliased, setAntiAliasing)
