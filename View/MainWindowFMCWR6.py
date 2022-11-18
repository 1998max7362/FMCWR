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
import queue

from SettingsFMCWRv3 import SettingsWindow
from mainWaterfall import WaterFallWindow
from mainGraph import GraphWindow
from Clamp import Clamp
from Worker import *
from TestTransiver import TestTranciver
from SignalSource import SignalSource
from Transceiver import Transceiver
# from TestTranciever import Transceiver
from WrapedUiElements import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Главное меню')
        self.y = np.array([])
        self.threadpool = QThreadPool()

        self._createActions()
        self._connectActions()
        self._createMenubar()

        #  Signal Settings
        fs = 44100
        segment = 200 # ms

        # Tranciever
        self.Tranciver = Transceiver()
        self.Tranciver.setDevice(0)             # choose device with hostapi = 0
        self.Tranciver.setChannels(1)           # set number of input channels
        self.Tranciver.setFs(fs) 
        self.Tranciver.window = segment

        # Graph window settings
        self.Chart0 = GraphWindow()
        self.Chart1 = WaterFallWindow()
        self.Chart1.set_fs(fs)
        self.Chart1.set_tSeg(segment)
        self.Chart1.nPerseg = 1136 # НЕПОНЯТНО TODO
        self.Chart1.nfft = 100*1136 # НЕПОНЯТНО TODO

        #  Add Clamps
        self.StartSopClamp = Clamp()
        self.PauseResumeClamp = Clamp()

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
        self.PauseResumeClamp.ConnectFrom(self.settings.PauseResumeClamp)
        self.PauseResumeClamp.HandleWithReceive(self.PauseResume)



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

    def StartStop(self,start_stop):
        print(start_stop)
        if start_stop:
            self.Tranciver.working = True
            self.worker_1  = Worker(self.Tranciver.run_realtime)
            self.worker_2  = Worker(self.Process_2)
            self.worker_3  = Worker(self.Process_3)
            self.threadpool.start(self.worker_1)
            self.threadpool.start(self.worker_2)
            self.threadpool.start(self.worker_3)
        else:
            self.Tranciver.working = False
    
    def PauseResume(self, pause_resume):
        print(pause_resume)
    
    def Process_2(self):
        while self.Tranciver.working:
            QtWidgets.QApplication.processEvents()
            try:
                currentData = self.Tranciver.received_signal.get_nowait()
                # a = currentData # for testTranciever
                a = np.concatenate(currentData)
                self.Chart1.specImage(a)
            except queue.Empty:
                    break    

    def Process_3(self):
        # self.Chart0.clearPlots(True)
        c = 0
        while self.Tranciver.working:
            QtWidgets.QApplication.processEvents()
            try:
                currentData = self.Tranciver.received_signal.get_nowait()
                # a = currentData # for testTranciever
                a = np.concatenate(currentData)
                a=a[::10]
                for s in a:
                    QtWidgets.QApplication.processEvents()
                    c=c+1
                    self.Chart0.plotData([c,s])
            except queue.Empty:
                    break



if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())