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

from SettingsWindowRecieverV2 import SettingsWindowReciever
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

        self.tranciever = Tranciever()
        self.settingsWindowReciever = SettingsWindowReciever()
        self.settingsWindowTransmitter = SettingsWindowTransmitter()
        
        self.graphUpdateInterval = self.settingsWindowReciever.currentUpdateInterval
        self.signalSource = self.settingsWindowReciever.currentSignalSource
        self.downSampling = self.settingsWindowReciever.currentDownSampling 


    def initConnections(self):
        self.settingsWindowReciever.inputDeviceChanged.connect(self.Tranciever.setInputDevice)
        # settingsWindowReciever.startToggled.connect(self.Tranciever.)
        self.settingsWindowReciever.sampleRateChanged.connect(self.Tranciever.setSamplerate)
        # settingsWindowReciever.updateIntervalChanged.connect(self.Tranciever.)
        # settingsWindowReciever.signalSourceChanged.connect(self.Tranciever.set)
        # self.settingsWindowReciever.downSamplingChanged.connect(self.Tranciever.)
        # self.settingsWindowReciever.yRangeChanged.connect(self.Tranciever.)
        # self.settingsWindowReciever.xRangeChanged.connect(self.Tranciever.)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())