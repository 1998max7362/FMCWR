from PyQt5.QtWidgets import *
import sys
import time 
import threading
import multiprocessing
from multiprocessing import Process, Queue
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

class simpleSignal(QObject):
    output = pyqtSignal(object)
    def emit(self,obj):
        self.output.emit(obj)
    def connect(self, slt):
        self.output.connect(slt)


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.counter = MyCounter()
        layout = QVBoxLayout(self)
        BTNlayout = QHBoxLayout()
        self.startBtn = QPushButton('Старт')
        self.stopBtn = QPushButton('Стоп')
        self.startBtn.clicked.connect(self.start)
        self.stopBtn.clicked.connect(self.stop)
        BTNlayout.addWidget(self.startBtn)
        BTNlayout.addWidget(self.stopBtn)
        layout.addLayout(BTNlayout)

        self.Label = QLabel()
        layout.addWidget(self.Label)


    def start(self):
        print('started')
        self.y = multiprocessing.Process(target=self.counter.StartCount)
        self.y.start()
    
    def stop(self):
        try:
            print('Stop')
            self.y.terminate()
            print(self.counter.i)
        except:
            'Процесс еще не был запущен'
        finally:
            print('finished')


class MyCounter():
    def __init__(self,):
        super().__init__()
        self.i = 0
    
    def StartCount(self):
        while True:
            self.i = self.i+1
            print(self.i)
            time.sleep(1)

    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    q=Queue()
    main = MyWindow()
    main.show()

    sys.exit(app.exec_())