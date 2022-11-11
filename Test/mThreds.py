import time
import sys
from multiprocessing import Process
sys.path.insert(0, "././Core/")
sys.path.insert(0, "././View/")
from mainWaterfall import WaterFallWindow
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtWidgets
from Clamp import Clamp


from MainWindowFMCWR import MainWindow

class Something():
    def __init__(self) -> None:
        self.i=0
        # pass
        # self.trig = Clamp()
        # self.trig.HandleWithReceive(self.ShowI)
        # self.SomeAction()


    def SomeAction(self):
        self.i=0
        while True:
            self.i=self.i+1
            time.sleep(1)
            # print(self.i)
    
    def ShowI(self,sig):
        print(sig)
        print(self.i)

def SomeAction2():
    i=0
    while True:
        i=i+1
        time.sleep(1)
        print(i)

if __name__ == '__main__':
    trig = Clamp()
    

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    smth = Something()
    
    main.settings.StartStopClamp.ConnectTo(trig)
    
    main.show()
    
    
    pr1 = Process(target=smth.SomeAction, args=())
    pr1.start()
    time.sleep(5)
    trig.HandleWithReceive(print(smth.i))


    sys.exit(app.exec_())