from lib2to3.pgen2.token import NT_OFFSET
from pyqtspecgram import pyqtspecgram
import pyqtgraph as pg
import numpy as np
import scipy as sp
from scipy import signal
from PyQt5.QtGui import QFont
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
import sys
import matplotlib.pyplot as plt


class WaterFallWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Разметка окна
        wFallWindowLayout = QHBoxLayout(self)
        # plotWidget
        self.graphWidget = pg.PlotWidget()
        # показать тестовый сигнал
        s, fs  = self.createTestSignal()
        # посчитать спектрограмму
        tSeg = 0.1
        nPerseg = int(tSeg*fs)
        nfft = 100*nPerseg
        f, t, Sxx = signal.spectrogram(s, fs, nperseg=nPerseg,nfft=nfft,scaling='spectrum')
        img = pg.ImageItem()
        img.setImage(Sxx)
        cm = pg.colormap.get('CET-L9')
        img.setColorMap(cm)
        # Подключение виджета к разметке 
        wFallWindowLayout.addWidget(self.graphWidget)
        # Построение спектрограммы
        self.graphWidget.addItem(img)

        # методы класса
    def createTestSignal(self):
        # Тестовый сигнал для водопада
        pi = np.pi
        fs = 192e3
        tvec = np.arange(0,5,1/fs)
        m = 0.3
        f0 = 40e3
        f1 = 5e3
        Un = 100
        testSig = Un*(1+m*np.cos(2*pi*f1*tvec))*np.cos(2*pi*f0*tvec)
        hz = np.linspace(0, fs/2, int(np.floor(len(testSig)/2)+1))
        pnts = len(testSig)
        spectra = 2*np.abs(sp.fft.fft(testSig)/pnts)
        #plt.plot(tvec[:100], testSig[:100])
        #plt.show()
        #plt.plot(hz, spectra[:len(hz)])
        #plt.show()
        return testSig, fs

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = WaterFallWindow()
    main.show()
    sys.exit(app.exec_())
