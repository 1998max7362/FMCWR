import sys
sys.path.insert(0, "././Core/")
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtWidgets
from SettingsFNCW import SettingsWindow


from Clamp import Clamp

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        self.settings = SettingsWindow()
        self.dockSettings = QDockWidget("Settings")
        self.dockSettings.setWidget(self.settings)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockSettings)

        self.dockGraph0 = QDockWidget("Chart 0")
        self.dockGraph1 = QDockWidget("Chart 1")
        Chart0 = QWidget()
        Chart0.setMinimumSize(300,200)
        Chart1 = QWidget()
        Chart1.setMinimumSize(300,200)
        self.dockGraph0.setWidget(Chart0)
        self.dockGraph0.setWidget(Chart1)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph0)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph1)
        


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())