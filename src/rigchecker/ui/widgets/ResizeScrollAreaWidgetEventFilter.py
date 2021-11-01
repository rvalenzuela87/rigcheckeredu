from PySide2 import QtCore


class ResizeScrollAreaWidgetEventFilter(QtCore.QObject):
	update_width = False
	update_height = False
	update_size = False

	__events_list = None

	def __init__(self, parent=None, update_width=False, update_height=False, update_size=False):
		super(ResizeScrollAreaWidgetEventFilter, self).__init__(parent)

		self.update_width = update_width
		self.update_height = update_height
		self.update_size = update_size

		self.__events_list = [
			QtCore.QEvent.Resize, QtCore.QEvent.GraphicsSceneResize, QtCore.QEvent.MacSizeChange,
			QtCore.QEvent.Show, QtCore.QEvent.Type.ChildPolished
		]

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
		# standard event processing
		#return QtCore.QObject.eventFilter(self, obj, event)
		if event.type() in self.__events_list:
			try:
				central_widget = obj.widget()
				central_widget_size = central_widget.sizeHint()
				new_proposed_size = QtCore.QSize(central_widget_size)
				obj_contents_margins = obj.contentsMargins()

				if self.update_width is True:
					if obj.verticalScrollBarPolicy() == QtCore.Qt.ScrollBarAlwaysOff or obj.verticalScrollBar().isHidden() is True:
						obj_width = obj.size().width()
					else:
						obj_width = obj.size().width()

					obj_width -= obj_contents_margins.left() + obj_contents_margins.right()

					# If the scroll area is wider than its central widget, then set the central widget's proposed size
					# to be as wide as the scroll bar minus the width of its vertical scroll bar assuming it has one
					# and it is currently visible and its left and right contents margins
					if obj_width > central_widget_size.width():
						new_proposed_size.setWidth(obj_width)

				if self.update_height is True:
					if obj.horizontalScrollBarPolicy() == QtCore.Qt.ScrollBarAlwaysOff or obj.horizontalScrollBar().isHidden() is True:
						obj_height = obj.size().height()
					else:
						obj_height = obj.size().height() - obj.horizontalScrollBar().height()

					obj_height -= obj_contents_margins.top() + obj_contents_margins.bottom()

					# If the scroll area is taller than its central widget, then set the central widget's proposed size
					# to be as tall as the scroll area minus the height of its horizontal scroll bar assuming it has one
					# and it is currently visible and its top and bottom contents margins
					if obj_height > central_widget_size.height():
						new_proposed_size.setHeight(obj_height)

				central_widget.resize(new_proposed_size)
			except(RuntimeError, Exception) as exc:
				print(exc.message)

		# standard event processing
		return QtCore.QObject.eventFilter(self, obj, event)
