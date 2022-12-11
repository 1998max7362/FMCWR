import sys, os
sys.path.insert(0, "././Core/")
sys.path.insert(0, "././SignalProcessing/")
sys.path.insert(0, "././View/")
sys.path.insert(0, "././Test/")
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
import time
from threading import Thread
import concurrent.futures as cf

from SettingsFMCWRv6 import SettingsWindow
from mainWaterfall import WaterFallWindow
from mainGraph import GraphWindow
from Clamp import Clamp
from Worker import *
from TestTransiver import TestTranciver
from SignalSource import SignalSource
from Transceiver import Transceiver
# from TestTranciever import Transceiver
from WrapedUiElements import *
import queue
from scipy.io.wavfile import write
from scipy.io import wavfile
from datetime import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.save_signal = queue.Queue()
        self.wav_data=np.array([])
        self.setWindowTitle('Главное меню')
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        # self.threadpool.setMaxThreadCount(1)

        self._createActions()
        self._connectActions()
        self._createMenubar()

        #  Signal Settings
        fs = 44100
        segment = 200 # ms
        self.signalType=SignalSource.RANGE

        # Tranciever
        self.Tranciver = Transceiver()
        self.Tranciver.setDevice(0)             # choose device with hostapi = 0
        self.Tranciver.setChannels(1)           # set number of input channels
        self.Tranciver.setFs(fs) 
        self.Tranciver.downsample = 1

        # Graph window settings
        self.Chart0 = GraphWindow()
        self.Chart1 = WaterFallWindow()
        self.Chart1.set_fs(fs)
        self.Chart1.set_tSeg(segment)
        self.downSample = 10
        self.bufCurrent = np.array([])  # буфер отображаемого фрейма в спектрограмме
        self.bufNext = np.array([])     # буфер следующего фремйа в спектрограмме

        #  Add Clamps
        self.StartStopClamp = Clamp()
        self.SignalTypeClamp = Clamp()

        # разметка
        layout = QHBoxLayout(self)
        # добавление виджетов
        self.settings = SettingsWindow()
        self.dockSettings = QDockWidget()

        self.dockSettings.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)

        self.dockSettings.setWidget(self.settings)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockSettings)

        self.dockGraph0 = QDockWidget("График 0")
        self.dockGraph1 = QDockWidget("График 1")
        self.dockGraph0.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.dockGraph1.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)

        # настройки виджетов
        self.Chart0.setMinimumSize(300,200)
        self.Chart1.setMinimumSize(300,200)
        self.dockGraph0.setWidget(self.Chart0)
        self.dockGraph1.setWidget(self.Chart1)

        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph0)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockGraph1)
        
        self.StartStopClamp.ConnectFrom(self.settings.StartStopClamp)
        self.StartStopClamp.HandleWithReceive(self.StartStop)
        self.SignalTypeClamp.HandleWithReceive(self.getSignalType)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.Process_2)

        self.settings.xRangeClamp.ConnectTo(self.Chart1.rangeClamp)
        self.settings.yRangeClamp.ConnectTo(self.Chart0.rangeClamp)
        self.settings.SignalTypeClamp.ConnectTo(self.SignalTypeClamp)
        self.settings.SignalTypeClamp.ConnectTo(self.Chart1.SignalTypeClamp)

        self.settings.deviceComboBox.currentTextChanged.connect(self.deviceUpdate)
        self.settings.SampleRateLineEdit.LineEdit.Text.ConnectTo(self.Tranciver.FsClamp)
        self.settings.infoLabel.TextClamp.ConnectFrom(self.Tranciver.ErrorClamp)
        self.settings.downSamplLineEdit.LineEdit.Text.HandleWithSend(self.setDownSample)
        self.settings.IntervalLineEdit.LineEdit.Text.HandleWithSend(self.timer.setInterval)

    def StartStop(self,start_stop):
        """ Обработчик нажатия на кнопку Старт/Стоп"""
        print(start_stop) # выводим в поток сообщений value кнопки Старт/Стоп
        if start_stop:
            # нажали на кнопку, получили "1"
            """ проверим для начала пустая ли очередь?
             если она пуста, то идем дальше, а если нет, тогда смотрим
             изменился ли режим работы.
             Режим не менялся - идем дальше
             спектрограмму не сбрасываем
             Режим поменялся - предлагаем сохранить очередь прежде чем писать новую
             сбрасываем спектрограмму для того, чтобы она не поломалась
             """
            # корректируем размер блока обработки
            if self.signalType.value == 0 :
                self.Tranciver.setBlkSz(int(30e-3*self.Tranciver.samplerate)) # на 30 мс для дальности
                
            else:
                self.Tranciver.setBlkSz(int(100e-3*self.Tranciver.samplerate))# на 100 мс для скорости

            self.settings.DeviceSettingsGroupBox.setEnabled(False)  # отключаем часть интерфейса
            self.MainWindowMenuBar.setEnabled(False)                # отключаем часть интерфейса
            self.Chart0.clearPlots(True)                            # ставим признак перерисовки окна
            self.Tranciver.working = True                           # ставим признак работы Tranciver
            self.worker_1  = Worker(self.Tranciver.run_realtime)    # упаковываем в отдельный поток запись с микрофомна
            self.threadpool.start(self.worker_1)                    # запускаем поток получения данных с микрофона
            self.timer.start()                                      # запускаем таймер для передергивания интерфейса
            self.firstQue = True
        else:
            # нажали на кнопку, получили "0"
            self.settings.DeviceSettingsGroupBox.setEnabled(True)   # включаем часть интерфейса
            self.MainWindowMenuBar.setEnabled(True)                # включаем часть интерфейса
            self.Tranciver.working = False                          # ставим признак выключения Tranciver
            self.timer.stop()                                       # отключаем таймер обновления
            # ждем снятия блокировки с очереди для записи и очищаем массив с записанным сигналом
            with self.Tranciver.received_signal.mutex: 
                self.Tranciver.received_signal.queue.clear()
            self.threadpool.clear()

            # saving data from the queue для записи в файл
            while not self.save_signal.empty():
                QtWidgets.QApplication.processEvents()
                self.wav_data=np.append(self.wav_data, self.save_signal.get())

    def Process_2(self):
        self.c = 0
        QtWidgets.QApplication.processEvents()
        if not self.Tranciver.received_signal.empty(): 
            currentData = np.concatenate(self.Tranciver.received_signal.get_nowait())
            oscillogramma=currentData[::self.downSample]
            if self.firstQue:
                xMax = len(currentData)
                self.settings.xMin.slider.setMaximum(xMax)
                self.settings.xMax.slider.setMaximum(xMax)
                self.settings.xMax.slider.setValue(xMax)
                self.settings.xMin.slider.setValue(0)
                self.Chart1.setRangeX([0,xMax])
                self.Chart1.nPerseg = xMax
                self.Chart1.nfft = 2*xMax
                self.firstQue = False
            # одинаковое отображение осциллограм вне зависимости от режима работы
            # self.Chart0.plotData(abs(np.diff(currentData))**2)
            self.Chart0.plotData(oscillogramma)
            # выбор варианта обработки currentData (скорость или дальность)
            if self.signalType.value:
                # "1" обработка скорости 
                self.Chart1.specImage(currentData)
            else:
                # "0" обработка дальности
                # 1) взять производную текущего фрейма
                diffSignal = abs(np.diff(currentData))**2
                # 2) найти положение максимума
                maxind = np.argmax(diffSignal)
                # 3.1) пристыковать левую часть к текущему буфферу кадра, правую к следующему кадру
                self.bufCurrent = np.concatenate((self.bufCurrent,currentData[:maxind]))
                self.bufNext = currentData[maxind:-1]
                n = self.Tranciver.blocksize
                # 3.2) поправить размер буфера, чтобы не развалилась спектрограмма
                if len(self.bufCurrent) < n :
                    self.bufCurrent = np.concatenate((self.bufCurrent,np.zeros(n-len(self.bufCurrent))))
                else:
                    self.bufCurrent = self.bufCurrent[:n]
                # 4) обобразить спектрограмму
                self.Chart1.specImage(self.bufCurrent)
                # 5) текущий буфер заменить буфером следующего кадра
                self.bufCurrent = self.bufNext

            self.save_signal.put(currentData)   
            # todo : use checkbox to save current queue or all queue since program start (continues)
            # now save only data pushed start|stop button

    def saveFile(self):
        """ создаем диалоговое окно сохранения файла """
        filename = self._saveFileDialog('Сохранение сигнала')
        if filename!='':
            write(filename+'_'+self.signalType.name+'_'+self.getCurDateTime()+".wav", int(self.Tranciver.samplerate), self.wav_data.astype(np.float32))
            self.wav_data = np.array([])
            QMessageBox.information(self,'Сохранение данных', 'Сохранено')

    def loadFile(self):
        """ загрузка файла """
        fileName, filter = QFileDialog.getOpenFileName()
        if fileName!='':
            if fileName[-4:]!='.wav':
                QMessageBox.warning(self,'Таблица','Неподходящий файл',QMessageBox.Ok)
            else:
                samplerate, data = wavfile.read(fileName)
                print('Loaded')
                """ тут логика должна быть следующей: открываем файл, у нас есть кнопка Плей, 
                она должна активироваться (тут вообще хороший вопрос, а должна ли она активироваться, 
                если мы просто записали файл и сразу хотим его воспроизвести).
                2) нажимаем плей, в зависимости от типа файла (вот тут тоже косяк, пользователь как бы должен
                наперед знать тип данных) нарезаем его на блоки (и тут снова косяк, размеры блоков мы могли менять,
                например меняя частоту дискретизации, т.е. надо определить базовую например 44100 и относительно
                нее делать все изменения по размерам блоков) и выводим на спектрограмму и осциллограмму пока 
                файл не закончится. 
                
                Вероятно нам захочется воспроизводить файл с заданной скоростью, тогда должны быть предусмотрены кнопки
                x0.5, x2 и т.д. рядом с кнопкой плей"""

    def getCurDateTime(self):
        """ возвращает метку фремени ггггммдд_ччммсс"""
        now = datetime.now()
        current_date_time = str(now.year)+str(now.month)+str(now.day)+'_'+str(now.hour)+str(now.minute)+str(now.second)
        return current_date_time

    def getSignalType(self,SignalType):
        """ установка типа записываемого сигнала """
        self.signalType=SignalType
    
    def setDownSample(self,value):
        """ установка прореживания для вывода осциллограммы """
        self.downSample = value

    def _saveFileDialog(self,text):
        """ настройка диалогового окна сохраанения файла """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,text,"","All Files (*);;wav files (*.wav)", options=options)
        return fileName

    def deviceUpdate(self,deviceName):
        self.Tranciver.device=self.settings.deviceComboBox.currentIndex()+1

    def _createMenubar(self):
        """ делаем пользовательское меню """
        menuBar = self.menuBar()
        self.MainWindowMenuBar = menuBar.addMenu("&Файл")
        self.MainWindowMenuBar.addAction(self.saveAction)
        self.MainWindowMenuBar.addAction(self.loadAction)

    def _createActions(self):
        """ делаем кнопки пользовательского меню """
        self.saveAction = QAction("&Сохранить",self)
        self.loadAction = QAction("&Загрузить",self)
    
    def _connectActions(self):
        """ соединяем кнопки пользовательского меню с обработчиками событий """
        self.saveAction.triggered.connect(self.saveFile)
        self.loadAction.triggered.connect(self.loadFile)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())