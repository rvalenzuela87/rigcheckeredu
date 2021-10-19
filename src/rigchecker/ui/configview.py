from collections import OrderedDict

from PySide2.QtWidgets import QWidget, QGroupBox, QComboBox, QLineEdit, QPushButton, QFormLayout, QVBoxLayout, QDialog
from PySide2.QtWidgets import QHBoxLayout, QGridLayout, QButtonGroup, QCheckBox, QScrollArea, QMessageBox, QLabel
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtGui import QRegExpValidator, QPalette, QBrush, QColor
from PySide2.QtCore import Qt, Signal, Slot, QRegExp, Property, QObject

from . import configcontroller
from .widgets import FlowLayout, ClickableLabel, ResizeScrollAreaWidgetEventFilter
from .. import getconf
reload(getconf)
reload(configcontroller)


class BlockLabel(QWidget):
	__text_label = None
	__close_button = None

	def __init__(self, text, *args, **kwargs):
		super(BlockLabel, self).__init__(*args, **kwargs)

		self.setLayout(QGridLayout(self))
		self.layout().setContentsMargins(5, 5, 5, 5)

		self.__text_label = QLabel(self)
		self.__close_button = ClickableLabel.ClickableLabel("x", self)
		self.__close_button.setSizePolicy(
			QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		)
		self.__close_button.clicked.connect(self.delete)

		self.layout().addWidget(self.__text_label, 0, 0)
		self.layout().addWidget(self.__close_button, 0, 1)

		if text is not None:
			self.setText(text)

		palette = self.palette()

		for role in [QPalette.Active, QPalette.Inactive]:
			palette.setBrush(role, QPalette.Window, QBrush(QColor(255, 0, 0)))
			palette.setBrush(role, QPalette.Base, QBrush(QColor(255, 0, 0)))
			palette.setBrush(role, QPalette.Text, QBrush(QColor(255, 255, 255)))

		self.setPalette(palette)
		self.setAutoFillBackground(True)

	def text(self):
		return self.__text_label.text()

	def setText(self, text):
		self.__text_label.setText(text)

	def closeButton(self):
		return self.__close_button

	@Slot()
	def delete(self):
		self.setVisible(False)
		self.setParent(None)
		self.deleteLater()


class NewTypeDialog(QDialog):
	__type_name_line_edit = None
	__add_button = None
	__cancel_button = None

	# Signals
	add_type = Signal(str)

	def __init__(self, *args, **kwargs):
		super(NewTypeDialog, self).__init__(*args, **kwargs)

		self.setWindowTitle("Add type")

		self.setLayout(QVBoxLayout(self))

		self.__type_name_line_edit = QLineEdit(self)
		self.__add_button = QPushButton("Add", self)
		self.__add_button.clicked.connect(self.emitAddType)
		self.__add_button.setDefault(True)

		self.__cancel_button = QPushButton("Cancel", self)
		self.__cancel_button.clicked.connect(self.reject)

		new_type_form_layout = QFormLayout(self)
		new_type_form_layout.setContentsMargins(0, 0, 0, 0)

		buttons_layout = QHBoxLayout(self)
		buttons_layout.setContentsMargins(0, 0, 0, 0)

		buttons_layout.addWidget(self.__add_button)
		buttons_layout.addWidget(self.__cancel_button)

		new_type_form_layout.addRow("Type name:", self.__type_name_line_edit)

		self.layout().addLayout(new_type_form_layout)
		self.layout().addLayout(buttons_layout)

	@Property(str)
	def typeName(self):
		return self.__type_name_line_edit.text()

	@typeName.setter
	def setTypeName(self, type_name):
		self.__type_name_line_edit.setText(type_name)

	@Slot()
	def emitAddType(self):
		self.add_type.emit(self.typeName)


