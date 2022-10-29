# this file contains class as a driver to audiodevice
# python-sounddevice module has to be installed first

import sounddevice as sd
import numpy as np
import queue
import sys

class Transceiver():
    """ This class is a wrapper to sounddevice object 
    providing control over input and output
    """
    # class properties
    transmitted_signal = np.array([])
    received_signal = queue.Queue

    # methods
    def __init__(self) -> None:
        #instance properties
        self.fs = None

    def setFs(self,fs = 44100):
        self.fs = fs
    
    def getAudioDevices(self):
        return sd.query_devices(kind='input')
    
    def setTransmittedSignal(self,pattern):
        pass

    def recorder_callback(self,indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        # Fancy indexing with mapping creates a (necessary!) copy:
        self.received_signal.put(indata[:, 0])

    def run(self,devid):
        # check if fs set or not
        if self.fs == None:
            device_info = sd.query_devices(kind='input')
            self.fs = device_info['default_samplerate']
        
        # create input stream
        try:
            stream = sd.InputStream(
            device=devid, channels=1,
            samplerate=self.fs, callback=self.recorder_callback)
            with stream:
                pass
        except Exception as e:
            print(type(e).__name__ + ': ' + str(e))

if __name__ == "__main__":
    tr = Transceiver()
    print(tr.getAudioDevices())
    tr.run(0)
    