from PySide2 import QtCore


class ResizeScrollAreaWidgetEventFilter(QtCore.QObject):
	update_width = False
	update_height = False
	update_size = False

	def __init__(self, parent=None, update_width=False, update_height=False, update_size=False):
		super(ResizeScrollAreaWidgetEventFilter, self).__init__(parent)

		self.update_width = update_width
		self.update_height = update_height
		self.update_size = update_size

	def force_update_width(self, force):
		self.update_width = force

		return self

	def force_update_height(self, force):
		self.update_height = force

		return self

	def force_update_size(self, force):
		self.update_size = force

		return self

	def eventFilter(self, obj, event):
		if event.type() in [
			QtCore.QEvent.Resize, QtCore.QEvent.GraphicsSceneResize,
			QtCore.QEvent.MacSizeChange, QtCore.QEvent.Show, QtCore.QEvent.Type.ChildPolished
		]:
			try:
				central_widget = obj.widget()
				central_widget_size = central_widget.sizeHint()
				new_proposed_size = QtCore.QSize(central_widget_size)

				if self.update_width is True:
					if obj.verticalScrollBarPolicy() in [QtCore.Qt.ScrollBarAlwaysOn, QtCore.Qt.ScrollBarAsNeeded] \
						and obj.verticalScrollBar().isVisible() is True \
						and obj.verticalScrollBar().isHidden() is False:
						obj_width = obj.size().width() - obj.verticalScrollBar().width()
					else:
						obj_width = obj.size().width()

					if obj_width > central_widget_size.width():
						new_proposed_size.setWidth(obj_width)

				if self.update_height is True:
					if obj.horizontalScrollBar() in [QtCore.Qt.ScrollBarAlwaysOn, QtCore.Qt.ScrollBarAsNeeded] \
						and obj.horizontalScrollBar().isVisible() is True \
						and obj.horizontalScrollBar().isHidden() is False:
						obj_height = obj.size().height() - obj.horizontalScrollBar().height()
					else:
						obj_height = obj.size().height()

					if obj_height > central_widget_size.height():
						new_proposed_size.setHeight(obj_height)

				central_widget.resize(new_proposed_size)
			except(RuntimeError, Exception) as exc:
				print(exc.message)

		# standard event processing
		return QtCore.QObject.eventFilter(self, obj, event)
