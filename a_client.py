import socket
from tkinter import *
import ttkbootstrap as tb #type: ignore
import numpy as np
from PIL import ImageTk, Image #type: ignore
from cv2 import *
import cv2 as cv
import zlib
import struct
import threading
import numpy as np
import pyaudio

SERVER = "192.168.29.224"
PORT= 65432
ADDR = (SERVER,PORT)

A_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 32000
CHUNK = 256


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

        self.received_frame = {}
        self.lock = threading.Lock()
        self.cap = None
        self.client_socket = None

        self.audio_stream = None
        self.audio = pyaudio.PyAudio()


    def Create_Meeting(self,host_name):

        if not hasattr(self, 'client_socket') or self.client_socket is None:
            try:
                self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self.client_socket.connect(ADDR)
                print("Connect to server")
            except Exception as e:
                print(f"Error connecting to server: {e}")
                return

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
                             #command=
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
                              font=('Arial Rounded MT Bold',14)
                              )
        
        menu2.add_radiobutton(label="Mute",
                               background="#d4342b",
                               foreground="#f8dedd",
                               font=('Arial Rounded MT Bold',14)
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

        self.recv_thread = threading.Thread(target=self.recv_video, daemon=True)
        self.recv_thread.start()

        self.grid_thread = threading.Thread(target=self.display_recv_frame,daemon=True)
        self.grid_thread.start()

        self.Arecv_thread = threading.Thread(target=self.recv_audio,daemon= True)
        self.Arecv_thread.start()

        btn1.config(state=DISABLED)
        btn2.config(state=DISABLED)
        

    def connecting_meeting(self,part_name):
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
                             #command=
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
                              font=('Arial Rounded MT Bold',14)
                              )

        menu1.add_radiobutton(label="Off",
                              variable= self.video_variable,
                              value= False,
                              background="#d4342b",
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14)
                              )
        
        menu2 = tb.Menu(audio_menu, tearoff=0)
        menu2.add_radiobutton(label="Unmute",
                              variable= self.audio_variable,
                              value= True,
                              background="#06f912",
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14)
                              )
        
        menu2.add_radiobutton(label="Mute",
                               background="#d4342b",
                               foreground="#f8dedd",
                               font=('Arial Rounded MT Bold',14)
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

        btn1.config(state=DISABLED)
        btn2.config(state=DISABLED)
    
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
                    self.client_socket.sendall(b"V" + struct.pack("Q",frame_size) + compressed_data)
                except Exception as e:
                    print(f"Error on sending data:{e}")
                    break
        finally:
            if self.cap:
                self.cap.release()

    def recv_video(self):
        try:
            while True:

                identifier = self.client_socket.recv(1)
                if not identifier:
                    break

                if identifier != b"V":  # Ignore non-video packets
                    continue
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

    def start_stop_audio(self):
        if self.audio_variable.get():
            if not hasattr(self,'audio_thread') or not self.audio_thread.is_alive():
                self.audio_thread = threading.Thread(target=self.send_audio, daemon=True)
                self.audio_thread.start()

        else:
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
                    
    def send_audio(self):
        self.audio_stream = self.audio.open(format=A_FORMAT, channels=CHANNELS, rate=RATE,input=True, frames_per_buffer=CHUNK)

        try:
            while self.audio_variable.get():
                data = self.audio_stream.read(CHUNK, exception_on_overflow=False)
                compressed_data = zlib.compress(data)

                try:
                    self.client_socket.sendall(b"A" + struct.pack("Q",len(compressed_data))+ compressed_data)
                except Exception as e:
                    print(f"Audio send error: {e}")
                    break
        finally:
            self.audio_stream.stop_stream()
            self.audio_stream.close()

    def recv_audio(self):
        stream = self.audio.open(format= A_FORMAT, channels=CHANNELS, rate=RATE,output=True, frames_per_buffer=CHUNK)

        try:
            while True:
                identifier = self.client_socket.recv(1)
                if not identifier:
                    break

                if identifier != b"A": 
                    continue
                frame_size_data = self.client_socket.recv(8)
                if not frame_size_data:
                    break
                frame_size = struct.unpack("Q", frame_size_data)[0]

                frame_data = b""
                while len(frame_data) < frame_size:
                    packet = self.client_socket.recv(min(frame_size - len(frame_data), 4096))
                    if not packet:
                        break
                    frame_data += packet

                decompressed_data = zlib.decompress(frame_data)
                stream.write(decompressed_data)
        except Exception as e:
            print(f"Audio receive error: {e}")
        finally:
            stream.stop_stream()
            stream.close()

    def end_meeting(self,Close):
        if Close in "End all meeting":
            if hasattr(self,'cap') and self.cap:
                self.cap.release()
                self.cap = None
            if not hasattr(self, 'send_thread') or not self.send_thread.is_alive():
                self.send_thread.join()
            if not hasattr(self, 'recv_thread') or not self.send_thread.is_alive():
                self.recv_thread.join()  
            if hasattr(self,'client_socket') and self.client_socket:
                self.client_socket.close()
            self.Meeting_root.destroy()
            btn1.config(state=NORMAL)
            btn2.config(state=NORMAL)

        if Close in "End meeting":
            if hasattr(self,'cap') and self.cap:
                self.cap.release()
                self.cap = None
            if not hasattr(self, 'send_thread') or not self.send_thread.is_alive():
                self.send_thread.join()
            if not hasattr(self, 'recv_thread') or not self.send_thread.is_alive():
                self.recv_thread.join()  
            if hasattr(self,'client_socket') and self.client_socket:
                self.client_socket.close()
            self.Meeting_root.destroy()
            btn1.config(state=NORMAL)
            btn2.config(state=NORMAL)

#GUI Creation
root = tb.Window(title="quak join",themename="morph",size=(800,400))

root.iconbitmap("img/ppico.ico")

#Meeting obj

meeting = Meeting()

#function

def connection_pop():
    global con_pop, MC_Sumbit_btn

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

title_label = tb.Label(root,text="quak join",bootstyle="primary",font=("Old English Text MT",50,'bold'))
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