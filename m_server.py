import socket
import threading
import struct
import zlib
import pyaudio
import numpy as np
from collections import deque

# Server Configuration
SERVER = socket.gethostbyname(socket.gethostname())
V_PORT = 65432
A_PORT = 12345
V_ADDR = (SERVER, V_PORT)
A_ADDR = (SERVER, A_PORT)

# Audio Settings
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 32000
# CHUNK = 128


V_clients = {}
A_clients = {}
lock = threading.Lock()
A_lock = threading.Lock()

def video_stream_handler(vid_client_socket, client_assign_id):
    """Handles video streaming for each client."""
    global V_clients
    try:
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

def audio_stream_handler(aud_clients,client_counter_id):
    try:
        while True:
            # Receive the audio header
            header = aud_clients.recv(4)
            if not header:
                break
            
            data_length = struct.unpack("!I", header)[0]
            compressed_data = b""
            
            while len(compressed_data) < data_length:
                packet = aud_clients.recv(data_length - len(compressed_data))
                if not packet:
                    print(f"Client {client_counter_id} disconnected unexpectedly.")
                    return
                compressed_data += packet

            # Broadcast audio data to all clients except sender
            with A_lock:
                for target_id, (target_socket, _) in A_clients.items():
                    if target_id != client_counter_id:
                        try:
                            packet_to_send = struct.pack("!II", client_counter_id, len(compressed_data)) + compressed_data
                            target_socket.sendall(packet_to_send)
                        except:
                            print(f"Failed to send audio to client {target_id}")
    
    except ConnectionResetError:
        print(f"Client {client_counter_id} disconnected forcefully.")
    finally:
        # Remove the client
        with A_lock:
            if client_counter_id in A_clients:
                del A_clients[client_counter_id]
        aud_clients.close()
#def mix_audio(audio_data_list):
    # """Mix multiple audio streams together."""
    # if not audio_data_list:
    #     return b'\x00' * CHUNK * 2  # Return silence if no audio
    
    # audio_arrays = [np.frombuffer(data, dtype=np.int16).astype(np.float32) for data in audio_data_list]
    # min_length = min(len(arr) for arr in audio_arrays)
    # audio_arrays = [arr[:min_length] for arr in audio_arrays]

    # mixed_audio = np.mean(audio_arrays, axis=0).astype(np.int16)  # Averaging technique
    # return mixed_audio.tobytes()

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
    # threading.Thread(target=audio_stream_handler, daemon=True).start()
    
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
                A_clients[client_counter_id] = aud_client


            threading.Thread(target=audio_stream_handler, args=(aud_client,client_counter_id),daemon=True).start()
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