class TypeConfEditForm(QGroupBox):
	__title = None
	__discovery_methods = None
	__selected_discovery_methods = None

	suffix_line_edit = None
	exp_line_edit = None
	add_type_button = None
	types_layout = None
	discovery_buttons_group = None
	discovery_methods_layout = None

	# Signals
	type_added = Signal()
	received_empty_type = Signal()

	def __init__(self, title, conf, *args, **kwargs):
		super(TypeConfEditForm, self).__init__(*args, **kwargs)

		if title is not None:
			self.setTitle(title)

		self.setLayout(QFormLayout(self))

		self.suffix_line_edit = QLineEdit(self)
		self.suffix_line_edit.setValidator(QRegExpValidator(QRegExp("[a-zA-Z0-9_]*"), self))

		self.exp_line_edit = QLineEdit(self)

		self.add_type_button = ClickableLabel.ClickableLabel("Add type", self)
		self.add_type_button.clicked.connect(self.__showAddNewTypeDialog)

		'''self.off_grp_suffix_line_edit = QLineEdit(self)
		self.off_grp_suffix_line_edit.setValidator(QRegExpValidator(QRegExp("[a-zA-Z0-9_]*"), self))

		self.off_grp_exp_line_edit = QLineEdit(self)'''

		self.types_layout = QVBoxLayout(self)
		self.types_layout.setAlignment(Qt.AlignTop)
		self.types_layout.setContentsMargins(0, 0, 0, 0)

		self.types_layout.addWidget(self.add_type_button)

		self.discovery_methods_layout = QVBoxLayout(self)
		self.discovery_methods_layout.setAlignment(Qt.AlignTop)
		self.discovery_methods_layout.setContentsMargins(0, 0, 0, 0)

		self.discovery_buttons_group = QButtonGroup(self)
		self.discovery_buttons_group.setExclusive(False)

		self.layout().addRow("Suffix:", self.suffix_line_edit)
		self.layout().addRow("Expression:", self.exp_line_edit)
		self.layout().addRow("Types:", self.types_layout)
		'''self.layout().addRow("Offset group suffix:", self.off_grp_suffix_line_edit)
		self.layout().addRow("Offset group expression:", self.off_grp_exp_line_edit)'''
		self.layout().addRow("Find by:", self.discovery_methods_layout)

	@Slot()
	def __showAddNewTypeDialog(self):
		new_type_dialog = NewTypeDialog(self)
		new_type_dialog.add_type.connect(self.addType)
		new_type_dialog.show()

		return new_type_dialog
	
	'''@Property(str)
	def title(self):
		return self.__title
	
	@title.setter
	def title(self, title):
		self.__title = title'''

	@Property(str)
	def suffix(self):
		return self.suffix_line_edit.text()

	@suffix.setter
	def suffix(self, suffix):
		self.suffix_line_edit.setText(suffix)

	@Property(str)
	def expression(self):
		return self.exp_line_edit.text()

	@expression.setter
	def expression(self, exp):
		self.exp_line_edit.setText(exp)

	@Property(list)
	def types(self):
		return [bl.text().lower() for bl in self.types_layout.parentWidget().findChildren(BlockLabel)]

	@types.setter
	def setTypes(self, types_list):
		for w in self.types_layout.parentWidget().findChildren(BlockLabel):
			w.setVisible(False)
			self.types_layout.removeWidget(w)
			w.delete()

		types_list.reverse()

		for t in types_list:
			type_block = BlockLabel(t, self)
			self.types_layout.insertWidget(0, type_block)

	@Slot(str)
	def addType(self, type_name):
		if len(type_name) == 0:
			self.received_empty_type.emit()
		else:
			self.types_layout.insertWidget(0, BlockLabel(type_name, self))
			self.type_added.emit()

	@Property(list)
	def discoveryMethods(self):
		return [cb.text().lower() for cb in self.discovery_buttons_group.buttons()]

	@discoveryMethods.setter
	def setDiscoveryMethods(self, methods):
		for cb in self.discovery_buttons_group.buttons():
			cb.setVisible(False)
			cb.setParent(None)
			self.discovery_methods_layout.removeWidget(cb)
			self.discovery_buttons_group.removeButton(cb)
			cb.deleteLater()

		for m in methods:
			method_checkbox = QCheckBox(m, self)
			self.discovery_methods_layout.addWidget(method_checkbox)
			self.discovery_buttons_group.addButton(method_checkbox)

		self.discovery_methods_layout.update()

	def addDiscoveryMethod(self, name):
		method_checkbox = QCheckBox(name, controls_conf_box)
		self.discovery_methods_layout.addWidget(method_checkbox)
		self.discovery_buttons_group.addButton(method_checkbox)

	def removeDiscoveryMethod(self, name):
		for cb in self.discovery_buttons_group.buttons():
			if cb.text().lower() == name:
				cb.setVisible(False)
				cb.setParent(0)
				self.discovery_methods_layout.removeWidget(cb)
				self.discovery_buttons_group.removeButton(cb)
				cb.deleteLater()
				break

	@Property(list)
	def selectedDiscoveryMethods(self):
		return [cb.text() for cb in self.discovery_buttons_group.buttons() if cb.isChecked() is True]

	@selectedDiscoveryMethods.setter
	def setSelectedDiscoveryMethods(self, selected):
		for cb in self.discovery_buttons_group.buttons():
			if cb.text().lower() in selected:
				cb.setChecked(True)
			else:
				cb.setChecked(False)

	@Property(dict)
	def configurationValues(self):
		conf_values = OrderedDict()

		for attr in ("suffix", "exp"):
			conf_values[attr] = self.__getattribute__("_".join([attr, "line_edit"])).text()

		conf_values["types"] = self.types
		conf_values["discovery_methods"] = self.discoveryMethods
		conf_values["selected_discovery_methods"] = self.selectedDiscoveryMethods

		return conf_values

	@configurationValues.setter
	def setConfigurationValues(self, conf):
		for attr in ("suffix", "exp"):
			try:
				self.__getattribute__("_".join([attr, "line_edit"])).setText(conf[attr])
			except TypeError:
				return False
			except KeyError:
				pass

		try:
			self.setDiscoveryMethods(conf["discovery_methods"])
		except KeyError:
			pass

		try:
			self.setSelectedDiscoveryMethods(conf["selected_discovery_methods"])
		except KeyError:
			pass

		try:
			self.setTypes(conf["types"])
		except KeyError:
			pass

		self.resize(self.layout().sizeHint())


