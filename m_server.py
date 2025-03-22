'''
import socket
import threading
import struct
import zlib
import select
import time
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
CHUNK = 128 

V_clients:dict = {}
A_clients:list = []
lock = threading.Lock()

def mix_audio(audio_data_list):
    if not audio_data_list:
        return b'\x00' * CHUNK * 2
    
    if len(audio_data_list) == 1:
        return audio_data_list[0]

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
                # print(f"Error decompressing data: {e}")
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

def audio_stream_handler():
    while True:
        with lock:
            if not A_clients:
                time.sleep(0.01)
                continue

        try:
            readable, _, _ = select.select(A_clients, [], [], 0.01)
        except Exception as e:
            print(f"Error in select(): {e}")
            continue

        audio_data_dict = {}

        for client in readable:
            try:
                data = client.recv(CHUNK * 2)
                if not data:
                    with lock:
                        A_clients.remove(client)
                        client.close()       
                    continue
                audio_data_dict[client] = data
            except Exception as e:
                print(f"Error receiving audio data: {e}")
                with lock:
                    A_clients.remove(client)
                client.close()
        
        with lock:
            for client in A_clients.copy():
                if client in audio_data_dict:
                    other_audio = [data for c, data in audio_data_dict.items() if c != client]
                else:
                    other_audio = list(audio_data_dict.values())
                
                mixed_audio = mix_audio(other_audio) if other_audio else b'\x00' * CHUNK * 2
                try:
                    client.sendall(mixed_audio)
                except:
                    A_clients.remove(client)


def start_server():
    video_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_server.bind(V_ADDR)
    video_server.listen(5)
    print(f"Video Server started on port {V_PORT}")

    audio_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    audio_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    audio_server.bind(A_ADDR)
    audio_server.listen(5)
    print(f"Audio Server started on port {A_PORT}")

    client_counter_id = 0
    threading.Thread(target=audio_stream_handler,daemon = True).start()
    try:
        while True:
            vid_client, vid_addr = video_server.accept()
            aud_client, aud_addr = audio_server.accept()

            print(f"NEW Video Connection : {vid_addr}")
            print(f"New Audio Connection : {aud_addr}")

            client_counter_id += 1

            with lock:
                V_clients[client_counter_id] = vid_client
                #A_clients[client_counter_id] = aud_client
                A_clients.append(aud_client)

            threading.Thread(target=video_stream_handler, args=(vid_client,client_counter_id), daemon = True).start()
            #threading.Thread(target=audio_stream_handler, args=(aud_client,client_counter_id), daemon = True).start()
    
    except KeyboardInterrupt:
        print("Server is shutting down ....")
    finally:
        with lock:
            for V_client_socket in V_clients.values():
                V_client_socket.close()

            for A_client_socket in A_clients:
                A_client_socket.close()

if __name__ == "__main__":
    print(f"SERVER listening om ...  {SERVER}")
    start_server()
'''
# import socket
# import threading
# import struct
# import zlib

# import time
# import pyaudio
# import numpy as np

# SERVER = socket.gethostbyname(socket.gethostname())
# V_PORT = 65432
# A_PORT = 50000
# V_ADDR = (SERVER,V_PORT)
# A_ADDR = (SERVER,A_PORT)

# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 32000
# CHUNK = 128 

# V_clients:dict = {}
# A_clients:list = []
# lock = threading.Lock()

# def mix_audio(audio_data_list):
#     if not audio_data_list:
#         return b'\x00' * CHUNK * 2
    
#     # if len(audio_data_list) == 1:
#     #     return audio_data_list[0]

#     audio_arrays = [np.frombuffer(data, dtype=np.int16).astype(np.float32) for data in audio_data_list]
#     min_length = min(len(arr) for arr in audio_arrays)
#     audio_arrays = [arr[:min_length] for arr in audio_arrays]

#     mixed_audio = np.add.reduce(audio_arrays)/len(audio_arrays)

#     return mixed_audio.astype(np.int16).tobytes()

# def video_stream_handler(vid_client_socket,client_assign_id):
#     global V_clients
#     try:
#         while True:
#             frame_size_data = vid_client_socket.recv(8)
#             if not frame_size_data:
#                 break

#             frame_size = struct.unpack("Q",frame_size_data)[0]
#             frame_data = b""

#             while len(frame_data) < frame_size:
#                 packet = vid_client_socket.recv(min(frame_size - len(frame_data), 4096))
#                 if not packet:
#                     break

#                 frame_data += packet

#             try:
#                 decompressed_data = zlib.decompress(frame_data)
#             except zlib.error as e:
#                 # print(f"Error decompressing data: {e}")
#                 continue
            
