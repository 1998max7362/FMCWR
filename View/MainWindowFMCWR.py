import sys
from mainWaterfall import WaterFallWindow
sys.path.insert(0, "././Core/")
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtWidgets
from SettingsFMCWRv2 import SettingsWindow

from mainGraph import GraphWindow
from Transmitter import Transmitter
from Clamp import Clamp
from PyQt5.QtCore import QTimer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Главное меню')


        self._createActions()
        self._connectActions()
        self._createMenubar()

        # вывод главного блока
        self.input = Clamp()
        self.output = Clamp()

        # разметка
        layout = QHBoxLayout(self)
        # добавление виджетов
        self.settings = SettingsWindow()
        self.dockSettings = QDockWidget()
        self.transmitter = Transmitter()
        self.dockSettings.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)

        self.dockSettings.setWidget(self.settings)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockSettings)

        self.dockGraph0 = QDockWidget("График 0")
        self.dockGraph1 = QDockWidget("График 1")
        self.dockGraph0.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.dockGraph1.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.Chart0 = GraphWindow()
        self.Chart1 = WaterFallWindow()
        # настройки виджетов
        self.Chart0.setMinimumSize(300,200)
        self.Chart1.setMinimumSize(300,200)
        self.dockGraph0.setWidget(self.Chart0)
        self.dockGraph1.setWidget(self.Chart1)

        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph0)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph1)
        # Подключение модулей
        self.demo = Clamp()
        #self.demo.ConnectTo(self.Chart1.demo)
        self.demo.ConnectTo(self.transmitter.demo)
        self.settings.StartStopClamp.ConnectTo(self.input)
        self.transmitter.output.ConnectTo(self.Chart0.input)
        self.transmitter.output.ConnectTo(self.Chart1.input)

        # включение демоверсии
        self.demo.Send(True)
        if self.demo.SentValue:
            self.i = 0
            self.timer = QTimer()
            self.output.ConnectTo(self.Chart0.input)
            self.output.ConnectTo(self.Chart1.input)
            self.input.HandleWithReceive(self.startReceived)

        self.settings.Period.LineEdit.Text.HandleWithSend(self.SendPeriod)

    def SendPeriod(self,smth):
        print(smth)

    def _createMenubar(self):
        menuBar = self.menuBar()
        MainWindowMenuBar = menuBar.addMenu("&Файл")
        MainWindowMenuBar.addAction(self.saveAction)
        MainWindowMenuBar.addAction(self.loadAction)

    def _createActions(self):
        self.saveAction = QAction("&Сохранить",self)
        self.loadAction = QAction("&Загрузить",self)
    
    def _connectActions(self):
        self.saveAction.triggered.connect(self.saveFile)
        self.loadAction.triggered.connect(self.loadFile)

    def saveFile(self):
        print('save')
    
    def loadFile(self):
        print('load')

    # методы класса
    def startReceived(self, data: bool):
        self.input.ReceivedValue = data
        if self.input.ReceivedValue:
            fs = 192e3
            dt = 1/fs
            self.timer.setInterval(int(dt*1000))
            self.timer.timeout.connect(self.demoTransmit)
            self.timer.start()
        elif not(self.input.ReceivedValue):
            self.timer.stop()
            pass

    def demoTransmit(self):
        fs = 192e3
        dt = 1/fs
        pi = np.pi
        m = 0.3
        f0 = 40000
        f1 = 5000
        Un = 100
        # init timer
        self.i += 1
        testSig = Un*(1+m*np.cos(2*pi*f1*dt*self.i))*np.cos(2*pi*f0*dt*self.i)
        self.output.Send([self.i*dt*1000, testSig])


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())