from PySide2.QtWidgets import QWidget, QPushButton, QTreeWidget, QTreeWidgetItem, QScrollArea, QLabel, QVBoxLayout
from PySide2.QtCore import Qt, Slot, Signal, Property, QObject, QSize
from PySide2.QtGui import QPalette, QColor, QIcon, QPixmap, QPainter, QPainterPath

from .widgets import ResizeScrollAreaWidgetEventFilter, MayaGroupBox, ClickableLabel
reload(MayaGroupBox)


class CirclePixmapBuilder(QObject):
	__width = 50
	__height = 50
	__radius = 25
	__antialiasing = True
	__fillColor = None
	__target = None

	def __init__(self, *args, **kwargs):
		super(CirclePixmapBuilder, self).__init__(*args, **kwargs)

	def buildPixmap(self):
		circle_size = QSize(self.width, self.height)
		self.__target = QPixmap(circle_size)
		self.__target.fill(Qt.transparent)

		p = QPixmap().scaled(self.width, self.height, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
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
		return self.__width

	def getHeight(self):
		return self.__height

	def getRadius(self):
		return self.__radius

	def getAntialiasing(self):
		return self.__antialiasing

	def getFillColor(self):
		return self.__fillColor

	def setWidth(self, width):
		self.__width = width

	def setHeight(self, height):
		self.__height = height

	def setRadius(self, radius):
		self.__radius = radius

	def setAntialiasing(self, anti):
		self.__antialiasing = anti

	def setFillColor(self, fillColor):
		self.__fillColor = fillColor

	width = Property(int, getWidth, setWidth)
	height = Property(int, getHeight, setHeight)
	radius = Property(int, getRadius, setRadius)
	antialiasing = Property(bool, getAntialiasing, setAntialiasing)
	fillColor = Property(QColor, getFillColor, setFillColor)


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
		self.selectNodes.emit(self.nodesPaths)

	def getNodesPaths(self):
		return self.__nodes_paths

	def setNodesPaths(self, nodesList):
		self.__nodes_paths = nodesList

	nodesPaths = Property(list, getNodesPaths, setNodesPaths)


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

		self.__validation_summary_tree = QTreeWidget(self.__validations_summary_box)
		self.__validation_summary_tree.setColumnCount(4)

		circle_builder = CirclePixmapBuilder(self)
		circle_builder.fillColor = QColor("green")

		self.success_pixmap = circle_builder.buildPixmap()
		self.success_column_icon = QIcon(self.success_pixmap)

		'''circle_builder.fillColor = QColor("red")

		self.failed_pixmap = circle_builder.buildPixmap()
		self.failed_column_icon = QIcon(self.failed_pixmap)'''

		validation_summary_tree_header_item = QTreeWidgetItem(self.__validation_summary_tree)
		validation_summary_tree_header_item.setText(0, "Validation")
		validation_summary_tree_header_item.setIcon(1, self.success_column_icon)
		validation_summary_tree_header_item.setText(2, "Failed")
		validation_summary_tree_header_item.setText(3, "Total")

		self.__validation_summary_tree.setHeaderItem(validation_summary_tree_header_item)
		self.__validations_summary_box.contentLayout().addWidget(self.__validation_summary_tree)

		# Validations details box construction
		self.__validations_details_box = MayaGroupBox.MayaGroupBox("Validations Details", center_widget)

		center_widget.layout().addWidget(self.__validations_summary_box)
		center_widget.layout().addWidget(self.__validations_details_box)

		scroll_area.setWidget(center_widget)
		self.__validate_button = QPushButton("Validate", self)

		self.layout().addWidget(scroll_area)
		self.layout().addWidget(self.__validate_button)
