import queue
import numpy as np
import time
from PyQt5 import QtCore, QtWidgets

class Transceiver():
    received_signal = queue.Queue()
    def __init__(self) -> None:
        self.working = False
    
    def run_realtime(self):
        t = np.arange(0, 1136, 1)*0.2
        sinewave = np.sin(2 * np.pi * self.fs * t)
        while self.working:
            # QtWidgets.QApplication.processEvents()
            self.received_signal.put(sinewave)
            time.sleep(0.2)

    
    def setFs(self,fs = 44100):
        self.fs = fs
    
    def setDevice(self, hostapi = 0):
        self.device = hostapi

    def setChannels(self,ch = 1):
        self.ch = ch