import sys

from mainWaterfall import WaterFallWindow
sys.path.insert(0, "././Core/")
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtWidgets
from SettingsFMCWR import SettingsWindow
from mainGraph import GraphWindow


from Clamp import Clamp

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Главное меню')
        layout = QHBoxLayout(self)
        self.settings = SettingsWindow()
        self.dockSettings = QDockWidget("Настройки")
        self.dockGraph0 = QDockWidget("График 0")
        self.dockGraph1 = QDockWidget("График 1")
        self.Chart0 = GraphWindow()
        self.Chart1 = WaterFallWindow()
        self.Chart0.setMinimumSize(300,200)
        self.Chart1.setMinimumSize(300,200)
        self.dockSettings.setWidget(self.settings)
        self.dockGraph0.setWidget(self.Chart0)
        self.dockGraph1.setWidget(self.Chart1)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockSettings)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph0)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph1)

        # включение демоверсии
        self.demo = Clamp()
        self.demo.ConnectTo(self.Chart1.demo)
        self.demo.Send(True)

        self.settings.Period.LineEdit.Text.HandleWithSend(self.SendPeriod)

    def SendPeriod(self,smth):
        print(smth)

        


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())