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

        self.Tranciever = Tranciever()
        settingsWindowReciever = SettingsWindowReciever()
        settingsWindowTransmitter = SettingsWindowTransmitter()

        


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())