from PySide2.QtWidgets import QLayout, QWidgetItem
from PySide2.QtCore import QSize, QRect, Qt, QPoint


class FlowLayout(QLayout):
	item_list = None
	"""Custom layout that mimics the behaviour of a flow layout"""

	def __init__(self, parent=None, margin=0, spacing=-1):
		"""
		Create a new FlowLayout instance.
		This layout will reorder the items automatically.

		@param parent (QWidget)
		@param margin (int)
		@param spacing (int)
		"""

		super(FlowLayout, self).__init__(parent)
		# Set margin and spacing

		if parent is not None:
			self.setMargin(margin)

		self.setSpacing(spacing)
		self.setContentsMargins(10, 10, 10, 10)

		self.item_list = []

	def __del__(self):
		"""Delete all the items in this layout by deleting this instance's reference to each of them"""
		item = self.takeAt(0)

		while item:
			item = self.takeAt(0)

	def addItem(self, item):
		"""
		(Overwritten method of class QLayout)
		Add an item at the end of the layout.
		This is automatically called when you do addWidget()
		item (QWidgetItem)
		"""

		self.item_list.append(item)

	def count(self):
		"""Get the number of items in the this layout
		@return (int)"""

		return len(self.item_list)

	def itemAt(self, index):
		"""
		(Overwritten method of class QLayout)
		Get the item at the given index
		@param index (int)
		@return (QWidgetItem)
		"""

		try:
			return self.item_list[index]
		except IndexError:
			return None

	def takeAt(self, index):
		"""
		(Overwritten method of class QLayout)
		Remove an item at the given index
		@param index (int)
		@return (None)
		"""

		try:
			return self.item_list.pop(index)
		except IndexError:
			return None

	def insertItem(self, index, item):
		"""Insert a widget at a given index
		@param index (int)
		@param widget (QWidget)"""

		self.item_list.insert(index, item)

		'''contents_rect = QRect(self.geometry())
		print("Rect: {}".format(contents_rect))
		minimum_height = self.heightForWidth(contents_rect.width())
		contents_rect.setHeight()
		print("New Rect: {}".format(contents_rect))

		self.setGeometry(contents_rect)'''

	def insertWidget(self, index, widget):
		contents_rect = QRect(self.geometry())

		self.insertItem(index, QWidgetItem(widget))

		widget.show()
		minimum_height = self.heightForWidth(contents_rect.width())

		if minimum_height < contents_rect.height():
			contents_rect.setHeight(minimum_height)

		self.setGeometry(contents_rect)

	def addLayout(self, layout):
		self.item_list.append(layout)

		super(FlowLayout, self).addChildLayout(layout)

	def expandingDirections(self):
		"""
		(Overwritten method from QLayoutItem)
		This layout grows only in the horizontal dimension
		"""

		return Qt.Orientations(Qt.Horizontal)

	def hasHeightForWidth(self):
		"""
		(Overwritten method of class QLayoutItem)
		If this layout's preferred height depends on its width
		@return (boolean) Always True
		"""

		return 1

	def heightForWidth(self, width):
		"""
		(Overwritten method of class QLayoutItem)
		Get the preferred height a layout item with the given width
		@param width (int)
		"""

		contents_margins = self.contentsMargins()

		height = self.doLayout(
			QRect(0 + contents_margins.left(), 0 + contents_margins.top(), width, 0),
			True
		)
		print("From height for width: {} | {}".format(width, height))
		return height

	def setGeometry(self, rect):
		"""
		(Overwritten method of class QLayoutItem)
		Set the geometry of this layout
		@param rect (QRect)
		"""

		super(FlowLayout, self).setGeometry(rect)

		self.doLayout(rect, False)

	def sizeHint(self):
		"""Get the preferred size of this layout
		@return (QSize) The minimum size"""

		return self.minimumSize()

	def minimumSize_bck(self):
		"""Get the minimum size of this layout
		@return (QSize)"""
		# Calculate the size
		size = QSize()
		height = QSize()
		width = QSize()

		parent_widget = self.parentWidget()
		if parent_widget not in [None, 0]:
			parent_width = parent_widget.size().width()
			size.setWidth(parent_width)
			size.setHeight(self.heightForWidth(parent_width))
		else:
			for item in self.item_list:
				item_min_size = item.minimumSize()
				size = size.expandedTo(item_min_size)
				width = width.expandedTo(item_min_size)
				height += item_min_size

		size += QSize(2 * self.margin(), 2 * self.margin())
		return size

	def minimumSize(self):
		"""Get the minimum size of this layout
		@return (QSize)"""

		# Calculate the size
		contents_margins = self.contentsMargins()
		size = QSize(
			contents_margins.left() + contents_margins.right(),
			contents_margins.top() + contents_margins.bottom()
		)
		height = (len(self.item_list) - 1) * self.spacing()
		width = 0

		for i, item in enumerate(self.item_list):
			width = max(width, item.sizeHint().width())
			height += item.sizeHint().height()

		size += QSize(width, height)
		return size

		for item in self.item_list:
			item_min_size = QSize(item.sizeHint())
			size = size.expandedTo(item_min_size)
			width = width.expandedTo(item_min_size)
			height += item_min_size

		size += QSize(
			(2 * self.margin()) + contents_margins.left() + contents_margins.right(),
			(2 * self.margin()) + contents_margins.top() + contents_margins.bottom()
		)
		return size
		'''# Add the margins
		minimum_size = QtCore.QSize(width.width(), height.height()) + QtCore.QSize(2 * self.margin(), 2 * self.margin())

		return minimum_size'''

	def doLayout(self, rect, testOnly):
		"""
		Layout all the items
		@param rect (QRect) Rect where in the items have to be laid out
		@param testOnly (boolean) Do the actual layout
		"""

		x = rect.x()
		y = rect.y()
		lineHeight = 0

		spaceX = self.spacing()
		spaceY = self.spacing()

		for item in self.item_list:
			nextX = x + item.sizeHint().width() + spaceX

			if nextX - spaceX > rect.right() and lineHeight > 0:
				x = rect.x()
				y = y + lineHeight + spaceY
				nextX = x + item.sizeHint().width() + spaceX
				lineHeight = 0

			if testOnly is False:
				item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

			x = nextX
			lineHeight = max(lineHeight, item.sizeHint().height())

		return y + lineHeight - rect.y()
