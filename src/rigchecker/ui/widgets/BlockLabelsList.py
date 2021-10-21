from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide2.QtCore import Signal, Slot, Property, Qt

from . import BlockLabel, ClickableLabel, EscapableLineEdit
reload(BlockLabel)


class BlockLabelsList(QWidget):
    __arrange = None
    __align = None

    __add_button = None
    __add_line_edit = None

    def __init__(self, arrange, *args, **kwargs):
        super(BlockLabelsList, self).__init__(*args, **kwargs)

        if arrange == Qt.Horizontal:
            self.setLayout(QHBoxLayout(self))
        else:
            self.setLayout(QVBoxLayout(self))

        self.__add_button = ClickableLabel.ClickableLabel("Add", self)

        self.__add_line_edit = EscapableLineEdit.EscapableLineEdit(self)
        self.__add_line_edit.escapeOnFocusOut = True
        self.__add_line_edit.setEnabled(False)
        self.__add_line_edit.setVisible(False)

        self.__add_button.clicked.connect(self.enableAddLabelMode)
        self.__add_line_edit.escaped.connect(self.disableAddLabelMode)
        self.__add_line_edit.accepted.connect(self.addLabel)
        #self.__add_line_edit.accepted.connect(self.disableAddLabelMode)

        self.layout().addWidget(self.__add_line_edit)
        self.layout().addWidget(self.__add_button)

    def getLabels(self):
        return [ch.getText() for ch in self.findChildren(BlockLabel.BlockLabel)]

    def getBlockLabels(self):
        return [ch for ch in self.findChildren(BlockLabel.BlockLabel)]

    @Slot(str)
    def addLabel(self, label):
        self.layout().insertWidget(0, BlockLabel.BlockLabel(label, self))
        self.__add_line_edit.setText("")

    @Slot(list)
    def setLabels(self, labels):
        self.clearLabels()

        labels.reverse()

        for l in labels:
            l = BlockLabel.BlockLabel(l, self)

            self.layout().insertWidget(0, l)

    @Slot()
    def clearLabels(self):
        for ch in self.findChildren(BlockLabel.BlockLabel):
            try:
                ch.delete()
            except(RuntimeError, Exception):
                ch.setVisible(False)
                ch.setParent(None)
                self.layout().removeWidget(ch)
                ch.deleteLater()
            else:
                self.layout().removeWidget(ch)

    @Slot()
    def enableAddLabelMode(self):
        self.__add_line_edit.setEnabled(True)
        self.__add_line_edit.setText("")
        self.__add_line_edit.setVisible(True)
        self.__add_line_edit.setFocus()

    @Slot()
    def disableAddLabelMode(self):
        self.__add_line_edit.setFocus()
        self.__add_line_edit.setVisible(False)
        self.__add_line_edit.setText("")
        self.__add_line_edit.setEnabled(False)

    def setAlignment(self, align):
        try:
            self.layout().setAlignment(align)
        except(RuntimeError, Exception):
            pass

    def setArrangement(self, arrange):
        pass

    labels = Property(list, getLabels, setLabels)
    blockLabels = Property(list, getBlockLabels, None)