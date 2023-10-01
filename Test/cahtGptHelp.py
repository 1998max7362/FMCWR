import sounddevice as sd
import numpy as np
import queue
import threading

# Constants
SAMPLE_RATE = 44100  # Sample rate (Hz)
CHANNELS = 1          # Number of audio channels (1 for mono, 2 for stereo)
BLOCK_SIZE = 1024    # Number of audio samples per block

# Input and output queues for audio data
input_queue = queue.Queue()
output_queue = queue.Queue()

# Function to capture audio and put it into the input queue
def capture_audio(input_stream):
    while True:
        input_data, overflowed = input_stream.read(BLOCK_SIZE)
        input_queue.put(input_data)

# Function to play audio from the output queue
def play_audio(output_stream):
    while True:
        output_data = output_queue.get()
        output_stream.write(output_data)

# Create audio streams
input_stream = sd.InputStream(callback=None, channels=CHANNELS, samplerate=SAMPLE_RATE)
output_stream = sd.OutputStream(callback=None, channels=CHANNELS, samplerate=SAMPLE_RATE)

# Start the audio capture and playback threads
capture_thread = threading.Thread(target=capture_audio, args=(input_stream,))
play_thread = threading.Thread(target=play_audio, args=(output_stream,))
capture_thread.daemon = True
play_thread.daemon = True
capture_thread.start()
play_thread.start()

# Main loop for processing audio data
try:
    while True:
        input_data = input_queue.get()
        
        # Process the input_data (you can apply your own audio processing here)
        # For demonstration, we'll just pass the input data to the output queue
        output_queue.put(input_data)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    # Close the audio streams gracefully
    input_stream.stop()
    input_stream.close()
    output_stream.stop()
    output_stream.close()
