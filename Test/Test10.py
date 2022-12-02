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
        self.i_adder = 1
        self.k_adder = 1
    def Transmit(self,q):
        self.i=self.i+self.i_adder
        return(self.i)
    def Reciev(self,q):
        self.k=self.k+self.k_adder
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
        i=0
        try:
            while True:
                self.result = self.fn(i,*self.args, **self.kwargs)
                print(self.result)
                time.sleep(0.2)
                while self.is_paused:
                    time.sleep(0)
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
        self.signals.result.emit(self.result)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.tranciever = Tranciever()
        self.started_1 = False
        self.started_2 = False
        # Some buttons
        w = QWidget()
        l = QVBoxLayout()
        w.setLayout(l)
        self.threadpool = QThreadPool()

        self.btn_start_1 = QPushButton("Start")
        self.btn_stop_1 = QPushButton("Stop")
        self.btn_pause_1 = QPushButton("Pause")
        self.btn_resume_1 = QPushButton("Resume")
        self.btn_show_results_1 = QPushButton("Show Results")
        self.btn_changeAdder_1 = QPushButton("Увеличить adder")
        self.btn_start_1.pressed.connect(self.start_1)
        self.btn_changeAdder_1.pressed.connect(self.ChangeAdder_1)

        l1 = QHBoxLayout()
        l1.addWidget(QLabel('Процесс 1'))
        l1.addWidget(self.btn_start_1)
        l1.addWidget(self.btn_stop_1)
        l1.addWidget(self.btn_pause_1)
        l1.addWidget(self.btn_resume_1)
        l1.addWidget(self.btn_show_results_1)
        l1.addWidget(self.btn_changeAdder_1)

        l.addLayout(l1)

        self.btn_start_2 = QPushButton("Start")
        self.btn_stop_2 = QPushButton("Stop")
        self.btn_pause_2 = QPushButton("Pause")
        self.btn_resume_2 = QPushButton("Resume")
        self.btn_show_results_2 = QPushButton("Show Results")
        self.btn_changeAdder_2 = QPushButton("Увеличить adder")
        self.btn_start_2.pressed.connect(self.start_2)
        self.btn_changeAdder_2.pressed.connect(self.ChangeAdder_2)

        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Процесс 2'))
        l2.addWidget(self.btn_start_2)
        l2.addWidget(self.btn_stop_2)
        l2.addWidget(self.btn_pause_2)
        l2.addWidget(self.btn_resume_2)
        l2.addWidget(self.btn_show_results_2)
        l2.addWidget(self.btn_changeAdder_2)

        l.addLayout(l2)

        
        self.setCentralWidget(w)
    
    def start_1(self):
        self.worker_1 = Worker(self.tranciever.Transmit)
        self.worker_1.signals.result.connect(self.print_output_1)
        self.btn_stop_1.pressed.connect(self.worker_1.kill)
        self.btn_pause_1.pressed.connect(self.worker_1.pause)
        self.btn_resume_1.pressed.connect(self.worker_1.resume)
        self.btn_show_results_1.pressed.connect(self.worker_1.show)
        self.threadpool.start(self.worker_1)

    
    def start_2(self):
        self.worker_2 = Worker(self.tranciever.Reciev)
        self.worker_2.signals.result.connect(self.print_output_2)
        self.btn_stop_2.pressed.connect(self.worker_2.kill)
        self.btn_pause_2.pressed.connect(self.worker_2.pause)
        self.btn_resume_2.pressed.connect(self.worker_2.resume)
        self.btn_show_results_2.pressed.connect(self.worker_2.show)
        self.threadpool.start(self.worker_2)


    def print_output_1(self, s):
        QMessageBox.about(self, "Внимание", 'Текущий результат по процессу 1: %s' %s)

    def print_output_2(self, s):
        QMessageBox.about(self, "Внимание", 'Текущий результат по процессу 2: %s' %s)

    def ChangeAdder_1(self):
        self.tranciever.i_adder = self.tranciever.i_adder+1

    def ChangeAdder_2(self):
        self.tranciever.k_adder = self.tranciever.k_adder+1        

if __name__ == '__main__':

    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())