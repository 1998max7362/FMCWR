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

        # Set initial values
        self.tranciever.setSignalType(self.settingsWindowTransmitter.currentSignalType) 
        self.tranciever.setSignalPeriod(self.settingsWindowTransmitter.currentPeriod) 
        self.tranciever.setOutputDevice(self.settingsWindowTransmitter.currentOutputDevice) 
        self.tranciever.setInputDevice(self.settingsWindowReciever.currentInputDevice)
        self.tranciever.setSamplerate(self.settingsWindowReciever.currentSampleRate) 

        self.graphUpdateInterval = self.settingsWindowReciever.currentUpdateInterval
        self.signalSource = self.settingsWindowReciever.currentSignalSource
        self.downSampling = self.settingsWindowReciever.currentDownSampling 
        # = self.settingsWindowReciever.currentYRange
        # = self.settingsWindowReciever.currentXRange

        self.initConnections()

    def runStop(self, state):
        if state:
            self.tranciever.run()
        else:
            self.tranciever.stop()

    def initConnections(self):
        self.settingsWindowReciever.inputDeviceChanged.connect(self.tranciever.setInputDevice)
        self.settingsWindowReciever.startToggled.connect(self.runStop)
        self.settingsWindowReciever.sampleRateChanged.connect(self.tranciever.setSamplerate)
        # settingsWindowReciever.updateIntervalChanged.connect(self.Tranciever.)
        # settingsWindowReciever.signalSourceChanged.connect(self.Tranciever.set)
        # self.settingsWindowReciever.downSamplingChanged.connect(self.Tranciever.)
        # self.settingsWindowReciever.yRangeChanged.connect(self.Tranciever.)
        # self.settingsWindowReciever.xRangeChanged.connect(self.Tranciever.)
        self.tranciever.errorAppeared.connect(self.settingsWindowReciever.setErrorText)
        self.settingsWindowTransmitter.signalTypeChanged.connect(self.tranciever.setSignalType)
        self.settingsWindowTransmitter.signalPeriodChanged.connect(self.tranciever.setSignalPeriod)
        self.settingsWindowTransmitter.outputDeviceChanged.connect(self.tranciever.setOutputDevice)

    def setGraphUpdateInterval(self,value):
        self.graphUpdateInterval = value

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())