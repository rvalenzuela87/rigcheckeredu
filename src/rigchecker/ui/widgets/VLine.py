from PySide2.QtWidgets import QFrame


class VLine(QFrame):
	def __init__(self, parent):
		super(VLine, self).__init__(parent)

		self.setFrameShape(QFrame.VLine)
		self.setFrameShadow(QFrame.Sunken)
