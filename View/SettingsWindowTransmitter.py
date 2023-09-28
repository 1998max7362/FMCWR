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
from getAudioDevice import getAudioDevice

class SettingsWindowTransmitter(QWidget):
    signalTypeChanged = pyqtSignal(object)
    signalPeriodChanged = pyqtSignal(object)
    outputDeviceChanged = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setFixedWidth(440)
        layout = QVBoxLayout(self)
        
        self.DefaultFont = QFont('Times',10)

        self.deviceSettingsInit()
        layout.addWidget(self.DeviceSettingsGroupBox)

        self.SignalTypeInit()
        layout.addWidget(self.signalTypesGroupBox)

        self.Period = NewNamedLineEditHorizontal("Период:", "мкс")
        self.Period.label.setFont(self.DefaultFont)
        self.Period.labelUnits.setFont(self.DefaultFont)
        self.Period.LineEdit.setFont(self.DefaultFont)
        self.Period.LineEdit.setValidator(QRegExpValidator(QRegExp("[+-]?[0-9]{1,2}[\.][0-9]{1,2}")))
        self.Period.LineEdit.setText('0')
        layout.addWidget(self.Period, alignment=Qt.AlignTop)
        
        layout.addStretch()

        self.Period.textEdited.connect(self.changePeriod)

    def deviceSettingsInit(self):
        self.DeviceSettingsGroupBox = QGroupBox('Настройки устройства')
        self.DeviceSettingsGroupBox.setFont(QFont('Times',10))
        layout = QGridLayout()
        layout.setSpacing(0)
        self.DeviceSettingsGroupBox.setLayout(layout)

        self.outputDevices = getAudioDevice("output")
        self.devices_list = []
        for device in self.outputDevices:
            self.devices_list.append(device["name"])
        
        self.deviceComboBox = QComboBox()
        self.deviceComboBox.addItems(self.devices_list)

        self.deviceComboBox.currentIndexChanged.connect(self.changeAudioDevice)
        layout.addWidget(self.deviceComboBox)

    def changeAudioDevice(self, index):
        self.outputDeviceChanged.emit(self.outputDevices[index]["index"])

    def SignalTypeInit(self):
        self.signalTypesGroupBox = QGroupBox('Тип сигнала')
        self.signalTypesGroupBox.setFont(self.DefaultFont)
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
        self.SignalsType[0].clicked.connect(lambda: self.SignalTypeSwitched(SignalType.TRIANGLE,0))
        self.SignalsType[1].clicked.connect(lambda: self.SignalTypeSwitched(SignalType.SAWTOOTH_FRONT,1))
        self.SignalsType[0].setIcon(QIcon('ExtraFiles/Icons/Triangle2.png'))
        self.SignalsType[0].setIconSize(QSize(400,255)) 
        self.SignalsType[1].setIcon(QIcon('ExtraFiles/Icons/Triangle2.png'))
        self.SignalsType[1].setIconSize(QSize(400,255))

    def SignalTypeSwitched(self,signalType, buttonNum:int):
        for RadioButton in self.SignalsType:
            RadioButton.blockSignals(False)
        self.SignalsType[buttonNum].blockSignals(True)
        self.signalTypeChanged.emit(signalType)
        print(signalType)

    def convertBackToFloat(self, value):
        try:
            return float(value)
        except:
            pass
    def convertToStr(self, value):
        return str(value)
    
    def changePeriod(self, value):
        self.signalPeriodChanged.emit(value)
        print(value)



if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = SettingsWindowTransmitter()
    main.show()

    sys.exit(app.exec_())