from PyQt5.QtCore import QObject, pyqtSignal

class Clamp(QObject):
    Output = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.ReceivedValue = None
        self.SentValue = None
        self.__handleWithSend = []
        self.__handleWithReceive = []

    def Input(self,data):
        if(self.__handleWithReceive):
            [x(data) for x in self.__handleWithReceive]
        self.ReceivedValue = data

    def ConnectTo(self,otherClamp :'Clamp'):
        self.Output.connect(otherClamp.Input)
        return otherClamp

    def DisconnectTo(self,otherClamp :'Clamp'):
        self.Output.disconnect(otherClamp.Input)

    def ConnectFrom(self,otherClamp :'Clamp'):
        otherClamp.Output.connect(self.Input)
        return self

    def DisconnnectFrom(self,otherClamp :'Clamp'):
        otherClamp.Output.disconnect(self.Input)

    def ConnectBoth(self,otherClamp :'Clamp'):
        self.Output.connect(otherClamp.Input)
        otherClamp.Output.connect(self.Input)

    def DisconnnectBoth(self,otherClamp :'Clamp'):
        self.Output.disconnect(otherClamp.Input)
        otherClamp.Output.disconnect(self.Input)

    def Send(self,data):
        self.SentValue = data
        if(self.__handleWithSend):
            [x(data) for x in self.__handleWithSend]
        self.Output.emit(data)

    def HandleWithSend(self,*funcs):
        if funcs:
            self.__handleWithSend.extend(funcs)

    def HandleWithReceive(self,*funcs):
        if funcs:
            self.__handleWithReceive.extend(funcs)

    def UnhandleWithSend(self, *funcs):
        if(funcs):
            [a for a in self.__handleWithSend if a not in funcs]
        else:
            self.__handleWithSend = []

    def UnhandleWithReceive(self, *funcs):
        if(funcs):
            [a for a in self.__handleWithReceive if a not in funcs]
        else:
            self.__handleWithReceive = []