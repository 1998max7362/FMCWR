import pyqtgraph as pg
import numpy as np
import scipy as sp
from PyQt5.QtGui import QFont
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
import sys

class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()
        # разметка окна
        GraphWindowLayout=QHBoxLayout(self)
        # создание графического виджета
        self.graphWidget = pg.PlotWidget()
        # глобальные настройки графического виджета
        pg.setConfigOptions(antialias=True)
        self.graphWidget.setBackground('w')
        # расстановка элементов в разметку
        GraphWindowLayout.addWidget(self.graphWidget)

        # классовые методы


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = GraphWindow()
    main.show()
    sys.exit(app.exec_())