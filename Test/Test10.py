import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import traceback, sys
import numpy as np
sys.path.insert(0, "././Core/")
from WrapedUiElements import *

class Tranciever():
    def __init__(self) -> None:
        self.i = 0
        self.k = 0
    def Transmit(self):
        self.i=self.i+1
        return(self.i)
    def Reciev(self):
        self.k=self.k+1
        return(self.k)

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        

        self.is_paused = False
        self.is_killed = False
        self.show_results = False

    @pyqtSlot()
    def run(self):
        try:
            while True:
                result = self.fn(*self.args, **self.kwargs)
                print(result)
                time.sleep(0.2)
                while self.is_paused:
                    time.sleep(0)
                if self.show_results:
                    self.signals.result.emit(result)
                    self.show_results = False
                if self.is_killed:
                    break
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def kill(self):
        self.is_killed = True
    
    def show(self):
        self.show_results = True

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        tranciever = Tranciever()
        self.started_1 = False
        self.started_2 = False
        # Some buttons
        w = QWidget()
        l = QVBoxLayout()
        w.setLayout(l)
        self.threadpool = QThreadPool()

        btn_start_1 = QPushButton("Start")
        btn_stop_1 = QPushButton("Stop")
        btn_pause_1 = QPushButton("Pause")
        btn_resume_1 = QPushButton("Resume")
        btn_show_results_1 = QPushButton("Show Results")

        l1 = QHBoxLayout()
        l1.addWidget(QLabel('Процесс 1'))
        l1.addWidget(btn_start_1)
        l1.addWidget(btn_stop_1)
        l1.addWidget(btn_pause_1)
        l1.addWidget(btn_resume_1)
        l1.addWidget(btn_show_results_1)

        l.addLayout(l1)
        
        self.worker_1 = Worker(tranciever.Transmit)
        self.worker_1.signals.result.connect(self.print_output_1)
        btn_start_1.pressed.connect(self.start_1)
        btn_stop_1.pressed.connect(self.worker_1.kill)
        btn_pause_1.pressed.connect(self.worker_1.pause)
        btn_resume_1.pressed.connect(self.worker_1.resume)
        btn_show_results_1.pressed.connect(self.worker_1.show)


        btn_start_2 = QPushButton("Start")
        btn_stop_2 = QPushButton("Stop")
        btn_pause_2 = QPushButton("Pause")
        btn_resume_2 = QPushButton("Resume")
        btn_show_results_2 = QPushButton("Show Results")

        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Процесс 2'))
        l2.addWidget(btn_start_2)
        l2.addWidget(btn_stop_2)
        l2.addWidget(btn_pause_2)
        l2.addWidget(btn_resume_2)
        l2.addWidget(btn_show_results_2)

        l.addLayout(l2)

        self.worker_2 = Worker(tranciever.Reciev)
        self.worker_2.signals.result.connect(self.print_output_2)
        btn_start_2.pressed.connect(self.start_2)
        btn_stop_2.pressed.connect(self.worker_2.kill)
        btn_pause_2.pressed.connect(self.worker_2.pause)
        btn_resume_2.pressed.connect(self.worker_2.resume)
        btn_show_results_2.pressed.connect(self.worker_2.show)
        
        self.setCentralWidget(w)

    def start_1(self):
        if self.started_1 == False:
            self.threadpool.start(self.worker_1)
        else:
            print('уже идет')
        self.started_1 = True

    def start_2(self):
        if self.started_2 == False:
            self.threadpool.start(self.worker_2)
        else:
            print('уже идет')
        self.started_2 = True

    def print_output_1(self, s):
        QMessageBox.about(self, "Внимание", 'Текущий результат по процессу 1: %s' %s)

    def print_output_2(self, s):
        QMessageBox.about(self, "Внимание", 'Текущий результат по процессу 2: %s' %s)



if __name__ == '__main__':

    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())