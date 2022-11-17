import sys
sys.path.insert(0, "././Core/")
import pyqtgraph as pg
import numpy as np
import scipy as sp
from scipy import signal
from PyQt5.QtGui import QFont
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from Clamp import Clamp
from threading import Thread


class WaterFallWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Выводы модуля
        self.input = Clamp()
        self.y = np.array([])
        self.First = True
        # Проверка демоверсии
        self.demo = Clamp()
        self.demo.ReceivedValue = False
        self.demo.HandleWithReceive(self.receiveDemo)
        # Разметка окна
        wFallWindowLayout = QHBoxLayout(self)
        # настройки plotWidget
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('k')
        self.graphWidget.getPlotItem().hideAxis('bottom')
        self.graphWidget.getViewBox().invertY(True)
        pg.setConfigOptions(antialias=True, leftButtonPan=True, imageAxisOrder='row-major')
        self.graphWidget.plotItem.setLabel(axis='left', text='Время, с')
        self.graphWidget.plotItem.setLabel(axis='top', text='Частота, Гц')
        cm = pg.colormap.get('viridis')
        self.img = pg.ImageItem()
        cm = pg.colormap.get('viridis')
        self.img.setColorMap(cm)
        self.graphWidget.addItem(self.img)
        minv, maxv = np.nanmin(np.nanmin(-40)), np.nanmax(np.nanmax(10))
        bar = pg.ColorBarItem(interactive=True, values=(minv, maxv), colorMap=cm, label='Мощность [дБ]')
        bar.setImageItem(self.img, insert_in=self.graphWidget.plotItem) 
        # настройки спектрограммы
        self.fs = 192e3
        self.tSeg = 0.001
        self.nPerseg = int(self.tSeg*self.fs)
        self.nfft = 100*self.nPerseg
        # рассчитать тестовый сигнал
        # расчет и построение спектрограммы
        self.input.HandleWithReceive(self.thStart) 
        # Подключение виджета к разметке 
        wFallWindowLayout.addWidget(self.graphWidget)
        

    # методы класса
    def set_fs(self,fs):
        self.fs = fs
        self.nPerseg = int(self.tSeg*self.fs)
        self.nfft = 100*self.nPerseg
        
    def set_tSeg(self,set_tSeg):
        self.set_tSeg = set_tSeg
        self.nPerseg = int(self.tSeg*self.fs)
        self.nfft = 100*self.nPerseg

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
        if self.demo.ReceivedValue:
            f, t, spectra = signal.spectrogram(np.real(s), self.fs, noverlap=0.1*self.nPerseg,nperseg=self.nPerseg,nfft=self.nfft,scaling='density')
            logSpectra = 10*np.log10(spectra)
            self.img.setImage(logSpectra.T)
            tr = pg.QtGui.QTransform()
            tr.scale(self.fs/self.nfft, np.max(t)/len(t))
            # вставить шкалу уровней
            minv, maxv = np.nanmin(np.nanmin(logSpectra[logSpectra != -np.inf])), np.nanmax(np.nanmax(logSpectra))
            #bar = pg.ColorBarItem(interactive=True, values=(minv, maxv), colorMap=cm, label='Мощность [дБ]')
            #bar.setImageItem(self.img, insert_in=self.graphWidget.plotItem)  
            self.img.setTransform(tr)
            self.graphWidget.plotItem.setLabel(axis='left', text='Время, с')
            self.graphWidget.plotItem.setLabel(axis='top', text='Частота, Гц')
            self.graphWidget.addItem(self.img)
        elif not(self.demo.ReceivedValue):
            #self.y = self.y[1:]
            f, t, spectra = signal.spectrogram(np.real(s), self.fs, noverlap=0*self.nPerseg,nperseg=self.nPerseg,nfft=self.nfft,scaling='density')
            spectra = np.reshape(spectra, (len(spectra), ))
            if (self.First):
                self.spectra = spectra
                self.First = False
                # print(np.shape(spectra))
                # print(np.shape(self.spectra))
                logSpectra = 10*np.log10(np.reshape(self.spectra, (1, len(self.spectra))))
                self.img.setImage(logSpectra)
                tr = pg.QtGui.QTransform()
                tr.scale(self.fs/self.nfft, 1)
                # вставить шкалу уровней 
                self.img.setTransform(tr)
                self.y = np.array([])
            else:
                self.spectra = np.vstack((self.spectra, spectra))
                if len(self.spectra[:,0]) >= 10:
                    self.spectra = self.spectra[1:,:]
                # print(np.shape(self.spectra))
                logSpectra = 10*np.log10(self.spectra)
                self.img.setImage(logSpectra)
                tr = pg.QtGui.QTransform()
                tr.scale(self.fs/self.nfft, 1)
                # вставить шкалу уровней 
                self.img.setTransform(tr)
                self.y = np.array([])


    # получить демо сигнал, если включен демо-режим
    def receiveDemo(self, data: bool):
        self.demo.ReceivedValue = data
        if self.demo.ReceivedValue:
            self.demo.ConnectTo(self.input)
            self.demo.Send(self.createTestSignal())
            self.demo.DisconnectTo(self.input)
            pass
        else:
            pass
    
    # начало обработки
    def thStart(self, s):
        self.y = np.append(self.y, s[1]) # накопление данных
        if len(self.y) > self.nPerseg:
            th = Thread(target=self.specImage, args=(self.y,)) # в потоке лежит функция получения спектрограммы
            th.start()
        
    # очищение графиков
    def clearPlots(self, data: bool):
        self.graphWidget.clear()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = WaterFallWindow()
    main.show()
    sys.exit(app.exec_())
