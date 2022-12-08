import sys, os
sys.path.insert(0, "././Core/")
sys.path.insert(0, "././SignalProcessing/")
sys.path.insert(0, "././View/")
sys.path.insert(0, "././Test/")
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
import time
from threading import Thread
import concurrent.futures as cf

from SettingsFMCWRv4 import SettingsWindow
from mainWaterfall import WaterFallWindow
from mainGraph import GraphWindow
from Clamp import Clamp
from Worker import *
from TestTransiver import TestTranciver
from SignalSource import SignalSource
from Transceiver import Transceiver
# from TestTranciever import Transceiver
from WrapedUiElements import *
import queue
from scipy.io.wavfile import write
from scipy.io import wavfile
from datetime import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.save_signal = queue.Queue()
        self.wav_data=np.array([])
        self.setWindowTitle('Главное меню')
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        self._createActions()
        self._connectActions()
        self._createMenubar()

        #  Signal Settings
        fs = 44100
        segment = 200 # ms
        self.signalType=SignalSource.RANGE

        # Tranciever
        self.Tranciver = Transceiver()
        self.Tranciver.setDevice(0)             # choose device with hostapi = 0
        self.Tranciver.setChannels(1)           # set number of input channels
        self.Tranciver.setFs(fs) 
        self.Tranciver.downsample = 1

        # Graph window settings
        self.Chart0 = GraphWindow()
        self.Chart1 = WaterFallWindow()
        self.Chart1.set_fs(fs)
        self.Chart1.set_tSeg(segment)
        self.downSample = 10

        #  Add Clamps
        self.StartSopClamp = Clamp()
        self.SignalTypeClamp=Clamp()

        # разметка
        layout = QHBoxLayout(self)
        # добавление виджетов
        self.settings = SettingsWindow()
        self.dockSettings = QDockWidget()

        self.dockSettings.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)

        self.dockSettings.setWidget(self.settings)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockSettings)

        self.dockGraph0 = QDockWidget("График 0")
        self.dockGraph1 = QDockWidget("График 1")
        self.dockGraph0.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.dockGraph1.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)

        # настройки виджетов
        self.Chart0.setMinimumSize(300,200)
        self.Chart1.setMinimumSize(300,200)
        self.dockGraph0.setWidget(self.Chart0)
        self.dockGraph1.setWidget(self.Chart1)

        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph0)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph1)
        
        self.StartSopClamp.ConnectFrom(self.settings.StartStopClamp)
        self.StartSopClamp.HandleWithReceive(self.StartStop)
        self.SignalTypeClamp.HandleWithReceive(self.getSignalType)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.Process_2)

        self.settings.xRangeClamp.ConnectTo(self.Chart1.rangeClamp)
        self.settings.yRangeClamp.ConnectTo(self.Chart0.rangeClamp)
        self.settings.SignalTypeClamp.ConnectTo(self.SignalTypeClamp)

        self.settings.deviceComboBox.currentTextChanged.connect(self.deviceUpdate)
        self.settings.SampleRateLineEdit.LineEdit.Text.ConnectTo(self.Tranciver.FsClamp)
        self.settings.infoLabel.TextClamp.ConnectFrom(self.Tranciver.ErrorClamp)
        self.settings.downSamplLineEdit.LineEdit.Text.HandleWithSend(self.setDownSample)
        self.settings.IntervalLineEdit.LineEdit.Text.HandleWithSend(self.timer.setInterval)

    def StartStop(self,start_stop):
        print(start_stop)
        if start_stop:
            self.settings.DeviceSettingsGroupBox.setEnabled(False)
            self.Chart0.clearPlots(True)
            self.Tranciver.working = True
            self.worker_1  = Worker(self.Tranciver.run_realtime)
            self.threadpool.start(self.worker_1) # получение данных с микрофона
            self.timer.start()
            self.fristQue = True
        else:
            self.settings.DeviceSettingsGroupBox.setEnabled(True)
            self.Tranciver.working = False
            self.timer.stop()
            with self.Tranciver.received_signal.mutex: self.Tranciver.received_signal.queue.clear()
            self.threadpool.clear()
            # saving data from the queue
            while not self.save_signal.empty():
                QtWidgets.QApplication.processEvents()
                self.wav_data=np.append(self.wav_data, self.save_signal.get())

    def Process_2(self):
        self.c = 0
        specdata=np.array([])
        QtWidgets.QApplication.processEvents()
        if not self.Tranciver.received_signal.empty(): 
            currentData = np.concatenate(self.Tranciver.received_signal.get_nowait())
            a=currentData[::self.downSample]
            if self.fristQue:
                xMax = len(currentData)
                self.settings.xMax.spinBox.setMaximum(xMax)
                self.settings.xMax.spinBox.setValue(xMax)
                self.settings.xMin.spinBox.setValue(0)
                self.Chart1.setRangeX([0,xMax])
                self.Chart1.nPerseg = xMax
                self.Chart1.nfft = 2*xMax
                self.fristQue = False
            self.Chart1.specImage(currentData)
            self.Chart0.plotData(a)
            self.save_signal.put(currentData)

    def saveFile(self):
        filename = self._saveFileDialog('Сохранение сигнала')
        write(filename+'_'+self.signalType.name+'_'+self.getCurDateTime()+".wav", int(self.Tranciver.samplerate), self.wav_data.astype(np.float32))
        self.wav_data = np.array([])
        QMessageBox.information(self,'Сохранение данных', 'Сохранено')

    def loadFile(self):
        fileName, filter = QFileDialog.getOpenFileName()
        if fileName!='':
            if fileName[-4:]!='.wav':
                QMessageBox.warning(self,'Таблица','Неподходящий файл',QMessageBox.Ok)
            else:
                samplerate, data = wavfile.read(fileName)
                print('Loaded')

    def getCurDateTime(self):
        now = datetime.now()
        current_date_time = str(now.year)+str(now.month)+str(now.day)+'_'+str(now.hour)+str(now.minute)+str(now.second)
        return current_date_time

    def getSignalType(self,SignalType):
        self.signalType=SignalType
    
    def setDownSample(self,value):
        self.downSample = value

    def _saveFileDialog(self,text):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,text,"","All Files (*);;wav files (*.wav)", options=options)
        return fileName

    def deviceUpdate(self,deviceName):
        self.Tranciver.device=self.settings.deviceComboBox.currentIndex()+1

    def _createMenubar(self):
        menuBar = self.menuBar()
        MainWindowMenuBar = menuBar.addMenu("&Файл")
        MainWindowMenuBar.addAction(self.saveAction)
        MainWindowMenuBar.addAction(self.loadAction)

    def _createActions(self):
        self.saveAction = QAction("&Сохранить",self)
        self.loadAction = QAction("&Загрузить",self)
    
    def _connectActions(self):
        self.saveAction.triggered.connect(self.saveFile)
        self.loadAction.triggered.connect(self.loadFile)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())