#             with lock:
#                 for other_client_id, other_client_socket in V_clients.items():
#                     if other_client_socket != vid_client_socket:
#                         try: 
#                             compressed_data = zlib.compress(decompressed_data)
#                             compressed_data_size = len(compressed_data)

#                             other_client_socket.sendall(
#                                 struct.pack("I", client_assign_id) +
#                                 struct.pack("Q", compressed_data_size) +
#                                 compressed_data
#                             )
#                         except Exception as e:
#                             print(f"error sending data to client {other_client_socket}: {e}")

#     except Exception as e:
#         print(f"Error with client {client_assign_id}: {e}")
#     finally:
#         with lock:
#             if client_assign_id in V_clients:
#                 del V_clients[client_assign_id]
#             vid_client_socket.close()

# def audio_stream_handler(aud_client):
#     try:
#         while True:
#             data = aud_client.recv(CHUNK * 2)
#             if not data:
#                 break

#             with lock:
#                 audio_data_list = [c.recv(CHUNK * 2, socket.MSG_DONTWAIT) for c in A_clients if c!= aud_client]
#                 mixed_audio = mix_audio(audio_data_list) if audio_data_list else b'\x00' * CHUNK * 2

#             aud_client.sendall(mixed_audio)
#     except Exception:
#         pass
#     finally:
#         with lock:
#             if aud_client in A_clients:
#                 A_clients.remove(aud_client)
#             aud_client.close()
# def start_server():
#     video_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     video_server.bind(V_ADDR)
#     video_server.listen(5)
#     print(f"Video Server started on port {V_PORT}")

#     audio_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#     audio_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     audio_server.bind(A_ADDR)
#     audio_server.listen(5)
#     print(f"Audio Server started on port {A_PORT}")

#     client_counter_id = 0
    
#     try:
#         while True:
#             vid_client, vid_addr = video_server.accept()
#             aud_client, aud_addr = audio_server.accept()

#             print(f"NEW Video Connection : {vid_addr}")
#             print(f"New Audio Connection : {aud_addr}")

#             client_counter_id += 1

#             with lock:
#                 V_clients[client_counter_id] = vid_client
#                 #A_clients[client_counter_id] = aud_client
#                 A_clients.append(aud_client)

#             threading.Thread(target=video_stream_handler, args=(vid_client,client_counter_id), daemon = True).start()
#             threading.Thread(target=audio_stream_handler, args=(aud_client,), daemon = True).start()
    
#     except KeyboardInterrupt:
#         print("Server is shutting down ....")
#     finally:
#         with lock:
#             for V_client_socket in V_clients.values():
#                 V_client_socket.close()

#             for A_client_socket in A_clients:
#                 A_client_socket.close()

# if __name__ == "__main__":
#     print(f"SERVER listening om ...  {SERVER}")
#     start_server()

import socket
import threading
import struct
import zlib
import time
import pickle
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
RATE = 32000
CHUNK = 128

V_clients = {}
A_clients = []
lock = threading.Lock()

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

def mix_audio(audio_data_list):
    """Mix multiple audio streams together."""
    if not audio_data_list:
        return b'\x00' * CHUNK * 2  # Return silence if no audio
    
    audio_arrays = [np.frombuffer(data, dtype=np.int16).astype(np.float32) for data in audio_data_list]
    min_length = min(len(arr) for arr in audio_arrays)
    audio_arrays = [arr[:min_length] for arr in audio_arrays]

    mixed_audio = np.mean(audio_arrays, axis=0).astype(np.int16)  # Averaging technique
    return mixed_audio.tobytes()

def audio_stream_handler():
    """Handles receiving and sending audio using pickle serialization."""
    while True:
        with lock:
            if not A_clients:
                time.sleep(0.01)
                continue

        readable_clients = A_clients.copy()
        audio_data_dict = {}

        for client in readable_clients:
            try:
                data = client.recv(4096)  # Increase buffer size for serialized data
                if not data:
                    with lock:
                        A_clients.remove(client)
                        client.close()
                    continue

                unpacked_data = pickle.loads(data)  # Deserialize audio data
                audio_data_dict[client] = unpacked_data

            except Exception as e:
                print(f"Error receiving audio: {e}")
                with lock:
                    A_clients.remove(client)
                    client.close()

        mixed_audio = mix_audio(list(audio_data_dict.values())) if audio_data_dict else b'\x00' * CHUNK * 2
        packed_audio = pickle.dumps(mixed_audio)  # Serialize mixed audio

        with lock:
            for client in readable_clients:
                try:
                    client.sendall(packed_audio)
                except Exception as e:
                    print(f"Error sending mixed audio: {e}")
                    with lock:
                        A_clients.remove(client)
                        client.close()

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