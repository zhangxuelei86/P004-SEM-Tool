#   File:   SEMTool.py
#
#   Brief:  Implement the SEM realtime diagnostic tool.
# 
#   Author: Liuchuyao Xu, 2019

import sys
import time
import numpy as np
from PIL import Image
from PIL import ImageQt
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

class SEMTool(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.panel          = QtWidgets.QDockWidget()
        self.canvas         = QtWidgets.QWidget()
        self.canvas.grid    = QtWidgets.QGridLayout()

        self.PILImage   = Image.Image()
        self.image      = QtWidgets.QLabel()
        self.imageXFFT  = QtWidgets.QLabel()
        self.imageYFFT  = QtWidgets.QLabel()
        self.imageXYFFT = QtWidgets.QLabel()

        self.frameCount = 1
        self.frameReady = True
        self.frameTimer = QtCore.QTimer()

        self.initCanvas()
        self.initPanel()

        self.setWindowTitle("SEM Realtime Diagnostic Tool")
        self.setCentralWidget(self.canvas)
        # self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.panel)

        self.frameTimer.timeout.connect(self.updateImage)
        self.frameTimer.start(30)

    def initCanvas(self):
        self.updateImage()
        self.canvas.setLayout(self.canvas.grid)
        self.canvas.grid.addWidget(self.image,      0, 0, QtCore.Qt.AlignCenter)
        self.canvas.grid.addWidget(self.imageXYFFT, 0, 1, QtCore.Qt.AlignCenter)
        self.canvas.grid.addWidget(self.imageXFFT,  1, 0, QtCore.Qt.AlignCenter)
        self.canvas.grid.addWidget(self.imageYFFT,  1, 1, QtCore.Qt.AlignCenter)

    def initPanel(self):
        self.panel.setWindowTitle("Control Panel")
        self.panel.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)

    def updateImage(self):
        if self.frameReady:
            self.frameReady = False
            begin = time.time()

            self.PILImage   = Image.open("../SEM Images/Armin24%d.tif" % self.frameCount)
            qtImage         = ImageQt.ImageQt(self.PILImage)
            qtPixmap        = QtGui.QPixmap.fromImage(qtImage)
            qtPixmap.setDevicePixelRatio(1.5)
            self.image.setPixmap(qtPixmap)
            
            self.updateImageXFFT()
            self.updateImageYFFT()
            self.updateImageXYFFT()

            self.frameCount += 1
            if self.frameCount == 7:
                self.frameCount = 1

            end = time.time()
            print(end - begin)
            self.frameReady = True
        else:
            pass

    def updateImageXFFT(self):
        arrayFFT    = np.asarray(self.PILImage)
        qtImage     = QtGui.QImage(arrayFFT.data, 
                                   arrayFFT.shape[1],
                                   arrayFFT.shape[0],
                                   QtGui.QImage.Format_Indexed8)
        qtPixmap    = QtGui.QPixmap.fromImage(qtImage)
        qtPixmap.setDevicePixelRatio(1.5)
        self.imageXFFT.setPixmap(qtPixmap)

    def updateImageYFFT(self):
        arrayFFT    = np.asarray(self.PILImage)
        qtImage     = QtGui.QImage(arrayFFT.data, 
                                   arrayFFT.shape[1],
                                   arrayFFT.shape[0],
                                   QtGui.QImage.Format_Indexed8)
        qtPixmap    = QtGui.QPixmap.fromImage(qtImage)
        qtPixmap.setDevicePixelRatio(1.5)
        self.imageYFFT.setPixmap(qtPixmap)

    def updateImageXYFFT(self):
        array       = np.asarray(self.PILImage)
        arrayFFT    = np.fft.fft2(array)
        arrayFFT    = np.fft.fftshift(arrayFFT)
        arrayFFT    = np.abs(arrayFFT)
        arrayFFT    = np.log(arrayFFT)
        arrayFFT    = arrayFFT / np.max(arrayFFT)
        arrayFFT    = 255 * arrayFFT
        arrayFFT    = np.require(arrayFFT, np.uint8, 'C')
        qtImage     = QtGui.QImage(arrayFFT.data, 
                                   arrayFFT.shape[1],
                                   arrayFFT.shape[0],
                                   QtGui.QImage.Format_Indexed8)
        qtPixmap    = QtGui.QPixmap.fromImage(qtImage)
        qtPixmap.setDevicePixelRatio(1.5)
        self.imageXYFFT.setPixmap(qtPixmap)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    gui = SEMTool()
    gui.show()
    sys.exit(app.exec_())