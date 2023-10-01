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

        self.outputDeviceList = getAudioDevice("output")

        self.currentSignalType = SignalType.TRIANGLE
        self.currentPeriod = 10
        self.currentOutputDevice = self.outputDeviceList[5]["index"]

        self.setWindowTitle("Настройки")
        self.setFixedWidth(440)
        layout = QVBoxLayout(self)
        
        self.DefaultFont = QFont('Times',10)
        self.setFont(self.DefaultFont)

        self.deviceSettingsInit()
        layout.addWidget(self.DeviceSettingsGroupBox)

        self.initSignalType()
        layout.addWidget(self.signalTypesGroupBox)

        preiodSpinBox = NamedHorizontalSpinBox('Период', 'мкс')
        preiodSpinBox.setFixedWidth(400)
        preiodSpinBox.label.setFixedWidth(210)
        preiodSpinBox.spinBox.setFixedWidth(100)
        preiodSpinBox.spinBox.setMaximum(100)
        preiodSpinBox.spinBox.setValue(self.currentPeriod)
        preiodSpinBox.valueChanged.connect(self.changePeriod)
        layout.addWidget(preiodSpinBox)

        layout.addStretch()

    def deviceSettingsInit(self):
        self.DeviceSettingsGroupBox = QGroupBox('Настройки устройства')
        self.DeviceSettingsGroupBox.setFont(QFont('Times',10))
        layout = QGridLayout()
        layout.setSpacing(0)
        self.DeviceSettingsGroupBox.setLayout(layout)
        
        self.deviceComboBox = QComboBox()
        for outputDevice in self.outputDeviceList:
            self.deviceComboBox.addItem(outputDevice["name"])
            if self.currentOutputDevice == outputDevice['index']:
                print(self.deviceComboBox.count())
                self.deviceComboBox.setCurrentIndex(self.deviceComboBox.count()-1)
        self.deviceComboBox.currentIndexChanged.connect(self.changeAudioDevice)
        layout.addWidget(self.deviceComboBox)

    def changeAudioDevice(self, index):
        self.currentOutputDevice = self.outputDeviceList[index]["index"]
        self.outputDeviceChanged.emit(self.currentOutputDevice)

    def initSignalType(self):
        self.signalTypesGroupBox = QGroupBox('Тип сигнала')
        self.signalTypesGroupBox.setFont(self.DefaultFont)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.signalTypesGroupBox.setLayout(layout)
        self.signalTypes = []
        signalTypeSelecter = QButtonGroup(self)
        signalTypeSelecter.setExclusive(True)
        for type in SignalType:
            signalTypeButton = QRadioButton()
            signalTypeButton.clicked.connect(lambda checked,type=type: self.switchSignalType(type))
            signalTypeButton.setIcon(QIcon(type.IconPath))
            signalTypeButton.setIconSize(QSize(400, 255))
            signalTypeSelecter.addButton(signalTypeButton)
            layout.addWidget(signalTypeButton)
            if type == self.currentSignalType: 
                signalTypeButton.setChecked(True)

    def switchSignalType(self,signalType):
        print(signalType)
        self.currentSignalType = signalType
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

    sys.exit(app.exec_())