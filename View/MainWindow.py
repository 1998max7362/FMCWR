import sys, os
sys.path.insert(0, "././utils/compoents")
sys.path.insert(0, "././Model/")
sys.path.insert(0, "././View/")
sys.path.insert(0, "././Test/")
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
import queue
from scipy.io.wavfile import write
from scipy.io import wavfile
from datetime import datetime

from SettingsWindow import SettingsWindow
from mainWaterfall import WaterFallWindow
from mainGraph import GraphWindow
from Clamp import Clamp
from Worker import *
from SignalSource import SignalSource
from Transceiver import Transceiver
from WrapedUiElements import *




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.save_signal = queue.Queue()
        self.wav_data=np.array([])
        self.setWindowTitle('Главное меню')
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        self._createActions()
        self._connectActions()
        self._createMenubar()

        #  Signal Settings
        fs = 44100
        segment = 100e-3 # 100 ms 
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
        self.downSample = 10            # задаваемое пользователем начальное прореживание (надо убрать)
        self.downSampleUsed = 10        # скорректированное значение прореживания с учетом частоты дискретизации
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
        # считываем все настройки для переинициализии микрофона
        # self.Tranciver.samplerate = ...
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
            # корректируем размер блока обработки И другие параметры зависящие от режима
            self.settings.xMin.slider.setValue(0)                # текущее значение xMin
            fs = self.Tranciver.samplerate
            # корректировка децимирующего коэффициента
            self.downSampleUsed = int(self.downSample*(np.round(fs/44100)))
            if self.downSampleUsed == 0:
                self.downSampleUsed = 1

            if self.signalType.value == 0 :
                self.Tranciver.setBlkSz(int(30e-3*fs))  # на 30 мс размер буфера для дальности
                self.Chart1.set_tSeg(23.3e-3)           # параметры стенда на 23.3 мс
                self.Chart1.set_fs(fs)
                coef = 3e8*23.3e-3/2/(221e6*(2.4/5))
                self.Chart1.setRangeX([1,int(self.Chart1.nfft/2)]) # выставляем правильно шкалу на спектрограмме по режиму
                self.settings.xMin.slider.setMaximum(int(self.Chart1.nfft/2)) # предельное значение xMin
                self.settings.xMax.slider.setMaximum(int(self.Chart1.nfft/2)) # предельное значение xMax
                pos = int(30/(coef*fs/2)*self.Chart1.nfft/2) # отсчет соотвествующий 30 метрам
                self.settings.xMax.slider.setValue(pos) # текущее значение xMax
            else:
                self.Tranciver.setBlkSz(int(50e-3*self.Tranciver.samplerate))# на 100 мс для скорости
                self.Chart1.set_tSeg(50e-3)
                self.Chart1.set_fs(self.Tranciver.samplerate)
                coef = 0.125/2
                self.Chart1.setRangeX([1,int(self.Chart1.nfft/2)]) # выставляем правильно шкалу на спектрограмме по режиму
                self.settings.xMin.slider.setMaximum(int(self.Chart1.nfft/2)) # предельное значение xMin
                self.settings.xMax.slider.setMaximum(int(self.Chart1.nfft/2)) # предельное значение xMax
                vel = int(40/(coef*fs/2)*self.Chart1.nfft/2) #  отсчет соответствующий 40 м/с
                self.settings.xMax.slider.setValue(vel)               # текущее значение xMax, m/s

            self.settings.DeviceSettingsGroupBox.setEnabled(False)  # отключаем часть интерфейса
            self.MainWindowMenuBar.setEnabled(False)                # отключаем часть интерфейса
            self.Chart0.clearPlots(True)                            # ставим признак перерисовки окна
            self.Tranciver.working = True                           # ставим признак работы Tranciver
            self.worker_1  = Worker(self.Tranciver.run_realtime)    # упаковываем в отдельный поток запись с микрофомна
            self.firstQue = 1                                       # номер записи в очереди
            self.threadpool.start(self.worker_1)                    # запускаем поток получения данных с микрофона
            self.timer.start()                                      # запускаем таймер для передергивания интерфейса
        else:
            # нажали на кнопку, получили "0"
            self.settings.DeviceSettingsGroupBox.setEnabled(True)   # включаем часть интерфейса
            self.MainWindowMenuBar.setEnabled(True)                 # включаем часть интерфейса
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
            n = int(self.Tranciver.samplerate*23.3e-3) # длина модулирующего импульса для режима дальность
            # выбор варианта обработки currentData (скорость или дальность)
            if self.signalType.value:
                # "1" обработка скорости
                self.Chart0.plotData(currentData[::self.downSampleUsed])
                self.Chart1.specImage(currentData)
            elif self.firstQue == 1:
                # "0" обработка дальности
                # 1) взять производную текущего фрейма
                diffSignal = abs(np.diff(currentData))**8
                # 2) найти положение максимума
                maxind = np.argmax(diffSignal)
                # этот максимум соотвествует началу записи, но  не началу сигнала, поэтому ищем следующий
                # 3.1) пристыковать левую часть к текущему буфферу кадра, правую к следующему кадру
                self.bufCurrent = np.concatenate((self.bufCurrent,currentData[:maxind]))
                self.bufNext = currentData[maxind:-1]
                # 3.2) поправить размер буфера, чтобы не развалилась спектрограмма
                if len(self.bufCurrent) < n :
                    self.bufCurrent = np.concatenate((np.zeros(n-len(self.bufCurrent)),self.bufCurrent))
                else:
                    self.bufCurrent = self.bufCurrent[-n-1:-1]
                # 4) обобразить спектрограмму (здесь нули, т.к. есть задержка включения устройства)
                self.Chart0.plotData(self.bufCurrent[::self.downSampleUsed])
                self.Chart1.specImage(self.bufCurrent)
                # 5) текущий буфер заменить буфером следующего кадра
                self.bufCurrent = self.bufNext
                self.firstQue = 2
            elif self.firstQue == 2:
                # 1) взять производную текущего фрейма
                diffSignal = abs(np.diff(currentData))**3
                # 2) найти положение истинного максимума - это начало второго импульса
                maxind = np.argmax(diffSignal)
                # 3.1) пристыковать левую часть к текущему буфферу кадра, правую к следующему кадру
                self.bufCurrent = np.concatenate((self.bufCurrent,currentData[:maxind]))
                self.bufNext = currentData[maxind:-1]
                # 3.2) поправить размер буфера, чтобы не развалилась спектрограмма
                if len(self.bufCurrent) < n :
                    self.bufCurrent = np.concatenate((np.zeros(n-len(self.bufCurrent)),self.bufCurrent))
                else:
                    self.bufCurrent = self.bufCurrent[-n-1:-1]
                # 4) обобразить спектрограмму (здесь случайный остаток сигнала)
                self.Chart0.plotData(self.bufCurrent[::self.downSampleUsed])
                self.Chart1.specImage(self.bufCurrent)
                # 5) текущий буфер заменить буфером следующего кадра
                self.bufCurrent = self.bufNext # (здесь неполный второй сигнал)
                self.firstQue = 0               
            else:
                m = n - len(self.bufCurrent)  # эту часть надо забрать из новых данных
                # 3.1) пристыковать левую часть к текущему буфферу кадра, правую к следующему кадру
                self.bufCurrent = np.concatenate((self.bufCurrent,currentData[:m])) # определили конце сигнала
                self.bufNext = currentData[m:-1]# здесь начало следующего импульса сигнала
                self.Chart0.plotData(self.bufCurrent[::self.downSampleUsed])
                self.Chart1.specImage(self.bufCurrent)
                # 6) проверить на наличие еще одного импульса
                if len(self.bufNext) > n:
                    k = len(self.bufNext)-n
                    self.bufCurrent = self.bufNext[-k-1:-1]
                    self.Chart0.plotData(self.bufNext[:n:self.downSampleUsed])
                    self.Chart1.specImage(self.bufNext[:n])
                else:
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
        """ возвращает метку времени ггггммдд_ччммсс"""
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