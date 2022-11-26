import sys
sys.path.insert(0, "././Core/")
import pyqtgraph as pg
import numpy as np
import scipy as sp
from PyQt5.QtGui import QFont
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
import sys
from Clamp import Clamp

class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Вход блока графика
        self.input = Clamp()
        self.i = 0
        self.x = []
        self.y = []
        self.clearClamp = Clamp()
        # разметка окна
        GraphWindowLayout=QHBoxLayout(self)
        # создание графического виджета
        self.graphWidget = pg.PlotWidget()
        # глобальные настройки графического виджета
        pg.setConfigOptions(antialias=True)
        self.graphWidget.setBackground('w')
        self.pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plotItem.plot(self.x, self.y, pen=self.pen)
        self.graphWidget.setYRange(-1, 1)
        # расстановка элементов в разметку
        GraphWindowLayout.addWidget(self.graphWidget)
        # Действия по приходу данных
        self.input.HandleWithReceive(self.plotData)
        self.clearClamp.HandleWithReceive(self.clearPlots)


    # классовые методы

    # построение графиков
    def plotData(self, data: list):
        self.x.append(data[0])
        self.y.append(data[1])

        if len(self.x) >= 1136:
            self.x = self.x[1:]
            self.y = self.y[1:]

        self.data_line.setData(self.x, np.real(self.y))

    # очистка графиков
    def clearPlots(self, data: bool):
        self.x = []
        self.y = []
        self.graphWidget.removeItem(self.data_line)
        self.data_line = self.graphWidget.plotItem.plot(self.x, self.y, pen=self.pen)

    def plotData_test(self, x,y):
        self.data_line.setData(x, np.real(y))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = GraphWindow()
    main.show()
    sys.exit(app.exec_())