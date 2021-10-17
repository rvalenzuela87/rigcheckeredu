from PySide2.QtWidgets import QWidget, QGroupBox, QComboBox, QLineEdit, QPushButton, QFormLayout, QVBoxLayout, QHBoxLayout, QButtonGroup, QCheckBox, QScrollArea
from PySide2.QtCore import Qt, Signal, Slot

from .widgets import FlowLayout
from .. import getconf

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

	def __init__(self, *args, **kwargs):
		super(ConfigView, self).__init__(*args, **kwargs)

		self.setLayout(QVBoxLayout(self))

		'''scroll_area = QScrollArea(self)
		central_widget = QWidget(scroll_area)
		central_widget.setLayout(QVBoxLayout(central_widget))
		central_widget.layout().setContentsMargins(0, 0, 0, 0)'''

		self.save_config_button = QPushButton("Save", self)
		self.set_to_default_config_button = QPushButton("Set to default", self)

		self.geo_discovery_buttons_group = QButtonGroup(self)
		self.geo_discovery_buttons_group.setExclusive(False)

		self.joints_discovery_buttons_group = QButtonGroup(self)
		self.joints_discovery_buttons_group.setExclusive(False)

		self.controls_discovery_buttons_group = QButtonGroup(self)
		self.controls_discovery_buttons_group.setExclusive(False)

		controls_conf_box = QGroupBox("Controls", self)
		controls_conf_box.setLayout(QFormLayout(controls_conf_box))
		controls_discovery_methods_layout = QVBoxLayout(controls_conf_box)
		controls_discovery_methods_layout.setAlignment(Qt.AlignTop)
		controls_discovery_methods_layout.setContentsMargins(0, 0, 0, 0)

		for dm in getconf.get_controls_discovery_methods():
			method_checkbox = QCheckBox(dm, controls_conf_box)
			controls_discovery_methods_layout.addWidget(method_checkbox)
			self.controls_discovery_buttons_group.addButton(method_checkbox)

		geo_conf_conf_box = QGroupBox("Geometry", self)
		geo_conf_conf_box.setLayout(QFormLayout(geo_conf_conf_box))
		geo_discovery_methods_layout = QVBoxLayout(geo_conf_conf_box)
		geo_discovery_methods_layout.setAlignment(Qt.AlignTop)
		geo_discovery_methods_layout.setContentsMargins(0, 0, 0, 0)

		for dm in getconf.get_geo_discovery_methods():
			method_checkbox = QCheckBox(dm, geo_conf_conf_box)
			geo_discovery_methods_layout.addWidget(method_checkbox)
			self.geo_discovery_buttons_group.addButton(method_checkbox)

		joints_conf_box = QGroupBox("Joints", self)
		joints_conf_box.setLayout(QFormLayout(joints_conf_box))
		joints_discovery_methods_layout = QVBoxLayout(joints_conf_box)
		joints_discovery_methods_layout.setAlignment(Qt.AlignTop)
		joints_discovery_methods_layout.setContentsMargins(0, 0, 0, 0)

		for dm in getconf.get_joints_discovery_methods():
			method_checkbox = QCheckBox(dm, joints_conf_box)
			joints_discovery_methods_layout.addWidget(method_checkbox)
			self.joints_discovery_buttons_group.addButton(method_checkbox)

		self.controls_suffix_line_edit = QLineEdit(controls_conf_box)
		self.controls_exp_line_edit = QLineEdit(controls_conf_box)
		self.off_grp_suffix_line_edit = QLineEdit(controls_conf_box)
		self.off_grp_exp_line_edit = QLineEdit(controls_conf_box)

		self.geo_suffix_line_edit = QLineEdit(geo_conf_conf_box)
		self.geo_exp_line_edit = QLineEdit(geo_conf_conf_box)

		self.joints_suffix_line_edit = QLineEdit(joints_conf_box)
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

		buttons_layout = QHBoxLayout(self)
		buttons_layout.setAlignment(Qt.AlignRight)

		buttons_layout.addWidget(self.save_config_button)
		buttons_layout.addWidget(self.set_to_default_config_button)

		self.layout().addWidget(controls_conf_box)
		self.layout().addWidget(geo_conf_conf_box)
		self.layout().addWidget(joints_conf_box)
		self.layout().addLayout(buttons_layout)
