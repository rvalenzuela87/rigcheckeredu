import os
from PySide2 import QtWidgets, QtCore, QtGui
from Rigging_Tool_App.UI.Widgets import WidgetsFactory
from Rigging_Tool_App.System import UIConstants


class ButtonLabelWidget(QtWidgets.QWidget):
	__expanded = False

	box_title = ""
	expanded = QtCore.Signal()
	contracted = QtCore.Signal()
	expand_icon = None

	def __init__(self, title="", parent=None):
		super(ButtonLabelWidget, self).__init__(parent)

		self.setSizePolicy(
			QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
		)
		self.setAutoFillBackground(True)
		self.setCursor(QtCore.Qt.PointingHandCursor)

		box_palette = self.palette()
		box_palette_copy = self.palette()

		for group in [QtGui.QPalette.Active, QtGui.QPalette.Inactive, QtGui.QPalette.Disabled]:
			box_palette_copy.setBrush(
				group, QtGui.QPalette.Base, box_palette.brush(group, QtGui.QPalette.Button)
			)
			box_palette_copy.setBrush(
				group, QtGui.QPalette.Window, box_palette.brush(group, QtGui.QPalette.Button)
			)
			box_palette_copy.setBrush(
				group, QtGui.QPalette.WindowText, box_palette.brush(group, QtGui.QPalette.ButtonText)
			)

		self.setPalette(box_palette_copy)

		self.expand_icon = QtWidgets.QLabel(self)
		self.expand_icon.setPixmap(
			QtGui.QPixmap(os.path.join(UIConstants.ICONS_DIRECTORY, "toolbox-arrow-right-s-fill.png"))
		)

		self.box_title = QtWidgets.QLabel(title, self)

		self.setLayout(WidgetsFactory.h_box_layout(self))

		contents_margins = self.layout().contentsMargins()
		contents_margins.setTop(5)
		contents_margins.setBottom(5)
		self.layout().setContentsMargins(contents_margins)

		self.layout().addWidget(self.expand_icon)
		self.layout().addWidget(self.box_title)
		self.layout().setAlignment(QtCore.Qt.AlignLeft)

	@QtCore.Slot()
	def toggleExpand(self):
		if self.__expanded is False:
			self.__expanded = True
			self.expand_icon.setPixmap(
				QtGui.QPixmap(os.path.join(UIConstants.ICONS_DIRECTORY, "toolbox-arrow-down-s-fill.png"))
			)
			self.expanded.emit()
		else:
			self.__expanded = False
			self.expand_icon.setPixmap(
				QtGui.QPixmap(os.path.join(UIConstants.ICONS_DIRECTORY, "toolbox-arrow-right-s-fill.png"))
			)
			self.contracted.emit()

	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.toggleExpand()

		super(ButtonLabelWidget, self).mouseReleaseEvent(event)


class MayaToolBoxItemWidget(QtWidgets.QWidget):
	__is_expanded = False

	box_title = None
	box_frame = None
	box_frame_animation = None

	expand_changed = QtCore.Signal()

	def __init__(self, title="", parent=None, contents_margins=None, spacing=5):
		super(MayaToolBoxItemWidget, self).__init__(parent)

		self.setLayout(WidgetsFactory.v_box_layout(self, contents_margins=[0, 0], spacing=0))
		self.layout().setAlignment(QtCore.Qt.AlignTop)

		self.box_title = ButtonLabelWidget(title=title, parent=self)
		self.box_title.expanded.connect(self.expand)
		self.box_title.contracted.connect(self.contract)

		self.box_frame = WidgetsFactory.v_group_box(self, contents_margins=contents_margins, spacing=spacing)
		self.box_frame.setVisible(False)
		self.box_frame.setSizePolicy(
			QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
		)

		for w in [self.box_title, self.box_frame]:
			self.layout().addWidget(w)

		self.__is_expanded = False

	@QtCore.Slot(bool)
	def expand(self):
		self.__is_expanded = True
		self.setSizePolicy(
			QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
		)
		self.box_frame.setVisible(True)

	@QtCore.Slot()
	def contract(self):
		self.__is_expanded = False
		self.box_frame.setVisible(False)
		self.setSizePolicy(
			QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
		)

	def expanded(self):
		return self.__is_expanded

	def title_widget(self):
		return self.box_title

	def content_widget(self):
		return self.box_frame

	def item(self):
		content_widget = self.content_widget()

		for ch in content_widget.children():
			if issubclass(type(ch), QtWidgets.QLayout):
				continue
			else:
				return ch

		return None

	def set_item(self, item):
		content_widget = self.content_widget()

		for ch in content_widget.children():
			if issubclass(type(ch), QtWidgets.QBoxLayout):
				continue
			else:
				content_widget.layout().removeWidget(ch)
				ch.setParent(None)
				ch.deleteLater()

		item.setParent(content_widget)
		content_widget.layout().addWidget(item)

		return self


