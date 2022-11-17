# this file contains class as a driver to audiodevice
# python-sounddevice module has to be installed first

import argparse
import queue
import sys
import time
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from matplotlib.animation import FuncAnimation


class Transceiver():
    """ This class is a wrapper to sounddevice object 
    providing control over input and output
    """
    # class properties
    transmitted_signal = np.array([])
    received_signal = queue.Queue()

    # prepare data for plot
    plotdata_signal = queue.Queue()
    plotdata = None
    lines = None

    parser = argparse.ArgumentParser(add_help=False)

    # methods
    def __init__(self) -> None:
        #instance properties
        self.working = False
        # input channels to plot (default: the first)
        self.channels = None
        # input device (numeric ID or substring)
        self.device = 0
        # visible time slot (default: 200 ms)
        self.window = 200
        # minimum time between plot updates (default: %30 ms)
        self.interval = 30
        # block size (in samples)
        self.blocksize = None
        # sampling rate of audio device
        self.samplerate = None
        # display every Nth sample (default: 10)
        self.downsample = 10
        # list of used channels
        self.mapping = None

    def setChannels(self,ch = 1):
        # manualy change number of channels
        # Channel numbers start with 1

        self.channels = []
        self.channels.append(ch)
        self.mapping = [c - 1 for c in self.channels]
    
    def setDevice(self, hostapi = 0):
        # set device hostapi
        self.device = hostapi

    def setFs(self,fs = 44100):
        # set device sample rate
        if self.samplerate == None:
            device_info = sd.query_devices(self.device, kind='input')
        show_defaults = device_info['default_samplerate']
        self.samplerate = float(fs)
        print('Default samplerate is ', show_defaults, ' set ',fs, '\n')

    def getAudioDevices(self):
        # show all input sounddevices
        return sd.query_devices(kind='input')

    def setTransmittedSignal(self,pattern):
        # do nothing
        pass

    def recplay_callback(self,indata, frames, time, status):
        # save data in query for saving
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        # Fancy indexing with mapping creates a (necessary!) copy:
        # print(indata[:, self.mapping])
        self.received_signal.put(indata[:, self.mapping])

    def run_realtime(self):
        # testbench to save data in query
        # create input stream
        try:
            stream = sd.InputStream(
                device=self.device, channels=max(self.channels),
                samplerate=self.samplerate, callback=self.recplay_callback)
            with stream:
                while self.working:
                    pass
        except Exception as e:
            print(type(e).__name__ + ': ' + str(e))

    def recplot_callback(self,indata, frames, time, status):
        # save downsampled data in quere to show
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        # Fancy indexing with mapping creates a (necessary!) copy:
        self.plotdata_signal.put(indata[::self.downsample, self.mapping])
        pass

    def update_plot(self,frame):
        # plt callback update frame
        """This is called by matplotlib for each plot update.
        Typically, audio callbacks happen more frequently than plot updates,
        therefore the queue tends to contain multiple blocks of audio data.
        """
        while True:
            try:
                data = self.plotdata_signal.get_nowait()
            except queue.Empty:
                break
            shift = len(data)
            self.plotdata = np.roll(self.plotdata, -shift, axis=0)
            self.plotdata[-shift:, :] = data
        for column, line in enumerate(self.lines):
            line.set_ydata(self.plotdata[:, column])
        return self.lines

    def run_plot(self):
        # testbench viewin data in matplotlib window
        try:
            length = int(self.window * self.samplerate / (1000 * self.downsample))
            self.plotdata = np.zeros((length, len(self.channels)))

            fig, ax = plt.subplots()
            self.lines = ax.plot(self.plotdata)
            if len(self.channels) > 1:
                ax.legend([f'channel {c}' for c in self.channels],
                loc='lower left', ncol=len(self.channels))
            ax.axis((0, len(self.plotdata), -1, 1))
            ax.set_yticks([0])
            ax.yaxis.grid(True)
            ax.tick_params(bottom=False, top=False, labelbottom=False,
                        right=False, left=False, labelleft=False)
            fig.tight_layout(pad=0)

            stream = sd.InputStream(
                device=self.device, channels=max(self.channels),
                samplerate=self.samplerate, callback=self.recplot_callback)
            ani = FuncAnimation(fig, self.update_plot, interval=self.interval, blit=True)
            with stream:
                plt.show()
            
        except Exception as e:
            self.parser.exit(type(e).__name__ + ': wow ' + str(e))

if __name__ == "__main__":
    tr = Transceiver()          # create object
    a = tr.getAudioDevices()
    print(tr.getAudioDevices()) # show all mic devices
    tr.setDevice(0)             # choose device with hostapi = 0
    tr.setChannels(1)           # set number of input channels
    tr.setFs(44100.0)           # set samplerate
    tr.run_plot()               # run mic viewer
    # tr.run_realtime(True)
    