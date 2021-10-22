from PySide2 import QtWidgets, QtCore, QtGui


class ClickableLabel(QtWidgets.QLabel):
	clicked = QtCore.Signal([None], [QtWidgets.QLabel])
	doubleClicked = QtCore.Signal([None], [QtWidgets.QLabel])

	def __init__(self, *args, **kwargs):
		super(ClickableLabel, self).__init__(*args, **kwargs)

		current_font = self.font()
		current_font.setUnderline(True)

		self.setCursor(QtCore.Qt.PointingHandCursor)
		self.setFont(current_font)

	@QtCore.Slot()
	def click(self):
		self.clicked[None].emit()
		self.clicked[QtWidgets.QLabel].emit(self)

	@QtCore.Slot()
	def doubleClick(self):
		self.doubleClicked[None].emit()
		self.doubleClicked[QtWidgets.QLabel].emit(self)

	def isUnderline(self):
		return self.font().isUnderline()

	def setUnderline(self, underline):
		font = self.font()
		font.setUnderline(underline)

		self.setFont(font)

	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.clicked[None].emit()
			self.clicked[QtWidgets.QLabel].emit(self)

		super(ClickableLabel, self).mouseReleaseEvent(event)

	def mouseDoubleClickEvent(self, event):
		super(ClickableLabel, self).mouseDoubleClickEvent(event)

	underline = QtCore.Property(bool, isUnderline, setUnderline)
