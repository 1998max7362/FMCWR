import sounddevice as sd

def getAudioDevice(kind=""):
    devices = sd.query_devices()
    print(type(devices))
    if kind=="output":
        outputs = tuple(filter(lambda x: x['max_output_channels']>x['max_input_channels'], devices))
        return list(outputs)
    if kind=="input":
        inputs = tuple(filter(lambda x: x['max_output_channels']<x['max_input_channels'], devices))
        return list(inputs)
    return list(devices)