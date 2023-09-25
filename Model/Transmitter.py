import numpy as np
import sounddevice as sd
import soundfile as sf


class Trasmitter():
    def __init__(self):
        self.isPlaying = False
        self.device = 0
        self.signalInit()

    def signalInit(self):
        duration = 1  # длительность сигнала сек
        frequency = 1000  # частота Гц
        self.samplerate = 44100  # битрейт
        amp = 10000  # амплитуда

        t = np.arange(duration * self.samplerate) / self.samplerate
        self.signal = amp*np.sin(2 * np.pi * frequency * t)

    def getAudioDevices(self):
        devices = sd.query_devices(kind='output')
        print(devices)
        return (devices)

    def setDevice(self, hostapi):
        self.device = hostapi

    def startStop(self):
        self.isPlaying = ~self.isPlaying

    def runRealtime(self):
        # while self.isPlaying:
        #     sd.play(self.signal)
        #     sd.wait()
        dev = sd.query_devices(kind='output')
        try:
            def callback(outdata, frames, time, status):
                outdata[:] = self.signal
                start_idx += frames

            with sd.OutputStream(device=self.device, channels=2, callback=callback, samplerate=self.samplerate):
                print('#' * 80)
                print('press Return to quit')
                print('#' * 80)
                input()
        except Exception as e:
            print(e)


if __name__ == '__main__':

    transmitter = Trasmitter()
    transmitter.getAudioDevices()
    transmitter.startStop()
    transmitter.runRealtime()
