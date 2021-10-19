from collections import namedtuple

from PySide2.QtWidgets import QWidget, QScrollArea, QPushButton, QLabel, QGroupBox, QTreeWidget, QTreeWidgetItem, QSplitter, QMessageBox, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QSizePolicy
from PySide2.QtCore import Qt, Property, Slot, Signal, QObject

from .widgets import ResizeScrollAreaWidgetEventFilter, MayaToolBoxWidget, BlockLabel
reload(BlockLabel)


NodeData = namedtuple("NodeData", ["name", "path"])


class InspectionController(QObject):
	specsFound = Signal([dict], [None])
	specsNotFound = Signal([str], [None])

	def __init__(self, *args, **kwargs):
		super(InspectionController, self).__init__(*args, **kwargs)

	@Slot(str)
	def getSpecs(self, specs_name):
		print("Trying to load %s" % specs_name)
		if specs_name == "controls":
			dummy = {
				"findby": ["type", "suffix"],
				"suffix": "ctrl",
				"type": ["curve", "locator"]
			}
		elif specs_name == "joints":
			dummy = {
				"findby": ["type", "suffix", "exp"],
				"suffix": "jnt",
				"type": ["joint"],
				"exp": ".*_jnt$"
			}
		elif specs_name == "geo":
			dummy = {
				"findby": ["type", "suffix"],
				"suffix": "_geo",
				"type": ["mesh", "surface"]
			}
		else:
			dummy = {
				"findby": ["type", "suffix"],
				"suffix": "",
				"type": [""]
			}

		self.specsFound[dict].emit(dummy)
		self.specsFound[None].emit()

		return dummy


class NodeEntryWidget(QWidget):
	__node_data = None

	def __init__(self, node_data, *args, **kwargs):
		super(NodeEntryWidget, self).__init__(*args, **kwargs)

		self.setLayout(QGridLayout(self))
		self.layout().setContentsMargins(5, 0, 5, 5)

		name_layout = QHBoxLayout(self)
		name_layout.setContentsMargins(0, 0, 0, 0)
		name_layout.setAlignment(Qt.AlignLeft)

		select_button_layout = QHBoxLayout(self)
		select_button_layout.setContentsMargins(0, 0, 0, 0)
		select_button_layout.setAlignment(Qt.AlignRight)

		name_label = QLabel(node_data.name)
		select_button = QPushButton("Select", self)
		select_button.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))

		name_layout.addWidget(name_label)
		select_button_layout.addWidget(select_button)

		self.layout().addLayout(name_layout, 0, 0)
		self.layout().addLayout(select_button_layout, 0, 1)

		self.setNodeData(node_data)

	def getNodeData(self):
		return self.__node_data

	def setNodeData(self, node_data):
		self.__node_data = node_data

	def getNodePath(self):
		return self.nodeData.path

	def getNodeName(self):
		return self.nodeData.name

	nodeData = Property(NodeData, getNodeData, setNodeData)
	nodePath = Property(str, getNodePath, None)
	nodeName = Property(str, getNodeName, None)


class NodesFoundWidget(QWidget):
	__load_button = None
	__list_scroll_area = None

	def __init__(self, *args, **kwargs):
		super(NodesFoundWidget, self).__init__(*args, **kwargs)

		self.setLayout(QVBoxLayout(self))
		self.layout().setContentsMargins(0, 0, 0, 0)

		central_widget = QWidget(self)
		central_widget.setLayout(QVBoxLayout(self))
		central_widget.layout().setAlignment(Qt.AlignTop)
		central_widget.layout().setContentsMargins(0, 5, 0, 0)

		self.__list_scroll_area = QScrollArea(self)
		self.__list_scroll_area.installEventFilter(
			ResizeScrollAreaWidgetEventFilter.ResizeScrollAreaWidgetEventFilter(
				self, update_width=True, update_height=True
			)
		)
		self.__list_scroll_area.setWidget(central_widget)

		self.__load_button = QPushButton("Load", self)

		self.layout().addWidget(self.__list_scroll_area)
		self.layout().addWidget(self.__load_button)

	def getNodes(self):
		for nw in self.__list_scroll_area.widget().findChildren(NodeEntryWidget):
			yield nw.nodeData

	def setNodes(self, nodes_data):
		central_widget = self.__list_scroll_area.widget()

		self.clearNodesList()

		for nd in nodes_data:
			central_widget.layout().addWidget(NodeEntryWidget(nd, central_widget))

	def getNodesNames(self):
		for nw in self.__list_scroll_area.widget().findChildren(NodeEntryWidget):
			yield nw.nodeName

	def getNodesPaths(self):
		for nw in self.__list_scroll_area.widget().findChildren(NodeEntryWidget):
			yield nw.nodePath

	@Slot()
	def clearNodesList(self):
		central_widget = self.__list_scroll_area.widget()

		for ch in central_widget.findChildren(NodeEntryWidget):
			ch.setVisible(False)
			ch.setParent(None)
			central_widget.layout().removeWidget(ch)
			ch.deleteLater()

	nodesList = Property(list, getNodes, setNodes)
	nodesNames = Property(list, getNodesNames, None)
	nodesPaths = Property(list, getNodesPaths, None)


