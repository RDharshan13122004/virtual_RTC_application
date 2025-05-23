import socket
from tkinter import *
import ttkbootstrap as tb #type: ignore
import numpy as np
from PIL import ImageTk, Image #type: ignore
from ttkbootstrap.toast import ToastNotification
from cv2 import *
import cv2 as cv
import zlib
import struct
import threading
import numpy as np
import pyaudio
import base64
import time

SERVER = "" #Entry ur server IP Address
V_PORT = 65432
A_PORT = 50007
VP_ADDR = (SERVER,V_PORT)
AP_ADDR = (SERVER,A_PORT)

A_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024


class Meeting():
    def __init__(self):
        self.video_image = Image.open("img/video-camera.png")
        resize_video_image = self.video_image.resize((35,35))
        self.video_image = ImageTk.PhotoImage(resize_video_image)

        self.audio_image = Image.open("img/audio.png")
        resize_audio_image = self.audio_image.resize((35,35))
        self.audio_image = ImageTk.PhotoImage(resize_audio_image) 

        self.info_image = Image.open("img/information.png")
        resize_info_image = self.info_image.resize((35,35))
        self.info_image = ImageTk.PhotoImage(resize_info_image)

        self.toast = None
        self.received_frame = {}
        self.lock = threading.Lock()
        self.cap = None
        self.client_socket = None

        self.audio_socket = None
        self.audio_active = False  # Audio toggle flag
        self.audio_stream = None
        self.stream = None 
        self.audio = pyaudio.PyAudio()
        self.audio_sending = False

    def setup_audio_streams(self):
        try:
            if hasattr(self, 'audio_stream') and self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                
            if hasattr(self, 'stream') and self.stream:
                self.stream.stop_stream()
                self.stream.close()
                
            self.audio_stream = self.audio.open(
                format=A_FORMAT, 
                channels=CHANNELS, 
                rate=RATE,
                input=True, 
                frames_per_buffer=CHUNK
            )
            
            self.stream = self.audio.open(
                format=A_FORMAT, 
                channels=CHANNELS, 
                rate=RATE,
                output=True, 
                frames_per_buffer=CHUNK
            )
            print("Audio streams successfully initialized")
        except Exception as e:
            print(f"Error setting up audio streams: {e}")

    def Create_Meeting(self,host_name):

        try:
            if not hasattr(self, 'client_socket') or self.client_socket is None:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self.client_socket.connect(VP_ADDR)
                #print("Connected to video server.")

            if not hasattr(self, 'audio_socket') or self.audio_socket is None:
                self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.audio_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.audio_socket.connect(AP_ADDR)
                #print("Connected to audio server.")

            self.toast = ToastNotification(title = "LinkHub",
                                        message = "Meeting is started",
                                        duration= 3000,
                                        bootstyle = "success",
                                        alert = True
                                        )
            self.toast.show_toast()
        except Exception as e:
            #print(f"Error connecting to server: {e}")
            self.toast = ToastNotification(title = "LinkHub",
                                          message = "Something went wrong",
                                          duration= 3000,
                                          bootstyle = "danger",
                                          alert = True,
                                          )
            self.toast.show_toast()
            return

        self.setup_audio_streams()            

        if HNE_Sumbit_btn:
            HNE_name_pop.destroy()

        self.Meeting_root = tb.Toplevel(title="meeting",position=(0,0))
        self.Meeting_root.iconbitmap("img/ppico.ico")    
        
        self.name = host_name

        container_frame = tb.Frame(self.Meeting_root)
        container_frame.pack(fill="both")

        menus_frame = tb.Frame(container_frame)
        menus_frame.pack(pady=10,side="left")

        info_btn = tb.Button(menus_frame,
                             image=self.info_image,
                             command= self.info_pop,
                             bootstyle = "success"
                             )
        info_btn.pack(pady=20,padx=30)

        self.video_variable = BooleanVar(value=False)
        self.audio_variable= BooleanVar(value=False)

        video_menu = tb.Menubutton(menus_frame,
                                    direction='above',
                                    #text="video status",
                                    image=self.video_image,
                                    compound=LEFT
                                    )
        video_menu.pack(pady=20,padx=30)

        audio_menu = tb.Menubutton(menus_frame,
                                    direction='above',
                                    image= self.audio_image,
                                    compound=LEFT
                                    )
        audio_menu.pack(pady=20,padx=30)

        Close_meeting = tb.Menubutton(menus_frame,
                                      direction='above',
                                      text="End",
                                      compound=LEFT,
                                      bootstyle = "danger"
                                      )
        Close_meeting.pack(pady=20,padx=30,ipadx=9,ipady=9)

        menu1= tb.Menu(video_menu, tearoff=0)
        menu1.add_radiobutton(label="On",
                              background="#06f912",
                              variable= self.video_variable,
                              value= True,
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14),
                              command = self.start_stop_video
                              )

        menu1.add_radiobutton(label="Off",
                              background="#d4342b",
                              foreground="#f8dedd",
                              variable= self.video_variable,
                              value= False,
                              font=('Arial Rounded MT Bold',14),
                              command = self.start_stop_video
                              )
        
        menu2 = tb.Menu(audio_menu, tearoff=0)
        menu2.add_radiobutton(label="Unmute",
                              variable= self.audio_variable,
                              value= True,
                              background="#06f912",
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14),
                              command = self.start_stop_audio
                              )
        
        menu2.add_radiobutton(label="Mute",
                               variable= self.audio_variable,
                               value= False,
                               background="#d4342b",
                               foreground="#f8dedd",
                               font=('Arial Rounded MT Bold',14),
                               command = self.start_stop_audio
                               )
        
        close_menu = tb.Menu(Close_meeting, tearoff=0)
        close_menu.add_radiobutton(label="End all meeting",
                                   background="#d4342b",
                                   foreground="#f8dedd",
                                   font=('Arial Rounded MT Bold',14),
                                   command= lambda :self.end_meeting("End all meeting")
                                   )
        
        close_menu.add_radiobutton(label="End meeting",
                                   background="#6a8daf",
                                   foreground="#f8dedd",
                                   font=('Arial Rounded MT Bold',14),
                                   command= lambda: self.end_meeting("End meeting")
                                   )
        
        video_menu['menu'] = menu1
        audio_menu['menu'] = menu2
        Close_meeting['menu'] = close_menu

        video_alignment_frame = tb.Frame(container_frame)
        video_alignment_frame.pack(pady=5)


        self.video_label = tb.Label(video_alignment_frame)
        self.video_label.pack(pady=5,padx=5,side="left")

        self.recv_video_label = tb.Label(video_alignment_frame)
        self.recv_video_label.pack(pady=10,padx=5,side="left")

        video_alignment_frame2 = tb.Frame(container_frame)
        video_alignment_frame2.pack(pady=5)

        self.recv_video_label2 = tb.Label(video_alignment_frame2)
        self.recv_video_label2.pack(pady=5,padx=5,side="left")

        self.recv_video_label3 = tb.Label(video_alignment_frame2)
        self.recv_video_label3.pack(pady=5,padx=5,side="left")

        self.update_blank_frame()

        try:
            self.recv_thread = threading.Thread(target=self.recv_video, daemon=True)
            self.recv_thread.start()

            self.grid_thread = threading.Thread(target=self.display_recv_frame, daemon=True)
            self.grid_thread.start()

            self.Arecv_thread = threading.Thread(target=self.recv_audio, daemon=True)
            self.Arecv_thread.start()
        except Exception as e:
            print(f"Error starting threads: {e}")

        btn1.config(state=DISABLED)
        btn2.config(state=DISABLED)
        

    def connecting_meeting(self,part_name):

        try:
            if not hasattr(self, 'client_socket') or self.client_socket is None:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self.client_socket.connect((MC_SERVER_IP_entry.get(),V_PORT))
                #print("Connected to video server.")

            if not hasattr(self, 'audio_socket') or self.audio_socket is None:
                self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.audio_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.audio_socket.connect((MC_SERVER_IP_entry.get(),A_PORT))
                #print("Connected to audio server.")

                self.toast = ToastNotification(title = "LinkHub",
                                          message = "Meeting is started",
                                          duration= 3000,
                                          bootstyle = "success",
                                          alert = True,
                                          )
                self.toast.show_toast()

        except Exception as e:
            #print(f"Error connecting to server: {e}")
            self.toast = ToastNotification(title = "LinkHub",
                                          message = "Something went wrong",
                                          duration= 3000,
                                          bootstyle = "danger",
                                          alert = True,
                                          )
            self.toast.show_toast()
            return

        self.setup_audio_streams()
            
        if MC_Sumbit_btn:
            con_pop.destroy()

        self.Meeting_root = tb.Toplevel(title="meeting",
                                        position= (0,0)
                                        )
        self.Meeting_root.iconbitmap("img/ppico.ico")
        
        
        self.name = part_name


        container_frame = tb.Frame(self.Meeting_root)
        container_frame.pack(fill="both")

        menus_frame = tb.Frame(container_frame)
        menus_frame.pack(side="left")

        info_btn = tb.Button(menus_frame,
                             image= self.info_image,
                             command= self.info_pop,
                             bootstyle = "success"
                             )
        info_btn.pack(pady=10,padx=30)

        self.video_variable = BooleanVar(value=False)
        self.audio_variable= BooleanVar(value=False)

        video_menu = tb.Menubutton(menus_frame,
                                    direction='above',
                                    #text="video status",
                                    image=self.video_image,
                                    compound=LEFT
                                    )
        video_menu.pack(pady=20,padx=30)

        audio_menu = tb.Menubutton(menus_frame,
                                    direction='above',
                                    image= self.audio_image,
                                    compound=LEFT
                                    )
        audio_menu.pack(pady=20,padx=30)

        menu1= tb.Menu(video_menu, tearoff=0)
        menu1.add_radiobutton(label="On",
                              variable= self.video_variable,
                              value= True,
                              background="#06f912",
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14),
                              command= self.start_stop_video
                              )

        menu1.add_radiobutton(label="Off",
                              variable= self.video_variable,
                              value= False,
                              background="#d4342b",
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14),
                              command= self.start_stop_video
                              )
        
        menu2 = tb.Menu(audio_menu, tearoff=0)
        menu2.add_radiobutton(label="Unmute",
                              variable= self.audio_variable,
                              value= True,
                              background="#06f912",
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14),
                              command = self.start_stop_audio
                              )
        
        menu2.add_radiobutton(label="Mute",
                               variable= self.audio_variable,
                               value= False,
                               background="#d4342b",
                               foreground="#f8dedd",
                               font=('Arial Rounded MT Bold',14),
                               command = self.start_stop_audio
                               )
        
        style = tb.Style()
        style.configure("danger.Outline.TButton",font=("Helvetica",17))

        close_meeting_btn = tb.Button(menus_frame,
                                      bootstyle = "danger",
                                      text="End",
                                      style="danger.Outline.TButton",
                                      command= lambda: meeting.end_meeting("End meeting")
                                      )
        close_meeting_btn.pack(pady=20,ipadx=5,padx=10)
        
        video_menu['menu'] = menu1
        audio_menu['menu'] = menu2

        video_alignment_frame = tb.Frame(container_frame)
        video_alignment_frame.pack(pady=5)

        self.video_label = tb.Label(video_alignment_frame)
        self.video_label.pack(pady=5,padx=5,side="left")

        self.recv_video_label = tb.Label(video_alignment_frame)
        self.recv_video_label.pack(pady=10,padx=5,side="left")

        video_alignment_frame2 = tb.Frame(container_frame)
        video_alignment_frame2.pack(pady=5)


        self.recv_video_label2 = tb.Label(video_alignment_frame2)
        self.recv_video_label2.pack(pady=5,padx=5,side="left")

        self.recv_video_label3 = tb.Label(video_alignment_frame2)
        self.recv_video_label3.pack(pady=5,padx=5,side="left")

        self.update_blank_frame()

        try:
            self.recv_thread = threading.Thread(target=self.recv_video, daemon=True)
            self.recv_thread.start()

            self.grid_thread = threading.Thread(target=self.display_recv_frame, daemon=True)
            self.grid_thread.start()

            self.Arecv_thread = threading.Thread(target=self.recv_audio, daemon=True)
            self.Arecv_thread.start()
        except Exception as e:
            print(f"Error starting threads: {e}")

        btn1.config(state=DISABLED)
        btn2.config(state=DISABLED)
    
    def info_pop(self):
        self.info_pp = tb.Toplevel(title="",position=(0,0))
        self.info_pp.iconbitmap("img/ppico.ico")

        self.info_server_id_label = tb.Label(self.info_pp,text=f"🛰️{SERVER}",bootstyle = "warning", font=("Rockwell Extra Bold",18))
        self.info_server_id_label.pack(padx=10,pady=10)

        self.info_meeting_password_label = tb.Label(self.info_pp,text=f"🔐: frgtyh",bootstyle= "success", font=("Rockwell Extra Bold",18))
        self.info_meeting_password_label.pack(padx=10,pady=10)

    def start_stop_video(self):   
        if self.video_variable.get():

            if not hasattr(self,"cap") or self.cap is None:
                self.cap = cv.VideoCapture(0)

                if not self.cap.isOpened():
                    print("Error: Could not open video source.")
                    self.cap.release()
                    self.cap = None
                    return

                if not hasattr(self, 'send_thread') or not self.send_thread.is_alive():
                    self.send_thread = threading.Thread(target=self.send_video,daemon=True)
                    self.send_thread.start()
        else: 
            self.update_blank_frame()
            if hasattr(self, 'cap') and self.cap:
                self.cap.release()
                self.cap = None
            
    def update_blank_frame(self):
        blank = np.zeros((430,470,3),dtype='uint8')
        text_size = cv.getTextSize(self.name,cv.FONT_HERSHEY_SIMPLEX,1.0,2)[0]
        text_x = (blank.shape[1] - text_size[0])//2
        text_y = (blank.shape[0] + text_size[1])//2
        text_frame = cv.putText(blank,self.name,(text_x,text_y),cv.FONT_HERSHEY_SIMPLEX,1.0,(255,255,255),2)
        img = Image.fromarray(text_frame)
        imageTK = ImageTk.PhotoImage(img)
        self.video_label.imageTK = imageTK
        self.video_label.configure(image=imageTK)

    def video_loop(self,frame):
        try:
            img = Image.fromarray(frame)
            imgTk = ImageTk.PhotoImage(img)
            self.video_label.imgTk = imgTk
            self.video_label.configure(image = imgTk)
        except Exception as e:
            print(f"Error in video loop: {e}")
                
        
    def send_video(self):
        try:
            while True:
                if not self.video_variable.get():

                    blank = np.zeros((430,470,3),dtype=np.uint8)
                    text_size = cv.getTextSize(self.name,cv.FONT_HERSHEY_SIMPLEX,1.0,2)[0]
                    text_x = (blank.shape[1] - text_size[0])//2
                    text_y = (blank.shape[0] + text_size[1])//2
                    frame = cv.putText(blank,self.name,(text_x,text_y),cv.FONT_HERSHEY_SIMPLEX,1.0,(255,255,255),2)

                    _,compressed_frame = cv.imencode('.jpg',frame,[cv.IMWRITE_JPEG_QUALITY,80])

                    compressed_data = zlib.compress(compressed_frame.tobytes())
                    
                if self.video_variable.get():
                    if hasattr(self, "cap") and self.cap is not None:
                        ret, frame = self.cap.read()
                    if ret:
                        new_width, new_height = 470,430
                        resize_frame = cv.resize(frame,(new_width,new_height))
                        frame = cv.cvtColor(resize_frame,cv.COLOR_BGR2RGB)
                        _,compressed_frame = cv.imencode('.jpg',resize_frame,[cv.IMWRITE_JPEG_QUALITY,80])

                        compressed_data = zlib.compress(compressed_frame.tobytes())

                    else:
                        print("Failed to capture frame")
                        continue
                
                self.video_label.after(10,self.video_loop,frame)
                
                frame_size = len(compressed_data)
                try:
                    self.client_socket.sendall(struct.pack("Q",frame_size) + compressed_data)
                except Exception as e:
                    print(f"Error on sending data:{e}")
                    break
        finally:
            if self.cap:
                self.cap.release()

    def recv_video(self):
        try:
            while True:
                client_id_data = self.client_socket.recv(4)
                if not client_id_data or len(client_id_data) < 4:
                    print("Error: Failed to receive client ID.")
                    continue

                client_id = struct.unpack("I",client_id_data)[0]

                frame_size_data = self.client_socket.recv(8)
                if not frame_size_data or len(frame_size_data) < 8:
                    print("Error: Failed to receive frame size.")
                    continue

                frame_size = struct.unpack("Q",frame_size_data)[0]
                frame_data = b""

                while len(frame_data) < frame_size:
                    packet = self.client_socket.recv(min(frame_size - len(frame_data),4096))
                    if not packet:
                        print("Connection closed by server.")
                        break

                    frame_data += packet

                if len(frame_data) != frame_size:
                    print(f"Incomplete frame received. Excepted: {frame_size}, Received: {len(frame_data)} ")
                    continue
                try:
                    decompressed_data = zlib.decompress(frame_data)
                    np_data = np.frombuffer(decompressed_data,dtype=np.uint8)
                    frame = cv.imdecode(np_data,cv.IMREAD_COLOR)

                    if frame is None:
                        print("Error: Decoded frame is None (possibly corrupted).")
                        continue

                    with self.lock:
                        self.received_frame[client_id] = frame

                except zlib.error as e:
                    print(f"Decompression error: {e}")
                except Exception as e:
                    print(f"Error in decoding frame: {e}")
        except Exception as e:
            print(f"Error on receving data: {e}")
        finally:
            self.client_socket.close()

    def display_recv_frame(self):
        try:
            with self.lock:
                received_clients = list(self.received_frame.keys())
                labels = [self.recv_video_label,self.recv_video_label2,self.recv_video_label3]

                for i in range(len(labels)):
                    if i >= len(received_clients):
                        labels[i].config(image= None)
                
                for i, client_id in enumerate(received_clients[:len(labels)]):
                    frame = self.received_frame.get(client_id)

                    if frame is not None:
                        frame = cv.resize(frame,(470,430))
                        img = Image.fromarray(cv.cvtColor(frame,cv.COLOR_BGR2RGB))
                        imgtk = ImageTk.PhotoImage(img)

                        labels[i].imgtk = imgtk
                        labels[i].configure(image=imgtk)
                    else:
                        del self.received_frame[client_id]
        except Exception as e:
            print(f"Error in video loop: {e}")
        
        self.recv_video_label.after(10,self.display_recv_frame)

    def encode_audio(self,audio_np):
        compressed = zlib.compress(audio_np.astype(np.int16).tobytes())
        return base64.b64encode(compressed)
    
    def decode_audio(self,data):    
        decompressed = zlib.decompress(base64.b64decode(data))
        return np.frombuffer(decompressed, dtype=np.int16)
    
    def start_stop_audio(self):
        if self.audio_variable.get():
            # Starting audio
            print("Unmuting audio")
            self.audio_sending = True
            if not hasattr(self, 'audio_thread') or not self.audio_thread.is_alive():
                self.audio_thread = threading.Thread(target=self.send_audio, daemon=True)
                self.audio_thread.start()
        else:
            # Stopping audio
            print("Muting audio")
            self.audio_sending = False
            # Don't stop the thread, just send silent frames

    def send_audio(self):
        print("Audio sending thread started")
        try:
            while True:
                if hasattr(self, 'audio_socket') and self.audio_socket:
                    try:
                        if self.audio_sending and hasattr(self, 'audio_stream') and self.audio_stream:
                            # Read real audio data when unmuted
                            data = self.audio_stream.read(CHUNK, exception_on_overflow=False)
                            audio_np = np.frombuffer(data, dtype=np.int16)
                        else:
                            # Send silent frames when muted
                            audio_np = np.zeros(CHUNK, dtype=np.int16)
                        
                        # Encode and send
                        encoded = self.encode_audio(audio_np)
                        size = struct.pack('!I', len(encoded))
                        self.audio_socket.sendall(size + encoded)
                        
                        # Brief pause to control rate
                        time.sleep(0.01)
                    except Exception as e:
                        print(f"Error sending audio: {e}")
                        break
                else:
                    # Socket closed or not available
                    break
        except Exception as e:
            print(f"Audio sending thread error: {e}")
        print("Audio sending thread ended")

    def recv_audio(self):
        print("Audio receiving thread started")
        try:
            while hasattr(self, 'audio_socket') and self.audio_socket:
                try:
                    size_data = self.audio_socket.recv(4)
                    if not size_data:
                        print("No data received from audio socket")
                        break
                        
                    size = struct.unpack('!I', size_data)[0]
                    data = b''
                    while len(data) < size:
                        packet = self.audio_socket.recv(size - len(data))
                        if not packet:
                            break
                        data += packet
                    
                    if len(data) < size:
                        print(f"Incomplete audio data received: {len(data)}/{size}")
                        continue
                    
                    audio_np = self.decode_audio(data)
                    if hasattr(self, 'stream') and self.stream:
                        self.stream.write(audio_np.tobytes())
                except Exception as e:
                    print(f"Error receiving audio: {e}")
                    break
        except Exception as e:
            print(f"Audio receiving thread error: {e}")
        print("Audio receiving thread ended")

    def end_meeting(self, Close):
        if Close in ("End all meeting", "End meeting"):
            print("Ending meeting...")
            # Stop sending audio
            self.audio_sending = False
            
            # Release camera
            if hasattr(self, 'cap') and self.cap:
                self.cap.release()
                self.cap = None
            
            # Close audio streams properly
            try:
                if hasattr(self, 'audio_stream') and self.audio_stream:
                    self.audio_stream.stop_stream()
                    self.audio_stream.close()
                    self.audio_stream = None
                
                if hasattr(self, 'stream') and self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
                    self.stream = None
            except Exception as e:
                print(f"Error closing audio streams: {e}")
            
            # Close sockets
            if hasattr(self, 'client_socket') and self.client_socket:
                try:
                    self.client_socket.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                self.client_socket.close()
                self.client_socket = None

            if hasattr(self, 'audio_socket') and self.audio_socket:
                try:
                    self.audio_socket.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                self.audio_socket.close()
                self.audio_socket = None

            # Close the meeting window
            self.Meeting_root.destroy()
            btn1.config(state=NORMAL)
            btn2.config(state=NORMAL)
            
            # Show toast notification
            self.toast = ToastNotification(title = "LinkHub",
                                            message = "Meeting ended",
                                            duration= 3000,
                                            bootstyle = "danger",
                                            alert = True,
                                            )
            self.toast.show_toast()


