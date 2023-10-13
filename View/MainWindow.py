import sys, os
sys.path.insert(0, "././utils/components")
sys.path.insert(0, "././Model/")
sys.path.insert(0, "././View/")
sys.path.insert(0, "././Test/")
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import *
from multiprocessing import Queue
import numpy as np
from scipy.io.wavfile import write
from datetime import datetime

from SettingsWindowReciever import SettingsWindowReciever
from SettingsWindowTransmitter import SettingsWindowTransmitter
from mainWaterfall import WaterFallWindow
from mainGraph import GraphWindow
from Worker import *
from WrapedUiElements import *
from TrancieverProcess import TrancieverProcess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.wavData=np.array([])

        self.setWindowTitle('Главное меню')
        layout = QHBoxLayout(self)

        self.recievedSignal = Queue(maxsize=5) # Очередь для записи принятого сигнала
        self.transmittedSignal = Queue(maxsize=5) # Очередь для записи излученного сигнала

        self._createActions()
        self._connectActions()
        self._createMenubar()
        
        self.settingsWindowReciever = SettingsWindowReciever()
        self.settingsWindowTransmitter = SettingsWindowTransmitter()
        self.Chart0 = GraphWindow()
        self.Chart1 = WaterFallWindow()
        self.chartUpdateTimer = QtCore.QTimer()
        
        self.Chart0.setMinimumSize(300,200)
        self.Chart1.setMinimumSize(300,200)


        # Dock Widgets
        self.dockSettingsWindowReciever = QDockWidget()
        self.dockSettingsWindowReciever.setWindowTitle('Приёмник')
        self.dockSettingsWindowReciever.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.dockSettingsWindowReciever.setWidget(self.settingsWindowReciever)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockSettingsWindowReciever)

        self.dockSettingsWindowTransmitter = QDockWidget()
        self.dockSettingsWindowTransmitter.setWindowTitle('Передатчик')
        self.dockSettingsWindowTransmitter.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.dockSettingsWindowTransmitter.setWidget(self.settingsWindowTransmitter)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockSettingsWindowTransmitter)

        self.tabifyDockWidget(self.dockSettingsWindowTransmitter, self.dockSettingsWindowReciever)

        self.dockChart0 = QDockWidget("Осциллограмма ")
        self.dockChart0.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.dockChart0.setWidget(self.Chart0)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockChart0)

        self.dockChart1 = QDockWidget("Спектрограмма ")
        self.dockChart1.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.dockChart1.setWidget(self.Chart1)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockChart1)

        # Set initial values
        self.setSignalSource(self.settingsWindowReciever.currentSignalSource)
        self.setDownSampling(self.settingsWindowReciever.currentDownSampling)
        self.chartUpdateTimer.setInterval(self.settingsWindowReciever.currentUpdateInterval)
        self.Chart0.setRangeY(self.settingsWindowReciever.currentYRange)
        self.Chart1.setRangeX(self.settingsWindowReciever.currentXRange)
        self.Chart1.set_fs(self.settingsWindowReciever.currentSampleRate)
        self.Chart1.set_tSeg(self.settingsWindowTransmitter.currentPeriod)

        # Set connections
        self.settingsWindowReciever.startToggled.connect(self.runStop)
        self.settingsWindowReciever.updateIntervalChanged.connect(self.setChartUpdateInterval)
        self.settingsWindowReciever.signalSourceChanged.connect(self.setSignalSource)
        self.settingsWindowReciever.downSamplingChanged.connect(self.setDownSampling)
        self.settingsWindowReciever.downSamplingChanged.connect(self.Chart1.set_fs)
        self.settingsWindowReciever.yRangeChanged.connect(self.Chart0.setRangeY)
        self.settingsWindowReciever.xRangeChanged.connect(self.Chart1.setRangeX)
        self.settingsWindowTransmitter.signalPeriodChanged.connect(self.Chart1.set_tSeg)
        self.chartUpdateTimer.timeout.connect(self.updateCharts)

        self.updateTranciever()
    
    def updateTranciever(self):
        self.tranciever = TrancieverProcess(self.recievedSignal,self.transmittedSignal)
        # Set initial values
        self.tranciever.setSignalSource(self.settingsWindowReciever.currentSignalSource)
        self.tranciever.setSignalType(self.settingsWindowTransmitter.currentSignalType) 
        self.tranciever.setSignalPeriod(self.settingsWindowTransmitter.currentPeriod) 
        self.tranciever.setOutputDevice(self.settingsWindowTransmitter.currentOutputDevice) 
        self.tranciever.setInputDevice(self.settingsWindowReciever.currentInputDevice)
        self.tranciever.setSamplerate(self.settingsWindowReciever.currentSampleRate) 
        self.Chart0.setMaxRangeX(self.tranciever.blockSize*10)
        self.setTrancieverConnections()

    def setTrancieverConnections(self):
        # Set connections
        self.settingsWindowReciever.inputDeviceChanged.connect(self.tranciever.setInputDevice)
        self.settingsWindowReciever.sampleRateChanged.connect(self.tranciever.setSamplerate)
        self.settingsWindowReciever.signalSourceChanged.connect(self.tranciever.setSignalSource)
        self.settingsWindowTransmitter.signalTypeChanged.connect(self.tranciever.setSignalType)
        self.settingsWindowTransmitter.signalPeriodChanged.connect(self.tranciever.setSignalPeriod)
        self.settingsWindowTransmitter.outputDeviceChanged.connect(self.tranciever.setOutputDevice)
        # self.tranciever.errorAppeared.connect(self.settingsWindowReciever.setErrorText)

    def unsetTrancieverConnections(self):
        # Unset connections
        self.settingsWindowReciever.inputDeviceChanged.disconnect(self.tranciever.setInputDevice)
        self.settingsWindowReciever.sampleRateChanged.disconnect(self.tranciever.setSamplerate)
        self.settingsWindowTransmitter.signalTypeChanged.disconnect(self.tranciever.setSignalType)
        self.settingsWindowTransmitter.signalPeriodChanged.disconnect(self.tranciever.setSignalPeriod)
        self.settingsWindowTransmitter.outputDeviceChanged.disconnect(self.tranciever.setOutputDevice)
        # self.tranciever.errorAppeared.connect(self.settingsWindowReciever.setErrorText)
    
    def updateCharts(self):
        indata = np.concatenate(self.tranciever.recievedSignal.get()) 
        downSampledIndata = indata[::self.downSampling]
        self.Chart0.plotData(downSampledIndata)
        self.Chart1.specImage(indata)
        self.wavData=np.append(self.wavData, indata)
        # print('update')

    def runStop(self, state):
        if state:
            self.settingsWindowTransmitter.setEnabled(False)
            self.wavData=np.array([])
            self.Chart0.clearPlots(True) 
            self.unsetTrancieverConnections()
            self.chartUpdateTimer.start()
            self.tranciever.start()
        else:
            self.settingsWindowTransmitter.setEnabled(True)
            self.chartUpdateTimer.stop()
            self.tranciever.end_process()
            self.updateTranciever()

    def setChartUpdateInterval(self,value):
        self.chartUpdateTimer.setInterval(value)
    
    def setSignalSource(self, value):
        self.signalSource = value
    
    def setDownSampling(self, value):
        self.downSampling = value
    
    def _createMenubar(self):
        # делаем пользовательское меню
        menuBar = self.menuBar()
        self.MainWindowMenuBar = menuBar.addMenu("&Файл")
        self.MainWindowMenuBar.addAction(self.saveAction)

    def _createActions(self):
        # делаем кнопки пользовательского меню
        self.saveAction = QAction("&Сохранить",self)
    
    def _connectActions(self):
        # соединяем кнопки пользовательского меню с обработчиками событий
        self.saveAction.triggered.connect(self.saveFile)

    def _saveFileDialog(self,text):
        # настройка диалогового окна сохраанения файла 
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,text,"","All Files (*);;wav files (*.wav)", options=options)
        return fileName
    
    def saveFile(self):
        #  создаем диалоговое окно сохранения файла 
        filename = self._saveFileDialog('Сохранение сигнала')
        if filename!='':
            write(filename+'_'+self.getCurDateTime()+".wav", int(self.settingsWindowReciever.currentSampleRate), self.wavData.astype(np.float32))
            self.wavData = np.array([])
            QMessageBox.information(self,'Сохранение данных', 'Сохранено')

    def getCurDateTime(self):
        # возвращает метку времени ггггммдд_ччммсс
        now = datetime.now()
        current_date_time = str(now.year)+str(now.month)+str(now.day)+'_'+str(now.hour)+str(now.minute)+str(now.second)
        return current_date_time

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())