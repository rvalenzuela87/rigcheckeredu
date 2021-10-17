from PySide2.QtWidgets import QWidget, QGroupBox, QComboBox, QLineEdit, QPushButton, QFormLayout, QVBoxLayout


class ConfigView(QWidget):
	def __init__(self, *args, **kwargs):
		super(ConfigView, self).__init__(args, kwargs)

		controls_conf_box = QGroupBox(self, "Controls")
		geo_group_conf_box = QGroupBox(self, "Geo Group")
		rig_group_conf_box = QGroupBox(self, "Rig Group")
