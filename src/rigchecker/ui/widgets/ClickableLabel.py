from PySide2 import QtWidgets, QtCore, QtGui


class ClickableLabel(QtWidgets.QLabel):
	clicked = QtCore.Signal()
	double_clicked = QtCore.Signal()

	def __init__(self, *args, **kwargs):
		super(ClickableLabel, self).__init__(*args, **kwargs)

		current_font = self.font()
		current_font.setUnderline(True)

		self.setCursor(QtCore.Qt.PointingHandCursor)
		self.setFont(current_font)

	@QtCore.Slot()
	def click(self):
		self.clicked.emit()

	@QtCore.Slot()
	def doubleClick(self):
		self.double_clicked.emit()

	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.clicked.emit()

		super(ClickableLabel, self).mouseReleaseEvent(event)

	def mouseDoubleClickEvent(self, event):
		super(ClickableLabel, self).mouseDoubleClickEvent(event)
