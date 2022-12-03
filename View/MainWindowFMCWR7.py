import sys
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
        self.fname="test"
        self.save_signal = queue.Queue()
        self.wav_data=np.array([])
        self.setWindowTitle('Главное меню')
        self.y = np.array([])
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
        self.Chart1.nPerseg = 1136 # НЕПОНЯТНО TODO
        self.Chart1.nfft = 2*1136 # НЕПОНЯТНО TODO

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
        # self.settings.downSamplLineEdit.LineEdit.Text.ConnectTo(self.Tranciver.downSampleClamp) # не нужно
        self.settings.IntervalLineEdit.LineEdit.Text.HandleWithSend(self.timer.setInterval)
    
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

    def StartStop(self,start_stop):
        print(start_stop)
        if start_stop:
            self.settings.DeviceSettingsGroupBox.setEnabled(False)
            self.Chart0.clearPlots(True)
            self.Tranciver.working = True
            self.worker_1  = Worker(self.Tranciver.run_realtime)
            self.threadpool.start(self.worker_1) # получение данных с микрофона
            self.timer.start()
        else:
            self.settings.DeviceSettingsGroupBox.setEnabled(True)
            self.Tranciver.working = False
            self.timer.stop()
            with self.Tranciver.received_signal.mutex: self.Tranciver.received_signal.queue.clear()
            self.threadpool.clear()
            # saving data from the queue
            while not self.save_signal.empty(): 
                self.wav_data=np.append(self.wav_data, self.save_signal.get())

            # todo : use checkbox to save current queue or all queue since program start (continues)
            # now save only data pushed start|stop button
            try:
                # write("Data/"+self.getCurTime()+"_"+self.signalType.name+".wav", int(self.Tranciver.samplerate), self.wav_data.astype(np.float32))
                write("lab0312/"+self.fname+self.signalType.name+".wav", int(self.Tranciver.samplerate), self.wav_data.astype(np.float32))
                self.wav_data = np.array([])
            except:
                print('Possible Data folder doesnt exist. Trying save it in current folder. \n')
                # write(self.getCurTime()+"_"+self.signalType.name+".wav", int(self.Tranciver.samplerate), self.wav_data.astype(np.float32))
                write("lab0312/"+self.fname+self.signalType.name+".wav", int(self.Tranciver.samplerate), self.wav_data.astype(np.float32))
                self.wav_data = np.array([])

    def loadData(self):
        samplerate, data = wavfile.read('Data/example.wav')
        pass

    def getCurTime(self):
        now = datetime.now()
        current_time = now.strftime("%H_%M_%S")
        return current_time

    def getSignalType(self,SignalType):
        self.signalType=SignalType

    def Process_2(self):
        self.c = 0
        specdata=np.array([])
        QtWidgets.QApplication.processEvents()
        if not self.Tranciver.received_signal.empty(): 
            currentData = np.concatenate(self.Tranciver.received_signal.get_nowait())
            a=currentData[::10] #TODO убрать это
            specdata=np.append(specdata,currentData)
            if len(specdata)*3==1136*3:
                self.Chart1.specImage(currentData)
                specdata=np.array([])
            # a=currentData
            self.Chart0.plotData(a)
            self.save_signal.put(currentData)

    def saveFile(self):
        print('save')

    def loadFile(self):
        print('load')


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())