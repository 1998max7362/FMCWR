from select import select
import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
sys.path.insert(0, "././Core/")
from Clamp import Clamp
import enum
from qtwidgets import Toggle, AnimatedToggle
from decimal import Decimal

class DoubleSlider(QSlider):

    # create our our signal that we can connect to if necessary
    doubleValueChanged = pyqtSignal(float)

    def __init__(self, decimals=3, *args, **kargs):
        super(DoubleSlider, self).__init__( *args, **kargs)
        self._multi = 10 ** decimals
        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super(DoubleSlider, self).value())/self._multi
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super(DoubleSlider, self).value()) / self._multi

    def setMinimum(self, value):
        self.__minval = value
        return super(DoubleSlider, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        self.__maxval = value
        return super(DoubleSlider, self).setMaximum(value * self._multi)

    def maximum(self):
        return super(DoubleSlider, self).maximum()/self._multi

    def minimum(self):
        return super(DoubleSlider, self).minimum()/self._multi

    def setSingleStep(self, value):
        myDecimal = Decimal(str(value))
        count_after_decimal = abs(myDecimal.as_tuple().exponent)
        self._multi = 10**count_after_decimal
        self.blockSignals(True)
        super(DoubleSlider, self).setMinimum(self.__minval * self._multi)
        super(DoubleSlider, self).setMaximum(self.__maxval * self._multi)
        super(DoubleSlider, self).setValue(int(self.__curval * self._multi))
        self.blockSignals(False)
        return super(DoubleSlider, self).setSingleStep(int(value * self._multi))

    def singleStep(self):
        return float(super(DoubleSlider, self).singleStep()) / self._multi

    def setValue(self, value):
        self.blockSignals(True)
        self.__curval = value
        super(DoubleSlider, self).setValue(int(value * self._multi))
        self.blockSignals(False)

class ToggleButtonState(enum.Enum):
    NOT_CLICKED = 0
    LEFT_CLICKED = 1
    RIGHT_CLICKED = 2


class ClampedPushButton(QPushButton):
    def __init__(self, button, parent = None):
        super(ClampedPushButton, self).__init__()
        self.setText(button)
        self.SelfClamp = Clamp()
        self.clicked.connect(self.send)
        self.SelfClamp.HandleWithReceive(self.setEnabled)
        if(parent != None):
            self.setParent = parent
        
    def send(self):
        self.SelfClamp.Send(False)

class ClampedPushButtonFocus(QPushButton):
    def __init__(self, button, parent = None):
        super(ClampedPushButtonFocus, self).__init__()
        self.setText(button)
        self.SelfClamp = Clamp()
        self.clicked.connect(self.send)
        self.SelfClamp.HandleWithReceive(self.recHandle)
        if(parent != None):
            self.setParent = parent
        
    def send(self):
        self.SelfClamp.Send(False)

    def recHandle(self, state):
        self.setEnabled(state)
        if(state):
            self.setFocus()

class ClampedComboBox(QComboBox):
    def __init__(self, convert=None, convertBack=None, parent = None):
        super(ClampedComboBox, self).__init__()
        self.SelectedClamp = Clamp()
        self.StateClamp = Clamp()
        self.currentTextChanged.connect(self.send)
        self.StateClamp.HandleWithReceive(self.recStateHandle)
        self.fromFormConverter = convertBack
        self.toFormConverter = convert
        if parent:
            self.setParent = parent
        
    def send(self, value):
        if self.fromFormConverter:
            self.SelectedClamp.Send(self.fromFormConverter(value))
        else:
            self.SelectedClamp.Send(value)

    def recStateHandle(self, state):
        self.setEnabled(state)


class ClampedToggleButton(QPushButton):
    def __init__(self, button, color):
        super(ClampedToggleButton, self).__init__()
        # self.setCheckable(True)
        self.state = ToggleButtonState.NOT_CLICKED
        self.setText(button)
        # self.setStyleSheet("background-color: "+str(color))

        self.Color = (int(color[0]*255),int(color[1]*255),int(color[2]*255),0.4)
        self.Style_NOT_CLICKED = "border-width: 5px; border-style: hidden; background-color: rgba"+str(self.Color)
        self.Style_LEFT_CLICKED = "border-width: 5px; border-style: outset; background-color: rgba"+str(self.Color)
        self.Style_RIGHT_CLICKED = "border-width: 5px; border-style: inset; background-color: rgba"+str(self.Color)
        
        self.Style_NOT_CLICKED = "background-color: rgba"+str(self.Color)
        self.Style_LEFT_CLICKED = "background-color: rgba"+str(self.Color)
        self.Style_RIGHT_CLICKED = "background-color: rgba"+str(self.Color)
        
        self.Text_NOT_CLICKED = self.text()
        self.Text_LEFT_CLICKED = self.text()
        self.Text_RIGHT_CLICKED = self.text()
        # self.setStyleSheet(self.Style_NOT_CLICKED)
        
        self.InitColor=color

        self.LeftButtonClamp = Clamp()
        self.RightButtonClamp = Clamp()
        self.clicked.connect(self.leftClickHandler)
        # self.LeftButtonClamp.HandleWithReceive(self.setEnabled)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightClickHandler)
        
    def leftClickHandler(self,a):
        # self.LeftButtonClamp.Send(self.nextCheckState())
        if(self.state == ToggleButtonState.LEFT_CLICKED):
            self.toState(ToggleButtonState.NOT_CLICKED)
        else:
            self.toState(ToggleButtonState.LEFT_CLICKED)
        self.LeftButtonClamp.Send(self.isChecked())

    def rightClickHandler(self):
        if(self.state == ToggleButtonState.RIGHT_CLICKED):
            self.toState(ToggleButtonState.NOT_CLICKED)
        else:
            self.toState(ToggleButtonState.RIGHT_CLICKED)
        self.RightButtonClamp.Send(self.isChecked())

    def toState(self, state:ToggleButtonState):
        if(state == ToggleButtonState.NOT_CLICKED):
            a=list(self.Color)
            a[3] = 0.4
            self.Color=tuple(a)
            self.setStyleSheet(self.Style_NOT_CLICKED)
            self.setText(self.Text_NOT_CLICKED)
            # self.setStyleSheet("border-style: hidden")
        if(state == ToggleButtonState.LEFT_CLICKED):
            a=list(self.Color)
            a[3] = 0.2
            self.Color=tuple(a)
            self.setStyleSheet(self.Style_LEFT_CLICKED)
            self.setText(self.Text_LEFT_CLICKED)
            # self.setStyleSheet("border-style: outset")
        if(state == ToggleButtonState.RIGHT_CLICKED):
            a=list(self.Color)
            a[3] = 1
            self.Color=tuple(a)
            self.setStyleSheet(self.Style_RIGHT_CLICKED)
            self.setText(self.Text_RIGHT_CLICKED)
        self.state = state

class ClampedLineEdit(QLineEdit):
    def __init__(self, convert, convertBack, defaultValue=None):
        super(ClampedLineEdit, self).__init__()
        self.Text = Clamp()
        self.State = Clamp()
        self.setText(str(defaultValue))
        self.textEdited.connect(self.send)
        self.Text.HandleWithReceive(self.handleReceiveText)
        self.State.HandleWithReceive(self.handleReceiveState)
        self.__convertToForm = convert
        self.__convertFromForm = convertBack

    def send(self,d):
        if self.text() == None:
            pass
            # self.Text.Send(0)    
        else:
            try: self.Text.Send(self.__convertFromForm(d))
            except: pass
            

    def handleReceiveText(self, value):
        if value!=None:
            self.setText(self.__convertToForm(value))

    def handleReceiveState(self, value:bool):
        self.setEnabled(value)

class NamedLineEditVertical(QWidget):
    def __init__(self, lineEdit:ClampedLineEdit, name:str):
        super().__init__()
        layoutVert = QVBoxLayout(self)
        label = QLabel(name)
        layoutVert.addWidget(label)
        layoutVert.addWidget(lineEdit)
        self.LineEdit = lineEdit

class NamedLineEditHorizontal(QWidget):
    def __init__(self, lineEdit:ClampedLineEdit, name:str, units = None):
        super().__init__()
        layoutVert = QHBoxLayout(self)
        self.label = QLabel(name)
        layoutVert.addWidget(self.label)
        layoutVert.addWidget(lineEdit)
        if units:
            self.labelUnits = QLabel(units)
            layoutVert.addWidget(self.labelUnits)
            self.labelUnits.setFixedWidth(30)
        self.LineEdit = lineEdit
        self.LineEdit.setFixedWidth(100)
        self.label.setFixedWidth(100)
        layoutVert.addStretch()
        

class ClampedSlider(QSlider):
    def __init__(self) -> None:
        super().__init__()
        self.ValueClamp = Clamp()
        self.ValueClamp.HandleWithReceive(self.setValue)
        self.valueChanged.connect(self.ValueClamp.Send)

class NamedSliderHorizontal(QWidget):
    def __init__(self, lineEdit:ClampedLineEdit, name:str, units = None):
        super().__init__()
        self.ValueClamp = Clamp()
        layout = QHBoxLayout(self)
        self.label = QLabel(name)
        self.lineEdit = lineEdit
        self.slider = ClampedSlider()
        self.slider.setOrientation(Qt.Horizontal)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.lineEdit)
        self.labelUnits = QLabel(units)
        layout.addWidget(self.labelUnits)
        layout.addStretch()

        self.lineEdit.Text.ConnectTo(self.slider.ValueClamp)
        self.slider.ValueClamp.ConnectTo(self.lineEdit.Text)

        self.lineEdit.Text.ConnectTo(self.ValueClamp)
        self.slider.ValueClamp.ConnectTo(self.ValueClamp)
        self.ValueClamp.HandleWithReceive(self.Send)
    
    def Send(self,value):
        if value>self.slider.maximum():
            value = self.slider.maximum()
            self.slider.ValueClamp.Send(value)
        if value<self.slider.minimum():
            value = self.slider.minimum()
            self.slider.ValueClamp.Send(value)
        self.ValueClamp.Send(value)


