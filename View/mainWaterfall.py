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
from SignalSource import SignalSource
import pyqtspecgram


class WaterFallWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Выводы модуля
        self.input = Clamp()
        self.rangeClamp = Clamp()
        self.y = np.array([])
        self.First = True
        self.SignalTypeClamp = Clamp()
        # Проверка демоверсии
        self.demo = Clamp()
        self.demo.ReceivedValue = False
        self.demo.HandleWithReceive(self.receiveDemo)
        # Разметка окна
        wFallWindowLayout = QHBoxLayout(self)
        ## элементы окна
        # галка ЧПК
        self.checkBox = QCheckBox()
        self.checkBox.setText('ЧПК')
        # настройки plotWidget
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('k')
        self.graphWidget.getPlotItem().hideAxis('bottom')
        self.graphWidget.getViewBox().invertY(True)
        pg.setConfigOptions(antialias=True, leftButtonPan=True, imageAxisOrder='row-major')
        self.graphWidget.plotItem.setLabel(axis='left', text='Время, с')
        self.graphWidget.plotItem.setLabel(axis='top', text='Частота, Гц')
        self.img = pg.ImageItem()
        self.img.setLevels([-30,0])
        # cm = pg.colormap.get('viridis')
        
        # bipolar colormap
        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        # color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
        color = np.array([[0,0,0,255], [255,255,255,255], [127,127,127,255], (63, 63, 63, 255), (190, 190, 190, 255)], dtype=np.ubyte)
        cm = pg.ColorMap(pos, color)
        lut = cm.getLookupTable(0.0, 1.0, 256)

        # set colormap
        self.img.setLookupTable(lut)
        self.img.setLevels([-50,0])

        self.img.setColorMap(cm)
        self.graphWidget.addItem(self.img)
        self.img.setLookupTable(lut)
        minv, maxv = (-40, 0)
        bar = pg.ColorBarItem(interactive=False, values=(minv, maxv), colorMap=cm, label='Мощность [дБ]')
        bar.setImageItem(self.img, insert_in=self.graphWidget.plotItem)
        self.graphWidget.setXRange(0, 20000) 
        # настройки спектрограммы
        self.fs = 44100
        self.tSeg = 0.001
        self.nPerseg = int(self.tSeg*self.fs)
        self.nfft = self.nPerseg
        self.lines = 100
        self.coef = 1
        # рассчитать тестовый сигнал
        # расчет и построение спектрограммы
        self.input.HandleWithReceive(self.thStart) 
        # Подключение виджета к разметке 
        wFallWindowLayout.addWidget(self.graphWidget)
        wFallWindowLayout.addWidget(self.checkBox)
        # действие по клампам
        self.rangeClamp.HandleWithReceive(self.setRangeX)
        self.SignalTypeClamp.HandleWithReceive(self.setCoef)
        
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
        QtWidgets.QApplication.processEvents()
        if self.demo.ReceivedValue:
            self.demoSpecgram(s)
        elif not(self.demo.ReceivedValue):
            # проверка на наличие галки ЧПК
            if not self.checkBox.isChecked():
                self.specgram(s)
            elif self.checkBox.isChecked():
                self.chpkSpecgram(s)

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
    
    # Изменить пределы по X
    def setRangeX(self, rangeVal: list):
        self.graphWidget.setXRange(rangeVal[0], rangeVal[1])
    
    # масштаб данных
    def setCoef(self, type: SignalSource):
        if type.value == SignalSource.RANGE.value:
            self.coef = 2/3e8/23.3e-3*221e6
        elif type.value ==SignalSource.VELOCITY.value:
            self.coef = 0.125/2

    # вычисление спектра
    def specgram(self, s):
        #self.y = self.y[1:]
        # f, t, spectra = signal.spectrogram(np.real(s), self.fs, noverlap=0.25*self.nPerseg,nperseg=self.nPerseg,nfft=self.nfft,window='hann')
        # win = np.hanning(len(s))
        f, spectra = signal.welch(s, self.fs, window='hann', nperseg=self.nPerseg,nfft=self.nfft,noverlap=0.25*self.nPerseg,scaling='spectrum')
        # spectra = spectra / len(spectra)
        spectra = np.reshape(spectra, (len(spectra), ))
        if (self.First):
            self.spectra = spectra
            self.First = False
            # print(np.shape(spectra))
            # print(np.shape(self.spectra))
            logSpectra = 10*np.log10(np.reshape(self.spectra, (1, len(self.spectra))))
            logSpectra[logSpectra < -100] = -120
            logSpectra[logSpectra > 0] = 0
            self.img.setImage(logSpectra,autolevels=False)
            tr = pg.QtGui.QTransform()
            tr.scale(self.fs/self.nfft * self.coef, 1)
            # вставить шкалу уровней 
            self.img.setTransform(tr)
        else:
            self.spectra = np.vstack((self.spectra, spectra))
            pass
            if len(self.spectra[:,0]) >= self.lines:
                self.spectra = self.spectra[1:,:]
            # print(np.shape(self.spectra))
            logSpectra = 10*np.log10(self.spectra)
            logSpectra[logSpectra < -100] = -120
            logSpectra[logSpectra > 0] = 0
            self.img.setImage(logSpectra, autolevels=False)
            tr = pg.QtGui.QTransform()
            tr.scale(self.fs/self.nfft*self.coef, 1)
            # вставить шкалу уровней 
            self.img.setTransform(tr)
    
    # спектрограмма с чпк
    def chpkSpecgram(self, s):
        #self.y = self.y[1:]
        # f, t, spectra = signal.spectrogram(np.real(s), self.fs, noverlap=0.25*self.nPerseg,nperseg=self.nPerseg,nfft=self.nfft)
        # win = np.hanning(len(s))
        # spectra = np.fft.rfft(s*win) / len(s)
        f, spectra = signal.welch(s, self.fs, window='hann', nperseg=self.nPerseg,nfft=self.nfft,noverlap=0.25*self.nPerseg,scaling='spectrum')
        # spectra = spectra / len(spectra)
        spectra = np.reshape(spectra, (len(spectra), ))
        if (self.First):
            self.spectra = spectra
            self.First = False
            # print(np.shape(spectra))
            # print(np.shape(self.spectra))
            logSpectra = 10*np.log10(np.reshape(self.spectra, (1, len(self.spectra))))
            logSpectra[logSpectra < -100] = -120
            logSpectra[logSpectra > 0] = 0
            self.img.setImage(logSpectra,autolevels=False)
            tr = pg.QtGui.QTransform()
            tr.scale(self.fs/self.nfft * self.coef, 1)
            # вставить шкалу уровней 
            self.img.setTransform(tr)
        else:
            self.spectra = np.vstack((self.spectra, spectra))
            new=np.abs(self.spectra[-1,:]-self.spectra[-2,:])
            new = new**2
            self.spectra[-1,:]=new
            if len(self.spectra[:,0]) >= self.lines:
                self.spectra = self.spectra[1:,:]
                # print(np.shape(self.spectra))
            logSpectra = 10*np.log10(self.spectra)
            logSpectra[logSpectra < -100] = -120
            logSpectra[logSpectra > 0] = 0
            self.img.setImage(logSpectra, autolevels=False)
            tr = pg.QtGui.QTransform()
            tr.scale(self.fs/self.nfft * self.coef, 1)
            # вставить шкалу уровней 
            self.img.setTransform(tr)

    def demoSpecgram(self, s):
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



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = WaterFallWindow()
    main.show()
    sys.exit(app.exec_())
