#server side code 
import socket
import wave
import pyaudio

# Configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
HOST = ''  # Listen on all interfaces
PORT = 5000
OUTPUT_FILE = "received_audio.wav"

# Setup audio file for writing
wf = wave.open(OUTPUT_FILE, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
wf.setframerate(RATE)

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server is listening on port {PORT}...")

try:
    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")
    
    while True:
        data = conn.recv(CHUNK * 2)  # Receive audio data
        if not data:
            break
        wf.writeframes(data)  # Save received data to file
except KeyboardInterrupt:
    print("Server stopped.")
finally:
    wf.close()
    server_socket.close()
    print(f"Audio saved to {OUTPUT_FILE}")








#transmitter
import socket
import pyaudio

# Configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
SERVER_IP = '192.168.1.2'  # Replace with your server's IP
PORT = 5000

# Initialize PyAudio
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))
print("Connected to the server. Streaming audio...")

try:
    while True:
        data = stream.read(CHUNK)
        client_socket.sendall(data)  # Send audio data to the server
except KeyboardInterrupt:
    print("Stopping transmission...")
finally:
    stream.stop_stream()
    stream.close()
    audio.terminate()
    client_socket.close()











#speech recognition
import socket
import pyaudio
import speech_recognition as sr
import numpy as np

# Configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
HOST = ''
PORT = 5000

# Initialize PyAudio
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

# Initialize Speech Recognition
recognizer = sr.Recognizer()

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Server is listening on port {PORT}...")

try:
    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")

    audio_data = b""  # Buffer to store audio
    while True:
        data = conn.recv(CHUNK * 2)  # Receive audio data
        if not data:
            break
        audio_data += data  # Store audio for processing
        
        # Convert audio data to numpy array for speech recognition
        np_audio = np.frombuffer(data, dtype=np.int16)
        audio_bytes = sr.AudioData(np_audio.tobytes(), RATE, 2)
        
        try:
            text = recognizer.recognize_google(audio_bytes)
            print(f"Recognized Speech: {text}")
        except sr.UnknownValueError:
            print("Could not understand audio.")
except KeyboardInterrupt:
    print("Server stopped.")
finally:
    stream.stop_stream()
    stream.close()
    audio.terminate()
    server_socket.close()
