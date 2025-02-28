import socket
from tkinter import * #import the module for creating GUI(graphical userinterface)
import ttkbootstrap as tb #type: ignore  #importing the support bootstrap module for tkinter
import numpy as np
from PIL import ImageTk, Image #type: ignore # this module helps to assign images for button and displaying the received image from clients into the grid system
from cv2 import *
import cv2 as cv
import zlib
import struct
import threading
import numpy as np
import pyaudio

SERVER = "192.168.29.12"
V_PORT = 65432
A_PORT = 50000 
VP_ADDR = (SERVER,V_PORT)
AP_ADDR = (SERVER,A_PORT)

A_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 32000
CHUNK = 256


class Meeting():
    def __init__(self):
        self.video_image = Image.open("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/img/video-camera.png") #collecting image from location
        resize_video_image = self.video_image.resize((35,35)) #resizing the image
        self.video_image = ImageTk.PhotoImage(resize_video_image) # assigning the resized image as object

        self.audio_image = Image.open("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/img/audio.png") #collecting image from location
        resize_audio_image = self.audio_image.resize((35,35)) #resizing the image
        self.audio_image = ImageTk.PhotoImage(resize_audio_image) # assigning the resized image as object

        self.info_image = Image.open("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/img/information.png") #collecting image from location
        resize_info_image = self.info_image.resize((35,35)) #resizing the image
        self.info_image = ImageTk.PhotoImage(resize_info_image) # assigning the resized image as object

        self.received_frame = {}
        self.lock = threading.Lock()
        self.cap = None
        self.client_socket = None
        self.audio_socket = None

        self.audio_stream = None
        self.audio = pyaudio.PyAudio()


    def Create_Meeting(self,host_name):

        try:
            if not hasattr(self, 'client_socket') or self.client_socket is None:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self.client_socket.connect(VP_ADDR)
                print("Connected to video server.")

            if not hasattr(self, 'audio_socket') or self.audio_socket is None:
                self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.audio_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.audio_socket.connect(AP_ADDR)
                print("Connected to audio server.")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return        
        
        
        if HNE_Sumbit_btn: #identifing the name GUI 
            HNE_name_pop.destroy() #destorying it once the condtition is satisfy 

        self.Meeting_root = tb.Toplevel(title="meeting",position=(0,0)) #creating a meeting pop object with title and position 
        self.Meeting_root.iconbitmap("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/ppico.ico") #setting icon for meeting
        
        
        self.name = host_name

        container_frame = tb.Frame(self.Meeting_root) #creating a frame that divides menu items and grid system
        container_frame.pack(fill="both")

        menus_frame = tb.Frame(container_frame) #creating a from holds menu items
        menus_frame.pack(pady=10,side="left")

        # adding meeting info button
        info_btn = tb.Button(menus_frame,
                             image=self.info_image,
                             bootstyle = "success"
                             )
        info_btn.pack(pady=20,padx=30)

        #setting boolean variable for video and audio button
        self.video_variable = BooleanVar(value=False)
        self.audio_variable= BooleanVar(value=False)

        #adding video button
        video_menu = tb.Menubutton(menus_frame,
                                    direction='above',
                                    #text="video status",
                                    image=self.video_image,
                                    compound=LEFT
                                    )
        video_menu.pack(pady=20,padx=30)

        # adding audio button
        audio_menu = tb.Menubutton(menus_frame,
                                    direction='above',
                                    image= self.audio_image,
                                    compound=LEFT
                                    )
        audio_menu.pack(pady=20,padx=30)

        # adding close meeting button
        Close_meeting = tb.Menubutton(menus_frame,
                                      direction='above',
                                      text="End",
                                      compound=LEFT,
                                      bootstyle = "danger"
                                      )
        Close_meeting.pack(pady=20,padx=30,ipadx=9,ipady=9)


        #setting video menu option
        menu1= tb.Menu(video_menu, tearoff=0)
        #setting option for video menu
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
        
        #setting audio menu option
        menu2 = tb.Menu(audio_menu, tearoff=0)
        #setting option for audio menu
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
                               font=('Arial Rounded MT Bold',14)
                               )
        # setting close meeting menu option
        close_menu = tb.Menu(Close_meeting, tearoff=0)
        #setting option for close meeting menu
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
        #setting menu object for the menu button object
        video_menu['menu'] = menu1
        audio_menu['menu'] = menu2
        Close_meeting['menu'] = close_menu

        #creating frame for first row in grid system 
        video_alignment_frame = tb.Frame(container_frame)
        video_alignment_frame.pack(pady=5)

        #assigning label row 0 col 0
        self.video_label = tb.Label(video_alignment_frame)
        self.video_label.pack(pady=5,padx=5,side="left")
        #assigning label row 0 col 1
        self.recv_video_label = tb.Label(video_alignment_frame)
        self.recv_video_label.pack(pady=10,padx=5,side="left")

        #creating frame for second row in grid system 
        video_alignment_frame2 = tb.Frame(container_frame)
        video_alignment_frame2.pack(pady=5)

        #assigning label row 1 col 0
        self.recv_video_label2 = tb.Label(video_alignment_frame2)
        self.recv_video_label2.pack(pady=5,padx=5,side="left")

        #assigning label row 1 col 1
        self.recv_video_label3 = tb.Label(video_alignment_frame2)
        self.recv_video_label3.pack(pady=5,padx=5,side="left")

        #assigning host frame
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

        #disabling creating meeting button and join meeting button onces the meeting started
        btn1.config(state=DISABLED)
        btn2.config(state=DISABLED)
        

    def connecting_meeting(self,part_name):
        if MC_Sumbit_btn: #identifing the name,ip address,password GUI
            con_pop.destroy() #destorying it once the condtition is satisfy 

        self.Meeting_root = tb.Toplevel(title="meeting",position= (0,0)) #creating a meeting pop object with title and position 
        self.Meeting_root.iconbitmap("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/ppico.ico") #setting icon for meeting
        
        self.name = part_name

        container_frame = tb.Frame(self.Meeting_root) #creating a frame that divides menu items and grid system
        container_frame.pack(fill="both")

        menus_frame = tb.Frame(container_frame) #creating a from holds menu items
        menus_frame.pack(side="left")

        # adding meeting info button
        info_btn = tb.Button(menus_frame,
                             image= self.info_image,
                             bootstyle = "success"
                             )
        info_btn.pack(pady=10,padx=30)

        #setting boolean variable for video and audio button
        self.video_variable = BooleanVar(value=False)
        self.audio_variable= BooleanVar(value=False)

        #adding video button
        video_menu = tb.Menubutton(menus_frame,
                                    direction='above',
                                    #text="video status",
                                    image=self.video_image,
                                    compound=LEFT
                                    )
        video_menu.pack(pady=20,padx=30)

        # adding audio button
        audio_menu = tb.Menubutton(menus_frame,
                                    direction='above',
                                    image= self.audio_image,
                                    compound=LEFT
                                    )
        audio_menu.pack(pady=20,padx=30)

        #setting video menu option
        menu1= tb.Menu(video_menu, tearoff=0)
        #setting option for video menu
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
        #setting audio menu option
        menu2 = tb.Menu(audio_menu, tearoff=0)
        #setting option for audio menu
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
        
        #giving style for the button
        style = tb.Style()
        style.configure("danger.Outline.TButton",font=("Helvetica",17))

        # adding End meeting button
        close_meeting_btn = tb.Button(menus_frame,
                                      bootstyle = "danger",
                                      text="End",
                                      style="danger.Outline.TButton",
                                      command= lambda: meeting.end_meeting("End meeting")
                                      )
        close_meeting_btn.pack(pady=20,ipadx=5,padx=10)
        
        #setting menu object for the menu button object
        video_menu['menu'] = menu1
        audio_menu['menu'] = menu2

        #creating frame for first row in grid system
        video_alignment_frame = tb.Frame(container_frame)
        video_alignment_frame.pack(pady=5)

        #assigning label row 0 col 0
        self.video_label = tb.Label(video_alignment_frame)
        self.video_label.pack(pady=5,padx=5,side="left")

        #assigning label row 0 col 1
        self.recv_video_label = tb.Label(video_alignment_frame)
        self.recv_video_label.pack(pady=10,padx=5,side="left")

        #creating frame for second row in grid system
        video_alignment_frame2 = tb.Frame(container_frame)
        video_alignment_frame2.pack(pady=5)

        #assigning label row 1 col 0
        self.recv_video_label2 = tb.Label(video_alignment_frame2)
        self.recv_video_label2.pack(pady=5,padx=5,side="left")

        #assigning label row 1 col 1
        self.recv_video_label3 = tb.Label(video_alignment_frame2)
        self.recv_video_label3.pack(pady=5,padx=5,side="left")

        #assigning host frame
        btn1.config(state=DISABLED)
        btn2.config(state=DISABLED)
    
    def start_stop_video(self):   
        if self.video_variable.get():  #if video is on then start the video stream 

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
        img = Image.fromarray(text_frame)  # converting the frame to image
        imageTK = ImageTk.PhotoImage(img) # converting the image to imageTK
        self.video_label.imageTK = imageTK # assigning the imageTK to the label
        self.video_label.configure(image=imageTK) # configuring the label with imageTK

    def video_loop(self,frame):
        try:
            img = Image.fromarray(frame) # converting the frame to image
            imgTk = ImageTk.PhotoImage(img) # converting the image to imageTK
            self.video_label.imgTk = imgTk # assigning the imageTK to the label
            self.video_label.configure(image = imgTk) # configuring the label with imageTK
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
                
                self.video_label.after(10,self.video_loop,frame) #updating the video label with the frame
                
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

    def display_recv_frame(self): #function for displaying the received frame
        try: #try block for displaying the received frame
            with self.lock: #lock the frame
                received_clients = list(self.received_frame.keys()) #get the list of received clients
                labels = [self.recv_video_label,self.recv_video_label2,self.recv_video_label3] #assigning the labels to the list

                for i in range(len(labels)): #looping through the labels
                    if i >= len(received_clients): #if the label is greater than the received clients then configure the label with imageTK as None
                        labels[i].config(image= None) #configuring the label with imageTK as None
                
                for i, client_id in enumerate(received_clients[:len(labels)]): #looping through the received clients
                    frame = self.received_frame.get(client_id) #get the frame from the received clients

                    if frame is not None: #if the frame is not None then resize the frame and convert it to image and imageTK
                        frame = cv.resize(frame,(470,430)) #resize the frame
                        img = Image.fromarray(cv.cvtColor(frame,cv.COLOR_BGR2RGB)) #convert the frame to image
                        imgtk = ImageTk.PhotoImage(img) #convert the image to imageTK

                        labels[i].imgtk = imgtk #assigning the imageTK to the label
                        labels[i].configure(image=imgtk) #configuring the label with imageTK
                    else:
                        del self.received_frame[client_id] #if the frame is None then delete the frame from the received clients
        except Exception as e: #except block for displaying the received frame
            print(f"Error in video loop: {e}") #print the error message
        
        self.recv_video_label.after(10,self.display_recv_frame) #updating the label with the frame

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
                try:
                    data = self.audio_stream.read(CHUNK, exception_on_overflow=False)
                    self.audio_socket.sendall(data)
                except Exception as e:
                    print(f"Audio send error: {e}")
                    break
        finally:
            self.audio_stream.stop_stream()
            self.audio_stream.close()

    def recv_audio(self):
        stream = self.audio.open(format= A_FORMAT, channels=CHANNELS, rate=RATE,output=True, frames_per_buffer=CHUNK)
        while True:
            try:    
                data = self.audio_socket.recv(CHUNK * 2)
                if not data:
                    break
                stream.write(data)
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
            if not hasattr(self, 'recv_thread') or not self.recv_thread.is_alive():
                self.recv_thread.join()  
            if not hasattr(self, 'audio_thread') or not self.audio_thread.is_alive():
                self.audio_thread.join()
            if not hasattr(self, 'Arecv_thread') or not self.Arecv_thread.is_alive():
                self.Arecv_thread.join() 
            if not hasattr(self, 'grid_thread') or not self.grid_thread.is_alive():
                self.grid_thread.join() 
            if hasattr(self,'client_socket') and self.client_socket:
                self.client_socket.close()
            if hasattr(self,'audio_socket') and self.audio_socket:
                self.audio_socket.close()
            self.Meeting_root.destroy() #destroy the meeting pop
            btn1.config(state=NORMAL) #enable the create meeting button
            btn2.config(state=NORMAL) # enable the join meeting button

        if Close in "End meeting":
            if hasattr(self,'cap') and self.cap:
                self.cap.release()
                self.cap = None
            if not hasattr(self, 'send_thread') or not self.send_thread.is_alive():
                self.send_thread.join()
            if not hasattr(self, 'recv_thread') or not self.recv_thread.is_alive():
                self.recv_thread.join()  
            if not hasattr(self, 'audio_thread') or not self.audio_thread.is_alive():
                self.audio_thread.join()
            if not hasattr(self, 'Arecv_thread') or not self.Arecv_thread.is_alive():
                self.Arecv_thread.join() 
            if not hasattr(self, 'grid_thread') or not self.grid_thread.is_alive():
                self.grid_thread.join() 
            if hasattr(self,'client_socket') and self.client_socket:
                self.client_socket.close()
            if hasattr(self,'audio_socket') and self.audio_socket:
                self.audio_socket.close()
            self.Meeting_root.destroy() #destroy the meeting pop
            btn1.config(state=NORMAL) #enable the create meeting button
            btn2.config(state=NORMAL) # enable the join meeting button

