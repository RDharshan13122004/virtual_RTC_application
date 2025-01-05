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

clients:dict = {}
lock = threading.Lock()

def client_handle(client_socket, client_id):
    global clients
    try:
        while True:

            frame_size_data = client_socket.recv(8)
            if not frame_size_data:
                break

            frame_size = struct.unpack("Q", frame_size_data)[0]
            frame_data = b""

            while len(frame_data) < frame_size:
                packet = client_socket.recv(min(frame_size - len(frame_data), 4096))
                if not packet:
                    break

                frame_data += packet

                try:
                    decompressed_data = zlib.decompress(frame_data)
                except zlib.error as e:
                    #print(f"decompression error: {e}")
                    continue
            
            with lock:
                for other_client_id, other_client_socket in clients.items():
                    if other_client_socket != client_socket:
                        try:
                            compressed_data = zlib.compress(decompressed_data)
                            compressed_data_size = len(compressed_data)

                            other_client_socket.sendall(
                                struct.pack("I", client_id) +
                                struct.pack("Q", compressed_data_size) +
                                compressed_data
                            )
                        except Exception as e:
                            print(f"error sending data to client {other_client_id}: {e}")

    except Exception as e:
        print(f"Error with client {client_id}: {e}")
    finally:
        with lock:
            if client_id in clients:
                del clients[client_id]
            client_socket.close()


def start_Server():
    client_counter_id = 0
    try:
        while True:
            client_socket ,addr = server.accept()
            print(f"NEW CONNECTION : {addr}")
            client_counter_id += 1
            with lock:
                clients[client_counter_id] = client_socket
            threading.Thread(target=client_handle, args=(client_socket, client_counter_id)).start()
    except KeyboardInterrupt:
        print("Server is shutting down ....")
    finally:
        #server.close()
        with lock:
            for client_socket in clients.values():
                client_socket.close()

print(f"Server is listening on .... {SERVER}")
start_Server()

