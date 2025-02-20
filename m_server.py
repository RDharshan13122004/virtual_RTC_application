import socket
import threading
import struct
import zlib
import pyaudio
import numpy as np

SERVER = socket.gethostbyname(socket.gethostname())
V_PORT = 65432
A_PORT = 50000
V_ADDR = (SERVER,V_PORT)
A_ADDR = (SERVER,A_PORT)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 32000
CHUNK = 256 

V_clients:dict = {}
A_clients:dict = {}
lock = threading.Lock()

def mix_audio(audio_data_list):
    if not audio_data_list:
        return b'\x00' * CHUNK * 2
    
    audio_arrays = [np.frombuffer(data, dtype=np.int16).astype(np.float32) for data in audio_data_list]
    min_length = min(len(arr) for arr in audio_arrays)
    audio_arrays = [arr[:min_length] for arr in audio_arrays]

    mixed_audio = np.mean(audio_arrays, axis=0).astype(np.int16)

    return mixed_audio.tobytes()

def video_stream_handler(vid_client_socket,client_assign_id):
    global V_clients
    try:
        while True:
            frame_size_data = vid_client_socket.recv(8)
            if not frame_size_data:
                break

        frame_size = struct.unpack("Q",frame_size_data)[0]
        frame_data = b""

        while len(frame_data) < frame_size:
            packet = vid_client_socket.recv(min(frame_size - len(frame_data), 4096))
            if not packet:
                break

            frame_data += packet

            try:
                decompressed_data = zlib.decompress(frame_data)
            except zlib.error as e:
                continue
        
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
                    except Exception as e:
                        print(f"error sending data to client {other_client_socket}: {e}")

    except Exception as e:
        print(f"Error with client {client_assign_id}: {e}")
    finally:
        with lock:
            if client_assign_id in V_clients:
                del V_clients[client_assign_id]
            vid_client_socket.close()

def audio_stream_handler(aud_client_socket,client_assign_id):
    try:
        while True:
            data = aud_client_socket.recv(CHUNK * 2)
            if not data:
                break
            
            with lock:
                other_audio = [d for c, d in A_clients.items() if c != client_assign_id]
                mixed_audio = mix_audio(other_audio) if other_audio else b'\x00' * CHUNK * 2
                
                for other_client_id, other_client_socket in A_clients.items():
                    if other_client_id != client_assign_id:
                        try:
                            other_client_socket.sendall(mixed_audio)
                        except:
                            with lock:
                                del A_clients[other_client_id]
                            other_client_socket.close()
    except Exception as e:
        print(f"Audio error with client {client_assign_id}: {e}")
    finally:
        with lock:
            if client_assign_id in A_clients:
                del A_clients[client_assign_id]
        aud_client_socket.close()


def start_server():
    video_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_server.bind(V_ADDR)
    video_server.listen(5)
    print(f"Video Server started on port {V_PORT}")

    audio_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    audio_server.bind(A_ADDR)
    audio_server.listen(5)
    print(f"Audio Server started on port {A_PORT}")

    client_counter_id = 0

    try:
        while True:
            vid_client, vid_addr = video_server.accept()
            aud_client, aud_addr = audio_server.accept()

            print(f"NEW Video Connection : {vid_addr}")
            print(f"New Audio Connection : {aud_addr}")

            client_counter_id += 1

            with lock:
                V_clients[client_counter_id] = vid_client
                A_clients[client_counter_id] = aud_client

            threading.Thread(target=video_stream_handler, args=(vid_client,client_counter_id), daemon = True).start()
            threading.Thread(target=audio_stream_handler, args=(aud_client,client_counter_id), daemon = True).start()
    
    except KeyboardInterrupt:
        print("Server is shutting down ....")
    finally:
        with lock:
            for V_client_socket in V_clients.values():
                V_client_socket.close()

            for A_client_socket in A_clients.values():
                A_client_socket.close()

if __name__ == "__main__":
    print(f"SERVER listening om ...  {SERVER}")
    start_server()