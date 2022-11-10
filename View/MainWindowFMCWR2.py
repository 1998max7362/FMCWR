import sys
sys.path.insert(0, "././Core/")
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import *

from SettingsFMCWRv3 import SettingsWindow
from mainWaterfall import WaterFallWindow
from mainGraph import GraphWindow
from Clamp import Clamp
from Worker import CountingWorker, Worker
from TestTransiver import TestTranciver
from SignalSource import SignalSource
from WrapedUiElements import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Главное меню')
        self.threadpool = QThreadPool()

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
        self.Tranciver = TestTranciver()

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
        # self.outputClamp.ConnectTo(self.Chart1.input)


    def SendPeriod(self,Period):
        self.Tranciver.T = Period*1e-3
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
            self.settings.PauseResumeButton.setEnabled(True)
            if self.source == SignalSource.TRANSMITTER:
                self.worker_1 = CountingWorker(self.Tranciver.Transmit)
            if self.source == SignalSource.RECIEVER:
                self.worker_1 = CountingWorker(self.Tranciver.Reciev)   
            self.worker_1.signals.result.connect(self.sigSent)
            self.threadpool.start(self.worker_1)
        else:
            self.settings.PauseResumeButton.toState(ToggleButtonState.NOT_CLICKED)
            self.settings.PauseResumeButton.setEnabled(False)
            self.worker_1.kill()

    def sigSent(self,sig):
        self.outputClamp.Send(sig)
    
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