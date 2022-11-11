import sys
sys.path.insert(0, "././Core/")
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
from Clamp import Clamp


class WaterFallWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Проверка демоверсии
        self.demo = Clamp()
        self.demo.HandleWithReceive(self.receiveDemo)
        # Разметка окна
        wFallWindowLayout = QHBoxLayout(self)
        # plotWidget
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('w')
        # настройки спектрограммы
        self.fs = 192e3
        tSeg = 0.1
        self.nPerseg = int(tSeg*self.fs)
        self.nfft = 100*self.nPerseg
        # рассчитать тестовый сигнал
        s = self.createTestSignal()
        # расчет спектрограммы
        img = self.specImage(s)
        # Подключение виджета к разметке 
        wFallWindowLayout.addWidget(self.graphWidget)
        # Построение спектрограммы
        self.graphWidget.addItem(img)

    # методы класса
    def createTestSignal(self):
        # Тестовый сигнал для водопада
        pi = np.pi
        fs = self.fs
        tvec = np.arange(0,1,1/fs)
        m = 0.3
        f0 = 40e3
        f1 = 5e3
        Un = 100
        testSig = Un*(1+m*np.cos(2*pi*f1*tvec,dtype='complex128'))*np.cos(2*pi*f0*tvec, dtype='complex128')
        pnts = len(testSig)
        noise = 1*(np.random.randn(pnts) + 1j*np.random.randn(pnts))
        testSig += noise
        hz = np.linspace(0, fs/2, int(np.floor(len(testSig)/2)+1))
        spectra = 2*np.abs(sp.fft.fft(testSig)/pnts)
        return testSig
    # построение спектрограммы
    def specImage(self, s):
        f, t, spectra = signal.spectrogram(np.real(s), self.fs, noverlap=0.1*self.nPerseg,nperseg=self.nPerseg,nfft=self.nfft,scaling='density')
        logSpectra = 10*np.log10(spectra)
        cm = pg.colormap.get('viridis')
        img = pg.ImageItem()
        img.setImage(logSpectra)
        img.setColorMap(cm)
        tr = pg.QtGui.QTransform()
        tr.scale(np.max(t)/len(t), self.fs/self.nfft)
        # вставить шкалу уровней
        minv, maxv = np.nanmin(np.nanmin(logSpectra[logSpectra != -np.inf])), np.nanmax(np.nanmax(logSpectra))
        bar = pg.ColorBarItem(interactive=True, values=(minv, maxv), colorMap=cm, label='Мощность [дБ]')
        bar.setImageItem(img, insert_in=self.graphWidget.plotItem)  
        img.setTransform(tr)
        self.graphWidget.plotItem.setLabel(axis='left', text='Частота, Гц')
        self.graphWidget.plotItem.setLabel(axis='bottom', text='Время, с')
        return img

    def receiveDemo(self, data: bool):
        self.demo.ReceivedValue = data
        pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = WaterFallWindow()
    main.show()
    sys.exit(app.exec_())
