from PySide2.QtWidgets import QLineEdit
from PySide2.QtCore import Signal, Slot, Property, Qt


class EscapableLineEdit(QLineEdit):
	escapeOnFocusOut = True

	# Signals
	escaped = Signal()
	accepted = Signal(str)

	def __init__(self, *args, **kwargs):
		super(EscapableLineEdit, self).__init__(*args, **kwargs)

		self.returnPressed.connect(self.accept)

	@Slot()
	def accept(self):
		self.accepted.emit(self.text())

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Escape:
			self.escaped.emit()
		elif event.key() == Qt.Key_Enter:
			self.accepted.emit(self.text())
		else:
			super(EscapableLineEdit, self).keyPressEvent(event)

	def focusOutEvent(self, event):
		if self.escapeOnFocusOut is True:
			self.escaped.emit()

		super(EscapableLineEdit, self).focusOutEvent(event)

