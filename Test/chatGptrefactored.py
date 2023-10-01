import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from queue import Queue
import threading

# Constants
SAMPLE_RATE = 44100  # Sample rate (Hz)
CHANNELS = 1          # Number of audio channels (1 for mono, 2 for stereo)
BLOCK_SIZE = 1024    # Number of audio samples per block

# Input and output queues for audio data
input_queue = Queue()
output_queue = Queue()

# Function to capture audio and put it into the input queue
def capture_audio(input_stream):
    while True:
        input_data, overflowed = input_stream.read(BLOCK_SIZE)
        if overflowed:
            print("Input stream overflowed!")
        input_queue.put(input_data.copy())  # Copy data to avoid buffer overwrite

# Function to play audio from the output queue
def play_audio(output_stream):
    while True:
        output_data = output_queue.get()
        output_stream.write(output_data)

# Function to plot audio data in real-time
def plot_audio_data(data_queue, title):
    plt.ion()  # Turn on interactive mode for real-time plotting
    fig, ax = plt.subplots()
    ax.set_title(title)
    plt.ylabel('Amplitude')
    plt.xlabel('Time (s)')

    while True:
        data = data_queue.get()
        ax.clear()
        ax.plot(np.arange(len(data)) / SAMPLE_RATE, data)
        plt.pause(0.01)  # Pause to update the plot

# Create audio streams
input_stream = sd.InputStream(callback=None, channels=CHANNELS, samplerate=SAMPLE_RATE)
output_stream = sd.OutputStream(callback=None, channels=CHANNELS, samplerate=SAMPLE_RATE)

# Start the audio capture, playback, and plotting threads
capture_thread = threading.Thread(target=capture_audio, args=(input_stream,))
play_thread = threading.Thread(target=play_audio, args=(output_stream,))
recorded_data_thread = threading.Thread(target=plot_audio_data, args=(input_queue, 'Recorded Audio'))
played_data_thread = threading.Thread(target=plot_audio_data, args=(output_queue, 'Played Audio'))

threads = [capture_thread, play_thread, recorded_data_thread, played_data_thread]

for thread in threads:
    thread.daemon = True
    thread.start()

# Main loop for processing audio data
try:
    while True:
        pass  # You can perform other tasks here if needed

except KeyboardInterrupt:
    print("Exiting...")

finally:
    # Close the audio streams gracefully
    input_stream.stop()
    input_stream.close()
    output_stream.stop()
    output_stream.close()
