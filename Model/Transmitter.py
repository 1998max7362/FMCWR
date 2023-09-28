import sys
sys.path.insert(0, "././utils/constants")
import numpy as np
import sounddevice as sd
import soundfile as sf
from PyQt5.QtCore import QObject, pyqtSignal
import queue
from SignalType import SignalType


class Transmitter(QObject):
    readyRead = pyqtSignal(object)
    errorAppeared = pyqtSignal(object)
    def __init__(self):
        super().__init__()

        self.isPlaying = True

        self.outputDeviceId = 4
        self.signalType = SignalType.SINE # форма сигнала
        self.signalPeriod = 100 # период сигнала в мс
        self.samplerate = 44100 # частота дискретизации Гц
        print(self.samplerate)

        self.createSignal()
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

    def createSignal(self):
        T = self.signalPeriod/1000 # из мс в с
        self.blksize = int(T*self.samplerate) # кол-во отсчетов в блоке
        self.scale = np.arange(self.blksize) / (self.blksize - 1) # шкала x
        print()
        match self.signalType:
            case SignalType.TRIANGLE:
                halfScale, _ = np.split(self.scale, 2)
                signalOne = -1 + 4 * halfScale
                signalTwo = 1 - 4 * halfScale
                self.signal = np.concatenate((signalOne, signalTwo), axis=0)
            case SignalType.SAWTOOTH_FRONT:
                self.signal = -1 + 2 * self.scale
            case SignalType.SAWTOOTH_REVERSE:
                self.signal = 1 - 2 * self.scale
            case SignalType.SINE:
                self.signal = np.sin(2 * np.pi * self.scale )

    def startStop(self):
        self.isPlaying = ~self.isPlaying

    def runRealtime(self):
        print('start')
        try:
            stream = sd.OutputStream(device=self.outputDeviceId,
                samplerate=self.samplerate,
                blocksize=self.blksize,
                # channels=1,
                callback=self.callback)
            
            with stream:
                while self.isPlaying:
                    pass
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
    
