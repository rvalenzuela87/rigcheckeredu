import random
from collections import namedtuple

from PySide2.QtWidgets import QWidget, QScrollArea, QPushButton, QLabel, QGroupBox, QTreeWidget, QTreeWidgetItem, QSplitter, QMessageBox, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QSizePolicy
from PySide2.QtCore import Qt, Property, Slot, Signal, QObject

from .widgets import ResizeScrollAreaWidgetEventFilter, MayaGroupBox, BlockLabel, BlockLabelsList
from .widgets import ClickableLabel, EditableLabel
reload(EditableLabel)
reload(BlockLabelsList)


NodeData = namedtuple("NodeData", ["name", "path"])
SpecData = namedtuple("SpecData", ["name", "value"])


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


class NewSpecFormWidget(QWidget):
	__specs_types = {
		"suffix": str,
		"expression": str,
		"type": list,
		"location": list
	}

	# Signals
	accepted = Signal(tuple)
	rejected = Signal()

	def __init__(self, *args, **kwargs):
		super(NewSpecFormWidget, self).__init__(*args, **kwargs)

		self.setLayout(QVBoxLayout(self))
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().setAlignment(Qt.AlignTop)

		form_layout = QHBoxLayout(self)
		form_layout.setContentsMargins(0, 0, 0, 0)
		form_layout.setAlignment(Qt.AlignLeft)

		buttons_layout = QHBoxLayout(self)
		buttons_layout.setContentsMargins(0, 0, 0, 0)
		buttons_layout.setAlignment(Qt.AlignRight)

		self.__spec_combo_box = QComboBox(self)
		self.__spec_combo_box.addItems(self.__specs_types.keys())
		self.__spec_combo_box.currentTextChanged.connect(self.enableEditMode)

		self.__esc_line_edit = EditableLabel.EditableLabel(self)
		self.__esc_line_edit.displayButtons = False
		self.__esc_line_edit.setEnabled(False)
		self.__esc_line_edit.setVisible(False)
		self.__esc_line_edit.changeDiscarded.connect(self.rejected.emit)
		self.__esc_line_edit.changed[None].connect(self.acceptSpec)

		self.__block_labels_list = BlockLabelsList.BlockLabelsList(Qt.Horizontal, self)
		self.__block_labels_list.setEnabled(False)
		self.__block_labels_list.setVisible(False)

		self.__accept_button = QPushButton("Add", self)
		self.__accept_button.clicked.connect(self.acceptSpec)

		self.__cancel_button = QPushButton("Cancel", self)
		self.__cancel_button.clicked.connect(self.rejected.emit)

		form_layout.addWidget(self.__spec_combo_box)
		form_layout.addWidget(self.__esc_line_edit)
		form_layout.addWidget(self.__block_labels_list)

		buttons_layout.addWidget(self.__accept_button)
		buttons_layout.addWidget(self.__cancel_button)

		self.layout().addLayout(form_layout)
		self.layout().addLayout(buttons_layout)

	@Slot(str)
	def enableEditMode(self, specType):
		if self.__specs_types[specType] is str:
			self.__block_labels_list.setVisible(False)
			self.__block_labels_list.setEnabled(False)

			self.__esc_line_edit.setText("")
			self.__esc_line_edit.setEnabled(True)
			self.__esc_line_edit.setVisible(True)
			self.__esc_line_edit.enableEditMode()
		elif self.__specs_types[specType] is list:
			self.__esc_line_edit.setVisible(False)
			self.__esc_line_edit.disableEditMode()
			self.__esc_line_edit.setEnabled(False)

			self.__block_labels_list.clearLabels()
			self.__block_labels_list.setEnabled(True)
			self.__block_labels_list.setVisible(True)
			self.__block_labels_list.enableAddLabelMode()

	@Slot()
	def disableEditMode(self):
		self.__esc_line_edit.setVisible(False)
		self.__esc_line_edit.setText("")
		self.__esc_line_edit.setEnabled(False)

		self.__block_labels_list.setVisible(False)
		self.__block_labels_list.clearLabels()
		self.__block_labels_list.setEnabled(False)

	@Slot()
	def acceptSpec(self):
		spec_type = self.__spec_combo_box.currentText()

		if self.__specs_types[spec_type] is str:
			spec_value = str(self.__esc_line_edit.text)
		else:
			spec_value = tuple(self.__block_labels_list.labels)

		self.accepted.emit((spec_type, spec_value))


class FindSpecsWidgetBck(QWidget):
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


