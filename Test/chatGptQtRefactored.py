import sys
import numpy as np
import pyaudio
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtChart import QChart, QLineSeries, QChartView
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Constants
SAMPLE_RATE = 44100  # Sample rate (Hz)
CHANNELS = 1          # Number of audio channels (1 for mono, 2 for stereo)
BLOCK_SIZE = 1024    # Number of audio samples per block

# Global variables
input_data = np.zeros(BLOCK_SIZE, dtype=np.float32)
output_data = np.zeros(BLOCK_SIZE, dtype=np.float32)

# PyAudio setup
p = pyaudio.PyAudio()

# Audio capture thread
class AudioCaptureThread(QThread):
    data_ready = pyqtSignal(np.ndarray)

    def run(self):
        stream = p.open(format=pyaudio.paFloat32, channels=CHANNELS, rate=SAMPLE_RATE,
                        input=True, frames_per_buffer=BLOCK_SIZE)

        while True:
            input_data = np.frombuffer(stream.read(BLOCK_SIZE), dtype=np.float32)
            self.data_ready.emit(input_data)

# Audio playback thread
class AudioPlaybackThread(QThread):
    def __init__(self):
        super().__init__()
        self.playing = False

    def run(self):
        stream = p.open(format=pyaudio.paFloat32, channels=CHANNELS, rate=SAMPLE_RATE,
                        output=True, frames_per_buffer=BLOCK_SIZE)

        while True:
            if self.playing:
                stream.write(output_data.tobytes())

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

        self.capture_thread = AudioCaptureThread()
        self.capture_thread.data_ready.connect(self.update_chart)

        self.playback_thread = AudioPlaybackThread()

    def create_chart(self):
        chart = QChart()
        chart.setTitle("Audio Data")
        self.audio_series = QLineSeries()
        chart.addSeries(self.audio_series)
        chart.createDefaultAxes()
        chart.legend().hide()
        chart.axisX().setRange(0, BLOCK_SIZE / SAMPLE_RATE)
        chart.axisY().setRange(-1, 1)
        return chart

    def start_audio(self):
        self.start_button.setEnabled(False)
        self.playback_thread.playing = True
        self.capture_thread.start()
        self.playback_thread.start()

    def update_chart(self, data):
        self.audio_series.clear()
        for i, value in enumerate(data):
            self.audio_series.append(i / SAMPLE_RATE, value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
