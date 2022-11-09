import sys
sys.path.insert(0, "././Core/")
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtGui import * 
from qtwidgets import Toggle, AnimatedToggle
from PyQt5.QtCore import QSize
from SignalSource import SignalSource
from SignalType import SignalType
from WrapedUiElements import *
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

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
        self.isMeasuring = False
        
        self.DefaultFont = QFont('Times',10)

        self.SignalTypeInit()
        layout.addWidget(self.signalTypesGroupBox)

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

    def NoneMethod(self):
        pass 

    def StartStop(self):
        self.isMeasuring = not(self.isMeasuring)
        self.StartStopClamp.Send(self.isMeasuring)
        print(self.isMeasuring)

    def SignalTypeInit(self):
        self.signalTypesGroupBox = QGroupBox('Тип сигнала')
        self.signalTypesGroupBox.setFont(QFont('Times',15))
        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.signalTypesGroupBox.setLayout(layout)
        self.SignalsType = []
        SignalTypeSelecter = QButtonGroup(self)
        self.SignalsType.append(QRadioButton())
        self.SignalsType.append(QRadioButton())
        for Signal in self.SignalsType:
            SignalTypeSelecter.addButton(Signal)
            layout.addWidget(Signal)
        self.SignalsType[0].clicked.connect(lambda: self.SignalTypeSwitched(SignalType.LINE,0))
        self.SignalsType[1].clicked.connect(lambda: self.SignalTypeSwitched(SignalType.TRIANGLE,1))
        self.SignalsType[0].setIcon(QIcon('Icons/Triangle2.png'))
        self.SignalsType[0].setIconSize(QSize(400,255)) 
        self.SignalsType[1].setIcon(QIcon('Icons/Triangle2.png'))
        self.SignalsType[1].setIconSize(QSize(400,255))

    
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