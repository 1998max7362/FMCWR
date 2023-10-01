# import enum

# class SignalType(enum.Enum):
#     __order__="TRIANGLE SAWTOOTH_FRONT SAWTOOTH_REVERSE SINE"
#     TRIANGLE = 0
#     SAWTOOTH_FRONT = 1
#     SAWTOOTH_REVERSE = 2
#     # SINE = 3

from enum_properties import EnumProperties, p
from enum import auto
from PyQt5.QtGui import QIcon

class SignalType(EnumProperties, p('IconPath')):

    TRIANGLE    = auto(), 'ExtraFiles/Icons/new/Triangle.png'
    SAWTOOTH_FRONT  = auto(), 'ExtraFiles/Icons/new/Sawtooth.png'
    SAWTOOTH_REVERSE   = auto(), 'ExtraFiles/Icons/new/SawtoothReverse.png'

    # name   value      QIcon       
    # TRIANGLE    = auto(), QIcon('ExtraFiles/Icons/new/Triangle.png')
    # SAWTOOTH_FRONT  = auto(), QIcon('ExtraFiles/Icons/new/Sawtooth.png')
    # SAWTOOTH_REVERSE   = auto(), QIcon('ExtraFiles/Icons/new/SawtoothReverse.png')