#GUI Creation
root = tb.Window(title="quak join",themename="morph",size=(800,400)) #creating a window object with title and size

root.iconbitmap("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/ppico.ico") #setting icon for the window

#Meeting obj

meeting = Meeting() #creating a meeting object

#function

def connection_pop(): #function for creating connection pop
    global con_pop, MC_Sumbit_btn #global variable for connection pop and submit button

    con_pop = tb.Toplevel(size=(600,450)) #creating a pop object with size
    con_pop.iconbitmap("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/ppico.ico") # setting icon for pop

    MC_SERVER_IP_label = tb.Label(con_pop,text="Enter the ID of the meeting:",font=("Rockwell Extra Bold",18)) #creating a label for the pop
    MC_SERVER_IP_label.pack(padx=40,pady=10)
    
    MC_SERVER_IP_entry = tb.Entry(con_pop,bootstyle="success") #creating an entry for the pop
    MC_SERVER_IP_entry.pack(padx=40,ipadx=60,pady=10)

    MC_Meeting_password_label = tb.Label(con_pop,text="Enter the Password:",font=("Rockwell Extra Bold",18)) #creating a label for the pop
    MC_Meeting_password_label.pack(padx=40,pady=10)

    MC_Meeting_password_entry = tb.Entry(con_pop,bootstyle = "success") #creating an entry for the pop
    MC_Meeting_password_entry.pack(padx=40,ipadx=60,pady=10)

    MC_name_entry_label = tb.Label(con_pop, text="Enter your Name:",font=("Rockwell Extra Bold",18)) #creating a label for the pop
    MC_name_entry_label.pack(padx=40,pady=10)

    MC_name_entry = tb.Entry(con_pop,bootstyle="success") #creating an entry for the pop
    MC_name_entry.pack(padx=40,ipadx=60,pady=10)

    MC_Sumbit_btn = tb.Button(con_pop,text="CONNECT",bootstyle="info",command=lambda : meeting.connecting_meeting(MC_name_entry.get())) #creating a button for the pop
    MC_Sumbit_btn.pack(padx=10,pady=20)

