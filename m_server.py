import socket
import threading
import struct
import zlib
import pyaudio
import numpy as np
import base64
import time

# Server Configuration
SERVER = socket.gethostbyname(socket.gethostname())
V_PORT = 65432
A_PORT = 50007
V_ADDR = (SERVER, V_PORT)
A_ADDR = (SERVER, A_PORT)

# Audio Settings
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 32000
CHUNK = 1024


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
                print(f"[WARNING] Frame decompression failed for client {client_assign_id}: {e}")
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

def decode_audio(data):
    try:
        raw = zlib.decompress(base64.b64decode(data))
        return np.frombuffer(raw, dtype=np.int16)
    except:
        return np.zeros(CHUNK, dtype=np.int16)

def encode_audio(audio_np):
    compressed = zlib.compress(audio_np.astype(np.int16).tobytes())
    return base64.b64encode(compressed)

def audio_stream_handler(aud_client, aud_addr, client_counter_id):
    print(f"[CONNECTED] Client {client_counter_id} from {aud_addr}")
    with A_lock:
        A_clients[client_counter_id] = {'conn': aud_client, 'audio': None}

    try:
        while True:
            # 1. Receive audio from client
            size_data = aud_client.recv(4)
            if not size_data:
                break
            size = struct.unpack('!I', size_data)[0]
            data = b''
            while len(data) < size:
                packet = aud_client.recv(size - len(data))
                if not packet:
                    break
                data += packet

            # Store this client's audio
            audio_np = decode_audio(data)
            with A_lock:
                # Update this client's audio in the dictionary
                if client_counter_id in A_clients:
                    A_clients[client_counter_id]['audio'] = audio_np.copy()

                # Create a mixed audio stream for this client (excluding their own audio)
                mixed = np.zeros(CHUNK, dtype=np.int32)
                active_speakers = 0
                
                for other_id, info in A_clients.items():
                    if other_id != client_counter_id and info['audio'] is not None:
                        # Only mix in audio that has actual sound (not just silence)
                        audio_level = np.abs(info['audio']).max()
                        if audio_level > 500:  # Threshold to detect active speech
                            mixed += info['audio'].astype(np.int32)
                            active_speakers += 1
                
                # Only normalize if we have multiple speakers to prevent division by zero
                if active_speakers > 1:
                    mixed = (mixed / active_speakers).astype(np.int32)
                
                mixed = np.clip(mixed, -32768, 32767).astype(np.int16)
                
                # Only send back audio if there's something to hear
                if np.abs(mixed).max() > 50 or active_speakers > 0:
                    encoded = encode_audio(mixed)
                    size_bytes = struct.pack('!I', len(encoded))
                    aud_client.sendall(size_bytes + encoded)
                else:
                    # Send a minimal packet to keep the connection alive
                    minimal_silence = np.zeros(10, dtype=np.int16)
                    encoded = encode_audio(minimal_silence)
                    size_bytes = struct.pack('!I', len(encoded))
                    aud_client.sendall(size_bytes + encoded)

            time.sleep(0.01)  # Reduce CPU usage
            
    except Exception as e:
        print(f"[ERROR] Client {client_counter_id}: {e}")
    finally:
        with A_lock:
            if client_counter_id in A_clients:
                del A_clients[client_counter_id]
        aud_client.close()
        print(f"[DISCONNECTED] Client {client_counter_id} from {aud_addr}")
        
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

            threading.Thread(target=audio_stream_handler, args=(aud_client,aud_addr,client_counter_id),daemon=True).start()
            threading.Thread(target=video_stream_handler, args=(vid_client, client_counter_id), daemon=True).start()
    
    except KeyboardInterrupt:
        print("🛑 Server is shutting down...")
    finally:
        with lock:
            for V_client_socket in V_clients.values():
                V_client_socket.close()

            for a_client_info in A_clients.values():
                if isinstance(a_client_info, dict):
                    a_client_info['conn'].close()
                else:
                    a_client_info.close()


if __name__ == "__main__":
    print(f"🌐 Server listening on {SERVER}")
    start_server()
