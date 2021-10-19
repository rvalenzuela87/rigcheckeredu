from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide2.QtCore import Qt, Signal, Slot, Property

from . import BlockLabel

class MayaGroupBox(QWidget):
    __content_area_layout = None

    def __init__(self, title, *args, **kwargs):
        super(MayaGroupBox, self).__init__(*args, **kwargs)

        self.setLayout(QVBoxLayout(self))
        self.layout().setAlignment(Qt.AlignTop)

        title_label = BlockLabel.BlockLabel(title, self)
        self.__content_area_layout = QVBoxLayout()