#GUI Creation
root = tb.Window(title="LinkHub",themename="morph",size=(800,400))

root.iconbitmap("img/ppico.ico")

#Meeting obj

meeting = Meeting()

#function

def connection_pop():
    global con_pop, MC_Sumbit_btn, MC_SERVER_IP_entry, MC_Meeting_password_entry

    con_pop = tb.Toplevel(size=(600,450))
    con_pop.iconbitmap("img/ppico.ico")

    MC_SERVER_IP_label = tb.Label(con_pop,text="Enter the ID of the meeting:",font=("Rockwell Extra Bold",18))
    MC_SERVER_IP_label.pack(padx=40,pady=10)
    
    MC_SERVER_IP_entry = tb.Entry(con_pop,bootstyle="success")
    MC_SERVER_IP_entry.pack(padx=40,ipadx=60,pady=10)

    MC_Meeting_password_label = tb.Label(con_pop,text="Enter the Password:",font=("Rockwell Extra Bold",18))
    MC_Meeting_password_label.pack(padx=40,pady=10)

    MC_Meeting_password_entry = tb.Entry(con_pop,bootstyle = "success")
    MC_Meeting_password_entry.pack(padx=40,ipadx=60,pady=10)

    MC_name_entry_label = tb.Label(con_pop, text="Enter your Name:",font=("Rockwell Extra Bold",18))
    MC_name_entry_label.pack(padx=40,pady=10)

    MC_name_entry = tb.Entry(con_pop,bootstyle="success")
    MC_name_entry.pack(padx=40,ipadx=60,pady=10)

    MC_Sumbit_btn = tb.Button(con_pop,text="CONNECT",bootstyle="info",command=lambda : meeting.connecting_meeting(MC_name_entry.get()))
    MC_Sumbit_btn.pack(padx=10,pady=20)