def host_name_entry(): # function for creating host name entry pop

    global HNE_name_pop, HNE_Sumbit_btn #global variable for host name pop and submit button

    HNE_name_pop = tb.Toplevel(size=(600,250)) #creating a pop object with size
    HNE_name_pop.iconbitmap("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/ppico.ico") #setting icon for pop
    HNE_name_entry_label = tb.Label(HNE_name_pop, text="Enter your Name:",font=("Rockwell Extra Bold",18)) #creating a label for the pop
    HNE_name_entry_label.pack(padx=40,pady=10)

    HNE_name_entry = tb.Entry(HNE_name_pop,bootstyle="success") #creating an entry for the pop
    HNE_name_entry.pack(padx=40,ipadx=60,pady=10)

    HNE_Sumbit_btn = tb.Button(HNE_name_pop,text="CONNECT",bootstyle="info",command=lambda: meeting.Create_Meeting(HNE_name_entry.get())) #creating a button for the pop
    HNE_Sumbit_btn.pack(padx=10,pady=20)


app_icon1 = Image.open("final_year_project/img/video-camera.png") #type: ignore #collecting image from location
resize_app_icon1 = app_icon1.resize((35,35)) #resizing the image
meeting_icon = ImageTk.PhotoImage(resize_app_icon1) # assigning the resized image as object

