from PyQt5.QtWidgets import *
import sys
import time 
import threading
import multiprocessing
from multiprocessing import Process, Queue
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

sentinel = -1

class simpleSignal(QObject):
    output = pyqtSignal(object)
    def emit(self,obj):
        self.output.emit(obj)
    def connect(self, slt):
        self.output.connect(slt)


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.q = Queue()
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
        data=[1,2]
        self.y = multiprocessing.Process(target=self.counter.StartCount, args=(data,self.q))
        self.y.start()
    
    def stop(self):
        try:
            print('Stop')
            self.y.terminate()

            while True:
                data = self.q.get()
                print('data found to be processed: {}'.format(data))
                if data is sentinel:
                    self.q.close()
                    self.q.join_thread()
                    break
        except:
            'Процесс еще не был запущен'

class MyCounter():
    def __init__(self,):
        super().__init__()
        self.i = 0
    
    def StartCount(self,data,q):
        while True:
            self.i = self.i+1
            q.put(self.i)
            time.sleep(1)

    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    q=Queue()
    main = MyWindow()
    main.show()

    sys.exit(app.exec_())