from PySide2 import QtWidgets, QtGui, QtCore


class AnimatedColorBackgroundButtonStyleOverride(QtWidgets.QCommonStyle):
	def drawControl(self, element, option, painter, widget):
		if element == QtWidgets.QStyle.CE_PushButtonBevel:
			pen = QtGui.QPen(QtGui.QColor(widget.palette().color(QtGui.QPalette.ButtonText)))
			painter.setPen(pen)
			painter.drawRoundRect(widget.rect(), 5, 5)
		else:
			super(AnimatedColorBackgroundButtonStyleOverride, self).drawControl(element, option, painter, widget)


class AnimatedColorBackgroundButton(QtWidgets.QPushButton):
	__background_color_anim = None
	__foreground_color_anim = None

	def __init__(self, *args, **kwargs):
		super(AnimatedColorBackgroundButton, self).__init__(*args, **kwargs)

		self.setCursor(QtCore.Qt.PointingHandCursor)

	def __start_animation(self):
		if self.isEnabled() is True:
			self.__background_color_anim = QtCore.QPropertyAnimation(self, b'backgroundColor')
			self.__background_color_anim.setStartValue(
				self.palette().color(QtGui.QPalette.Active, QtGui.QPalette.Button)
			)
			self.__background_color_anim.setEndValue(
				self.palette().color(QtGui.QPalette.Active, QtGui.QPalette.Highlight)
			)

			self.__background_color_anim.setLoopCount(1)
			self.__background_color_anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
			self.__background_color_anim.setDuration(500)

			self.__foreground_color_anim = QtCore.QPropertyAnimation(self, b'foregroundColor')
			self.__foreground_color_anim.setStartValue(
				self.palette().color(QtGui.QPalette.Active, QtGui.QPalette.ButtonText)
			)
			self.__foreground_color_anim.setEndValue(
				self.palette().color(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText))

			self.__foreground_color_anim.setLoopCount(1)
			self.__foreground_color_anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
			self.__foreground_color_anim.setDuration(400)

			self.__background_color_anim.start()
			self.__foreground_color_anim.start()

	def __stop_animation(self):
		if self.isEnabled() is True:
			try:
				self.__background_color_anim.stop()
				self.__foreground_color_anim.stop()

				self.setBackgroundColor(
					self.__background_color_anim.startValue()
				)
				self.setForegroundColor(
					self.__foreground_color_anim.startValue()
				)

				self.__background_color_anim = None
				self.__foreground_color_anim = None
			except AttributeError:
				pass

	@QtCore.Slot()
	def toggleAnim(self):
		if self.isEnabled() is True:
			if self.__background_color_anim.state() is QtCore.QAbstractAnimation.Running:
				self.__background_color_anim.stop()
				self.setPalette(self.__default_palette)
			else:
				self.__background_color_anim.start()

			if self.__foreground_color_anim.state() is QtCore.QAbstractAnimation.Running:
				self.__foreground_color_anim.stop()
				self.setPalette(self.__default_palette)
			else:
				self.__foreground_color_anim.start()

	@QtCore.Property(QtGui.QColor)
	def backgroundColor(self):
		return self.palette().color(QtGui.QPalette.Active, QtGui.QPalette.Button)

	@QtCore.Property(QtGui.QColor)
	def foregroundColor(self):
		return self.palette().color(QtGui.QPalette.Active, QtGui.QPalette.ButtonText)
	
	@backgroundColor.setter
	def setBackgroundColor(self, qcolor):
		palette = self.palette()
		palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Button, qcolor)
		palette.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Button, qcolor)
		self.setPalette(palette)

	@foregroundColor.setter
	def setForegroundColor(self, qcolor):
		palette = self.palette()
		palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, qcolor)
		palette.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, qcolor)
		self.setPalette(palette)

	def showEvent(self, event):
		super(AnimatedColorBackgroundButton, self).showEvent(event)

	def enterEvent(self, event):
		self.__start_animation()

		super(AnimatedColorBackgroundButton, self).enterEvent(event)

	def leaveEvent(self, event):
		self.__stop_animation()

		super(AnimatedColorBackgroundButton, self).leaveEvent(event)
