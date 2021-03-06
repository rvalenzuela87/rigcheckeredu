import random
from collections import namedtuple

from PySide2.QtWidgets import QWidget, QScrollArea, QPushButton, QLabel, QGroupBox, QTreeWidget, QTreeWidgetItem
from PySide2.QtWidgets import QSplitter, QMessageBox, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QSizePolicy
from PySide2.QtCore import Qt, Property, Slot, Signal, QObject

from .widgets import ResizeScrollAreaWidgetEventFilter, MayaToolBoxWidget, MayaGroupBox, BlockLabel, ClickableLabel


NodeData = namedtuple("NodeData", ["name", "path"])


class InspectionController(QObject):
	# Signals
	specsFound = Signal([str, dict], [None])
	specsNotFound = Signal([str], [None])

	matchingNodesFound = Signal(list)
	noMatchingNodesFound = Signal([str], [None])

	nodesSelected = Signal()
	selectNodesFailed = Signal()

	nodesIsolated = Signal()
	isolateNodesFailed = Signal()

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

		self.specsFound[str, dict].emit(specs_name, dummy)
		self.specsFound[None].emit()

		return dummy

	@Slot(dict)
	def getMatchingNodes(self, specs):
		nodes = [NodeData("nodeName_%i" % i, "node%iPath" % i) for i in xrange(random.randint(0, 15))]
		self.matchingNodesFound.emit(nodes)
		return nodes

	@Slot(list)
	def selectNodes(self, nodesPaths):
		self.nodesSelected.emit()

	@Slot(list)
	def isolateNodes(self, nodesPaths):
		self.nodesIsolatede.emit()


class NodeEntryWidget(QWidget):
	__node_data = None

	def __init__(self, node_data, *args, **kwargs):
		super(NodeEntryWidget, self).__init__(*args, **kwargs)

		#self.setLayout(QGridLayout(self))
		self.setLayout(QHBoxLayout(self))
		self.layout().setContentsMargins(5, 0, 5, 5)

		name_label = ClickableLabel.ClickableLabel(node_data.name, self)
		name_label.setUnderline(False)
		name_label_size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
		name_label.setSizePolicy(name_label_size_policy)

		select_button = QPushButton("Iso", self)
		select_button_size_policy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
		select_button.setSizePolicy(select_button_size_policy)

		self.layout().addWidget(name_label)
		self.layout().addWidget(select_button)

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


class NodesFoundWidget(MayaGroupBox.MayaGroupBox):
	__nodes_list = None

	__load_button = None
	__list_scroll_area = None

	def __init__(self, *args, **kwargs):
		super(NodesFoundWidget, self).__init__(*args, **kwargs)

		self.setContentLayout(QVBoxLayout(self))
		self.contentLayout().setContentsMargins(0, 0, 0, 0)

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
		self.__load_button.clicked.connect(self.loadNodes)

		self.contentLayout().addWidget(self.__list_scroll_area)
		self.contentLayout().addWidget(self.__load_button)

	def getNodesList(self):
		return self.__nodes_list

	def setNodesList(self, nodes_data):
		self.clearNodesList()

		self.__nodes_list = nodes_data

	def getNodesNames(self):
		for nd in self.nodesList:
			yield nd.name

	def getNodesPaths(self):
		for nd in self.nodesList:
			yield nd.path

	@Slot()
	def loadNodes(self):
		self.clearNodesList()

		central_widget = self.__list_scroll_area.widget()

		for nd in self.nodesList:
			central_widget.layout().addWidget(NodeEntryWidget(nd, central_widget))

	@Slot()
	def clearNodesList(self):
		central_widget = self.__list_scroll_area.widget()

		for ch in central_widget.findChildren(NodeEntryWidget):
			ch.setVisible(False)
			ch.setParent(None)
			central_widget.layout().removeWidget(ch)
			ch.deleteLater()

	nodesList = Property(list, getNodesList, setNodesList)
	nodesNames = Property(list, getNodesNames, None)
	nodesPaths = Property(list, getNodesPaths, None)


