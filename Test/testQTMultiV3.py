import tensorflow as tf
from sys             import exit, argv
from multiprocessing import Process, Queue
from PyQt5.QtWidgets import QPushButton, QApplication, QHBoxLayout, QWidget, QLabel
from PyQt5.QtCore    import QRunnable, QObject, pyqtSignal, QThreadPool
import threading as th

class Window(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.__btn_run = QPushButton("Start")
        self.__btn_stp = QPushButton("Stop")
        self.__label   = QLabel("Idle")

        self.__runner  = Runner()
        self.__pool    = QThreadPool.globalInstance()

        self.__btn_run.clicked.connect(self.__run_net)
        self.__btn_stp.clicked.connect(self.__stp_net)
        self.__runner.signals.finished.connect(self.__on_finished)

        self.__btn_stp.setDisabled(True)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.__btn_run)
        self.layout().addWidget(self.__btn_stp)
        self.layout().addWidget(self.__label)

    def __run_net(self):
        self.__btn_run.setDisabled(True)
        self.__btn_stp.setEnabled(True)
        self.__label.setText("Running")
        self.__pool.start(self.__runner)

    def __stp_net(self):
        self.__runner.close()
        # What to do here?

    def __on_finished(self):
        self.__btn_run.setEnabled(True)
        self.__btn_stp.setDisabled(True)
        self.__label.setText("Finished")
        self.__runner = Runner()


class Runner(QRunnable):

    def __init__(self):
        QRunnable.__init__(self)
        self.__queue = Queue()
        self.__net   = Mnist(self.__queue)
        self.signals = RunnerSignal()

    def run(self):
        self.__net.start()
        while True:
            data = self.__queue.get()
            if data == NetSignal.finished:
                self.signals.finished.emit()
                break

    def close(self):
        self.__net.end_process()


class RunnerSignal(QObject):
    finished = pyqtSignal()


class Mnist(Process):
    def __init__(self, queue: Queue):
        Process.__init__(self)
        self.__queue = queue

    def run(self):
        # mnist = tf.keras.datasets.mnist  # 28x28 Bilder hangeschriebener Ziffern von 0-9

        # (x_train, y_train), (x_test, y_test) = mnist.load_data()

        # x_train = tf.keras.utils.normalize(x_train, axis=1)

        # model   = tf.keras.models.Sequential()
        # model.add(tf.keras.layers.Flatten())
        # model.add(tf.keras.layers.Dense(128, activation=tf.nn.relu))
        # model.add(tf.keras.layers.Dense(128, activation=tf.nn.relu))
        # model.add(tf.keras.layers.Dense(10, activation=tf.nn.softmax))

        # model.compile(optimizer="adam",
        #               loss="sparse_categorical_crossentropy",
        #               metrics=['accuracy'])

        # model.fit(x_train, y_train, epochs=8)
        # condition = th.Condition()
        # condition.acquire()
        # condition.wait()
        while True:
            self.__queue.put(1)
        self.__queue.put(NetSignal.finished)
        self.__queue.close()

    def end_process(self):
        self.terminate()
        self.__queue.put(NetSignal.finished)


class NetSignal:
    finished = "finished"


if __name__ == "__main__":
    main_thread = QApplication(argv)
    main_window = Window()
    main_window.show()
    exit(main_thread.exec())