class ClampedDoubleSlider(DoubleSlider):
    def __init__(self) -> None:
        super().__init__()
        self.ValueClamp = Clamp()
        self.ValueClamp.HandleWithReceive(self.setValue)
        self.doubleValueChanged.connect(self.ValueClamp.Send)

class NamedDoubleSliderHorizontal(QWidget):
    def __init__(self, lineEdit:ClampedLineEdit, name:str, units = None):
        super().__init__()
        self.ValueClamp = Clamp()
        layout = QHBoxLayout(self)
        self.label = QLabel(name)
        self.lineEdit = lineEdit
        self.slider = ClampedDoubleSlider()
        self.slider.setOrientation(Qt.Horizontal)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.lineEdit)
        self.labelUnits = QLabel(units)
        layout.addWidget(self.labelUnits)
        layout.addStretch()

        self.lineEdit.Text.ConnectTo(self.slider.ValueClamp)
        self.slider.ValueClamp.ConnectTo(self.lineEdit.Text)

        self.lineEdit.Text.ConnectTo(self.ValueClamp)
        self.slider.ValueClamp.ConnectTo(self.ValueClamp)
        self.ValueClamp.HandleWithReceive(self.Send)
    
    def Send(self,value):
        if value>self.slider.maximum():
            value = self.slider.maximum()
            self.slider.ValueClamp.Send(value)
        if value<self.slider.minimum():
            value = self.slider.minimum()
            self.slider.ValueClamp.Send(value)
        self.ValueClamp.Send(value)

