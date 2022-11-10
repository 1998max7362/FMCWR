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
        # разметка окна
        GraphWindowLayout=QHBoxLayout(self)
        # создание графического виджета
        self.graphWidget = pg.PlotWidget()
        # глобальные настройки графического виджета
        pg.setConfigOptions(antialias=True)
        self.graphWidget.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plotItem.plot(self.x, self.y, pen=pen)
        # расстановка элементов в разметку
        GraphWindowLayout.addWidget(self.graphWidget)
        # Действия по приходу данных
        self.input.HandleWithReceive(self.plotData)


    # классовые методы
    def plotData(self, data: list):
        self.x.append(data[0])
        self.y.append(data[1])

        if len(self.x) >= 500:
            self.x = self.x[1:]
            self.y = self.y[1:]

        self.data_line.setData(self.x, np.real(self.y))

    def clearPlots(self):
        self.graphWidget.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = GraphWindow()
    main.show()
    sys.exit(app.exec_())