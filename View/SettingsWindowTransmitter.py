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

        # self.currentSignalType
        # self.currentPeriod
        # self.currentOutputDevice

        self.setWindowTitle("Настройки")
        self.setFixedWidth(440)
        layout = QVBoxLayout(self)
        
        self.DefaultFont = QFont('Times',10)

        self.deviceSettingsInit()
        layout.addWidget(self.DeviceSettingsGroupBox)

        self.initSignalType()
        layout.addWidget(self.signalTypesGroupBox)

        self.period = NewNamedLineEditHorizontal("Период:", "мкс")
        self.period.label.setFont(self.DefaultFont)
        self.period.labelUnits.setFont(self.DefaultFont)
        self.period.LineEdit.setFont(self.DefaultFont)
        self.period.LineEdit.setValidator(QRegExpValidator(QRegExp("[+-]?[0-9]{1,2}[\.][0-9]{1,2}")))
        self.period.LineEdit.setText('20')
        layout.addWidget(self.period, alignment=Qt.AlignTop)
        layout.addStretch()

        self.period.textEdited.connect(self.changePeriod)
        self.currentPeriod = self.period.LineEdit.text()
        print()

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
        self.currentOutputDevice = self.outputDevices[self.deviceComboBox.currentIndex()]["index"]
        layout.addWidget(self.deviceComboBox)

    def changeAudioDevice(self, index):
        self.currentOutputDevice = self.outputDevices[index]["index"]
        self.outputDeviceChanged.emit(self.currentOutputDevice)

    def initSignalType(self):
        self.signalTypesGroupBox = QGroupBox('Тип сигнала')
        self.signalTypesGroupBox.setFont(self.DefaultFont)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.signalTypesGroupBox.setLayout(layout)
        self.signalsType = []
        signalTypeSelecter = QButtonGroup(self)
        self.signalsType.append(QRadioButton())
        self.signalsType.append(QRadioButton())
        self.signalsType.append(QRadioButton())
        for Signal in self.signalsType:
            signalTypeSelecter.addButton(Signal)
            layout.addWidget(Signal)
        self.signalsType[0].clicked.connect(lambda: self.switchSignalType(SignalType.TRIANGLE,0))
        self.signalsType[1].clicked.connect(lambda: self.switchSignalType(SignalType.SAWTOOTH_FRONT,1))
        self.signalsType[2].clicked.connect(lambda: self.switchSignalType(SignalType.SAWTOOTH_REVERSE,2))
        self.currentSignalType = SignalType.TRIANGLE
        self.signalsType[0].setIcon(QIcon('ExtraFiles/Icons/new/Triangle.png'))
        self.signalsType[0].setIconSize(QSize(400,255)) 
        self.signalsType[1].setIcon(QIcon('ExtraFiles/Icons/new/Sawtooth.png'))
        self.signalsType[1].setIconSize(QSize(400,255))
        self.signalsType[2].setIcon(QIcon('ExtraFiles/Icons/new/SawtoothReverse.png'))
        self.signalsType[2].setIconSize(QSize(400,255))


    def checkSignalTypesSelected(self):
        if self.signalsType[0].isChecked():
            self.switchSignalType(SignalType.TRIANGLE,0)
        if self.signalsType[1].isChecked():
            self.switchSignalType(SignalType.SAWTOOTH_FRONT,1)
        if self.signalsType[2].isChecked():
            self.switchSignalType(SignalType.SAWTOOTH_REVERSE,2)



    def switchSignalType(self,signalType, buttonNum:int):
        self.currentSignalType = signalType
        for RadioButton in self.signalsType:
            RadioButton.blockSignals(False)
        self.signalsType[buttonNum].blockSignals(True)
        self.signalTypeChanged.emit(self.currentSignalType)

    def convertBackToFloat(self, value):
        try:
            return float(value)
        except:
            pass
    def convertToStr(self, value):
        return str(value)
    
    def changePeriod(self, value):
        self.currentPeriod = value
        self.signalPeriodChanged.emit(self.currentPeriod)
        print(value)



if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = SettingsWindowTransmitter()
    main.show()
    main.updateState()

    sys.exit(app.exec_())