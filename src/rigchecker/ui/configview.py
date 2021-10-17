from PySide2.QtWidgets import QWidget, QGroupBox, QComboBox, QLineEdit, QPushButton, QFormLayout, QVBoxLayout
from PySide2.QtWidgets import QHBoxLayout, QButtonGroup, QCheckBox, QScrollArea, QMessageBox, QLabel
from PySide2.QtGui import QRegExpValidator
from PySide2.QtCore import Qt, Signal, Slot, QRegExp, Property

from .widgets import FlowLayout
from .. import getconf
reload(getconf)

class BlockLabel(QWidget):
	__text = None
	__close_button = None

	def __init__(self, text, *args, **kwargs):
		super(BlockLabel, self).__init__(*args, **kwargs)

		self.__text = Property(str, self.text, self.setText)
		self.__close_button = Property(QPushButton, self.closeButton, None)

		if text is not None:
			self.setText(text)

	def text(self):
		return self.__text

	def setText(self, text):
		self.__text = text

	def closeButton(self):
		return self.__close_button

	def delete(self):
		pass


class ConfigView(QWidget):
	geo_suffix_line_edit = None
	geo_exp_line_edit = None

	joints_suffix_line_edit = None
	joints_exp_line_edit = None

	controls_suffix_line_edit = None
	controls_exp_line_edit = None
	off_grp_suffix_line_edit = None
	off_grp_exp_line_edit = None

	geo_discovery_buttons_group = None
	joints_discovery_buttons_group = None
	controls_discovery_buttons_group = None

	save_config_button = None
	set_to_default_config_button = None

	# Signals

	def __init__(self, conf, *args, **kwargs):
		super(ConfigView, self).__init__(*args, **kwargs)

		self.setLayout(QVBoxLayout(self))

		scroll_area = QScrollArea(self)
		central_widget = QWidget(scroll_area)
		central_widget.setLayout(QVBoxLayout(central_widget))
		central_widget.layout().setContentsMargins(0, 0, 0, 0)

		self.save_config_button = QPushButton("Save", self)
		self.save_config_button.clicked.connect(self.showSaveDialog)

		self.set_to_default_config_button = QPushButton("Set to default", self)
		self.set_to_default_config_button.clicked.connect(self.showResetToDefaultDialog)

		self.geo_discovery_buttons_group = QButtonGroup(self)
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

		scroll_area.setWidget(central_widget)

		self.layout().addWidget(scroll_area)
		self.layout().addLayout(buttons_layout)

		if conf is not None:
			self.setConfigurationValues(conf)

	@Slot()
	def setConfigurationValues(self, conf):
		for section in ("controls", "joints", "geo"):
			for attr in ("suffix", "exp"):
				try:
					self.__getattribute__("_".join([section, attr, "line_edit"])).setText(conf[section][attr])
				except TypeError:
					return False
				except KeyError:
					continue

			try:
				for m in conf[section]["selected_discovery_methods"]:
					for b in self.__getattribute__("_".join([section, "discovery_buttons_group"])).buttons():
						if b.text().lower() == m:
							b.setChecked(True)
							break
			except KeyError:
				continue

	@Slot()
	def showSaveDialog(self):
		answer = QMessageBox.question(
			self, "Save current changes?",
			"Are you sure you want to change the changes made to the configuration file?"
		)

		if answer == QMessageBox.Yes:
			print("Saving changes to config file...")
		else:
			print("Changes to config file were discarded")


	@Slot()
	def showResetToDefaultDialog(self):
		answer = QMessageBox.question(
			self, "Reset to default?",
			"Are you sure you want to reset the current configuration file to the default values?"
		)

		if answer == QMessageBox.Yes:
			print("Config file reset to default...")
		else:
			print("Config file was not reset to default")
