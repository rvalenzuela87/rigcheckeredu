import os

from PySide2.QtWidgets import QWidget, QLabel, QGroupBox, QScrollArea, QSizePolicy, QHBoxLayout, QVBoxLayout, QBoxLayout, QLayout
from PySide2.QtCore import Signal, Slot, Qt, QSize
from PySide2.QtGui import QPalette, QPixmap


class ButtonLabelWidget(QWidget):
	__expanded = False

	box_title = ""
	expanded = Signal()
	contracted = Signal()
	expand_icon = None

	def __init__(self, title="", parent=None):
		super(ButtonLabelWidget, self).__init__(parent)

		self.setSizePolicy(
			QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
		)
		self.setAutoFillBackground(True)
		self.setCursor(Qt.PointingHandCursor)

		box_palette = self.palette()
		box_palette_copy = self.palette()

		for group in [QPalette.Active, QPalette.Inactive, QPalette.Disabled]:
			box_palette_copy.setBrush(
				group, QPalette.Base, box_palette.brush(group, QPalette.Button)
			)
			box_palette_copy.setBrush(
				group, QPalette.Window, box_palette.brush(group, QPalette.Button)
			)
			box_palette_copy.setBrush(
				group, QPalette.WindowText, box_palette.brush(group, QPalette.ButtonText)
			)

		self.setPalette(box_palette_copy)

		self.expand_icon = QLabel(self)
		self.expand_icon.setPixmap(
			QPixmap(os.path.join(os.environ["ICONS_DIR"], "toolbox-arrow-right-s-fill.png"))
		)

		self.box_title = QLabel(title, self)

		self.setLayout(QHBoxLayout(self))

		contents_margins = self.layout().contentsMargins()
		contents_margins.setTop(5)
		contents_margins.setBottom(5)
		self.layout().setContentsMargins(contents_margins)

		self.layout().addWidget(self.expand_icon)
		self.layout().addWidget(self.box_title)
		self.layout().setAlignment(Qt.AlignLeft)

	@Slot()
	def toggleExpand(self):
		if self.__expanded is False:
			self.__expanded = True
			self.expand_icon.setPixmap(
				QPixmap(os.path.join(os.environ["ICONS_DIR"], "toolbox-arrow-down-s-fill.png"))
			)
			self.expanded.emit()
		else:
			self.__expanded = False
			self.expand_icon.setPixmap(
				QPixmap(os.path.join(os.environ["ICONS_DIR"], "toolbox-arrow-right-s-fill.png"))
			)
			self.contracted.emit()

	def mouseReleaseEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.toggleExpand()

		super(ButtonLabelWidget, self).mouseReleaseEvent(event)


class MayaToolBoxItemWidget(QWidget):
	__is_expanded = False

	box_title = None
	box_frame = None
	box_frame_animation = None

	expand_changed = Signal()

	def __init__(self, title="", parent=None, contents_margins=None, spacing=5):
		super(MayaToolBoxItemWidget, self).__init__(parent)

		self.setLayout(QVBoxLayout(self))
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().setSpacing(0)
		self.layout().setAlignment(Qt.AlignTop)

		self.box_title = ButtonLabelWidget(title=title, parent=self)
		self.box_title.expanded.connect(self.expand)
		self.box_title.contracted.connect(self.contract)

		self.box_frame = QGroupBox(self)
		self.box_frame.setLayout(QVBoxLayout(self.box_frame))

		try:
			self.box_frame.layout().setContentsMargins(
				contents_margins[0], contents_margins[1], contents_margins[2], contents_margins[3]
			)
		except IndexError:
			try:
				self.box_frame.layout().setContentsMargins(
					contents_margins[0], contents_margins[1], contents_margins[0], contents_margins[1]
				)
			except IndexError:
				pass
		except TypeError:
			pass

		self.box_frame.layout().setSpacing(spacing)
		self.box_frame.setVisible(False)
		self.box_frame.setSizePolicy(
			QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
		)

		for w in [self.box_title, self.box_frame]:
			self.layout().addWidget(w)

		self.__is_expanded = False

	@Slot(bool)
	def expand(self):
		self.__is_expanded = True
		self.setSizePolicy(
			QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
		)
		self.box_frame.setVisible(True)

	@Slot()
	def contract(self):
		self.__is_expanded = False
		self.box_frame.setVisible(False)
		self.setSizePolicy(
			QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
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
			if issubclass(type(ch), QLayout):
				continue
			else:
				return ch

		return None

	def set_item(self, item):
		content_widget = self.content_widget()

		for ch in content_widget.children():
			if issubclass(type(ch), QBoxLayout):
				continue
			else:
				content_widget.layout().removeWidget(ch)
				ch.setParent(None)
				ch.deleteLater()

		item.setParent(content_widget)
		content_widget.layout().addWidget(item)

		return self


class MayaToolBoxWidget(QWidget):
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

		self.setLayout(QVBoxLayout(self))
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().setSpacing(0)
		self.layout().setAlignment(Qt.AlignTop)
		self.setSizePolicy(
			QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		)

		self.scroll_area = QScrollArea(self)
		self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self.scroll_area.setWidgetResizable(True)
		self.scroll_area.setSizePolicy(
			QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		)

		self.container = QWidget(self.scroll_area)
		self.container.setLayout(QVBoxLayout(self.container))
		self.container.layout().setContentsMargins(0, 0, 0, 0)
		self.container.layout().setAlignment(Qt.AlignTop)
		self.container.setSizePolicy(
			QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		)

		self.scroll_area.setWidget(self.container)
		self.layout().addWidget(self.scroll_area)

	@Slot()
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
				item.resize(QSize(item_size.width(), (items_height + item.title_widget().size().height())))

		for item in flatten_items:
			item.resize(item.title_widget().size())'''

		return self

	@Slot()
	def updateSize(self):
		available_height = self.container.size().height() - (self.container.layout().spacing() * (len(self.__items) - 1))
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
		else:
			for item in expanded_items:
				item_size = item.size()
				item.resize(QSize(item_size.width(), (items_height + item.title_widget().size().height())))

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
