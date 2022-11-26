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
        self.y = np.array([])
        self.clearClamp = Clamp()
        # разметка окна
        GraphWindowLayout=QHBoxLayout(self)
        # создание графического виджета
        self.graphWidget = pg.PlotWidget()
        # глобальные настройки графического виджета
        pg.setConfigOptions(antialias=True)
        self.graphWidget.setBackground('k')
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
        self.y = np.append(self.y,data)
        # self.i += 1 
        # self.x.append(self.i*np.array(range(len(data))))

        if len(self.y) >= 1136:
           self.y = self.y[len(data):]

        # self.data_line.setData(self.x, np.real(self.y))
        self.data_line.setData(np.real(self.y))

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