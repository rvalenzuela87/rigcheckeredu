import os
import random
from collections import namedtuple

from PySide2.QtWidgets import QWidget, QScrollArea, QPushButton, QLabel, QTreeWidget, QTreeWidgetItem, QSplitter, QMessageBox, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QSizePolicy
from PySide2.QtCore import Qt, Property, Slot, Signal, QObject, QRegExp, QSize
from PySide2.QtGui import QPixmap, QRegExpValidator, QPalette, QBrush, QColor

from .widgets import ResizeScrollAreaWidgetEventFilter, MayaGroupBox, BlockLabelsList
from .widgets import ClickableLabel, EditableLabel
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
		central_widget.layout().setContentsMargins(0, 0, 0, 0)
		central_widget.layout().setSpacing(0)

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

		for i, nd in enumerate(self.nodesList):
			node_entry_widget = NodeEntryWidget(nd, central_widget)
			palette = node_entry_widget.palette()

			for role in [QPalette.Active, QPalette.Inactive]:
				if i % 2 == 0:
					palette.setBrush(role, QPalette.Window, QBrush(QColor(255, 255, 0)))
					palette.setBrush(role, QPalette.Base, QBrush(QColor(255, 255, 0)))
				else:
					palette.setBrush(role, QPalette.Window, QBrush(QColor(0, 255, 255)))
					palette.setBrush(role, QPalette.Base, QBrush(QColor(0, 255, 255)))

			node_entry_widget.setPalette(palette)
			node_entry_widget.setAutoFillBackground(True)

			central_widget.layout().addWidget(node_entry_widget)

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
	__new_spec_mode_on = False
	__editable = False
	__specs_id = None
	__specs = None
	__specs_types = {
		"suffix": str,
		"expression": str,
		"type": list,
		"location": list
	}

	__controller = None

	__new_spec_elements_widget = None
	__new_spec_buttons_widget = None
	__new_spec_type_combo = None
	__new_spec_line_edit = None
	__new_spec_block_labels_list = None
	__new_spec_accept_button = None
	__new_spec_cancel_button = None

	__specs_box = None
	__results_box = None
	__new_spec_widget = None
	__add_spec_button = None
	__nodes_found_widget = None
	__total_nodes_found_label = None
	__save_specs_button = None
	__edit_specs_button = None

	# Signals
	specAdded = Signal([str], [None])
	searchNodes = Signal([dict], [None])
	selectNodes = Signal(list)
	isolateNodes = Signal(list)

	def __init__(self, specs_id, specs, *args, **kwargs):
		super(FindSpecsWidget, self).__init__(*args, **kwargs)

		self.setLayout(QVBoxLayout(self))
		self.layout().setAlignment(Qt.AlignTop)

		size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
		size_policy.setHorizontalStretch(1.0)

		self.setSizePolicy(size_policy)

		self.__add_spec_button = ClickableLabel.ClickableLabel("New Spec", self)
		self.__add_spec_button.clicked[None].connect(self.enableNewSpecForm)
		self.__add_spec_button.setEnabled(self.__editable)
		self.__add_spec_button.setVisible(self.__editable)

		self.__specs_box = MayaGroupBox.MayaGroupBox("Finding Specs", self)
		self.__specs_box.setLayout(QVBoxLayout(self.__specs_box))

		specs_form_layout = QGridLayout(self.__specs_box)
		specs_form_layout.setContentsMargins(0, 0, 0, 0)
		#specs_form_layout.setAlignment(Qt.AlignVCenter)
		specs_form_layout.setColumnStretch(0, 0)
		specs_form_layout.setColumnStretch(1, 1)
		specs_form_layout.setColumnStretch(2, 0)

		specs_box_size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		specs_box_size_policy.setHorizontalStretch(1)

		self.__specs_box.layout().addLayout(specs_form_layout)

		self.__results_box = MayaGroupBox.MayaGroupBox("Results", self)
		self.__results_box.setContentLayout(QVBoxLayout(self.__results_box))
		self.__results_box.setFlat(True)

		search_nodes_button = QPushButton("Find", self)
		search_nodes_button.clicked.connect(self.emitSearchNodes)

		self.__total_nodes_found_label = QLabel("0", self)

		self.__nodes_found_widget = NodesFoundWidget("Matching Nodes", self)
		self.__nodes_found_widget.setFlat(True)

		self.__edit_specs_button = QPushButton("Edit", self.__specs_box)
		self.__edit_specs_button.clicked.connect(self.__toggleEditSaveModes)

		# Build specifications box
		new_spec_layout = QHBoxLayout(self.__specs_box)
		new_spec_layout.setAlignment(Qt.AlignRight)
		new_spec_layout.setContentsMargins(0, 0, 0, 0)

		new_spec_layout.addWidget(self.__add_spec_button)
		new_spec_layout.addWidget(self.__edit_specs_button)

		self.__specs_box.layout().addLayout(new_spec_layout)

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

	@Slot()
	def __acceptSpecs(self):
		spec_type = self.__new_spec_type_combo.currentText()

		if self.__specs_types[self.__new_spec_type_combo.currentText()] is str:
			spec_value = str(self.__new_spec_line_edit.text)
		elif self.__specs_types[self.__new_spec_type_combo.currentText()] is list:
			spec_value = tuple(self.__new_spec_block_labels_list.labels)
		else:
			spec_value = ""

		self.addSpec((spec_type, spec_value))

	@Slot(ClickableLabel.ClickableLabel)
	def __removeRow(self, closeButton):
		specs_form_layout = self.__specs_box.findChild(QGridLayout)

		try:
			row, __, __, __ = specs_form_layout.getItemPosition(specs_form_layout.indexOf(closeButton))
		except(AttributeError, Exception) as exc:
			print(exc.message)

		columns_count = specs_form_layout.columnCount()
		list_widgets = map(
			specs_form_layout.itemAtPosition, (row for __ in xrange(columns_count)), xrange(columns_count)
		)

		try:
			for w in (li.widget() for li in list_widgets):
				w.setVisible(False)
				w.setParent(None)
				specs_form_layout.removeWidget(w)
				w.deleteLater()
		except(RuntimeError, Exception) as exc:
			pass

	@Slot()
	def __toggleEditSaveModes(self):
		if self.editable is False:
			self.editable = True
			self.__edit_specs_button.setText("Save")

			if self.__new_spec_mode_on is False:
				self.enableNewSpecForm()
		else:
			self.editable = False
			self.__edit_specs_button.setText("Edit")

			if self.__new_spec_mode_on is True:
				self.disableNewSpecForm()

	def getSpecsId(self):
		return self.__specs_id

	def getSpecs(self):
		return self.__specs

	def isEditable(self):
		return self.__editable

	def setEditable(self, editable):
		self.__editable = editable

		specs_form_layout = self.__specs_box.findChild(QGridLayout)

		for row, col in ((r, c) for r in xrange(specs_form_layout.rowCount()) for c in  xrange(specs_form_layout.columnCount())):
			try:
				widget = specs_form_layout.itemAtPosition(row, col).widget()
			except AttributeError:
				continue

			if type(widget) is ClickableLabel.ClickableLabel:
				widget.setVisible(editable)
				widget.setEnabled(editable)
			else:
				try:
					widget.editable = editable
				except AttributeError:
					pass

		self.__add_spec_button.setEnabled(editable)
		self.__add_spec_button.setVisible(editable)

		'''if editable is True:
			self.__edit_specs_button.setText("Save")
			self.__edit_specs_button.clicked.disconnect(self.enableEditMode)
			self.__edit_specs_button.clicked.connect(self.disableEditMode)
		else:
			self.__edit_specs_button.setText("Edit")
			self.__edit_specs_button.clicked.disconnect(self.disableEditMode)
			self.__edit_specs_button.clicked.connect(self.enableEditMode)'''

	@Slot(tuple)
	def addSpec(self, specData):
		specData = SpecData(specData[0], specData[1])

		self.__specs[specData.name] = specData.value
		specs_form_layout = self.__specs_box.findChild(QGridLayout)

		spec_type_label = QLabel("%s:" % specData.name, self.__specs_box)
		spec_type_label.setAlignment(Qt.AlignRight)
		#spec_type_label.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))

		prev_to_last_row = specs_form_layout.rowCount() - 1

		if type(specData.value) in [str, 'unicode']:
			value_edit_label = EditableLabel.EditableLabel(specData.value, self.__specs_box)
			value_edit_label.displayButtons = False
			value_edit_label.editable = self.editable
			value_edit_label.setValidator(QRegExpValidator(QRegExp("[a-zA-Z0-9_]+")))
			value_edit_label.setPlaceholderText("Enter a %s value" % specData.name)

			specs_form_layout.addWidget(spec_type_label, prev_to_last_row, 0)
			specs_form_layout.addWidget(value_edit_label, prev_to_last_row, 1)
		elif type(specData.value) in [list, tuple]:
			block_labels_list = BlockLabelsList.BlockLabelsList(Qt.Horizontal, self.__specs_box)
			block_labels_list.labels = [v for v in specData.value]
			block_labels_list.editable = self.editable
			block_labels_list.setAlignment(Qt.AlignLeft)
			#block_labels_list.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
			block_labels_list.setValidator(QRegExpValidator(QRegExp("[a-zA-Z0-9_]+")))
			#####################################
			'''palette = block_labels_list.palette()
			palette.setBrush(QPalette.Active, QPalette.Window, QBrush(QColor(255, 255, 0)))
			block_labels_list.setPalette(palette)
			block_labels_list.setAutoFillBackground(True)'''
			#####################################

			specs_form_layout.addWidget(spec_type_label, prev_to_last_row, 0)
			specs_form_layout.addWidget(block_labels_list, prev_to_last_row, 1)

		remove_row_pixmap = QPixmap(
			os.path.join(os.environ["ICONS_DIR"], "delete-bin-2-fill.png")
		)

		remove_row_button = ClickableLabel.ClickableLabel(self.__specs_box)
		remove_row_button.clicked[QLabel].connect(self.__removeRow)
		remove_row_button.setPixmap(remove_row_pixmap)
		remove_row_button.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
		remove_row_button.setVisible(self.editable)
		remove_row_button.setEnabled(self.editable)

		specs_form_layout.addWidget(remove_row_button, prev_to_last_row, 2)

		self.specAdded[str].emit(specData.name)
		self.specAdded[None].emit()

		self.disableNewSpecForm()
		self.enableNewSpecForm()

	def getNodesList(self):
		return self.__nodes_found_widget.nodesList

	@Slot()
	def enableNewSpecForm(self):
		if self.__new_spec_mode_on is True:
			return

		form_layout = self.findChild(QGridLayout)

		self.__new_spec_type_combo = QComboBox(self)
		#self.__new_spec_type_combo.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum))

		self.__new_spec_line_edit = EditableLabel.EditableLabel(self)
		self.__new_spec_line_edit.editable = True
		self.__new_spec_line_edit.displayButtons = False
		self.__new_spec_line_edit.setEnabled(False)
		self.__new_spec_line_edit.setVisible(False)
		self.__new_spec_line_edit.setValidator(QRegExpValidator(QRegExp("[a-zA-Z0-9_]+")))
		self.__new_spec_line_edit.changeDiscarded.connect(self.disableNewSpecForm)
		self.__new_spec_line_edit.changed[None].connect(self.__acceptSpecs)

		self.__new_spec_block_labels_list = BlockLabelsList.BlockLabelsList(Qt.Horizontal, self)
		self.__new_spec_block_labels_list.editable = True
		self.__new_spec_block_labels_list.setEnabled(False)
		self.__new_spec_block_labels_list.setVisible(False)
		self.__new_spec_block_labels_list.setAlignment(Qt.AlignLeft)
		#self.__new_spec_block_labels_list.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
		self.__new_spec_block_labels_list.setValidator(QRegExpValidator(QRegExp("[a-zA-Z0-9_]+")))
		#####################################
		'''palette = self.__new_spec_block_labels_list.palette()
		palette.setBrush(QPalette.Active, QPalette.Window, QBrush(QColor(255, 255, 0)))
		self.__new_spec_block_labels_list.setPalette(palette)
		self.__new_spec_block_labels_list.setAutoFillBackground(True)'''
		#####################################
		accept_target_alias_edit_pixmap = QPixmap(
			os.path.join(os.environ["ICONS_DIR"], "checkbox-circle-fill.png")
		)
		cancel_target_alias_edit_pixmap = QPixmap(
			os.path.join(os.environ["ICONS_DIR"], "close-line.png")
		)

		self.__new_spec_accept_button = ClickableLabel.ClickableLabel(self)
		self.__new_spec_accept_button.setPixmap(accept_target_alias_edit_pixmap)
		self.__new_spec_accept_button.clicked[None].connect(self.__acceptSpecs)
		self.__new_spec_accept_button.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))

		self.__new_spec_cancel_button = ClickableLabel.ClickableLabel(self)
		self.__new_spec_cancel_button.setPixmap(cancel_target_alias_edit_pixmap)
		self.__new_spec_cancel_button.clicked[None].connect(self.disableNewSpecForm)
		self.__new_spec_cancel_button.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))

		self.__new_spec_elements_widget = QWidget(self.__specs_box)
		#self.__new_spec_elements_widget.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
		self.__new_spec_elements_widget.setLayout(QHBoxLayout(self.__new_spec_elements_widget))
		self.__new_spec_elements_widget.layout().setContentsMargins(0, 0, 0, 0)
		self.__new_spec_elements_widget.layout().addWidget(self.__new_spec_line_edit)
		self.__new_spec_elements_widget.layout().addWidget(self.__new_spec_block_labels_list)

		self.__new_spec_buttons_widget = QWidget(self.__specs_box)
		self.__new_spec_buttons_widget.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
		self.__new_spec_buttons_widget.setLayout(QHBoxLayout(self.__new_spec_buttons_widget))
		self.__new_spec_buttons_widget.layout().setContentsMargins(0, 0, 0, 0)
		self.__new_spec_buttons_widget.layout().setAlignment(Qt.AlignRight)

		self.__new_spec_buttons_widget.layout().addWidget(self.__new_spec_accept_button)
		self.__new_spec_buttons_widget.layout().addWidget(self.__new_spec_cancel_button)

		last_row = form_layout.rowCount()

		form_layout.addWidget(self.__new_spec_type_combo, last_row, 0)
		form_layout.addWidget(self.__new_spec_elements_widget, last_row, 1)
		form_layout.addWidget(self.__new_spec_buttons_widget, last_row, 2)

		self.__new_spec_type_combo.currentTextChanged.connect(self.enableSpecEditElements)
		self.__new_spec_type_combo.addItems(self.__specs_types.keys())

		self.__specs_box.resize(form_layout.sizeHint())
		self.__new_spec_mode_on = True

	@Slot(str)
	def enableSpecEditElements(self, specType):
		if self.__specs_types[specType] is str:
			self.__new_spec_block_labels_list.setVisible(False)
			self.__new_spec_block_labels_list.setEnabled(False)

			self.__new_spec_line_edit.setText("")
			self.__new_spec_line_edit.setEnabled(True)
			self.__new_spec_line_edit.setVisible(True)
			self.__new_spec_line_edit.enableEditMode()
		elif self.__specs_types[specType] is list:
			self.__new_spec_line_edit.setVisible(False)
			self.__new_spec_line_edit.disableEditMode()
			self.__new_spec_line_edit.setEnabled(False)

			self.__new_spec_block_labels_list.clearLabels()
			self.__new_spec_block_labels_list.setEnabled(True)
			self.__new_spec_block_labels_list.setVisible(True)
			self.__new_spec_block_labels_list.enableAddLabelMode()

	@Slot()
	def disableNewSpecForm(self):
		specs_form_layout = self.__specs_box.findChild(QGridLayout)

		self.__new_spec_type_combo.setVisible(False)
		self.__new_spec_elements_widget.setVisible(False)
		self.__new_spec_buttons_widget.setVisible(False)

		try:
			self.__new_spec_type_combo.currentTextChanged.disconnect(self.enableSpecEditElements)
		except AttributeError:
			pass
		else:
			self.__new_spec_type_combo.setParent(None)
			specs_form_layout.removeWidget(self.__new_spec_type_combo)
			self.__new_spec_type_combo.deleteLater()

		try:
			self.__new_spec_line_edit.changed[None].disconnect(self.__acceptSpecs)
			self.__new_spec_line_edit.changeDiscarded.connect(self.disableNewSpecForm)
		except AttributeError:
			pass
		else:
			self.__new_spec_line_edit.setParent(None)
			self.__new_spec_elements_widget.layout().removeWidget(self.__new_spec_line_edit)
			self.__new_spec_line_edit.deleteLater()

		try:
			self.__new_spec_block_labels_list.setParent(None)
		except AttributeError:
			pass
		else:
			self.__new_spec_elements_widget.layout().removeWidget(self.__new_spec_block_labels_list)
			self.__new_spec_block_labels_list.deleteLater()

		try:
			self.__new_spec_accept_button.clicked[None].disconnect(self.__acceptSpecs)
		except AttributeError:
			pass
		else:
			self.__new_spec_accept_button.setParent(None)
			self.__new_spec_buttons_widget.layout().removeWidget(self.__new_spec_accept_button)
			self.__new_spec_accept_button.deleteLater()

		try:
			self.__new_spec_cancel_button.clicked[None].disconnect(self.disableNewSpecForm)
		except AttributeError:
			pass
		else:
			self.__new_spec_cancel_button.setParent(None)
			self.__new_spec_buttons_widget.layout().removeWidget(self.__new_spec_cancel_button)
			self.__new_spec_cancel_button.deleteLater()

		self.__new_spec_elements_widget.setParent(None)
		specs_form_layout.removeWidget(self.__new_spec_elements_widget)
		self.__new_spec_elements_widget.deleteLater()

		self.__new_spec_buttons_widget.setParent(None)
		specs_form_layout.removeWidget(self.__new_spec_buttons_widget)
		self.__new_spec_buttons_widget.deleteLater()

		self.__new_spec_mode_on = False

	@Slot()
	def disableSpecEditElements(self):
		self.__new_spec_line_edit.setVisible(False)
		self.__new_spec_line_edit.setText("")
		self.__new_spec_line_edit.setEnabled(False)

		self.__new_spec_block_labels_list.setVisible(False)
		self.__new_spec_block_labels_list.clearLabels()
		self.__new_spec_block_labels_list.setEnabled(False)

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
	editable = Property(bool, isEditable, setEditable)


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
			rect = self.__dynamic_scroll_area_widget.contentsRect()
			specs_widget.resize(QSize(rect.width(), rect.height()))