def host_name_entry():

    global HNE_name_pop, HNE_Sumbit_btn

    HNE_name_pop = tb.Toplevel(size=(600,250))
    HNE_name_pop.iconbitmap("img/ppico.ico")
    HNE_name_entry_label = tb.Label(HNE_name_pop, text="Enter your Name:",font=("Rockwell Extra Bold",18))
    HNE_name_entry_label.pack(padx=40,pady=10)

    HNE_name_entry = tb.Entry(HNE_name_pop,bootstyle="success")
    HNE_name_entry.pack(padx=40,ipadx=60,pady=10)

    HNE_Sumbit_btn = tb.Button(HNE_name_pop,text="CONNECT",bootstyle="info",command=lambda: meeting.Create_Meeting(HNE_name_entry.get()))
    HNE_Sumbit_btn.pack(padx=10,pady=20)


app_icon1 = Image.open("img/video-camera.png") #type: ignore
resize_app_icon1 = app_icon1.resize((35,35))
meeting_icon = ImageTk.PhotoImage(resize_app_icon1)

app_icon2 = Image.open("img/add.png") #type: ignore
resize_app_icon2 = app_icon2.resize((35,35))
meeting_icon2 = ImageTk.PhotoImage(resize_app_icon2)

title_label = tb.Label(root,text="LinkHub",bootstyle="primary",font=("Old English Text MT",50,'bold'))
title_label.pack(pady=20,padx=20)

frame = tb.Frame(root)
frame.pack(pady=20,padx=20,fill=X)

inter_frame = tb.Frame(frame)
inter_frame.pack(pady=10)
btn1= tb.Button(inter_frame,
                bootstyle = "danger",
                image=meeting_icon,
                compound="left",
                command= host_name_entry
                )
btn1.pack(pady=10,side="left")

btn1_label = tb.Label(inter_frame,text="Create a meeting",font=("Rockwell Extra Bold",18))
btn1_label.pack(padx=10,pady=10,side="left")

inter_frame2 = tb.Frame(frame)
inter_frame2.pack(pady=10)

btn2= tb.Button(inter_frame2,
                bootstyle = "warning",
                image=meeting_icon2,
                compound="left",
                command= connection_pop
                )
btn2.pack(pady=10,side="left")
btn2_label = tb.Label(inter_frame2,text="join a meeting",font=("Rockwell Extra Bold",18))
btn2_label.pack(padx=35,pady=10,side="left")

root.mainloop()