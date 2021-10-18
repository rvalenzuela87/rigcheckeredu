from PySide2.QtWidgets import QFrame


class HLine(QFrame):
	def __init__(self, parent):
		super(HLine, self).__init__(parent)

		self.setFrameShape(QFrame.HLine)
		self.setFrameShadow(QFrame.Sunken)
