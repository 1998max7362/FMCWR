import sys
sys.path.insert(0, "././Core/")
sys.path.insert(0, "././SignalProcessing/")
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
import time

from SettingsFMCWRv3 import SettingsWindow
from mainWaterfall import WaterFallWindow
from mainGraph import GraphWindow
from Clamp import Clamp
from Worker import CountingWorker, Worker
from TestTransiver import TestTranciver
from SignalSource import SignalSource
from Transceiver import Transceiver
from WrapedUiElements import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Главное меню')
        self.threadpool = QThreadPool()
        self.y = np.array([])
        self.fl = True

        self._createActions()
        self._connectActions()
        self._createMenubar()

        # вывод главного блока
        self.StartSopClamp = Clamp()
        self.outputClamp = Clamp()
        self.SignalSourceClamp = Clamp()
        self.PauseResumeClamp = Clamp()

        # разметка
        layout = QHBoxLayout(self)
        # добавление виджетов
        self.settings = SettingsWindow()
        self.dockSettings = QDockWidget()
        # self.Tranciver = TestTranciver()
        self.RealTranciver = Transceiver()
        self.RealTranciver.setDevice(0)             # choose device with hostapi = 0
        self.RealTranciver.setChannels(1)           # set number of input channels
        self.RealTranciver.setFs(45100.0) 

        self.dockSettings.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)

        self.dockSettings.setWidget(self.settings)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockSettings)

        self.dockGraph0 = QDockWidget("График 0")
        self.dockGraph1 = QDockWidget("График 1")
        self.dockGraph0.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.dockGraph1.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.Chart0 = GraphWindow()
        self.Chart1 = WaterFallWindow()
        # настройки виджетов
        self.Chart0.setMinimumSize(300,200)
        self.Chart1.setMinimumSize(300,200)
        self.dockGraph0.setWidget(self.Chart0)
        self.dockGraph1.setWidget(self.Chart1)

        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph0)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph1)
        
        #  Clamps connections
        self.settings.Period.LineEdit.Text.HandleWithSend(self.SendPeriod)
        self.StartSopClamp.ConnectFrom(self.settings.StartStopClamp)
        self.StartSopClamp.HandleWithReceive(self.StartStop)
        self.SignalSourceClamp.ConnectFrom(self.settings.SignalSourceSwitchClamp)
        self.SignalSourceClamp.HandleWithReceive(self.SwitchSource)
        self.PauseResumeClamp.ConnectFrom(self.settings.PauseResumeClamp)
        self.PauseResumeClamp.HandleWithReceive(self.PauseResume)
        
        self.SwitchSource(SignalSource.TRANSMITTER)

        self.outputClamp.ConnectTo(self.Chart0.input)
        self.clearClamp = Clamp()
        self.clearClamp.ConnectTo(self.Chart0.clearClamp)
        # self.outputClamp.ConnectTo(self.Chart1.input)


    def SendPeriod(self,Period):
        # self.Tranciver.T = Period*1e-3
        print(Period)

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

    def saveFile(self):
        print('save')
    
    def loadFile(self):
        print('load')

    # ЗАГЛУШКИ
    def SwitchSource(self,source):
        self.source = source
        if self.settings.isMeasuring:
            if self.worker_1.is_paused == False:
                self.worker_1.kill()
                self.StartStop(True)

    def StartStop(self,start_stop):
        if start_stop:
            self.Chart0.clearPlots(True)
            # self.RealTranciver.run_realtime(start_stop)
            self.RealTranciver.run_realtime(start_stop)
            self.worker_3 = Worker(self.RealTranciver.run_realtime, start_stop)
            self.worker_1 = Worker(self.readQueue)
            # self.Chart1.clearPlots(True)
            # self.clearClamp.Send(True)
        #     self.settings.PauseResumeButton.setEnabled(True)
        #     if self.source == SignalSource.TRANSMITTER:
        #         # self.worker_1 = CountingWorker(self.Tranciver.Transmit)
        #         self.worker_1 = Worker(self.RealTranciver.run_realtime, 0)
        #     if self.source == SignalSource.RECIEVER:
        #         # self.worker_1 = CountingWorker(self.Tranciver.Reciev)   
        #         pass
        #     self.worker_1.signals.result.connect(self.sigSent)
            self.threadpool.start(self.worker_1)
            self.threadpool.start(self.worker_3)
        else:
            self.RealTranciver.fl = False
        #     self.settings.PauseResumeButton.toState(ToggleButtonState.NOT_CLICKED)
        #     self.settings.PauseResumeButton.setEnabled(False)
        #     self.worker_1.kill()

    def readQueue(self):
        while True:
            if(self.RealTranciver.received_signal.empty()): 
                continue
            currentData = self.RealTranciver.received_signal.get()
            print(currentData)


    def sigSent(self,sig):
        self.outputClamp.Send(sig)
        self.y = np.append(self.y, sig[1])
        if self.fl:
            self.fl = False
            self.worker_2 = Worker(self.spectShow)
            self.threadpool.start(self.worker_2)
    
    def spectShow(self):
        while len(self.y)<194:
            time.sleep(0)
        else:
            self.Chart1.specImage(self.y[0:193])
            self.y = np.array([])
            
            
    
    def PauseResume(self,state):
        if state:
            self.worker_1.pause()
        else:
            self.worker_1.resume()





if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())