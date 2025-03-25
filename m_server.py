import socket
import threading
import struct
import zlib
import pyaudio
import numpy as np
import av  # Opus codec

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
audio_data_dict = {}
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

def create_opus_encoder():
    """Creates an Opus encoder context."""
    container = av.open(format='ogg', mode='w')
    stream = container.add_stream('opus', RATE)
    stream.channels = CHANNELS
    stream.codec_context.sample_rate = RATE
    stream.codec_context.bit_rate = 32000  # Adjust bitrate if needed
    return container, stream

def audio_stream_handler(client_socket):
    """Handles audio streaming for a single client."""
    global A_clients, audio_data_dict

    try:
        while True:
            data = client_socket.recv(CHUNK * 2)
            if not data:
                break  # Client disconnected
            
            with A_lock:
                audio_data_dict[client_socket] = data  # Store client audio

            # Prepare mixed audio excluding this client's own data
            with A_lock:
                other_audio = [
                    data for c, data in audio_data_dict.items() if c != client_socket
                ]

            mixed_audio = mix_audio(other_audio) if other_audio else b'\x00' * CHUNK * 2

            try:
                client_socket.sendall(mixed_audio)  # Send mixed audio back
            except:
                break  # Client disconnected

    except Exception as e:
        print(f"⚠️ Error with audio client: {e}")
    
    finally:
        with A_lock:
            if client_socket in A_clients:
                A_clients.remove(client_socket)
            if client_socket in audio_data_dict:
                del audio_data_dict[client_socket]
        client_socket.close()


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

            threading.Thread(target=audio_stream_handler, args=(aud_client,), daemon=True).start()
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
