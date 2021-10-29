import os

from PySide2.QtWidgets import QWidget, QPushButton, QTreeWidget, QTreeWidgetItem, QScrollArea, QLabel, QSplitter, QHeaderView, QVBoxLayout, QHBoxLayout
from PySide2.QtCore import Qt, Slot, Signal, Property, QObject, QSize
from PySide2.QtGui import QPalette, QColor, QIcon, QPixmap, QPainter, QPainterPath

from .widgets import ResizeScrollAreaWidgetEventFilter, MayaGroupBox, ClickableLabel
reload(MayaGroupBox)


class CirclePixmapBuilder(object):
	width = 50
	height = 50
	radius = 25
	antialiasing = True
	fillColor = None
	__target = None

	def __init__(self, *args, **kwargs):
		super(CirclePixmapBuilder, self).__init__()

	def buildPixmap(self):
		circle_size = QSize(self.width, self.height)
		self.__target = QPixmap(circle_size)
		self.__target.fill(Qt.transparent)

		p = QPixmap(circle_size).scaled(self.width, self.height, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
		p.fill(self.fillColor)

		painter = QPainter(self.__target)

		if self.antialiasing:
			painter.setRenderHint(QPainter.Antialiasing, True)
			painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
			painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

		path = QPainterPath()
		path.addRoundedRect(0, 0, self.width, self.height, self.radius, self.radius)

		painter.setClipPath(path)
		painter.drawPixmap(0, 0, p)

		return self.__target

	def getWidth(self):
		return self.width

	def getHeight(self):
		return self.height

	def getRadius(self):
		return self.radius

	def getAntialiasing(self):
		return self.antialiasing

	def getFillColor(self):
		return self.fillColor

	def setWidth(self, width):
		self.width = width

	def setHeight(self, height):
		self.height = height

	def setRadius(self, radius):
		self.radius = radius

	def setAntialiasing(self, anti):
		self.antialiasing = anti

	def setFillColor(self, fillColor):
		self.fillColor = fillColor


class NodesTotalClickableLabel(ClickableLabel.ClickableLabel):
	__nodes_paths = None

	# Signals
	selectNodes = Signal(list)

	def __init__(self, nodes_paths, *args, **kwargs):
		super(NodesTotalClickableLabel, self).__init__(*args, **kwargs)

		if nodes_paths is not None:
			self.__nodes_paths = nodes_paths
		else:
			self.__nodes_paths = []

		self.clicked.connect(self.__emitSelectNodes)

	@Slot()
	def __emitSelectNodes(self):
		print("Selecting nodes...")
		self.selectNodes.emit(self.nodesPaths)

	def getNodesPaths(self):
		return self.__nodes_paths

	def setNodesPaths(self, nodesList):
		self.__nodes_paths = nodesList

	nodesPaths = Property(list, getNodesPaths, setNodesPaths)


class NodeValidationDetails(MayaGroupBox.MayaGroupBox):
	__node_path = None
	__validations_list = None

	__select_node_button = None
	__update_button = None

	#Signals
	select = Signal(str)
	update = Signal(str)

	def __init__(self, node_path, title, *args, **kwargs):
		super(NodeValidationDetails, self).__init__(title, *args, **kwargs)

		self.setContentLayout(QVBoxLayout(self))

		self.__validations_list = []

		self.__select_node_button = QPushButton("Select", self)
		self.__select_node_button.clicked.connect(self.__emitSelectNode)

		self.__update_button = QPushButton("Update", self)
		self.__update_button.clicked.connect(self.__emitUpdateNode)

		circle_builder = CirclePixmapBuilder()
		circle_builder.fillColor = QColor("red")

		for i in xrange(4):
			status_label = QLabel(self)
			status_label.setMinimumSize(QSize(circle_builder.width, circle_builder.height))
			status_label.setMaximumSize(QSize(circle_builder.width, circle_builder.height))
			status_label.setPixmap(circle_builder.buildPixmap())

			validation_label = QLabel("Validation %i" % (i + 1), self)

			validation_layout = QHBoxLayout(self)
			validation_layout.setAlignment(Qt.AlignLeft)
			validation_layout.addWidget(status_label)
			validation_layout.addWidget(validation_label)

			self.contentLayout().insertLayout(0, validation_layout)

		self.contentLayout().addWidget(self.__select_node_button)
		self.contentLayout().addWidget(self.__update_button)

	def __emitUpdateNode(self):
		self.update.emit(self.nodePath)

	def __emitSelectNode(self):
		self.select.emit(self.nodePath)

	def getNodePath(self):
		return self.__node_path

	def setNodePath(self, path):
		self.__node_path = path

	nodePath = Property(str, getNodePath, setNodePath)


class ValidationsView(QWidget):
	__validate_button = None
	__validations_summary_box = None
	__validation_summary_tree = None
	__validations_details_box = None

	def __init__(self, *args, **kwargs):
		super(ValidationsView, self).__init__(*args, **kwargs)

		self.setLayout(QVBoxLayout(self))

		scroll_area = QScrollArea(self)
		scroll_area.installEventFilter(
			ResizeScrollAreaWidgetEventFilter.ResizeScrollAreaWidgetEventFilter(
				self, update_width=True, update_height=True
			)
		)

		center_widget = QWidget(scroll_area)
		center_widget.setLayout(QVBoxLayout(center_widget))
		center_widget.layout().setAlignment(Qt.AlignTop)

		# Validations summary box construction
		self.__validations_summary_box = MayaGroupBox.MayaGroupBox("Validations Summary", center_widget)
		self.__validations_summary_box.setContentLayout(QVBoxLayout(self.__validations_summary_box))
		self.__validations_summary_box.contentLayout().setAlignment(Qt.AlignTop)

		self.__validation_summary_tree = QTreeWidget(self.__validations_summary_box)
		self.__validation_summary_tree.setHeaderLabels(["Validation", "", "", "Total"])
		self.__validation_summary_tree.setColumnCount(4)
		self.__validation_summary_tree.setAlternatingRowColors(True)

		validation_summary_tree_header = self.__validation_summary_tree.header()
		validation_summary_tree_header.setSectionResizeMode(0, QHeaderView.Stretch)
		validation_summary_tree_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
		validation_summary_tree_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
		validation_summary_tree_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
		validation_summary_tree_header.setStretchLastSection(False)

		circle_builder = CirclePixmapBuilder(self)
		circle_builder.fillColor = QColor("green")

		self.success_column_icon = QIcon()
		self.success_column_icon.addPixmap(circle_builder.buildPixmap(), QIcon.Normal, QIcon.On)

		circle_builder.fillColor = QColor("red")

		self.failed_column_icon = QIcon()
		self.failed_column_icon.addPixmap(circle_builder.buildPixmap(), QIcon.Normal, QIcon.On)

		validation_summary_tree_header_item = self.__validation_summary_tree.headerItem()

		'''success_label = QLabel("S", self)
		failed_label = QLabel("F", self)

		self.__validation_summary_tree.setItemWidget(validation_summary_tree_header_item, 1, success_label)
		self.__validation_summary_tree.setItemWidget(validation_summary_tree_header_item, 2, failed_label)'''
		validation_summary_tree_header_item.setIcon(1, self.success_column_icon)
		validation_summary_tree_header_item.setIcon(2, self.failed_column_icon)

		validation_summary_tree_header_item.setTextAlignment(0, Qt.AlignLeft)
		validation_summary_tree_header_item.setTextAlignment(1, Qt.AlignRight)
		validation_summary_tree_header_item.setTextAlignment(2, Qt.AlignRight)
		validation_summary_tree_header_item.setTextAlignment(3, Qt.AlignRight)

		for i in xrange(4):
			test_item = QTreeWidgetItem(self.__validation_summary_tree)
			test_item.setText(0, "Validation %i name" % (i + 1))
			test_item.setText(3, "97")

			test_item.setTextAlignment(0, Qt.AlignLeft)
			test_item.setTextAlignment(1, Qt.AlignRight)
			test_item.setTextAlignment(2, Qt.AlignRight)
			test_item.setTextAlignment(3, Qt.AlignRight)

			success_label = NodesTotalClickableLabel(None, "10", self)
			success_label.setAlignment(Qt.AlignRight)

			failed_label = NodesTotalClickableLabel(None, "87", self)
			failed_label.setAlignment(Qt.AlignRight)

			self.__validation_summary_tree.addTopLevelItem(test_item)
			self.__validation_summary_tree.setItemWidget(test_item, 1, success_label)
			self.__validation_summary_tree.setItemWidget(test_item, 2, failed_label)

		#self.__validation_summary_tree.setHeaderItem(validation_summary_tree_header_item)
		self.__validations_summary_box.contentLayout().addWidget(self.__validation_summary_tree)

		# Validations details box construction
		self.__validations_details_box = MayaGroupBox.MayaGroupBox("Validations Details", center_widget)
		self.__validations_details_box.setContentLayout(QVBoxLayout(self.__validations_details_box))

		specs_tree_widget = QTreeWidget(self.__validations_details_box)
		specs_tree_widget.setHeaderLabels(["Specifications"])

		nodes_list_widget = QWidget(self.__validations_details_box)
		nodes_list_widget.setLayout(QVBoxLayout(nodes_list_widget))
		nodes_list_widget.layout().setAlignment(Qt.AlignTop)

		for i in xrange(3):
			node_details = NodeValidationDetails("", "Node_0%i" % (i + 1), nodes_list_widget)
			nodes_list_widget.layout().addWidget(node_details)

		for s in ("Controls", "Joints", "Geo"):
			specs_tree_widget.addTopLevelItem(QTreeWidgetItem(specs_tree_widget, [s]))

		validations_splitter = QSplitter(self.__validations_details_box)
		validations_splitter.setOrientation(Qt.Horizontal)

		validations_splitter.addWidget(specs_tree_widget)
		validations_splitter.addWidget(nodes_list_widget)

		self.__validations_details_box.contentLayout().addWidget(validations_splitter)

		center_widget.layout().addWidget(self.__validations_summary_box)
		center_widget.layout().addWidget(self.__validations_details_box)

		scroll_area.setWidget(center_widget)
		self.__validate_button = QPushButton("Validate", self)

		self.layout().addWidget(scroll_area)
		self.layout().addWidget(self.__validate_button)