class MayaToolBoxWidget(QtWidgets.QWidget):
	contents_margins = None
	spacing = 5

	__items = None
	scroll_area = None
	container = None

	def __init__(self, parent, contents_margins=None, spacing=5):
		super(MayaToolBoxWidget, self).__init__(parent)
		self.__items = []

		self.contents_margins = contents_margins
		self.spacing = spacing

		self.setLayout(WidgetsFactory.v_box_layout(self, contents_margins=[0, 0], spacing=0))
		self.layout().setAlignment(QtCore.Qt.AlignTop)
		self.setSizePolicy(
			QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		)

		self.scroll_area = QtWidgets.QScrollArea(self)
		self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.scroll_area.setWidgetResizable(True)
		self.scroll_area.setSizePolicy(
			QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		)

		self.container = WidgetsFactory.v_widget(self.scroll_area, contents_margins=[0, 0])
		self.container.layout().setAlignment(QtCore.Qt.AlignTop)
		self.container.setSizePolicy(
			QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		)

		self.scroll_area.setWidget(self.container)
		self.layout().addWidget(self.scroll_area)

	@QtCore.Slot()
	def updateSize_bck(self):
		available_height = self.size().height() - (self.spacing * (len(self.__items) - 1))
		expanded_items = []
		flatten_items = []

		for item in self.__items:
			available_height -= item.title_widget().size().height()

			if item.expanded() is True:
				expanded_items.append(item)
			else:
				flatten_items.append(item)
		try:
			items_height = available_height / len(expanded_items)
		except ZeroDivisionError:
			pass
		'''else:
			for item in expanded_items:
				item_size = item.size()
				item.resize(QtCore.QSize(item_size.width(), (items_height + item.title_widget().size().height())))

		for item in flatten_items:
			item.resize(item.title_widget().size())'''

		return self

	@QtCore.Slot()
	def updateSize(self):
		# print("Spacing: {}".format(self.container.layout().spacing()))
		# print("Current height: {}".format(self.container.size().height()))
		available_height = self.container.size().height() - (self.container.layout().spacing() * (len(self.__items) - 1))
		expanded_items = []
		flatten_items = []

		for item in self.__items:
			# print("-- Item height: {}".format(item.title_widget().size().height()))
			available_height -= item.title_widget().size().height()

			if item.expanded() is True:
				expanded_items.append(item)
			else:
				flatten_items.append(item)
		# print("Available_height: {}".format(available_height))

		try:
			items_height = available_height / len(expanded_items)
			# print("Items height: {}".format(items_height))
		except ZeroDivisionError:
			pass
		else:
			for item in expanded_items:
				item_size = item.size()
				item.resize(QtCore.QSize(item_size.width(), (items_height + item.title_widget().size().height())))

		for item in flatten_items:
			item.resize(item.title_widget().size())

		self.container.resize(self.container.layout().sizeHint())
		return self

	def items(self):
		return [iw.item() for iw in self.container.children() if type(iw) is MayaToolBoxItemWidget]

	def addItem(self, item, icon=None, title=""):
		new_item = MayaToolBoxItemWidget(
			title=title, parent=self.container, contents_margins=self.contents_margins, spacing=self.spacing
		)
		new_item.set_item(item)
		new_item.expand_changed.connect(self.updateSize)
		self.__items.append(new_item)

		self.container.layout().addWidget(new_item)
		'''self.container.resize(self.container.layout().sizeHint())
		self.resize(self.layout().sizeHint())'''

		return self

	def removeItem(self, item):
		for ch in [iw for iw in self.container.children() if type(iw) is MayaToolBoxItemWidget]:
			try:
				ch_item = ch.item()
				assert ch_item == item
			except AssertionError:
				continue
			else:
				ch.expand_changed.disconnect(self.updateSize)
				self.container.layout().removeWidget(ch)
				ch.setParent(None)
				ch.deleteLater()

				try:
					self.__items.pop(self.__items.index(ch))
				except(ValueError, IndexError):
					pass

				break

	def clearItems(self):
		for ch in [iw for iw in self.container.children() if type(iw) is MayaToolBoxItemWidget]:
			ch.expand_changed.disconnect(self.updateSize)
			self.container.layout().removeWidget(ch)
			ch.setParent(None)
			ch.deleteLater()

			try:
				self.__items.pop(self.__items.index(ch))
			except(ValueError, IndexError):
				pass

		return self
