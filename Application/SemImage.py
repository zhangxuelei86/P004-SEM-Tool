#   File:   SemImage.py   
#
#   Author: Liuchuyao Xu, 2020
# 
#   Brief:  Implement the SemImage class.
#           The class encapsulates all data and methods relevant to an SEM image.

from abc import ABC
from abc import abstractmethod

try:
    import cupy as cp
except:
    import numpy as np
    cp = False
    print('Warning, could not import CuPy, GPU acceleration will be disabled.')

class SemImage(ABC):
    _image = None
    bitDepth = None
    maxLevel = None

    fft = None
    histogram = None

    def __init__(self, image):
        self.image = image
        self.bitDepth = 8
        self.maxLevel = 2**self.bitDepth
        self.updateFft()
        self.updateHistogram()

    @property
    def image(self):
        return self._image

    @image.setter
    @abstractmethod
    def image(self, image):
        ...

    @abstractmethod
    def applyHanning(self):
        ...

    @abstractmethod
    def applyHistogramEqualisation(self):
        ...

    @abstractmethod
    def updateFft(self):
        ...
    
    @abstractmethod
    def updateHistogram(self):
        ...

    @classmethod
    def create(self, image):
        if cp:
            return SemImageCuPy(image)
        else:
            return SemImageNumPy(image)

class SemImageNumPy(SemImage):

    @SemImage.image.setter
    def image(self, image):
        self._image = np.asarray(image)

    def applyHanning(self):
        col = np.hanning(self._image.shape[0])
        row = np.hanning(self._image.shape[1])
        window = np.sqrt(np.outer(col, row))
        self._image = np.multiply(window, self._image)

    def applyHistogramEqualisation(self):
        transFunc = np.cumsum(self.histogram)
        transFunc = transFunc / transFunc.max()
        transFunc = transFunc * self.maxLevel
        transFunc = transFunc.round()
        self._image = np.asarray(map(lambda x: transFunc[x], self._image))

    def updateFft(self):
        fft = np.fft.fft2(self._image)
        fft = np.fft.fftshift(fft)
        fft = np.abs(fft)
        self.fft = fft

    def updateHistogram(self):
        self.histogram = np.histogram(self._image, bins=np.arange(self.maxLevel+1))

class SemImageCuPy(SemImage):

    @SemImage.image.setter
    def image(self, image):
        self._image = cp.asarray(image)

    def applyHanning(self):
        col = cp.hanning(self._image.shape[0])
        row = cp.hanning(self._image.shape[1])
        window = cp.sqrt(cp.outer(col, row))
        self._image = cp.multiply(window, self._image)

    def applyHistogramEqualisation(self):
        transFunc = cp.cumsum(self.histogram)
        transFunc = transFunc / transFunc.max()
        transFunc = transFunc * self.maxLevel
        transFunc = transFunc.round()
        gpuMap = cp.ElementwiseKernel(
            'T x, raw T y', 'T z',
            'z = y[x]',
            'gpuMap'
        )
        self._image = cp.asarray(gpuMap(self._image, transFunc))

    def updateFft(self):
        fft = cp.fft.fft2(self._image)
        fft = cp.fft.fftshift(fft)
        fft = cp.abs(fft)
        self.fft = fft

    def updateHistogram(self):
        self.histogram = cp.histogram(self._image, bins=cp.arange(self.maxLevel+1))

if __name__ == '__main__':
    import os
    import time
    from PIL import Image
    
    imageDir = './Sample Images'
    imageList = os.listdir(imageDir)
    image = Image.open(os.path.join(imageDir, imageList[0]))
    semImage = SemImage.create(image)

    start = time.time()
    semImage = SemImage.create(image)
    end = time.time()
    print(end-start, ' seconds')

    print(type(semImage))
    print(type(semImage.image))
    print(type(semImage.fft))
    print(type(semImage.histogram))
