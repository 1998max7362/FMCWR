import sys, os
sys.path.insert(0, "././utils/compoents")
sys.path.insert(0, "././Model/")
sys.path.insert(0, "././View/")
sys.path.insert(0, "././Test/")
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
import queue
from scipy.io.wavfile import write
from scipy.io import wavfile
from datetime import datetime

from SettingsWindowReciever import SettingsWindowReciever
from SettingsWindowTransmitter import SettingsWindowTransmitter
from mainWaterfall import WaterFallWindow
from mainGraph import GraphWindow
from Clamp import Clamp
from Worker import *
from SignalSource import SignalSource
from Reciever import Reciever
from WrapedUiElements import *
from Transmitter import Transmitter
from Tranciever import Tranciever

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.recievedSignalQueueForSave = queue.Queue()

        self.setWindowTitle('Главное меню')
        layout = QHBoxLayout(self)

        self.tranciever = Tranciever()
        self.settingsWindowReciever = SettingsWindowReciever()
        self.settingsWindowTransmitter = SettingsWindowTransmitter()
        self.Chart0 = GraphWindow()
        self.Chart1 = WaterFallWindow()
        self.chartUpdateTimer = QtCore.QTimer()
        
        self.Chart0.setMinimumSize(300,200)
        self.Chart1.setMinimumSize(300,200)


        # Dock Widgets
        self.dockSettingsWindowReciever = QDockWidget()
        self.dockSettingsWindowReciever.setWindowTitle('Приёмник')
        self.dockSettingsWindowReciever.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.dockSettingsWindowReciever.setWidget(self.settingsWindowReciever)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockSettingsWindowReciever)

        self.dockSettingsWindowTransmitter = QDockWidget()
        self.dockSettingsWindowTransmitter.setWindowTitle('Передатчик')
        self.dockSettingsWindowTransmitter.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.dockSettingsWindowTransmitter.setWidget(self.settingsWindowTransmitter)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockSettingsWindowTransmitter)

        self.tabifyDockWidget(self.dockSettingsWindowTransmitter, self.dockSettingsWindowReciever)

        self.dockChart0 = QDockWidget("Осциллограмма ")
        self.dockChart0.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.dockChart0.setWidget(self.Chart0)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockChart0)

        self.dockChart1 = QDockWidget("Спектрограмма ")
        self.dockChart1.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.dockChart1.setWidget(self.Chart1)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockChart1)

        # Set initial values
        self.tranciever.setSignalType(self.settingsWindowTransmitter.currentSignalType) 
        self.tranciever.setSignalPeriod(self.settingsWindowTransmitter.currentPeriod) 
        self.tranciever.setOutputDevice(self.settingsWindowTransmitter.currentOutputDevice) 
        self.tranciever.setInputDevice(self.settingsWindowReciever.currentInputDevice)
        self.tranciever.setSamplerate(self.settingsWindowReciever.currentSampleRate) 
        self.setSignalSource(self.settingsWindowReciever.currentSignalSource)
        self.setDownSampling(self.settingsWindowReciever.currentDownSampling)
        self.chartUpdateTimer.setInterval(self.settingsWindowReciever.currentUpdateInterval)
        self.Chart0.setRangeY(self.settingsWindowReciever.currentYRange)
        self.Chart0.setMaxRangeX(self.tranciever.blockSize*10)
        self.Chart1.setRangeX(self.settingsWindowReciever.currentXRange)
        self.Chart1.set_fs(self.settingsWindowReciever.currentSampleRate)
        self.Chart1.set_tSeg(self.settingsWindowTransmitter.currentPeriod)

        # Set connections
        self.settingsWindowReciever.inputDeviceChanged.connect(self.tranciever.setInputDevice)
        self.settingsWindowReciever.startToggled.connect(self.runStop)
        self.settingsWindowReciever.sampleRateChanged.connect(self.tranciever.setSamplerate)
        self.settingsWindowReciever.updateIntervalChanged.connect(self.setChartUpdateInterval)
        self.settingsWindowReciever.signalSourceChanged.connect(self.setSignalSource)
        self.settingsWindowReciever.downSamplingChanged.connect(self.setDownSampling)
        self.settingsWindowReciever.downSamplingChanged.connect(self.Chart1.set_fs)
        self.settingsWindowReciever.yRangeChanged.connect(self.Chart0.setRangeY)
        self.settingsWindowReciever.xRangeChanged.connect(self.Chart1.setRangeX)
        self.tranciever.errorAppeared.connect(self.settingsWindowReciever.setErrorText)
        self.settingsWindowTransmitter.signalTypeChanged.connect(self.tranciever.setSignalType)
        self.settingsWindowTransmitter.signalPeriodChanged.connect(self.tranciever.setSignalPeriod)
        self.settingsWindowTransmitter.signalPeriodChanged.connect(self.Chart1.set_tSeg)
        self.settingsWindowTransmitter.outputDeviceChanged.connect(self.tranciever.setOutputDevice)
        self.chartUpdateTimer.timeout.connect(self.updateCharts)

    def updateCharts(self):
        indata = self.tranciever.recievedSignal.get()
        downSampledIndata = indata[::self.downSampling]
        self.Chart0.plotData(downSampledIndata)
        self.Chart1.specImage(indata)
        # print('update')

    def runStop(self, state):
        if state:
            self.settingsWindowTransmitter.setEnabled(False)
            self.Chart0.clearPlots(True) 
            self.chartUpdateTimer.start()
            self.tranciever.run()
        else:
            self.settingsWindowTransmitter.setEnabled(True)
            self.chartUpdateTimer.stop()
            self.tranciever.stop()

    def setChartUpdateInterval(self,value):
        self.chartUpdateTimer.setInterval(value)
    
    def setSignalSource(self, value):
        self.signalSource = value
    
    def setDownSampling(self, value):
        self.downSampling = value


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())