import numpy as np
import scipy as sp
import sys
sys.path.insert(0, "././Core/")
from Clamp import Clamp
from PyQt5.QtCore import QTimer

class Transmitter():
    def __init__(self):
        # Демо режим
        self.demo = Clamp()
        self.timer = QTimer()
        self.i = 0 # счетчик
        self.fs = 192e3/100
        self.dt = 1/self.fs
        # Выводы передатчика
        self.output = Clamp()
        self.input = Clamp()
        # Действия при получении данных
        self.demo.HandleWithReceive(self.demoReceived, self.setTimer)
        self.input.HandleWithReceive(self.startReceived, self.startTransmit)

    # методы класса
    def demoReceived(self, data: bool):
        self.demo.ReceivedValue = data

    def setTimer(self, data: bool):
        if self.demo.ReceivedValue:
            self.timer.setInterval(self.dt*1000)
            self.timer.timeout.connect(self.demoTransmit)
        else:
            pass

    def startReceived(self, data: bool):
        self.input.ReceivedValue = data

    def startTransmit(self, data: bool):
        while(self.input.ReceivedValue):
            if self.demo.ReceivedValue:
                if (self.i == 0):
                    self.timer.start()
                else:
                    pass
            else:
                self.timer.stop()
                pass
        self.i = 0

    def demoTransmit(self):
        dt = self.dt
        pi = np.pi
        m = 0.3
        f0 = 40e3
        f1 = 5e3
        Un = 100
        # init timer
        testSig = Un*(1+m*np.cos(2*pi*f1*dt,dtype='complex128'))*np.cos(2*pi*f0*dt, dtype='complex128')
        self.i += 1
        self.output.Send(testSig)
