import sys
sys.path.insert(0, "././utils/constants")
sys.path.insert(0, "././utils/components")
import numpy as np
import sounddevice as sd
from SignalType import SignalType
import math
import multiprocessing as mp
import threading as th

class Tranciever():
        def __init__(self):
            super().__init__()

            self.isWorking = False

            # Параметры сигнала
            self.signalType = SignalType.TRIANGLE # форма сигнала
            self.signalPeriod = 1 # период сигнала в мс

            # Параметры устройств ввода-вывода
            self.outputDeviceId = 4
            self.inputDeviceId = 2
            self.samplerate = 44100 # частота дискретизации Гц
            
            self.blockSize = self.getBlockSize()
            self.scale = np.arange(self.blockSize) / (self.blockSize - 1) # шкала x
            self.signal = self.generateSignal() # сформированные отсчёты 1-го периода сигнала

            self.recievedSignal = mp.Queue(maxsize=5) # Очередь для записи принятого сигнала
            self.transmittedSignal = mp.Queue(maxsize=5) # Очередь для записи излученного сигнала


        def generateSignal(self):
            match self.signalType:
                case SignalType.TRIANGLE:
                    if self.scale.size%2==0:
                        firstHalfScale, secondHalfScale = np.split(self.scale, 2)
                    else:
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
                
        def updateSignal(self):
            self.blockSize = self.getBlockSize()
            self.scale = np.arange(self.blockSize) / (self.blockSize - 1) # шкала x
            self.signal = self.generateSignal()
        
        def getBlockSize(self):
            T = self.signalPeriod/1000 # из мс в с
            blockSize = int(T*self.samplerate) # кол-во отсчетов в блоке (одном периоде сигнала)
            return  blockSize
        
        def stop(self):
            self.isWorking = False
        
        def runProcess(self):
            p = mp.Process(target = self.run)
            p.start()

        def run(self):
            self.isWorking=True
            try:
                stream = sd.Stream(
                    device=(self.inputDeviceId, self.outputDeviceId),
                    samplerate=self.samplerate,
                    blocksize=self.blockSize,
                    channels=(1,1),
                    callback=self.callback)
                with stream:
                    while self.isWorking:
                        pass
            except Exception as e:
                print(type(e).__name__ + ': ' + str(e))
        
        def callback(self, indata, outdata, frames, time, status):
            if status:
                print(status)
            outdata[:] = self.signal
            if self.transmittedSignal.full(): #Чистим очередь, если она переполняется
                self.transmittedSignal.get() # записываем в очеред излученный сигнал
            if self.recievedSignal.full(): #Чистим очередь, если она переполняется
                self.recievedSignal.get() # записываем в очеред принятый сигнал
            self.transmittedSignal.put(outdata[:]) # записываем в очеред излученный сигнал
            self.recievedSignal.put(indata[:]) # записываем в очеред принятый сигнал
        
        def setSignalType(self, type):
            self.signalType = type
            self.updateSignal()

        def setSignalPeriod(self, period):
            self.signalPeriod = period
            self.updateSignal()

        def setSamplerate(self, samplerate):
            self.samplerate = samplerate
            self.updateSignal()

        def setOutputDevice(self, deviceId):
            self.outputDeviceId = deviceId

        def setInputDevice(self, deviceId):
            self.inputDeviceId = deviceId



if __name__ == '__main__':
    tranciever = Tranciever()
    tranciever.runProcess()
    # tranciever.run()
