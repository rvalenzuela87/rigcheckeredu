from PySide2 import QtWidgets, QtCore


class EscapableLineEdit(QtWidgets.QLineEdit):
	escape_on_focus_out = True
	escaped = QtCore.Signal()

	def __init__(self, *args, **kwargs):
		super(EscapableLineEdit, self).__init__(*args, **kwargs)

	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Escape:
			self.escaped.emit()
		else:
			super(EscapableLineEdit, self).keyPressEvent(event)

	def focusOutEvent(self, event):
		if self.escape_on_focus_out is True:
			self.escaped.emit()

		super(EscapableLineEdit, self).focusOutEvent(event)