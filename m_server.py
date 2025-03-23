import socket
import threading
import struct
import zlib
import time
import select
import pyaudio
import numpy as np


# Server Configuration
SERVER = socket.gethostbyname(socket.gethostname())
V_PORT = 65432
A_PORT = 50000
V_ADDR = (SERVER, V_PORT)
A_ADDR = (SERVER, A_PORT)

# Audio Settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 32000  # Opus optimized rate
CHUNK = 128   # Opus optimized chunk size

V_clients = {}
A_clients = []
lock = threading.Lock()


def adpcm_encode(audio_data):
    """Encodes 16-bit PCM audio to 4-bit ADPCM."""
    step = 7
    encoded_audio = []
    prev_sample = 0

    for sample in np.frombuffer(audio_data, dtype=np.int16):
        diff = sample - prev_sample
        step_index = diff // step
        step_index = max(-8, min(7, step_index))  # Keep within 4-bit range
        
        prev_sample += step_index * step
        encoded_audio.append(step_index & 0xF)  # Store 4-bit values

    return struct.pack(f'{len(encoded_audio)}B', *encoded_audio)

def adpcm_decode(encoded_audio):
    """Decodes 4-bit ADPCM to 16-bit PCM."""
    step = 7
    decoded_audio = []
    prev_sample = 0

    encoded_values = struct.unpack(f'{len(encoded_audio)}B', encoded_audio)

    for val in encoded_values:
        step_index = (val & 0xF) - 8  # Convert 4-bit back to signed integer
        prev_sample += step_index * step
        decoded_audio.append(prev_sample)

    return np.array(decoded_audio, dtype=np.int16).tobytes()
def video_stream_handler(vid_client_socket, client_assign_id):
    """Handles video streaming for each client."""
    global V_clients
    try:
        vid_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8192)  # Increase buffer size

        while True:
            frame_size_data = vid_client_socket.recv(8)
            if not frame_size_data:
                break

            frame_size = struct.unpack("Q", frame_size_data)[0]
            frame_data = b""

            while len(frame_data) < frame_size:
                packet = vid_client_socket.recv(min(frame_size - len(frame_data), 4096))
                if not packet:
                    break
                frame_data += packet

            try:
                decompressed_data = zlib.decompress(frame_data)
            except zlib.error:
                continue  # Skip corrupted data
            
            with lock:
                for other_client_id, other_client_socket in V_clients.items():
                    if other_client_socket != vid_client_socket:
                        try:
                            compressed_data = zlib.compress(decompressed_data)
                            compressed_data_size = len(compressed_data)

                            other_client_socket.sendall(
                                struct.pack("I", client_assign_id) +
                                struct.pack("Q", compressed_data_size) +
                                compressed_data
                            )
                        except Exception:
                            pass

    except Exception as e:
        print(f"Error with video client {client_assign_id}: {e}")
    finally:
        with lock:
            V_clients.pop(client_assign_id, None)
        vid_client_socket.close()

def audio_stream_handler():
    while True:
        with lock:
            if not A_clients:
                time.sleep(0.05)  # Allow CPU to breathe
                continue

        readable, _, _ = select.select(A_clients, [], [], 0.05)
        audio_data_dict = {}

        for client in readable:
            try:
                data = client.recv(CHUNK // 2)  # Since ADPCM is half the size
                if not data:
                    with lock:
                        A_clients.remove(client)
                    client.close()
                    continue
                audio_data_dict[client] = data
            except:
                with lock:
                    if client in A_clients:
                        A_clients.remove(client)
                client.close()

        if audio_data_dict:
            with lock:
                for client in A_clients:
                    other_audio = [adpcm_decode(data) for c, data in audio_data_dict.items() if c != client]
                    mixed_audio = mix_audio(other_audio) if other_audio else b'\x00' * CHUNK * 2
                    compressed_audio = adpcm_encode(mixed_audio)  # Compress before sending
                    try:
                        client.sendall(compressed_audio)
                    except:
                        with lock:
                            if client in A_clients:
                                A_clients.remove(client)
        time.sleep(0.01)

def mix_audio(audio_data_list):
    """Mix multiple audio streams together."""
    if not audio_data_list:
        return b'\x00' * CHUNK * 2  # Return silence if no audio
    
    audio_arrays = [np.frombuffer(data, dtype=np.int16).astype(np.float32) for data in audio_data_list]
    min_length = min(len(arr) for arr in audio_arrays)
    audio_arrays = [arr[:min_length] for arr in audio_arrays]

    mixed_audio = np.mean(audio_arrays, axis=0).astype(np.int16)  # Averaging technique
    return mixed_audio.tobytes()

def start_server():
    """Starts the video and audio servers."""
    video_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_server.bind(V_ADDR)
    video_server.listen(5)
    print(f"🎥 Video Server started on port {V_PORT}")

    audio_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    audio_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    audio_server.bind(A_ADDR)
    audio_server.listen(5)
    print(f"🎙️ Audio Server started on port {A_PORT}")

    client_counter_id = 0
    threading.Thread(target=audio_stream_handler, daemon=True).start()
    
    try:
        while True:
            vid_client, vid_addr = video_server.accept()
            aud_client, aud_addr = audio_server.accept()
            aud_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Reduce latency

            print(f"✅ New Video Connection: {vid_addr}")
            print(f"✅ New Audio Connection: {aud_addr}")

            client_counter_id += 1

            with lock:
                V_clients[client_counter_id] = vid_client
                A_clients.append(aud_client)

            threading.Thread(target=video_stream_handler, args=(vid_client, client_counter_id), daemon=True).start()
    
    except KeyboardInterrupt:
        print("🛑 Server is shutting down...")
    finally:
        with lock:
            for V_client_socket in V_clients.values():
                V_client_socket.close()

            for A_client_socket in A_clients:
                A_client_socket.close()

if __name__ == "__main__":
    print(f"🌐 Server listening on {SERVER}")
    start_server()