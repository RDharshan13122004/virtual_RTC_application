import socket
import threading
import struct
import zlib

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 65432
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen(5)

clients = {}
lock = threading.Lock()


def recv_video(client_socket, client_id):
    """Handles video data from client."""
    try:
        while True:
            identifier = client_socket.recv(1)
            if not identifier:
                break

            if identifier != b"V":
                continue  # Ignore non-video packets

            data_size = client_socket.recv(8)
            if not data_size:
                break

            data_size = struct.unpack("Q", data_size)[0]
            data = b""

            while len(data) < data_size:
                packet = client_socket.recv(min(data_size - len(data), 4096))
                if not packet:
                    break
                data += packet

            try:
                decompressed_data = zlib.decompress(data)
            except zlib.error:
                continue  # Ignore corrupted frames

            with lock:
                for other_client_id, other_client_socket in clients.items():
                    if other_client_socket != client_socket:
                        try:
                            other_client_socket.sendall(
                                b"V" +
                                struct.pack("I", client_id) +
                                struct.pack("Q", len(data)) +
                                data
                            )
                        except Exception as e:
                            print(f"Error sending video to client {other_client_id}: {e}")

    except Exception as e:
        print(f"Error in video handling for client {client_id}: {e}")
    finally:
        with lock:
            if client_id in clients:
                del clients[client_id]
            client_socket.close()


def recv_audio(client_socket, client_id):
    """Handles audio data from client."""
    try:
        while True:
            identifier = client_socket.recv(1)
            if not identifier:
                break

            if identifier != b"A":
                continue  # Ignore non-audio packets

            data_size = client_socket.recv(8)
            if not data_size:
                break

            data_size = struct.unpack("Q", data_size)[0]
            data = b""

            while len(data) < data_size:
                packet = client_socket.recv(min(data_size - len(data), 4096))
                if not packet:
                    break
                data += packet

            with lock:
                for other_client_id, other_client_socket in clients.items():
                    if other_client_socket != client_socket:
                        try:
                            other_client_socket.sendall(b"A" + struct.pack("Q", data_size) + data)
                        except Exception as e:
                            print(f"Error sending audio to client {other_client_id}: {e}")

    except Exception as e:
        print(f"Error in audio handling for client {client_id}: {e}")
    finally:
        with lock:
            if client_id in clients:
                del clients[client_id]
            client_socket.close()


def handle_client(client_socket, client_id):
    """Starts separate threads for video and audio."""
    video_thread = threading.Thread(target=recv_video, args=(client_socket, client_id), daemon=True)
    audio_thread = threading.Thread(target=recv_audio, args=(client_socket, client_id), daemon=True)

    video_thread.start()
    audio_thread.start()

    video_thread.join()
    audio_thread.join()


def start_server():
    """Accepts new client connections."""
    client_counter_id = 0
    try:
        while True:
            client_socket, addr = server.accept()
            print(f"New Connection: {addr}")
            client_counter_id += 1
            with lock:
                clients[client_counter_id] = client_socket

            threading.Thread(target=handle_client, args=(client_socket, client_counter_id), daemon=True).start()

    except KeyboardInterrupt:
        print("Server is shutting down...")
    finally:
        with lock:
            for client_socket in clients.values():
                client_socket.close()
        server.close()


print(f"Server is listening on {SERVER}:{PORT}")
start_server()
