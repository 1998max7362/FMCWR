import sys
sys.path.insert(0, "././utils/constants")
sys.path.insert(0, "././utils/components")
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import *
from getAudioDevice import getAudioDevice
from PyQt5.QtCore import *
from WrapedUiElements import *
from SignalSource import SignalSource
from PyQt5.QtWidgets import *

class SettingsWindowReciever(QWidget):
    inputDeviceChanged = pyqtSignal(object)
    startToggled = pyqtSignal(object)
    sampleRateChanged = pyqtSignal(object)
    signalSourceChanged = pyqtSignal(object)
    downSamplingChanged = pyqtSignal(object)
    yRangeChanged = pyqtSignal(object)
    def __init__(self):
        super().__init__()

        DefaultFont = QFont('Times', 10)
        self.inputAudioDeviceList = getAudioDevice("input")

        self.setWindowTitle("Настройки")
        self.setFixedWidth(440)
        layout = QVBoxLayout(self)

        self.deviceSettingsGroupBox = self.createDeviceSettingsGroupBox(DefaultFont)
        layout.addWidget(self.deviceSettingsGroupBox)

        plotSettingsGroupBox = self.createGraphSettingsGroupBox(DefaultFont)
        layout.addWidget(plotSettingsGroupBox)

        self.startStopButton = ToggleButton(
            textNotClicked='Start',
            textClicked='Stop',
            styleSheetNotClicked="background-color: white",
            styleSheetClicked="background-color: green")
        self.startStopButton.setFont(DefaultFont)
        self.startStopButton.setToolTip('Запуск устройства')
        self.startStopButton.toggled.connect(self.startStop)
        layout.addWidget(self.startStopButton)

        self.errorLabel = QLabel('')
        self.errorLabel.setFixedHeight(20)
        layout.addWidget(self.errorLabel)
    
    def setErrorText(self, text:str):
        errorIcon = QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical)
        if text!='':
            self.errorLabel.setPixmap(errorIcon.pixmap(QSize(20, 20)))
            self.startStopButton.toggle()
        self.errorLabel.setText(text)

    def startStop(self,state):
        self.startToggled.emit(state)
        self.deviceSettingsGroupBox.setEnabled(not state)
    
    def createGraphSettingsGroupBox(self, DefaultFont):
        plotSettingsGroupBox = QGroupBox('Настройки графиков')
        plotSettingsGroupBox.setFont(QFont('Times', 10))
        layout = QVBoxLayout()
        plotSettingsGroupBox.setLayout(layout)

        downSamplingSpinBox = NamedHorizontalSpinBox('downsample', '')
        downSamplingSpinBox.setFixedWidth(400)
        downSamplingSpinBox.label.setFixedWidth(210)
        downSamplingSpinBox.spinBox.setFixedWidth(100)
        downSamplingSpinBox.spinBox.setMaximum(100)
        downSamplingSpinBox.spinBox.setValue(10)
        downSamplingSpinBox.valueChanged.connect(self.changeSampleRate)
        layout.addWidget(downSamplingSpinBox)

        updateIntervalSpinBox = NamedHorizontalSpinBox('Интервал обновления', 'мс')
        updateIntervalSpinBox.setFixedWidth(400)
        updateIntervalSpinBox.label.setFixedWidth(210)
        updateIntervalSpinBox.spinBox.setFixedWidth(100)
        updateIntervalSpinBox.spinBox.setMaximum(100000)
        updateIntervalSpinBox.spinBox.setValue(10)
        updateIntervalSpinBox.valueChanged.connect(self.changeSampleRate)
        layout.addWidget(updateIntervalSpinBox)

        warningIcon = QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning)
        chart0SettingsGroupBox = self.createChart0SettingsGroupBox(warningIcon)
        chart1SettingsGroupBox = self.createChart1SettingsGroupBox(warningIcon)
        layout.addWidget(chart0SettingsGroupBox)
        layout.addWidget(chart1SettingsGroupBox)

        return plotSettingsGroupBox
    
    def createChart1SettingsGroupBox(self,warningIcon):
        chart1SettingsBox = QGroupBox('График 1')
        layout = QVBoxLayout()
        chart1SettingsBox.setLayout(layout)

        self.xMax=NamedDoubleSliderHorizontal('Xmax')
        self.xMax.labelUnits.setPixmap(warningIcon.pixmap(QSize(20, 20)))
        self.xMax.labelUnits.setToolTip('Xmax не может меньше больше либо равно Xmin')
        self.xMax.labelUnits.setHidden(True)
        self.xMax.label.setFixedWidth(50)
        self.xMax.slider.setFixedWidth(140)
        self.xMax.slider.setMinimum(1)
        self.xMax.slider.setMaximum(20000)
        self.xMax.slider.setValue(20000)
        self.xMax.slider.setSingleStep(1)  # Сначала нужно ставить шаг
        self.xMax.spinBox.setMinimum(1)
        self.xMax.spinBox.setMaximum(20000)
        self.xMax.spinBox.setValue(20000)

        self.xMin=NamedDoubleSliderHorizontal('Xmin')
        self.xMin.labelUnits.setPixmap(warningIcon.pixmap(QSize(20, 20)))
        self.xMin.labelUnits.setToolTip('Xmin не может быть больше либо равно Xmax')
        self.xMin.labelUnits.setHidden(True)
        self.xMin.label.setFixedWidth(50)
        self.xMin.slider.setFixedWidth(140)
        self.xMin.slider.setMinimum(1)
        self.xMin.slider.setMaximum(20000)
        self.xMin.slider.setValue(1)
        self.xMin.slider.setSingleStep(1)  # Сначала нужно ставить шаг
        self.xMin.spinBox.setMinimum(1)
        self.xMin.spinBox.setMaximum(20000)
        self.xMin.spinBox.setValue(1)

        self.xMax.valueChanged.connect(self.changeXRange)
        self.xMin.valueChanged.connect(self.changeXRange)

        layout.addWidget(self.xMax)
        layout.addWidget(self.xMin)
        
        return chart1SettingsBox    
    
    def createChart0SettingsGroupBox(self,warningIcon):
        chart0SettingsBox = QGroupBox('График 0')
        layout = QVBoxLayout()
        chart0SettingsBox.setLayout(layout)

        self.yMax=NamedDoubleSliderHorizontal('Ymax')
        self.yMax.labelUnits.setPixmap(warningIcon.pixmap(QSize(20, 20)))
        self.yMax.labelUnits.setToolTip('Ymax не может меньше больше либо равно Ymin')
        self.yMax.labelUnits.setHidden(True)
        self.yMax.label.setFixedWidth(50)
        self.yMax.slider.setFixedWidth(140)
        self.yMax.slider.setMinimum(-10)
        self.yMax.slider.setMaximum(10)
        self.yMax.slider.setValue(1)
        self.yMax.slider.setSingleStep(0.1)  # Сначала нужно ставить шаг
        self.yMax.spinBox.setMinimum(-10)
        self.yMax.spinBox.setMaximum(10)
        self.yMax.spinBox.setValue(1)

        self.yMin=NamedDoubleSliderHorizontal('Ymin')
        self.yMin.labelUnits.setPixmap(warningIcon.pixmap(QSize(20, 20)))
        self.yMin.labelUnits.setToolTip('Ymin не может быть больше либо равно Ymax')
        self.yMin.labelUnits.setHidden(True)
        self.yMin.label.setFixedWidth(50)
        self.yMin.slider.setFixedWidth(140)
        self.yMin.slider.setMinimum(-10)
        self.yMin.slider.setMaximum(10)
        self.yMin.slider.setValue(-1)
        self.yMin.slider.setSingleStep(0.1)  # Сначала нужно ставить шаг
        self.yMin.spinBox.setMinimum(-10)
        self.yMin.spinBox.setMaximum(10)
        self.yMin.spinBox.setValue(-1)

        self.yMax.valueChanged.connect(self.changeYRange)
        self.yMin.valueChanged.connect(self.changeYRange)

        layout.addWidget(self.yMax)
        layout.addWidget(self.yMin)
        
        return chart0SettingsBox

    def changeYRange(self):
        if self.yMin.spinBox.value() < self.yMax.spinBox.value():
            self.yRangeChanged.emit([self.yMin.spinBox.value(), self.yMax.spinBox.value()])
            self.yMin.labelUnits.setHidden(True)
            self.yMax.labelUnits.setHidden(True)
        else:
            self.yMin.labelUnits.setHidden(False)
            self.yMax.labelUnits.setHidden(False)

    def changeXRange(self):
        if self.xMin.spinBox.value() < self.xMax.spinBox.value():
            self.yRangeChanged.emit([self.xMin.spinBox.value(), self.xMax.spinBox.value()])
            self.xMin.labelUnits.setHidden(True)
            self.xMax.labelUnits.setHidden(True)
        else:
            self.xMin.labelUnits.setHidden(False)
            self.xMax.labelUnits.setHidden(False)

    def changeDownSampling(self, value):
        self.downSamplingChanged.emit(value)


    def createDeviceSettingsGroupBox(self, DefaultFont):
        deviceSettingsGroupBox = QGroupBox('Настройки устройства')
        deviceSettingsGroupBox.setFont(DefaultFont)

        layout = QGridLayout()
        layout.setSpacing(0)
        deviceSettingsGroupBox.setLayout(layout)

        deviceComboBox = QComboBox()
        for inputDevice in self.inputAudioDeviceList:
            deviceComboBox.addItem(inputDevice["name"])
        deviceComboBox.currentIndexChanged.connect(self.changeInputDevice)
        layout.addWidget(deviceComboBox)

        sampleRateSpinBox = NamedHorizontalSpinBox('Частота дискретизации', 'Гц')
        sampleRateSpinBox.setFixedWidth(400)
        sampleRateSpinBox.label.setFixedWidth(210)
        sampleRateSpinBox.spinBox.setFixedWidth(100)
        sampleRateSpinBox.spinBox.setMaximum(1000000)
        sampleRateSpinBox.spinBox.setValue(44100)
        sampleRateSpinBox.valueChanged.connect(self.changeSampleRate)
        layout.addWidget(sampleRateSpinBox)

        self.signalSourceSwitcher = NamedHorizontalSwitcher('Дальность', 'Скорость')
        self.signalSourceSwitcher.Switcher.setFixedWidth(150)
        self.signalSourceSwitcher.LeftLabel.setFixedWidth(100)
        self.signalSourceSwitcher.RightLabel.setFixedWidth(100)
        self.signalSourceSwitcher.stateChanged.connect(self.switchSignalSource)
        self.switchSignalSource(self.signalSourceSwitcher.Switcher.checkState())
        layout.addWidget(self.signalSourceSwitcher)

        return deviceSettingsGroupBox

    def changeInputDevice(self, index):
        deviceId = self.inputAudioDeviceList[index]["index"]
        self.inputDeviceChanged.emit(deviceId)
    
    def changeSampleRate(self,value):
        self.sampleRateChanged.emit(value)

    def switchSignalSource(self, state):
        boldFont = QFont('Times', 10)
        boldFont.setBold(True)
        unboldFont = QFont('Times', 10)
        unboldFont.setBold(False)
        if state == 0:
            self.signalSourceSwitcher.RightLabel.setFont(unboldFont)
            self.signalSourceSwitcher.LeftLabel.setFont(boldFont)
            source = SignalSource.RANGE
        if state == 2:
            self.signalSourceSwitcher.LeftLabel.setFont(unboldFont)
            self.signalSourceSwitcher.RightLabel.setFont(boldFont)
            source = SignalSource.VELOCITY
        self.signalSourceChanged.emit(source)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = SettingsWindowReciever()
    main.show()

    sys.exit(app.exec_())