app_icon2 = Image.open("final_year_project/img/add.png") #type: ignore #collecting image from location
resize_app_icon2 = app_icon2.resize((35,35)) #resizing the image
meeting_icon2 = ImageTk.PhotoImage(resize_app_icon2) # assigning the resized image as object

title_label = tb.Label(root,text="quak join",bootstyle="primary",font=("Old English Text MT",50,'bold')) #creating a label for the window
title_label.pack(pady=20,padx=20)

frame = tb.Frame(root) #creating a frame for the window
frame.pack(pady=20,padx=20,fill=X)

inter_frame = tb.Frame(frame) #creating a frame for the frame
inter_frame.pack(pady=10)
btn1= tb.Button(inter_frame, #creating a button for the frame
                bootstyle = "danger",
                image=meeting_icon,
                compound="left",
                command= host_name_entry
                )
btn1.pack(pady=10,side="left")

btn1_label = tb.Label(inter_frame,text="Create a meeting",font=("Rockwell Extra Bold",18)) #creating a label for the frame
btn1_label.pack(padx=10,pady=10,side="left")
 
inter_frame2 = tb.Frame(frame) #creating a frame for the frame
inter_frame2.pack(pady=10)

btn2= tb.Button(inter_frame2, # creating a button for the frame
                bootstyle = "warning",
                image=meeting_icon2,
                compound="left",
                command= connection_pop
                )
btn2.pack(pady=10,side="left")
btn2_label = tb.Label(inter_frame2,text="join a meeting",font=("Rockwell Extra Bold",18)) #creating a label for the frame
btn2_label.pack(padx=35,pady=10,side="left")

root.mainloop() #running the window