class FindSpecsWidget(QWidget):
	__specs_id = None
	__specs = None

	__controller = None

	__specs_box = None
	__results_box = None
	__new_spec_widget = None
	__add_spec_button = None
	__nodes_found_widget = None
	__total_nodes_found_label = None
	__save_specs_button = None

	# Signals
	specAdded = Signal([str], [None])
	searchNodes = Signal([dict], [None])
	selectNodes = Signal(list)
	isolateNodes = Signal(list)

	def __init__(self, specs_id, specs, *args, **kwargs):
		super(FindSpecsWidget, self).__init__(*args, **kwargs)

		self.setLayout(QVBoxLayout(self))
		self.layout().setAlignment(Qt.AlignTop)

		self.__add_spec_button = ClickableLabel.ClickableLabel("New Spec", self)
		self.__add_spec_button.clicked.connect(self.enableNewSpecForm)

		self.__specs_box = MayaGroupBox.MayaGroupBox("Finding Specs", self)
		self.__specs_box.setContentLayout(QVBoxLayout(self.__specs_box))

		specs_form_layout = QFormLayout(self.__specs_box)
		specs_form_layout.setContentsMargins(0, 0, 0, 0)
		specs_form_layout.setAlignment(Qt.AlignVCenter)

		self.__specs_box.contentLayout().addLayout(specs_form_layout)

		self.__results_box = MayaGroupBox.MayaGroupBox("Results", self)
		self.__results_box.setContentLayout(QVBoxLayout(self.__results_box))
		self.__results_box.setFlat(True)

		search_nodes_button = QPushButton("Find", self)
		search_nodes_button.clicked.connect(self.emitSearchNodes)

		self.__total_nodes_found_label = QLabel("0", self)

		self.__nodes_found_widget = NodesFoundWidget("Matching Nodes", self)
		self.__nodes_found_widget.setFlat(True)

		self.__save_specs_button = QPushButton("Save", self.__specs_box)

		# Build specifications box
		new_spec_layout = QHBoxLayout(self.__specs_box)
		new_spec_layout.setAlignment(Qt.AlignRight)
		new_spec_layout.setContentsMargins(0, 0, 0, 0)

		new_spec_layout.addWidget(self.__add_spec_button)
		new_spec_layout.addWidget(self.__save_specs_button)

		self.__specs_box.contentLayout().addLayout(new_spec_layout)

		# Build results box
		select_all_nodes_found_button = QPushButton("Sel", self)
		isolate_all_nodes_found_button = QPushButton("Iso", self)

		found_nodes_layout = QHBoxLayout(self.__results_box)
		found_nodes_layout.setContentsMargins(0, 0, 0, 0)
		found_nodes_layout.setAlignment(Qt.AlignLeft)

		found_nodes_layout.addWidget(QLabel("Found:", self.__results_box))
		found_nodes_layout.addWidget(self.__total_nodes_found_label)
		found_nodes_layout.addWidget(select_all_nodes_found_button)
		found_nodes_layout.addWidget(isolate_all_nodes_found_button)

		self.__results_box.contentLayout().addLayout(found_nodes_layout)
		self.__results_box.contentLayout().addWidget(self.__nodes_found_widget)

		self.layout().addWidget(self.__specs_box)
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

	@Slot(tuple)
	def addSpec(self, specData):
		specData = SpecData(specData[0], specData[1])

		self.__specs[specData.name] = specData.value
		specs_form_layout = self.__specs_box.findChild(QFormLayout)

		if type(specData.value) in [str, 'unicode']:
			value_edit_label = EditableLabel.EditableLabel(specData.value, self.__specs_box)
			value_edit_label.displayButtons = False

			specs_form_layout.addRow("%s:" % specData.name, value_edit_label)
		elif type(specData.value) in [list, tuple]:
			block_labels_list = BlockLabelsList.BlockLabelsList(Qt.Horizontal, self.__specs_box)

			block_labels_list.labels = [v for v in specData.value]

			specs_form_layout.addRow("%s:" % specData.name, block_labels_list)

		self.specAdded[str].emit(specData.name)
		self.specAdded[None].emit()

		self.disableNewSpecForm()

	def getNodesList(self):
		return self.__nodes_found_widget.nodesList

	@Slot()
	def enableNewSpecForm(self):
		if self.__new_spec_widget is None:
			self.__new_spec_widget = NewSpecFormWidget(self.__specs_box)
			self.__new_spec_widget.setVisible(False)
			self.__new_spec_widget.setEnabled(False)

			self.__new_spec_widget.accepted.connect(self.addSpec)
			self.__new_spec_widget.rejected.connect(self.disableNewSpecForm)

			self.__specs_box.contentLayout().insertWidget(1, self.__new_spec_widget)

		self.__new_spec_widget.setEnabled(True)
		self.__new_spec_widget.setVisible(True)

	@Slot()
	def disableNewSpecForm(self):
		if self.__new_spec_widget is not None:
			self.__new_spec_widget.setVisible(False)
			self.__new_spec_widget.setEnabled(False)
			self.__new_spec_widget.setParent(None)

			self.__new_spec_widget.accepted.disconnect(self.addSpec)
			self.__new_spec_widget.rejected.disconnect(self.disableNewSpecForm)

			self.__specs_box.layout().removeWidget(self.__new_spec_widget)

			self.__new_spec_widget.deleteLater()
			self.__new_spec_widget = None

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
