from PyQt5.QtMultimedia import QAudioDeviceInfo, QAudio
from PyQt5.QtCore import pyqtSlot
from PyQt5 import uic
from PyQt5 import QtCore, QtWidgets
import sounddevice as sd
import numpy as np
import queue
import matplotlib.ticker as ticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import os
sys.path.insert(0, "././View/")
import matplotlib
from PyQt5.QtGui import QIcon
from mainWaterfall import WaterFallWindow

matplotlib.use("Qt5Agg")


# uses QAudio to obtain all the available devices on the system
input_audio_deviceInfos = QAudioDeviceInfo.availableDevices(QAudio.AudioInput)

# class with all the specification for plotting the matplotlib figure


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.patch.set_facecolor("#00B28C")
        self.axes = fig.add_subplot(111)

        super(MplCanvas, self).__init__(fig)
        fig.tight_layout()

# The main window that is called to run the application


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        # import the QT designer created ui for the application
        self.ui = uic.loadUi("main.ui", self)
        self.resize(888, 600)  # reset the sizefig
        self.ui.setWindowTitle('Voice Plotter')
        self.ui.setWindowIcon(QIcon(os.path.join('icons', 'sound.png')))

        self.threadpool = QtCore.QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        self.devices_list = []
        for device in input_audio_deviceInfos:
            self.devices_list.append(device.deviceName())
        


        # add all the available device name to the combo box
        self.comboBox.addItems(self.devices_list)
        # when the combobox selection changes run the function update_now
        self.comboBox.currentIndexChanged["QString"].connect(self.update_now)
        self.comboBox.setCurrentIndex(0)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas.axes.set_facecolor("#D5F9FF")
        self.ui.gridLayout_4.addWidget(self.canvas, 2, 1, 1, 1) #create gridlayout for matplotlib figure in the canvas
        self.reference_plot = None
        self.q = queue.Queue(maxsize=20)

        # Add some UI elements
        self.Chart1 = WaterFallWindow()
        self.Chart1.set_fs(44100)
        self.Chart1.set_tSeg(200)
        self.Chart1.nPerseg = 1136 # НЕПОНЯТНО TODO
        self.Chart1.nfft = 100*1136 # НЕПОНЯТНО TODO
        self.ui.gridLayout_4.addWidget(self.Chart1, 3, 1, 1, 1)

        # plot specifications
        self.window_length = 1000  # for obtaining sound
        self.downsample = 1  # for obtaining sound
        self.channels = [1]
        self.interval = 30  # update plot every 30/1000 second
        self.yrangeMinVal = -0.5
        self.yrangeMaxVal = 0.5
        # self.all_devices = list(sd.query_devices())
        # print(len(self.all_devices))
        self.device_success = 0
        for self.device in range(len(input_audio_deviceInfos)):
            try:
                device_info = sd.query_devices(self.device, "input")
                if device_info:
                    self.device_success = 1
                    break
            except:
                pass
        if self.device_success:  # run if the device connection is successful
            # print(device_info)
            self.samplerate = device_info["default_samplerate"]
            length = int(self.window_length * self.samplerate /
                         (1000 * self.downsample))
            sd.default.samplerate = self.samplerate
            self.plotdata = np.zeros((length, len(self.channels)))
        else:
          # run if no devices found
            self.disable_buttons()
            self.pushButton_2.setEnabled(False)
            self.pushButton_2.setStyleSheet(
                "QPushButton" "{" "background-color : lightblue;" "}"
            )
            self.devices_list.append("No Devices Found")
            self.comboBox.addItems(self.devices_list)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.interval)  # msec
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
        self.data = [0]
        self.lineEdit.textChanged["QString"].connect(self.update_window_length)
        self.lineEdit_2.textChanged.connect(self.update_sample_rate)
        self.spinBox_downsample.valueChanged.connect(self.update_down_sample)
        self.spinBox_updateInterval.valueChanged.connect(self.update_interval)

        self.doubleSpinBox_yrangemin.valueChanged.connect(
            self.update_yrange_min)  # change the yminvalues when the Yrange is changed
        self.doubleSpinBox_yrangemax.valueChanged.connect(
            self.update_yrange_max)

        self.pushButton.clicked.connect(self.start_worker)
        self.pushButton_2.clicked.connect(self.stop_worker)
        self.worker = None
        self.go_on = False

    def getAudio(self):
        try:
            #Processes some pending events for the calling thread
            #One can call this function occasionally when your program is busy performing a long operation 
            QtWidgets.QApplication.processEvents()
            def audio_callback(indata, frames, time, status):
                self.q.put(indata[:: self.downsample, [0]])
            # uses sounddevice to obtain the input stream, check the InputStream for details
            stream = sd.InputStream(
                device=self.device,
                channels=max(self.channels),
                samplerate=self.samplerate,
                callback=audio_callback,
            )
            with stream:
                while True:
                    QtWidgets.QApplication.processEvents()
                    if self.go_on:
                        break
            self.enable_buttons()

        except Exception as e:
            # print("ERROR: ", e)
            self.stop_worker
            pass

    def disable_buttons(self):
        self.lineEdit.setEnabled(False)
        self.lineEdit_2.setEnabled(False)
        self.spinBox_downsample.setEnabled(False)
        self.spinBox_updateInterval.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.pushButton.setStyleSheet(
            "QPushButton" "{" "background-color : lightblue;" "}"
        )

        self.canvas.axes.clear()

    def enable_buttons(self):
        self.pushButton.setEnabled(True)
        self.lineEdit.setEnabled(True)
        self.lineEdit_2.setEnabled(True)
        self.spinBox_downsample.setEnabled(True)
        self.spinBox_updateInterval.setEnabled(True)
        self.comboBox.setEnabled(True)

    def start_worker(self):

        self.disable_buttons()

        self.canvas.axes.clear()

        self.go_on = False
        self.worker = Worker(
            self.start_stream,
        )
        self.threadpool.start(self.worker)
        self.reference_plot = None
        self.timer.setInterval(self.interval)  # msec

    def stop_worker(self):

        self.go_on = True
        with self.q.mutex:
            self.q.queue.clear()
        self.pushButton.setStyleSheet(
            "QPushButton"
            "{"
            "background-color : rgb(92, 186, 102);"
            "}"
            "QPushButton"
            "{"
            "color : white;"
            "}"
        )
        self.enable_buttons()

    def start_stream(self):
        self.getAudio()

    def update_now(self, value):
        self.device = self.devices_list.index(value)

    def update_window_length(self, value):
        self.window_length = int(value)
        length = int(self.window_length * self.samplerate /
                     (1000 * self.downsample))
        self.plotdata = np.zeros((length, len(self.channels)))

    def update_sample_rate(self, value):
        try:
            self.samplerate = int(value)
            sd.default.samplerate = self.samplerate
            length = int(
                self.window_length * self.samplerate / (1000 * self.downsample)
            )
            print(self.samplerate, sd.default.samplerate)
            self.plotdata = np.zeros((length, len(self.channels)))
        except:
            pass

    def update_down_sample(self, value):
        self.downsample = int(value)
        length = int(self.window_length * self.samplerate /
                     (1000 * self.downsample))
        self.plotdata = np.zeros((length, len(self.channels)))

    def update_interval(self, value):
        self.interval = int(value)

    def update_yrange_min(self, minval):
        self.yrangeMinVal = float(minval)

    def update_yrange_max(self, maxval):
        self.yrangeMaxVal = float(maxval)

    def update_plot(self):
        try:

            print("ACTIVE THREADS:", self.threadpool.activeThreadCount(), end=" \r")
            self.label_18.setText(f"{self.threadpool.activeThreadCount()}")
            while self.go_on is False:
                QtWidgets.QApplication.processEvents()
                try:
                    self.data = self.q.get_nowait()

                except queue.Empty:
                    break

                shift = len(self.data)
                self.plotdata = np.roll(self.plotdata, -shift, axis=0)
                self.plotdata[-shift:, :] = self.data
                self.ydata = self.plotdata[:]
                self.canvas.axes.set_facecolor("#D5F9FF")

                if self.reference_plot is None:
                    plot_refs = self.canvas.axes.plot(
                        self.ydata, color="green")
                    self.reference_plot = plot_refs[0]
                else:
                    self.reference_plot.set_ydata(self.ydata)
                    a=np.concatenate(self.data)
                    self.Chart1.specImage(a)
                    

            self.canvas.axes.yaxis.grid(True, linestyle="--")
            start, end = self.canvas.axes.get_ylim()
            self.canvas.axes.yaxis.set_ticks(np.arange(start, end, 0.1))
            self.canvas.axes.yaxis.set_major_formatter(
                ticker.FormatStrFormatter("%0.1f")
            )
            self.canvas.axes.set_ylim(
                ymin=self.yrangeMinVal, ymax=self.yrangeMaxVal)

            self.canvas.draw()

        except Exception as e:
            print("Error:", e)
            pass


class Worker(QtCore.QRunnable):
    def __init__(self, function, *args, **kwargs):
        super(Worker, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):

        self.function(*self.args, **self.kwargs)


app = QtWidgets.QApplication(sys.argv)

if __name__ == "__main__":
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
