import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import traceback, sys
import numpy as np
sys.path.insert(0, "././Core/")
from WrapedUiElements import *

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

class MyFunctions():
    def __init__(self) -> None:
        self.is_paused = False
        self.is_killed = False

    def PermanentTrasnitter(self):
        self.i=0
        while True:
            self.i=self.i+1
            while self.is_paused:
                
                time.sleep(0)
            if self.is_killed:
                break

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def kill(self):
        self.is_killed = True

    # def reciveData(self):
    #     fs = 192e3
    #     dt = 1/fs
    #     pi = np.pi
    #     m = 0.3
    #     f0 = 40000
    #     f1 = 5000
    #     Un = 100
    #     RecivedSignal = np.array(1024)
    #     for i in range(1024):
    #         RecivedSignal[i] = Un*(1+m*np.cos(2*pi*f1*dt*i))*np.cos(2*pi*f0*dt*i)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.isMeasuring = False
        w = QWidget(self)
        self.setCentralWidget(w)

        layout = QVBoxLayout()
        w.setLayout(layout)

        self.StartStopButton = ClampedToggleButton('Start','100,0,0')
        self.StartStopButton.Text_NOT_CLICKED = ('Start')
        self.StartStopButton.Text_LEFT_CLICKED = ('Stop')
        self.StartStopButton.setFont(QFont('Times',10))
        self.StartStopButton.Style_NOT_CLICKED = "background-color: green"
        self.StartStopButton.Style_LEFT_CLICKED = "background-color: red"
        self.StartStopButton.toState(ToggleButtonState.NOT_CLICKED)
        self.StartStopButton.customContextMenuRequested.disconnect(self.StartStopButton.rightClickHandler)
        self.StartStopButton.customContextMenuRequested.connect(self.NoneMethod)
        self.StartStopButton.setToolTip('Запуск устройства')
        self.StartStopButton.clicked.connect(self.StartStop)

        layout.addWidget(self.StartStopButton)

        self.MyFunctions = MyFunctions()

        self.threadpool = QThreadPool()


    def NoneMethod(self):
        pass 

    def StartStop(self):
        self.isMeasuring = not(self.isMeasuring)
        Transmit = Worker(self.MyFunctions.PermanentTrasnitter)
        self.threadpool.start(Transmit)
        print(self.isMeasuring)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())