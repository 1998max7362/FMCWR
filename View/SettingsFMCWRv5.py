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
from PyQt5.QtMultimedia import QAudioDeviceInfo, QAudio
from Clamp import Clamp

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setFixedWidth(440)
        self.warningIcon=QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning)
        layout = QVBoxLayout(self)

        self.StartStopClamp = Clamp()
        self.xRangeClamp = Clamp()
        self.yRangeClamp = Clamp()
        self.SignalTypeClamp=Clamp()
        self.isMeasuring = False
        
        self.DefaultFont = QFont('Times',10)

        self.input_audio_deviceInfos = QAudioDeviceInfo.availableDevices(QAudio.AudioInput)
        #  Настройка параметров устройства
        self.deviceSettings()
        layout.addWidget(self.DeviceSettingsGroupBox)

        #  Настройка параметров графиков
        self.graphSettingsInit()
        layout.addWidget(self.GraphSettingsGroupBox)

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

        self.infoLabel = ClampedLabel()
        self.infoLabel.setStyleSheet('font-size: 12px')
        layout.addWidget(self.infoLabel)
        layout.addStretch()

        self.xRangeChanged(False)
        self.yRangeChanged(False)


    def deviceSettings(self):
        self.DeviceSettingsGroupBox = QGroupBox('Настройки устройства')
        self.DeviceSettingsGroupBox.setFont(QFont('Times',10))
        layout = QGridLayout()
        layout.setSpacing(0)
        self.DeviceSettingsGroupBox.setLayout(layout)

        self.devices_list = []
        for device in self.input_audio_deviceInfos:
            self.devices_list.append(device.deviceName())
        
        self.deviceComboBox = ClampedComboBox()
        self.deviceComboBox.addItems(self.devices_list)
        layout.addWidget(self.deviceComboBox)

        self.SampleRateLineEdit = NamedLineEditHorizontal(ClampedLineEdit(self.convertToStr,self.convertBackToInt),'Частота дискретизации','Гц') 
        self.SampleRateLineEdit.label.setFixedWidth(200)
        self.SampleRateLineEdit.LineEdit.setValidator(QRegExpValidator(QRegExp("[0-9]+")))
        self.SampleRateLineEdit.LineEdit.setText('44100')
        layout.addWidget(self.SampleRateLineEdit)

        self.SignalTypeSwitcher=NamedHorizontalSwitcher('Дальность','Скорость')
        self.SignalTypeSwitcher.Switcher.setFixedWidth(150)
        self.SignalTypeSwitcher.LeftLabel.setFixedWidth(100)
        self.SignalTypeSwitcher.RightLabel.setFixedWidth(100)
        self.SignalTypeSwitcher.Switcher.stateChanged.connect(self.SignalSourceTypeSwitched)
        layout.addWidget(self.SignalTypeSwitcher)

    def graphSettingsInit(self):
        self.GraphSettingsGroupBox = QGroupBox('Настройки графиков')
        self.GraphSettingsGroupBox.setFont(QFont('Times',10))
        layout=QVBoxLayout()
        self.GraphSettingsGroupBox.setLayout(layout)

        self.downSamplLineEdit = NamedLineEditHorizontal(ClampedLineEdit(self.convertToStr,self.convertBackToInt),'downsample',None) 
        self.downSamplLineEdit.label.setFixedWidth(200)
        self.downSamplLineEdit.LineEdit.setValidator(QRegExpValidator(QRegExp("[0-9]{1,2}")))
        self.downSamplLineEdit.LineEdit.setText('10')
        layout.addWidget(self.downSamplLineEdit)

        self.IntervalLineEdit = NamedLineEditHorizontal(ClampedLineEdit(self.convertToStr,self.convertBackToInt),'Интервал обновления','мс') 
        self.IntervalLineEdit.label.setFixedWidth(200)
        self.IntervalLineEdit.LineEdit.setValidator(QRegExpValidator(QRegExp("[0-9]+")))
        self.IntervalLineEdit.LineEdit.setText('10')
        layout.addWidget(self.IntervalLineEdit)

        gridLayout = QGridLayout()
        layout.addLayout(gridLayout)
        gridLayout.setSpacing(0)

        self.Chart0Settings()
        self.Chart1Settings()
        layout.addWidget(self.Chart0SettingsBox)
        layout.addWidget(self.Chart1SettingsBox)

    def Chart0Settings(self):
        self.Chart0SettingsBox = QGroupBox('График 0')
        layout = QVBoxLayout(self)
        self.Chart0SettingsBox.setLayout(layout)
        self.yMin = NamedClampedDoubleSpinBox('Ymin:')
        self.yMax = NamedClampedDoubleSpinBox('Ymax:')
        self.yMin.warning.setPixmap(self.warningIcon.pixmap(QSize(20, 20)))
        self.yMax.warning.setPixmap(self.warningIcon.pixmap(QSize(20, 20)))
        self.yMin.label.setFixedWidth(70)
        self.yMax.label.setFixedWidth(70)
        self.yMin.doubleSpinBox.setMinimum(-100)
        self.yMin.doubleSpinBox.setMaximum(100)
        self.yMax.doubleSpinBox.setMinimum(-100)
        self.yMax.doubleSpinBox.setMaximum(100)
        self.yMin.doubleSpinBox.setValue(-1)
        self.yMin.doubleSpinBox.setSingleStep(0.1)
        self.yMax.doubleSpinBox.setValue(1)
        self.yMax.doubleSpinBox.setSingleStep(0.1)
        self.yMin.warning.setToolTip('Ymin не может быть больше Ymax')
        self.yMax.warning.setToolTip('Ymin не может быть больше Ymax')
        self.yMin.doubleSpinBox.valueChanged.connect(self.yRangeChanged)
        self.yMax.doubleSpinBox.valueChanged.connect(self.yRangeChanged)
        layout.addWidget(self.yMin)
        layout.addWidget(self.yMax)
        
    
    def Chart1Settings(self):
        self.Chart1SettingsBox = QGroupBox('График 1')
        layout = QVBoxLayout(self)
        self.Chart1SettingsBox.setLayout(layout)
        self.xMin = NamedClampedSpinBox('Xmin:')
        self.xMax = NamedClampedSpinBox('Xmax:')
        self.xMin.warning.setPixmap(self.warningIcon.pixmap(QSize(20, 20)))
        self.xMax.warning.setPixmap(self.warningIcon.pixmap(QSize(20, 20)))
        self.xMin.label.setFixedWidth(70)
        self.xMax.label.setFixedWidth(70)
        self.xMin.spinBox.setMinimum(0)
        self.xMin.spinBox.setMaximum(20000)
        self.xMin.spinBox.setValue(0)
        self.xMin.spinBox.setSingleStep(100)
        self.xMax.spinBox.setMinimum(0)
        self.xMax.spinBox.setMaximum(20000)
        self.xMax.spinBox.setValue(20000)
        self.xMax.spinBox.setSingleStep(1)
        self.xMin.warning.setToolTip('Xmin не может быть больше Xmax')
        self.xMax.warning.setToolTip('Xmin не может быть больше Xmax')
        self.xMin.spinBox.valueChanged.connect(self.xRangeChanged)
        self.xMax.spinBox.valueChanged.connect(self.xRangeChanged)
        layout.addWidget(self.xMin)
        layout.addWidget(self.xMax)



    def SignalSourceTypeSwitched(self,type): # 0 - первый источник, 2 - второй источник
        boldFont = QFont('Times',10)
        boldFont.setBold(True)
        unboldFont = QFont('Times',10)
        unboldFont.setBold(False)
        if type == 0:
            self.SignalTypeSwitcher.RightLabel.setFont(unboldFont)
            self.SignalTypeSwitcher.LeftLabel.setFont(boldFont)
            type = SignalSource.RANGE
        if type == 2:
            self.SignalTypeSwitcher.LeftLabel.setFont(unboldFont)
            self.SignalTypeSwitcher.RightLabel.setFont(boldFont)
            type = SignalSource.VELOCITY
        self.SignalTypeClamp.Send(type)
        # print(type)
    
    def convertToStr(self, value):
        if value=='':
            value=1
        return str(value)

    def convertBackToInt(self, value):
        if value=='':
            value=1
        return int(value)

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

        self.deviceComboBox.setEnabled(not self.isMeasuring)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = SettingsWindow()
    main.show()

    sys.exit(app.exec_())

