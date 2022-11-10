import easygui
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf


patrange = '*_range.wav'
patvel = '*_velocity.wav'
pattern = patrange

try:
    filepath = easygui.fileopenbox(
        default="C:\\Users\\libra\\YandexDisk\\Курсы\\РЛИИК\\radarexp\\exp_data_2021\\"+pattern)
except Exception as e:
    print(e)

data, samplerate = sf.read(filepath)
print(data.shape)
print('samplerate is ', samplerate, '\n')
try:
    cutedge = data[::10,:]
    print(cutedge.shape)
    fig,(ax1, ax2) = plt.subplots(2,1, sharex = 'all')
    ax1.plot(cutedge[:,0:1])
    ax2.plot(cutedge[:,1:2])
except Exception as e:
    print(e)
    cutedge = data[::10]
    plt.plot(cutedge)
plt.show()