class ClampedAction(QAction):
    def __init__(self, action, parent = None):
        super(ClampedAction, self).__init__()
        self.setText(action)
        self.TriggeredClamp = Clamp()
        self.triggered.connect(self.send)
        self.TriggeredClamp.HandleWithReceive(self.setEnabled)
        if(parent != None):
            self.setParent = parent
        
    def send(self):
        self.TriggeredClamp.Send(False)

class ClampedCheckBox(QCheckBox):
    def __init__(self, text, parent = None):
        super(ClampedCheckBox, self).__init__()
        self.setText(text)
        self.SelfClamp = Clamp()
        self.stateChanged.connect(self.send)
        self.SelfClamp.HandleWithReceive(self.setEnabled)
        if(parent != None):
            self.setParent = parent
        
    def send(self, state):
        self.SelfClamp.Send(state)

class ClampedLabel(QLabel):
    def __init__(self):
        super(ClampedLabel, self).__init__()
        self.TextClamp = Clamp()
        self.TextClamp.HandleWithReceive(self.changeLabel)
    
    def changeLabel(self, message):
        if message==None:
            self.setHidden(True)
        else:
            self.setHidden(False)
            self.setText(message)

class NamedClampedSpinBox(QWidget):
    def __init__(self,LabelText:str):
        super(NamedClampedSpinBox, self).__init__()
        layout=QHBoxLayout(self)
        self.ValueClamp = Clamp()
        self.label = QLabel(LabelText)
        self.spinBox = QSpinBox()
        self.warning =QLabel()
        icon=QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning)
        self.warning.setPixmap(icon.pixmap(QSize(20, 20)))
        self.warning.setHidden(True)
        layout.addWidget(self.label)
        layout.addWidget(self.spinBox)
        layout.addWidget(self.warning)
        layout.addStretch()
        self.spinBox.valueChanged.connect(self.ValueChanged)
        self.ValueClamp.HandleWithReceive(self.ChangeValue)

    def ChangeValue(self,value):
        self.spinBox.setValue(value)
    
    def ValueChanged(self,value):
        self.ValueClamp.Send(value)

class NamedClampedDoubleSpinBox(QWidget):
    def __init__(self,LabelText:str):
        super(NamedClampedDoubleSpinBox, self).__init__()
        layout=QHBoxLayout(self)
        self.ValueClamp = Clamp()
        self.label = QLabel(LabelText)
        self.doubleSpinBox = QDoubleSpinBox()
        self.warning =QLabel()
        self.warning.setHidden(True)
        layout.addWidget(self.label)
        layout.addWidget(self.doubleSpinBox)
        layout.addWidget(self.warning)
        layout.addStretch()
        self.doubleSpinBox.valueChanged.connect(self.ValueChanged)
        self.ValueClamp.HandleWithReceive(self.ChangeValue)

    def ChangeValue(self,value):
        self.doubleSpinBox.setValue(value)
    
    def ValueChanged(self,value):
        self.ValueClamp.Send(value)
class NamedHorizontalSwitcher(QWidget):
    def __init__(self,leftName:str=None,rightName:str=None):
        super(NamedHorizontalSwitcher, self).__init__()
        layout = QHBoxLayout(self)
        self.LeftLabel = QLabel(leftName)
        self.RightLabel = QLabel(rightName)
        self.Switcher = AnimatedToggle(
            bar_color=Qt.lightGray,
            handle_color=Qt.darkGray,
            checked_color="#808080",
            pulse_checked_color="#00FF00",
            pulse_unchecked_color ="#00FF00")
        layout.addWidget(self.LeftLabel)
        layout.addWidget(self.Switcher)
        layout.addWidget(self.RightLabel)
        layout.addStretch()