class FindSpecsWidget(QWidget):
	__nodes_found_widget = None
	__total_nodes_found_label = None

	def __init__(self, specs, *args, **kwargs):
		super(FindSpecsWidget, self).__init__(*args, **kwargs)

		self.setLayout(QVBoxLayout(self))

		specs_box = QGroupBox("Finding Specs", self)
		specs_box.setLayout(QVBoxLayout(specs_box))

		results_box = MayaToolBoxWidget.MayaToolBoxWidget(self)
		search_nodes_button = QPushButton("Search", self)
		select_all_nodes_found_button = QPushButton("Sel", self)
		isolate_all_nodes_found_button = QPushButton("Iso", self)
		self.__total_nodes_found_label = QLabel("0", self)
		self.__nodes_found_widget = NodesFoundWidget(self)

		# Build specifications box
		specs_list_widget = QWidget(specs_box)
		specs_list_widget.setLayout(QFormLayout(specs_list_widget))
		specs_list_widget.layout().setContentsMargins(0, 0, 0, 0)

		find_methods_layout = QHBoxLayout(specs_list_widget)
		find_methods_layout.setAlignment(Qt.AlignLeft)
		find_methods_layout.setContentsMargins(0, 0, 0, 0)

		try:
			for fm in specs["findby"]:
				block_label = BlockLabel.BlockLabel(fm, specs_list_widget)
				block_label.setLocked(True)

				find_methods_layout.addWidget(block_label)
		except(KeyError, TypeError, ValueError, RuntimeError):
			pass

		specs_list_widget.layout().addRow("Find by:", find_methods_layout)

		for k in specs:
			if k == "findby":
				continue

			if type(specs[k]) is list:
				list_layout = QHBoxLayout(specs_list_widget)
				list_layout.setAlignment(Qt.AlignLeft)
				list_layout.setContentsMargins(0, 0, 0, 0)

				for t in specs[k]:
					block_label = BlockLabel.BlockLabel(t, specs_list_widget)
					block_label.setLocked(True)
					list_layout.addWidget(block_label)

				specs_list_widget.layout().addRow("%s:" % k.capitalize(), list_layout)
			else:
				specs_list_widget.layout().addRow("%s:" % k.capitalize(), QLabel(specs[k], specs_list_widget))

		specs_box.layout().addWidget(specs_list_widget)

		# Build results box
		results_widget = QWidget(results_box)
		results_widget.setLayout(QVBoxLayout(results_widget))

		found_nodes_layout = QHBoxLayout(results_widget)
		found_nodes_layout.setContentsMargins(0, 0, 0, 0)
		found_nodes_layout.setAlignment(Qt.AlignLeft)

		found_nodes_layout.addWidget(QLabel("Found:", results_widget))
		found_nodes_layout.addWidget(self.__total_nodes_found_label)
		found_nodes_layout.addWidget(select_all_nodes_found_button)
		found_nodes_layout.addWidget(isolate_all_nodes_found_button)

		results_widget.layout().addLayout(found_nodes_layout)
		results_widget.layout().addWidget(self.__nodes_found_widget)

		results_box.addItem(results_widget, None, "Results")

		self.layout().addWidget(specs_box)
		self.layout().addWidget(search_nodes_button)
		self.layout().addWidget(results_box)


class InspectionView(QWidget):
	__controller = None

	__finding_specs_tree = None
	__dynamic_scroll_area_widget = None

	# Signals
	loadSelectedSpecs = Signal([str], [None])

	def __init__(self, specs, *args, **kwargs):
		super(InspectionView, self).__init__(*args, **kwargs)

		self.setWindowTitle("Inspect scene")
		self.setLayout(QVBoxLayout(self))
		self.layout().setContentsMargins(0, 0, 0, 0)

		main_split_widget = QSplitter(self)
		main_split_widget.setOrientation(Qt.Horizontal)

		self.__finding_specs_tree = QTreeWidget(main_split_widget)
		self.__dynamic_scroll_area_widget = QScrollArea(main_split_widget)
		self.__dynamic_scroll_area_widget.installEventFilter(
			ResizeScrollAreaWidgetEventFilter.ResizeScrollAreaWidgetEventFilter(
				self, update_width=True, update_height=True
			)
		)

		main_split_widget.addWidget(self.__finding_specs_tree)
		main_split_widget.addWidget(self.__dynamic_scroll_area_widget)

		self.__finding_specs_tree.setHeaderLabels(["Specs"])

		try:
			for sn in specs:
				self.__finding_specs_tree.addTopLevelItem(QTreeWidgetItem(self.__finding_specs_tree, [sn]))
		except(TypeError, RuntimeError):
			pass

		self.__finding_specs_tree.currentItemChanged.connect(self.__loadNewSpecs)

		self.layout().addWidget(main_split_widget)

		# Connect signals

		self.__controller = InspectionController(self)
		self.loadSelectedSpecs[str].connect(self.__controller.getSpecs)

		self.__controller.specsFound[dict].connect(self.loadSpecs)

	def __new_section_widget(self, parent):
		section_widget = NodesFoundWidget(parent)
		section_widget.nodesList = ["node 1", "node 2", "node 3"]

		return section_widget

	@Slot(QTreeWidgetItem, QTreeWidgetItem)
	def __loadNewSpecs(self, currentTreeItem, previousTreeItem):
		self.clearSpecs()

		self.loadSelectedSpecs[str].emit(currentTreeItem.text(0).lower())
		self.loadSelectedSpecs[None].emit()

	@Slot()
	def clearSpecs(self):
		try:
			dynamic_widget = self.__dynamic_scroll_area_widget.widget()
		except AttributeError:
			pass
		else:
			try:
				dynamic_widget.setVisible(False)
				dynamic_widget.setParent(None)
			except AttributeError:
				pass

			self.__dynamic_scroll_area_widget.setWidget(None)

	@Slot(dict)
	def loadSpecs(self, specs):
		try:
			specs_widget = FindSpecsWidget(specs, self)
		except(RuntimeError, Exception) as exc:
			#QMessageBox.critical("Failed loading specifications", "Unable to load the received specifications")
			print(exc.message)
			pass
		else:
			self.__dynamic_scroll_area_widget.setWidget(specs_widget)
