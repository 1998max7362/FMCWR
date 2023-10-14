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
import sounddevice as sd

class SettingsWindowReciever(QWidget):
    inputDeviceChanged = pyqtSignal(object)
    startToggled = pyqtSignal(object)
    sampleRateChanged = pyqtSignal(object)
    updateIntervalChanged = pyqtSignal(object)
    signalSourceChanged = pyqtSignal(object)
    downSamplingChanged = pyqtSignal(object)
    yRangeChanged = pyqtSignal(object)
    xRangeChanged = pyqtSignal(object)
    def __init__(self):
        super().__init__()

        DefaultFont = QFont('Times', 10)
        self.inputAudioDeviceList = getAudioDevice("input")

        # Начальные значения
        self.currentInputDevice = self.inputAudioDeviceList[1]["index"] 
        self.currentSampleRate = 44100
        self.currentUpdateInterval = 20
        self.currentSignalSource = SignalSource.RANGE
        self.currentDownSampling = 10
        self.currentYRange = [-1,1]
        self.currentXRange = [1, 20000]

        self.setWindowTitle("Настройки")
        self.setFixedWidth(440)
        layout = QVBoxLayout(self)

        self.deviceSettingsGroupBox = self.createDeviceSettingsGroupBox(DefaultFont)
        layout.addWidget(self.deviceSettingsGroupBox)

        plotSettingsGroupBox = self.createGraphSettingsGroupBox()
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
        layout.addWidget(self.errorLabel)

        layout.addStretch()
    
    def setErrorText(self, text:str):
        errorIcon = QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical)
        if text!='':
            self.deviceSettingsGroupBox.setEnabled(True)
            self.errorLabel.setPixmap(errorIcon.pixmap(QSize(20, 20)))
            self.startStopButton.toggle()
        self.errorLabel.setText(text)

    def startStop(self,state):
        self.deviceSettingsGroupBox.setEnabled(not state)
        self.startToggled.emit(state)
        
    
    def createGraphSettingsGroupBox(self):
        plotSettingsGroupBox = QGroupBox('Настройки графиков')
        plotSettingsGroupBox.setFont(QFont('Times', 10))
        layout = QVBoxLayout()
        plotSettingsGroupBox.setLayout(layout)

        downSamplingSpinBox = NamedHorizontalSpinBox('downsample', '')
        downSamplingSpinBox.setFixedWidth(400)
        downSamplingSpinBox.label.setFixedWidth(210)
        downSamplingSpinBox.spinBox.setFixedWidth(100)
        downSamplingSpinBox.spinBox.setMaximum(100)
        downSamplingSpinBox.spinBox.setValue(self.currentDownSampling)
        downSamplingSpinBox.valueChanged.connect(self.changeDownSampling)
        layout.addWidget(downSamplingSpinBox)

        updateIntervalSpinBox = NamedHorizontalSpinBox('Интервал обновления', 'мс')
        updateIntervalSpinBox.setFixedWidth(400)
        updateIntervalSpinBox.label.setFixedWidth(210)
        updateIntervalSpinBox.spinBox.setFixedWidth(100)
        updateIntervalSpinBox.spinBox.setMaximum(100000)
        updateIntervalSpinBox.spinBox.setValue(self.currentUpdateInterval)
        updateIntervalSpinBox.valueChanged.connect(self.changeUpdateInterval)
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
        self.xMax.slider.setValue(self.currentXRange[1])
        self.xMax.slider.setSingleStep(1)  # Сначала нужно ставить шаг
        self.xMax.spinBox.setMinimum(1)
        self.xMax.spinBox.setMaximum(20000)
        self.xMax.spinBox.setValue(self.currentXRange[1])
        self.xMax.spinBox.setSingleStep(0.1)

        self.xMin=NamedDoubleSliderHorizontal('Xmin')
        self.xMin.labelUnits.setPixmap(warningIcon.pixmap(QSize(20, 20)))
        self.xMin.labelUnits.setToolTip('Xmin не может быть больше либо равно Xmax')
        self.xMin.labelUnits.setHidden(True)
        self.xMin.label.setFixedWidth(50)
        self.xMin.slider.setFixedWidth(140)
        self.xMin.slider.setMinimum(1)
        self.xMin.slider.setMaximum(20000)
        self.xMin.slider.setValue(self.currentXRange[0])
        self.xMin.slider.setSingleStep(1)  # Сначала нужно ставить шаг
        self.xMin.spinBox.setMinimum(1)
        self.xMin.spinBox.setMaximum(20000)
        self.xMin.spinBox.setValue(self.currentXRange[0])
        self.xMin.spinBox.setSingleStep(0.1)

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
        self.yMax.slider.setValue(self.currentYRange[1])
        self.yMax.slider.setSingleStep(0.1)  # Сначала нужно ставить шаг
        self.yMax.spinBox.setMinimum(-10)
        self.yMax.spinBox.setMaximum(10)
        self.yMax.spinBox.setValue(self.currentYRange[1])
        self.yMax.spinBox.setSingleStep(0.1)

        self.yMin=NamedDoubleSliderHorizontal('Ymin')
        self.yMin.labelUnits.setPixmap(warningIcon.pixmap(QSize(20, 20)))
        self.yMin.labelUnits.setToolTip('Ymin не может быть больше либо равно Ymax')
        self.yMin.labelUnits.setHidden(True)
        self.yMin.label.setFixedWidth(50)
        self.yMin.slider.setFixedWidth(140)
        self.yMin.slider.setMinimum(-10)
        self.yMin.slider.setMaximum(10)
        self.yMin.slider.setValue(self.currentYRange[0])
        self.yMin.slider.setSingleStep(0.1)  # Сначала нужно ставить шаг
        self.yMin.spinBox.setMinimum(-10)
        self.yMin.spinBox.setMaximum(10)
        self.yMin.spinBox.setValue(self.currentYRange[0])
        self.yMin.spinBox.setSingleStep(0.1)

        self.yMax.valueChanged.connect(self.changeYRange)
        self.yMin.valueChanged.connect(self.changeYRange)

        layout.addWidget(self.yMax)
        layout.addWidget(self.yMin)
        
        return chart0SettingsBox

    def changeYRange(self):
        self.currentYRange= [self.yMin.spinBox.value(), self.yMax.spinBox.value()]
        if self.currentYRange[0] < self.currentYRange[1]:
            self.yRangeChanged.emit(self.currentYRange)
            self.yMin.labelUnits.setHidden(True)
            self.yMax.labelUnits.setHidden(True)
        else:
            self.yMin.labelUnits.setHidden(False)
            self.yMax.labelUnits.setHidden(False)

    def changeXRange(self):
        self.currentXRange = [self.xMin.spinBox.value(), self.xMax.spinBox.value()]
        if self.currentXRange[0] < self.currentXRange[1]:
            self.xRangeChanged.emit(self.currentXRange)
            self.xMin.labelUnits.setHidden(True)
            self.xMax.labelUnits.setHidden(True)
        else:
            self.xMin.labelUnits.setHidden(False)
            self.xMax.labelUnits.setHidden(False)

    def changeDownSampling(self, value):
        self.currentDownSampling = value
        self.downSamplingChanged.emit(self.currentDownSampling)


    def createDeviceSettingsGroupBox(self, DefaultFont):
        deviceSettingsGroupBox = QGroupBox('Настройки устройства')
        deviceSettingsGroupBox.setFont(DefaultFont)

        layout = QGridLayout()
        layout.setSpacing(0)
        deviceSettingsGroupBox.setLayout(layout)

        deviceComboBox = QComboBox()
        inputId,_=sd.default.device
        for inputDevice in self.inputAudioDeviceList:
            deviceComboBox.addItem(inputDevice["name"])
            inputId,_=sd.default.device
            if inputId == inputDevice['index']:
                deviceComboBox.setCurrentIndex(deviceComboBox.count()-1)
        deviceComboBox.currentIndexChanged.connect(self.changeInputDevice)
        layout.addWidget(deviceComboBox)

        sampleRateSpinBox = NamedHorizontalSpinBox('Частота дискретизации', 'Гц')
        sampleRateSpinBox.setFixedWidth(400)
        sampleRateSpinBox.label.setFixedWidth(210)
        sampleRateSpinBox.spinBox.setFixedWidth(100)
        sampleRateSpinBox.spinBox.setMaximum(1000000)
        sampleRateSpinBox.spinBox.setValue(self.currentSampleRate)
        sampleRateSpinBox.valueChanged.connect(self.changeSampleRate)
        layout.addWidget(sampleRateSpinBox)

        self.signalSourceSwitcher = NamedHorizontalSwitcher('Дальность', 'Скорость')
        self.signalSourceSwitcher.Switcher.setFixedWidth(150)
        self.signalSourceSwitcher.LeftLabel.setFixedWidth(100)
        self.signalSourceSwitcher.RightLabel.setFixedWidth(100)
        self.signalSourceSwitcher.Switcher.setCheckState(self.currentSignalSource.value)
        self.signalSourceSwitcher.stateChanged.connect(self.switchSignalSource)
        layout.addWidget(self.signalSourceSwitcher)

        return deviceSettingsGroupBox

    def changeInputDevice(self, index):
        deviceId = self.inputAudioDeviceList[index]["index"]
        self.currentInputDevice = deviceId
        self.inputDeviceChanged.emit(self.currentInputDevice)
    
    def changeSampleRate(self,value):
        self.currentSampleRate = value
        self.sampleRateChanged.emit(self.currentSampleRate)

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
        self.currentSignalSource = source
        self.signalSourceChanged.emit(self.currentSignalSource)
    
    def changeUpdateInterval(self,value):
        self.currentUpdateInterval = value
        self.updateIntervalChanged.emit(self.currentUpdateInterval)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = SettingsWindowReciever()
    main.show()

    sys.exit(app.exec_())