import sys
sys.path.insert(0, "././Core/")
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtWidgets
from qtwidgets import Toggle, AnimatedToggle
from SignalSource import SignalSource
from SignalType import SignalType
from WrapedUiElements import *
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import Qt

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setFixedWidth(440)
        layout = QVBoxLayout(self)

        self.SignalTypeSwitchlamp = Clamp()
        self.SignalSourceSwitchClamp = Clamp()
        self.PeriodClamp = Clamp()
        self.StartStopClamp = Clamp()
        self.xRangeClamp = Clamp()
        self.yRangeClamp = Clamp()
        self.isMeasuring = False
        
        self.DefaultFont = QFont('Times',10)

        #  Настройка параметров графиков
        self.graphSettingsInit()
        layout.addWidget(self.GraphSettingsGroupBox)


        self.Period = NamedLineEditHorizontal(ClampedLineEdit(self.convertToStr,self.convertBackToFloat),"Период:", "мкс")
        self.Period.label.setFont(self.DefaultFont)
        self.Period.labelUnits.setFont(self.DefaultFont)
        self.Period.LineEdit.setText('0')
        self.Period.LineEdit.setFont(self.DefaultFont)
        self.Period.LineEdit.setValidator(QRegExpValidator(QRegExp("[+-]?[0-9]{1,2}[\.][0-9]{1,2}")))
        # self.Period.LineEdit.setValidator(QDoubleValidator(
        #         0.0, # bottom
        #         100.0, # top
        #         1, # decimals 
        #         notation=QDoubleValidator.StandardNotation))
        layout.addWidget(self.Period, alignment=Qt.AlignTop)

        SourceSelecterLayout = QHBoxLayout()
        self.Source1 = QLabel('Передатчик')
        self.Source1.setMaximumWidth(110)
        self.Source1.setFont(self.DefaultFont)
        self.Source2 = QLabel('Приёмник')
        self.Source2.setMaximumWidth(90)
        self.Source2.setFont(self.DefaultFont)
        self.SignalSourceSelecter = AnimatedToggle(
            bar_color=Qt.lightGray,
            handle_color=Qt.darkGray,
            checked_color="#808080",
            pulse_checked_color="#00FF00",
            pulse_unchecked_color ="#00FF00")
        self.SignalSourceSelecter.stateChanged.connect(self.SignalSourceSwitched)
        SourceSelecterLayout.addWidget(self.Source1)
        SourceSelecterLayout.addWidget(self.SignalSourceSelecter)
        SourceSelecterLayout.addWidget(self.Source2)
        layout.addLayout(SourceSelecterLayout)

        self.StartStopButton = ClampedToggleButton('Start','100,0,0')
        self.StartStopButton.Text_NOT_CLICKED = ('Start')
        self.StartStopButton.Text_LEFT_CLICKED = ('Stop')
        self.StartStopButton.setFont(self.DefaultFont)
        self.StartStopButton.Style_NOT_CLICKED = "background-color: white"
        self.StartStopButton.Style_LEFT_CLICKED = "background-color: green"
        self.StartStopButton.toState(ToggleButtonState.NOT_CLICKED)
        self.StartStopButton.customContextMenuRequested.disconnect(self.StartStopButton.rightClickHandler)
        self.StartStopButton.customContextMenuRequested.connect(self.NoneMethod)
        self.StartStopButton.setToolTip('Запуск устройства')
        self.StartStopButton.clicked.connect(self.StartStop)

        layout.addWidget(self.StartStopButton)
        layout.addStretch()

        self.xRangeChanged(False)
        self.yRangeChanged(False)

    def graphSettingsInit(self):
        self.GraphSettingsGroupBox = QGroupBox('Настройка графиков')
        # self.GraphSettingsGroupBox.setStyleSheet("::title{font-size:50px}")
        self.GraphSettingsGroupBox.setFont(QFont('Times',10))
        layout = QGridLayout()
        layout.setSpacing(0)
        self.GraphSettingsGroupBox.setLayout(layout)
        self.xMin = NamedClampedSpinBox('Xmin:')
        self.xMax = NamedClampedSpinBox('Xmax:')
        self.yMin = NamedClampedDoubleSpinBox('Ymin:')
        self.yMax = NamedClampedDoubleSpinBox('Ymax:')
        self.xMin.label.setFixedWidth(70)
        self.xMax.label.setFixedWidth(70)
        self.yMin.label.setFixedWidth(70)
        self.yMax.label.setFixedWidth(70)
        layout.addWidget(self.xMin,0,0)
        layout.addWidget(self.xMax,1,0)
        layout.addWidget(self.yMin,0,1)
        layout.addWidget(self.yMax,1,1)
        self.xMin.spinBox.setMinimum(0)
        self.xMin.spinBox.setMaximum(20000)
        self.xMin.spinBox.setValue(0)
        self.xMin.spinBox.setSingleStep(100)
        self.xMax.spinBox.setMinimum(0)
        self.xMax.spinBox.setMaximum(20000)
        self.xMax.spinBox.setValue(20000)
        self.xMax.spinBox.setSingleStep(100)
        self.yMin.doubleSpinBox.setMinimum(-100)
        self.yMin.doubleSpinBox.setMaximum(100)
        self.yMax.doubleSpinBox.setMinimum(-100)
        self.yMax.doubleSpinBox.setMaximum(100)
        self.yMin.doubleSpinBox.setValue(-1)
        self.yMin.doubleSpinBox.setSingleStep(0.1)
        self.yMax.doubleSpinBox.setValue(1)
        self.yMax.doubleSpinBox.setSingleStep(0.1)
        self.xMin.warning.setToolTip('Xmin не может быть больше Xmax')
        self.xMax.warning.setToolTip('Xmin не может быть больше Xmax')
        self.yMin.warning.setToolTip('Ymin не может быть больше Ymax')
        self.yMax.warning.setToolTip('Ymin не может быть больше Ymax')
        self.xMin.spinBox.valueChanged.connect(self.xRangeChanged)
        self.xMax.spinBox.valueChanged.connect(self.xRangeChanged)
        self.yMin.doubleSpinBox.valueChanged.connect(self.yRangeChanged)
        self.yMax.doubleSpinBox.valueChanged.connect(self.yRangeChanged)
    
    def xRangeChanged(self,smth):
        if self.xMin.spinBox.value()<=self.xMax.spinBox.value():
            self.xRangeClamp.Send([self.xMin.spinBox.value(),self.xMax.spinBox.value()])
            self.xMin.warning.setHidden(True)
            self.xMax.warning.setHidden(True)
        else:
            self.xMin.warning.setHidden(False)
            self.xMax.warning.setHidden(False)

    def yRangeChanged(self,smth):
        if self.yMin.doubleSpinBox.value()<=self.yMax.doubleSpinBox.value():
            self.yRangeClamp.Send([self.yMin.doubleSpinBox.value(),self.yMax.doubleSpinBox.value()])
            self.yMin.warning.setHidden(True)
            self.yMax.warning.setHidden(True)
        else:
            self.yMin.warning.setHidden(False)
            self.yMax.warning.setHidden(False)

    def NoneMethod(self):
        pass 

    def StartStop(self):
        self.isMeasuring = not(self.isMeasuring)
        self.StartStopClamp.Send(self.isMeasuring)
    
    def SignalSourceSwitched(self,source): # 0 - первый источник, 2 - второй источник
        boldFont = QFont('Times',10)
        boldFont.setBold(True)
        unboldFont = QFont('Times',10)
        unboldFont.setBold(False)
        if source == 0:
            self.Source1.setFont(boldFont)
            self.Source2.setFont(unboldFont)
            source = SignalSource.TRANSMITTER
        if source == 2:
            self.Source2.setFont(boldFont)
            self.Source1.setFont(unboldFont)
            source = SignalSource.RECIEVER
        self.SignalSourceSwitchClamp.Send(source)
        print(source)

    def SignalTypeSwitched(self,signalType, buttonNum:int):
        for RadioButton in self.SignalsType:
            RadioButton.blockSignals(False)
        self.SignalsType[buttonNum].blockSignals(True)
        self.SignalTypeSwitchlamp.Send(signalType)
        print(signalType)

    def convertBackToFloat(self, value):
        try:
            return float(value)
        except:
            pass
    def convertToStr(self, value):
        return str(value)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = SettingsWindow()
    main.show()

    sys.exit(app.exec_())