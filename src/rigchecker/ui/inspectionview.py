from PySide2.QtWidgets import QWidget, QScrollArea, QPushButton, QLabel, QToolBox, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy
from PySide2.QtCore import Qt, Property, Slot, Signal

from .widgets import ResizeScrollAreaWidgetEventFilter


class NodeEntryWidget(QWidget):
	def __init__(self, name, *args, **kwargs):
		super(NodeEntryWidget, self).__init__(*args, **kwargs)

		self.setLayout(QGridLayout(self))

		name_layout = QHBoxLayout(self)
		name_layout.setContentsMargins(0, 0, 0, 0)
		name_layout.setAlignment(Qt.AlignLeft)

		select_button_layout = QHBoxLayout(self)
		select_button_layout.setContentsMargins(0, 0, 0, 0)
		select_button_layout.setAlignment(Qt.AlignRight)

		name_label = QLabel(name)
		select_button = QPushButton("Select", self)
		select_button.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))

		name_layout.addWidget(name_label)
		select_button_layout.addWidget(select_button)

		self.layout().addLayout(name_layout, 0, 0)
		self.layout().addLayout(select_button_layout, 0, 1)


class SectionWidget(QWidget):
	__load_button = None
	__list_scroll_area = None

	def __init__(self, *args, **kwargs):
		super(SectionWidget, self).__init__(*args, **kwargs)

		self.setLayout(QVBoxLayout(self))

		central_widget = QWidget(self)
		central_widget.setLayout(QVBoxLayout(self))
		central_widget.layout().setAlignment(Qt.AlignTop)

		self.__list_scroll_area = QScrollArea(self)
		self.__list_scroll_area.installEventFilter(
			ResizeScrollAreaWidgetEventFilter.ResizeScrollAreaWidgetEventFilter(
				self, update_width=True, update_height=True
			)
		)
		self.__list_scroll_area.setWidget(central_widget)

		self.__load_button = QPushButton("Find", self)

		self.layout().addWidget(self.__list_scroll_area)
		self.layout().addWidget(self.__load_button)

	def getNodesList(self):
		return [l.text() for l in self.__list_scroll_area.widget().findChildren(NodeEntryWidget)]

	def setNodesList(self, nodes_names):
		central_widget = self.__list_scroll_area.widget()

		self.clearNodesList()

		for n in nodes_names:
			node_widget = NodeEntryWidget(n, central_widget)
			central_widget.layout().addWidget(node_widget)

	@Slot()
	def clearNodesList(self):
		central_widget = self.__list_scroll_area.widget()

		for ch in central_widget.findChildren(QWidget):
			ch.setVisible(False)
			ch.setParent(None)
			central_widget.layout().removeWidget(ch)
			ch.deleteLater()

	nodesList = Property(list, getNodesList, setNodesList)


class InspectionView(QWidget):
	def __init__(self, *args, **kwargs):
		super(InspectionView, self).__init__(*args, **kwargs)

		self.setLayout(QVBoxLayout(self))
		self.layout().setContentsMargins(0, 0, 0, 0)

		main_list_widget = QToolBox(self)

		for s in ("controls", "geo", "joints"):
			main_list_widget.addItem(self.__new_section_widget(self), s)

		self.layout().addWidget(main_list_widget)

	def __new_section_widget(self, parent):
		section_widget = SectionWidget(parent)
		section_widget.nodesList = ["node 1", "node 2", "node 3"]

		return section_widget
