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
import sounddevice as sd
class SettingsWindowTransmitter(QWidget):
    signalTypeChanged = pyqtSignal(object)
    signalPeriodChanged = pyqtSignal(object)
    outputDeviceChanged = pyqtSignal(object)
    def __init__(self):
        super().__init__()

        self.outputDeviceList = getAudioDevice("output")

        # Начальные значения
        self.currentSignalType = SignalType.TRIANGLE
        self.currentPeriod = 10
        self.currentOutputDevice = self.outputDeviceList[1]["index"]

        self.setWindowTitle("Настройки")
        self.setFixedWidth(440)
        layout = QVBoxLayout(self)
        
        self.DefaultFont = QFont('Times',10)
        self.setFont(self.DefaultFont)

        deviceSettingsGroupBox = self.createDeviceSettingsGroupBox()
        layout.addWidget(deviceSettingsGroupBox)

        signalTypesGroupBox = self.createSignalTypeGroupBox()
        layout.addWidget(signalTypesGroupBox)

        preiodSpinBox = NamedHorizontalSpinBox('Период', 'мс')
        preiodSpinBox.setFixedWidth(400)
        preiodSpinBox.label.setFixedWidth(210)
        preiodSpinBox.spinBox.setFixedWidth(100)
        preiodSpinBox.spinBox.setMaximum(100)
        preiodSpinBox.spinBox.setValue(self.currentPeriod)
        preiodSpinBox.valueChanged.connect(self.changePeriod)
        layout.addWidget(preiodSpinBox)

        layout.addStretch()

    def createDeviceSettingsGroupBox(self):
        deviceSettingsGroupBox = QGroupBox('Настройки устройства')
        deviceSettingsGroupBox.setFont(QFont('Times',10))
        layout = QGridLayout()
        layout.setSpacing(0)
        deviceSettingsGroupBox.setLayout(layout)
        
        deviceComboBox = QComboBox()
        _,outputId=sd.default.device
        for outputDevice in self.outputDeviceList:
            deviceComboBox.addItem(outputDevice["name"])
            if outputId == outputDevice['index']:
                deviceComboBox.setCurrentIndex(deviceComboBox.count()-1)
        deviceComboBox.currentIndexChanged.connect(self.changeAudioDevice)
        layout.addWidget(deviceComboBox)
        return deviceSettingsGroupBox

    def changeAudioDevice(self, index):
        self.currentOutputDevice = self.outputDeviceList[index]["index"]
        self.outputDeviceChanged.emit(self.currentOutputDevice)

    def createSignalTypeGroupBox(self):
        signalTypesGroupBox = QGroupBox('Тип сигнала')
        signalTypesGroupBox.setFont(self.DefaultFont)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        signalTypesGroupBox.setLayout(layout)
        signalTypeSelecter = QButtonGroup(self)
        signalTypeSelecter.setExclusive(True)
        for type in SignalType:
            signalTypeButton = QRadioButton()
            signalTypeButton.clicked.connect(lambda checked,type=type: self.switchSignalType(type))
            signalTypeButton.setIcon(QIcon(type.IconPath))
            signalTypeButton.setIconSize(QSize(360, 204))
            signalTypeSelecter.addButton(signalTypeButton)
            layout.addWidget(signalTypeButton)
            if type == self.currentSignalType: 
                signalTypeButton.setChecked(True)
        return signalTypesGroupBox

    def switchSignalType(self,signalType):
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



if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = SettingsWindowTransmitter()
    main.show()

    sys.exit(app.exec_())