class FindSpecsWidget(QWidget):
	__specs_id = None
	__specs = None

	__controller = None

	__results_box = None
	__nodes_found_widget = None
	__total_nodes_found_label = None

	# Signals
	searchNodes = Signal([dict], [None])
	selectNodes = Signal(list)
	isolateNodes = Signal(list)

	def __init__(self, specs_id, specs, *args, **kwargs):
		super(FindSpecsWidget, self).__init__(*args, **kwargs)

		self.setLayout(QVBoxLayout(self))
		self.layout().setAlignment(Qt.AlignTop)

		specs_box = MayaGroupBox.MayaGroupBox("Finding Specs", self)
		specs_box.setContentLayout(QVBoxLayout(specs_box))

		self.__results_box = MayaGroupBox.MayaGroupBox("Results", self)
		self.__results_box.setContentLayout(QVBoxLayout(self.__results_box))
		self.__results_box.setFlat(True)

		search_nodes_button = QPushButton("Find", self)
		search_nodes_button.clicked.connect(self.emitSearchNodes)

		select_all_nodes_found_button = QPushButton("Sel", self)
		isolate_all_nodes_found_button = QPushButton("Iso", self)
		self.__total_nodes_found_label = QLabel("0", self)

		self.__nodes_found_widget = NodesFoundWidget("Matching Nodes", self)
		self.__nodes_found_widget.setFlat(True)

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

		specs_box.contentLayout().addWidget(specs_list_widget)

		# Build results box
		found_nodes_layout = QHBoxLayout(self.__results_box)
		found_nodes_layout.setContentsMargins(0, 0, 0, 0)
		found_nodes_layout.setAlignment(Qt.AlignLeft)

		found_nodes_layout.addWidget(QLabel("Found:", self.__results_box))
		found_nodes_layout.addWidget(self.__total_nodes_found_label)
		found_nodes_layout.addWidget(select_all_nodes_found_button)
		found_nodes_layout.addWidget(isolate_all_nodes_found_button)

		self.__results_box.contentLayout().addLayout(found_nodes_layout)
		self.__results_box.contentLayout().addWidget(self.__nodes_found_widget)

		self.layout().addWidget(specs_box)
		self.layout().addWidget(search_nodes_button)
		self.layout().addWidget(self.__results_box)

		self.__specs_id = specs_id
		self.__specs = specs

		# Connect signals
		self.__controller = InspectionController(self)

		self.searchNodes[dict].connect(self.__controller.getMatchingNodes)
		self.selectNodes.connect(self.__controller.selectNodes)
		self.isolateNodes.connect(self.__controller.isolateNodes)

		self.__controller.matchingNodesFound.connect(self.setNodesList)

	def getSpecsId(self):
		return self.__specs_id

	def getSpecs(self):
		return self.__specs

	def getNodesList(self):
		return self.__nodes_found_widget.nodesList

	@Slot()
	def setNodesList(self, nodesList):
		self.__total_nodes_found_label.setText(str(len(nodesList)))
		self.__nodes_found_widget.nodesList = nodesList
		self.__results_box.setFlat(False)

	@Slot()
	def emitSearchNodes(self):
		self.searchNodes[dict].emit(self.specs)
		self.searchNodes[None].emit()

	@Slot()
	def emitSelectNodes(self):
		self.selectNodes.emit(self.__nodes_found_widget.nodesPaths)

	specsId = Property(str, getSpecsId, None)
	specs = Property(dict, getSpecs, None)
	nodesList = Property(list, getNodesList, setNodesList)


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
		self.__controller.specsFound[str, dict].connect(self.loadSpecs)

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

	@Slot(str, dict)
	def loadSpecs(self, specs_id, specs):
		try:
			specs_widget = FindSpecsWidget(specs_id, specs, self)
		except(RuntimeError, Exception) as exc:
			#QMessageBox.critical("Failed loading specifications", "Unable to load the received specifications")
			print(exc.message)
			pass
		else:
			self.__dynamic_scroll_area_widget.setWidget(specs_widget)
