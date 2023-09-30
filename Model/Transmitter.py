import sys
sys.path.insert(0, "././utils/constants")
import numpy as np
import sounddevice as sd
import soundfile as sf
from PyQt5.QtCore import QObject, pyqtSignal
import queue
from SignalType import SignalType
from PyQt5 import QtWidgets
import math


class Transmitter(QObject):
    readyRead = pyqtSignal(object)
    errorAppeared = pyqtSignal(object)
    def __init__(self):
        super().__init__()

        self.isPlaying = True

        self.outputDeviceId = 4
        self.signalType = SignalType.SINE # форма сигнала
        self.signalPeriod = 1 # период сигнала в мс
        self.samplerate = 44100 # частота дискретизации Гц
        print(self.samplerate)

        self.blockSize = self.getBlockSize()
        self.scale = np.arange(self.blockSize) / (self.blockSize - 1) # шкала x
        self.signal = self.generateSignal() # сформированные отсчёты 1-го периода сигнала
        self.blksize=self.blockSize

        # self.transmittedSignal = queue.Queue()

    def setSignalType(self, type):
        self.signalType = type
        print(type)
    
    def setSignalPeriod(self, period):
        self.signalPeriod = period
        print(period)
    
    def setOutputDevice(self, deviceId):
        self.outputDeviceId = deviceId
        print(deviceId)
    
    def setSamplerate(self, samplerate):
        self.samplerate = samplerate
        print(samplerate)

    def getBlockSize(self):
        T = self.signalPeriod/1000 # из мс в с
        blockSize = int(T*self.samplerate) # кол-во отсчетов в блоке (одном периоде сигнала)
        return  blockSize

    def generateSignal(self):
        match self.signalType:
            case SignalType.TRIANGLE:
                if self.scale.size%2==0:
                    firstHalfScale, secondHalfScale = np.split(self.scale, 2)
                else:
                    print(math.ceil(self.scale.size/2))
                    firstHalfScale = self.scale[0:math.ceil(self.scale.size/2)]
                    secondHalfScale = self.scale[0:math.floor(self.scale.size/2)]
                signalOne = -1 + 4 * firstHalfScale
                signalTwo = 1 - 4 * secondHalfScale
                signal = np.concatenate((signalOne, signalTwo), axis=0)
                return signal.reshape(-1, 1)
            case SignalType.SAWTOOTH_FRONT:
                signal = -1 + 2 * self.scale
                return signal.reshape(-1, 1)
            case SignalType.SAWTOOTH_REVERSE:
                signal = 1 - 2 * self.scale
                return signal.reshape(-1, 1)
            case SignalType.SINE:
                signal = np.sin(2 * np.pi * self.scale )
                return signal.reshape(-1, 1)

    def startStop(self):
        self.isPlaying = ~self.isPlaying

    def runRealtime(self):
        print('start')
        try:
            stream = sd.OutputStream(device=self.outputDeviceId,
                samplerate=self.samplerate,
                blocksize=self.blockSize,
                # channels=1,
                callback=self.callback)
            
            with stream:
                while self.isPlaying:
                    QtWidgets.QApplication.processEvents()
        except Exception as e:
            print(e)
            self.errorAppeared.emit(e)
    #     # stream.start()
    #     with sd.Stream(device=(1, 4),
    #         samplerate=44000,
    #         blocksize=1200,
    #         # dtype="int16",
    #         channels=(1,2),
    #         callback=self.callback_fun):
    #         print('#' * 80)
    #         print('press Return to quit')
    #         print('#' * 80)
    #         input()
    #     print()

        # while self.isPlaying:
        #     sd.play(self.signal)
        #     sd.wait()
        # try:
        #     def callback(outdata, frames, time, status):
        #         outdata[:] = self.signal
        #         start_idx += frames

            # with sd.OutputStream(device=self.device, channels=2, callback=callback, samplerate=self.samplerate):
        #         print('#' * 80)
        #         print('press Return to quit')
        #         print('#' * 80)
        #         input()
        # except Exception as e:
        #     print(e)

    def callback(self, outdata, time, status, frames):
        # if status: 
        #     print(status) 
        outdata[:] = self.signal.reshape(-1, 1)
        # self.transmittedSignal.put(outdata)



if __name__ == '__main__':

    transmitter = Transmitter()
    transmitter.runRealtime()
    