class ConfigView(QWidget):
	__controller = None
	__scroll_area = None

	'''geo_suffix_line_edit = None
	geo_exp_line_edit = None

	joints_suffix_line_edit = None
	joints_exp_line_edit = None

	controls_suffix_line_edit = None
	controls_exp_line_edit = None
	controls_types_widget = None
	off_grp_suffix_line_edit = None
	off_grp_exp_line_edit = None

	geo_discovery_buttons_group = None
	joints_discovery_buttons_group = None
	controls_discovery_buttons_group = None'''

	save_config_button = None
	set_to_default_config_button = None

	# Signals

	def __init__(self, conf, *args, **kwargs):
		super(ConfigView, self).__init__(*args, **kwargs)

		self.setLayout(QVBoxLayout(self))

		self.__scroll_area = QScrollArea(self)
		self.__scroll_area.installEventFilter(
			ResizeScrollAreaWidgetEventFilter.ResizeScrollAreaWidgetEventFilter(
				self, update_width=True, update_height=True
			)
		)
		central_widget = QWidget(self.__scroll_area)
		central_widget.setLayout(QVBoxLayout(central_widget))
		central_widget.layout().setContentsMargins(0, 0, 0, 0)

		self.save_config_button = QPushButton("Save", self)
		self.save_config_button.clicked.connect(self.showSaveDialog)

		self.set_to_default_config_button = QPushButton("Set to default", self)
		self.set_to_default_config_button.clicked.connect(self.showResetToDefaultDialog)
		
		for t in ["Controls", "Joints", "Geo"]:
			central_widget.layout().addWidget(TypeConfEditForm(t, None, central_widget))

		buttons_layout = QHBoxLayout(self)
		buttons_layout.addWidget(self.save_config_button)
		buttons_layout.addWidget(self.set_to_default_config_button)

		self.__scroll_area.setWidget(central_widget)

		self.layout().addWidget(self.__scroll_area)
		self.layout().addLayout(buttons_layout)

		self.setController(configcontroller.ConfigController(self))

		if conf is not None:
			self.setConfigurationValues(conf)

		'''self.geo_discovery_buttons_group = QButtonGroup(self)
		self.geo_discovery_buttons_group.setExclusive(False)

		self.joints_discovery_buttons_group = QButtonGroup(self)
		self.joints_discovery_buttons_group.setExclusive(False)

		self.controls_discovery_buttons_group = QButtonGroup(self)
		self.controls_discovery_buttons_group.setExclusive(False)

		controls_conf_box = QGroupBox("Controls", central_widget)
		controls_conf_box.setLayout(QFormLayout(controls_conf_box))
		controls_discovery_methods_layout = QVBoxLayout(controls_conf_box)
		controls_discovery_methods_layout.setAlignment(Qt.AlignTop)
		controls_discovery_methods_layout.setContentsMargins(0, 0, 0, 0)

		self.controls_types_widget = QWidget(controls_conf_box)
		self.controls_types_widget.setLayout(QVBoxLayout(self.controls_types_widget))
		self.controls_types_widget.layout().setAlignment(Qt.AlignTop)
		self.controls_types_widget.layout().setContentsMargins(0, 0, 0, 0)

		for dm in getconf.get_controls_discovery_methods():
			method_checkbox = QCheckBox(dm, controls_conf_box)
			controls_discovery_methods_layout.addWidget(method_checkbox)
			self.controls_discovery_buttons_group.addButton(method_checkbox)

		geo_conf_conf_box = QGroupBox("Geometry", central_widget)
		geo_conf_conf_box.setLayout(QFormLayout(geo_conf_conf_box))
		geo_discovery_methods_layout = QVBoxLayout(geo_conf_conf_box)
		geo_discovery_methods_layout.setAlignment(Qt.AlignTop)
		geo_discovery_methods_layout.setContentsMargins(0, 0, 0, 0)

		for dm in getconf.get_geo_discovery_methods():
			method_checkbox = QCheckBox(dm, geo_conf_conf_box)
			geo_discovery_methods_layout.addWidget(method_checkbox)
			self.geo_discovery_buttons_group.addButton(method_checkbox)

		joints_conf_box = QGroupBox("Joints", central_widget)
		joints_conf_box.setLayout(QFormLayout(joints_conf_box))
		joints_discovery_methods_layout = QVBoxLayout(joints_conf_box)
		joints_discovery_methods_layout.setAlignment(Qt.AlignTop)
		joints_discovery_methods_layout.setContentsMargins(0, 0, 0, 0)

		for dm in getconf.get_joints_discovery_methods():
			method_checkbox = QCheckBox(dm, joints_conf_box)
			joints_discovery_methods_layout.addWidget(method_checkbox)
			self.joints_discovery_buttons_group.addButton(method_checkbox)

		self.controls_suffix_line_edit = QLineEdit(controls_conf_box)
		self.controls_suffix_line_edit.setValidator(QRegExpValidator(QRegExp("[a-zA-Z0-9_]*"), self))

		self.controls_exp_line_edit = QLineEdit(controls_conf_box)

		self.off_grp_suffix_line_edit = QLineEdit(controls_conf_box)
		self.off_grp_suffix_line_edit.setValidator(QRegExpValidator(QRegExp("[a-zA-Z0-9_]*"), self))

		self.off_grp_exp_line_edit = QLineEdit(controls_conf_box)

		self.geo_suffix_line_edit = QLineEdit(geo_conf_conf_box)
		self.geo_suffix_line_edit.setValidator(QRegExpValidator(QRegExp("[a-zA-Z0-9_]*"), self))

		self.geo_exp_line_edit = QLineEdit(geo_conf_conf_box)

		self.joints_suffix_line_edit = QLineEdit(joints_conf_box)
		self.joints_suffix_line_edit.setValidator(QRegExpValidator(QRegExp("[a-zA-Z0-9_]*"), self))

		self.joints_exp_line_edit = QLineEdit(joints_conf_box)

		controls_conf_box.layout().addRow("Controls suffix:", self.controls_suffix_line_edit)
		controls_conf_box.layout().addRow("Controls expression:", self.controls_exp_line_edit)
		controls_conf_box.layout().addRow("Controls types:", self.controls_types_widget)
		controls_conf_box.layout().addRow("Offset group suffix:", self.off_grp_suffix_line_edit)
		controls_conf_box.layout().addRow("Offset group expression:", self.off_grp_exp_line_edit)
		controls_conf_box.layout().addRow("Find by:", controls_discovery_methods_layout)

		geo_conf_conf_box.layout().addRow("Geo suffix:", self.geo_suffix_line_edit)
		geo_conf_conf_box.layout().addRow("Geo expression:", self.geo_exp_line_edit)
		geo_conf_conf_box.layout().addRow("Find by:", geo_discovery_methods_layout)

		joints_conf_box.layout().addRow("Joints suffix:", self.joints_suffix_line_edit)
		joints_conf_box.layout().addRow("Joints expression:", self.joints_exp_line_edit)
		joints_conf_box.layout().addRow("Find by:", joints_discovery_methods_layout)

		central_widget.layout().addWidget(controls_conf_box)
		central_widget.layout().addWidget(geo_conf_conf_box)
		central_widget.layout().addWidget(joints_conf_box)

		buttons_layout = QHBoxLayout(self)

		buttons_layout.addWidget(self.save_config_button)
		buttons_layout.addWidget(self.set_to_default_config_button)

		self.__scroll_area.setWidget(central_widget)

		self.layout().addWidget(self.__scroll_area)
		self.layout().addLayout(buttons_layout)

		if conf is not None:
			self.setConfigurationValues(conf)'''

	@Slot(str)
	def __showSuccessMessage(self, mssg):
		success_message_box = QMessageBox.information(self, "Success", mssg)

		return success_message_box

	@Slot(str)
	def __showErrorMessage(self, mssg):
		error_message_box = QMessageBox.critical(self, "Error", mssg)

		return error_message_box

	@Property(QObject)
	def controller(self):
		return self.__controller

	@controller.setter
	def setController(self, controller):
		self.__controller = controller

		controller.configuration_saved[str].connect(self.__showSuccessMessage)
		controller.save_configuration_failed[str].connect(self.__showErrorMessage)
		controller.configuration_reset[str].connect(self.__showSuccessMessage)
		controller.configuration_reset[dict].connect(self.setConfigurationValues)
		controller.reset_configuration_failed[str].connect(self.__showErrorMessage)
	
	@Property(OrderedDict)
	def editForms(self):
		forms = OrderedDict()

		for w in self.__scroll_area.widget().findChildren(TypeConfEditForm):
			forms[w.title().lower()] = w

		return forms

	@Property(OrderedDict)
	def configurationValues(self):
		conf_values = OrderedDict()
		edit_forms = self.editForms

		for k in edit_forms:
			conf_values[k] = edit_forms[k].configurationValues

		return conf_values

	@configurationValues.setter
	def setConfigurationValues(self, conf):
		forms = self.editForms

		for k in conf.keys():
			try:
				forms[k].setConfigurationValues(conf[k])
			except KeyError:
				continue

	@Slot()
	def showSaveDialog(self):
		answer = QMessageBox.question(
			self, "Save current changes?",
			"Are you sure you want to change the changes made to the configuration file?"
		)

		if answer == QMessageBox.Yes:
			self.controller.saveConfiguration(self.configurationValues)

	@Slot()
	def showResetToDefaultDialog(self):
		answer = QMessageBox.question(
			self, "Reset to default?",
			"Are you sure you want to reset the current configuration file to the default values?"
		)

		if answer == QMessageBox.Yes:
			self.controller.resetConfiguration()
