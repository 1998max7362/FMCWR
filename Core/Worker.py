from PyQt5.QtCore import *
import time
import traceback, sys

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
                self.result = self.fn(*self.args, **self.kwargs)
                print(self.result)
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