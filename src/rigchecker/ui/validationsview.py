from PySide2.QtWidgets import QWidget, QScrollArea, QPushButton, QVBoxLayout
from PySide2.QtCore import Qt, Signal, Slot, Property, QSize

from .widgets import ResizeScrollAreaWidgetEventFilter, MayaGroupBox, BlockLabel, BlockLabelsList


# I use PySide6, but whatever library should work.
from PySide2.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor
from PySide2.QtCore import QRectF

class RoundedButton(QPushButton):
    def __init__(self, text, bordersize, outlineColor, fillColor, *args, **kwargs):
        super(RoundedButton, self).__init__(text, *args, **kwargs)
        self.bordersize = bordersize
        self.outlineColor = outlineColor
        self.fillColor = fillColor
        self.setText(text)

    def paintEvent(self, event):
        # Create the painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Create the path
        path = QPainterPath()
        # Set painter colors to given values.
        pen = QPen(self.outlineColor, self.bordersize)
        painter.setPen(pen)
        brush = QBrush(self.fillColor)
        painter.setBrush(brush)

        rect = QRectF(event.rect())
        # Slighly shrink dimensions to account for bordersize.
        rect.adjust(self.bordersize/2, self.bordersize/2, -self.bordersize/2, -self.bordersize/2)

        # Add the rect to path.
        path.addRoundedRect(rect, 10, 10)
        painter.setClipPath(path)

        # Fill shape, draw the border and center the text.
        painter.fillPath(path, painter.brush())
        painter.strokePath(path, painter.pen())
        painter.drawText(rect, Qt.AlignCenter, self.text())


class ValidationsView(QWidget):
    __update_button = None

    def __init__(self, *args, **kwargs):
        super(ValidationsView, self).__init__(*args, **kwargs)

        self.setLayout(QVBoxLayout(self))

        self.__update_button = RoundedButton("Update", 1, QColor("red"), QColor(90, 90, 90), self)

        scroll_area = QScrollArea(self)
        scroll_area.installEventFilter(
            ResizeScrollAreaWidgetEventFilter.ResizeScrollAreaWidgetEventFilter(
                self, update_width=True, update_height=True
            )
        )

        central_widget = QWidget(scroll_area)
        central_widget.setLayout(QVBoxLayout(central_widget))
        central_widget.layout().setContentsMargins(0, 0, 0, 0)
        central_widget.layout().setAlignment(Qt.AlignTop)

        scroll_area.setWidget(central_widget)

        self.layout().addWidget(scroll_area)
        self.layout().addWidget(self.__update_button)
