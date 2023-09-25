import sys
sys.path.insert(0, "././utils/constants/")
sys.path.insert(0, "././utils/components/")
sys.path.insert(0, "././ExtraFiles/Icons/")
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import * 
from PyQt5.QtCore import QSize
from SignalType import SignalType
from WrapedUiElements import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSignal 
from PyQt5.QtCore import *

class SettingsWindow(QWidget):
    signalTypeChanged = pyqtSignal(object)
    signalPeriodChanged = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setFixedWidth(440)
        layout = QVBoxLayout(self)
        
        self.DefaultFont = QFont('Times',10)

        self.SignalTypeInit()
        layout.addWidget(self.signalTypesGroupBox)

        self.Period = NamedLineEditHorizontal(ClampedLineEdit(self.convertToStr,self.convertBackToFloat),"Период:", "мкс")
        self.Period.label.setFont(self.DefaultFont)
        self.Period.labelUnits.setFont(self.DefaultFont)
        self.Period.LineEdit.setText('0')
        self.Period.LineEdit.setFont(self.DefaultFont)
        self.Period.LineEdit.setValidator(QRegExpValidator(QRegExp("[+-]?[0-9]{1,2}[\.][0-9]{1,2}")))
        layout.addWidget(self.Period, alignment=Qt.AlignTop)
        
        layout.addStretch()

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
        self.SignalsType[0].setIcon(QIcon('ExtraFiles/Icons/Triangle2.png'))
        self.SignalsType[0].setIconSize(QSize(400,255)) 
        self.SignalsType[1].setIcon(QIcon('ExtraFiles/Icons/Triangle2.png'))
        self.SignalsType[1].setIconSize(QSize(400,255))

    def SignalTypeSwitched(self,signalType, buttonNum:int):
        for RadioButton in self.SignalsType:
            RadioButton.blockSignals(False)
        self.SignalsType[buttonNum].blockSignals(True)
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