import sys
sys.path.insert(0, "././Core/")
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtWidgets
from SettingsFMCWRv2 import SettingsWindow


from Clamp import Clamp

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Главное меню')

        self._createActions()
        self._connectActions()
        self._createMenubar()

        layout = QHBoxLayout(self)
        self.settings = SettingsWindow()
        # self.dockSettings = QDockWidget("Настройки")
        self.dockSettings = QDockWidget()
        self.dockSettings.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)

        self.dockSettings.setWidget(self.settings)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockSettings)

        self.dockGraph0 = QDockWidget("График 0")
        self.dockGraph1 = QDockWidget("График 1")
        Chart0 = QWidget()
        Chart0.setMinimumSize(300,200)
        Chart1 = QWidget()
        Chart1.setMinimumSize(300,200)
        self.dockGraph0.setWidget(Chart0)
        self.dockGraph0.setWidget(Chart1)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph0)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph1)

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


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())