import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtChart import QChart, QLineSeries, QChartView
from PyQt5.QtCore import Qt, QTimer, QIODevice  # Import QIODevice here
from PyQt5.QtMultimedia import QAudioDeviceInfo, QAudio, QAudioInput, QAudioOutput, QAudioFormat

# Constants
SAMPLE_RATE = 44100  # Sample rate (Hz)
CHANNELS = 1          # Number of audio channels (1 for mono, 2 for stereo)
BLOCK_SIZE = 1024    # Number of audio samples per block
FORMAT = QAudioFormat()
FORMAT.setSampleRate(SAMPLE_RATE)
FORMAT.setChannelCount(CHANNELS)
FORMAT.setSampleSize(16)
FORMAT.setCodec("audio/pcm")
FORMAT.setByteOrder(QAudioFormat.LittleEndian)
FORMAT.setSampleType(QAudioFormat.SignedInt)

# Global variables
input_data = np.zeros(BLOCK_SIZE, dtype=np.int16)
output_data = np.zeros(BLOCK_SIZE, dtype=np.int16)

# Audio capture class
class AudioCapture(QIODevice):
    def __init__(self):
        super().__init__()

    def readData(self, maxlen):
        data = np.frombuffer(input_device.read(maxlen), dtype=np.int16)
        return data.tobytes()

# Audio playback class
class AudioPlayback(QIODevice):
    def __init__(self):
        super().__init__()
        self.buffer = np.zeros(BLOCK_SIZE, dtype=np.int16)

    def writeData(self, data):
        self.buffer = np.frombuffer(data, dtype=np.int16)

# MainWindow class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-Time Audio Plot")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.start_button = QPushButton("Start Recording and Playing")
        self.start_button.clicked.connect(self.start_audio)
        self.layout.addWidget(self.start_button)

        self.chart_view = QChartView(self.create_chart())
        self.layout.addWidget(self.chart_view)

        self.audio_capture = AudioCapture()
        self.audio_playback = AudioPlayback()

        self.capture_device = QAudioInput(QAudioDeviceInfo.defaultInputDevice(), FORMAT)
        self.playback_device = QAudioOutput(QAudioDeviceInfo.defaultOutputDevice(), FORMAT)

        self.capture_device.setNotifyInterval(10)
        self.capture_device.setBufferSize(BLOCK_SIZE)
        self.capture_device.notify.connect(self.update_chart)
        self.capture_device.start(self.audio_capture)

    def create_chart(self):
        chart = QChart()
        chart.setTitle("Audio Data")
        self.audio_series = QLineSeries()
        chart.addSeries(self.audio_series)
        chart.createDefaultAxes()
        chart.legend().hide()
        chart.axisX().setRange(0, BLOCK_SIZE / SAMPLE_RATE)
        chart.axisY().setRange(-32768, 32767)
        return chart

    def start_audio(self):
        self.start_button.setEnabled(False)
        self.playback_device.start(self.audio_playback)
        self.capture_device.start(self.audio_capture)

    def update_chart(self):
        data = self.audio_capture.read(BLOCK_SIZE)
        if data is not None:
            data = np.frombuffer(data, dtype=np.int16)
            self.audio_series.clear()
            for i, value in enumerate(data):
                self.audio_series.append(i / SAMPLE_RATE, value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
