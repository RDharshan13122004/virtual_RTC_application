import socket
from tkinter import *
import ttkbootstrap as tb
import numpy as np
from PIL import ImageTk,Image
from cv2 import *
import cv2 as cv

SERVER = ""
PORT= 65432
ADDR = (SERVER,PORT)
FORMAT = 'utf-8'

class Meeting():

    def Create_Meeting(self,name):
        self.Meeting_root = tb.Window(title="meeting",
                                      themename="morph",
                                      #size=(600,400)
                                      )
        self.Meeting_root.iconbitmap("final_year_project/ppico.ico")
        
        global cap, running, video_label,host_name
        
        host_name = name
        self.meeting_host = True

        cap = None
        running = False

        self.video_image = Image.open("final_year_project/img/video-camera.png")
        resize_video_image = self.video_image.resize((35,35))
        self.video_image = ImageTk.PhotoImage(resize_video_image)

        self.audio_image = Image.open("final_year_project/img/audio.png")
        resize_audio_image = self.audio_image.resize((35,35))
        self.audio_image = ImageTk.PhotoImage(resize_audio_image)


        '''
        self.capture = cv.VideoCapture(0)

        while True:

            isTrue , frame = self.capture.read()
            cv.imshow('Video',frame)

            if cv.waitKey(20) & 0XFF==ord('d'):
                break

        self.capture.release()
        cv.destroyAllWindows()
        '''

        video_label = tb.Label(self.Meeting_root)
        video_label.pack(pady=20)

        menus_frame = tb.Frame(self.Meeting_root)
        menus_frame.pack(pady=10)

        video_variable = StringVar(value="Off")
        audio_variable= StringVar(value="Mute")
        Close_meeting_variable = StringVar()

        video_menu = tb.Menubutton(menus_frame,
                                    direction='above',
                                    #text="video status",
                                    image=self.video_image,
                                    compound=LEFT
                                    )
        video_menu.pack(pady=20,padx=30,side="left")

        audio_menu = tb.Menubutton(menus_frame,
                                    direction='above',
                                    image= self.audio_image,
                                    compound=LEFT
                                    )
        audio_menu.pack(pady=20,padx=30,side="left")

        Close_meeting = tb.Menubutton(menus_frame,
                                      direction='above',
                                      text="End",
                                      compound=LEFT,
                                      bootstyle = "danger"
                                      )
        Close_meeting.pack(pady=20,padx=30,ipadx=9,ipady=9)

        menu1= tb.Menu(video_menu, tearoff=0)
        menu1.add_radiobutton(label="On",
                              variable=video_variable,
                              background="#06f912",
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14),
                              command = start_video
                              )

        menu1.add_radiobutton(label="Off",
                              variable=video_variable,
                              background="#d4342b",
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14),
                              command = stop_video
                              )
        
        menu2 = tb.Menu(audio_menu, tearoff=0)
        menu2.add_radiobutton(label="Unmute",
                              variable=audio_variable,
                              background="#06f912",
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14)
                              )
        
        menu2.add_radiobutton(label="Mute",
                               variable=audio_variable,
                               background="#d4342b",
                               foreground="#f8dedd",
                               font=('Arial Rounded MT Bold',14)
                               )
        
        close_menu = tb.Menu(Close_meeting, tearoff=0)
        close_menu.add_radiobutton(label="End all",
                                   variable=Close_meeting_variable,
                                   background="#d4342b",
                                   foreground="#f8dedd",
                                   font=('Arial Rounded MT Bold',14)
                                   )
        
        close_menu.add_radiobutton(label="End meeting",
                                   variable=Close_meeting_variable,
                                   background="#6a8daf",
                                   foreground="#f8dedd",
                                   font=('Arial Rounded MT Bold',14)
                                   )
        
        video_menu['menu'] = menu1
        audio_menu['menu'] = menu2
        Close_meeting['menu'] = close_menu

        self.Meeting_root.mainloop()

    def connecting_meeting():
        pass

    def send_video():
        pass

    def recv_video():
        pass

    def send_audio():
        pass

    def recv_audio():
        pass

def start_video():
    global cap, running

    if not running:
        running = True
        cap = cv.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open video source.")
            running = False
            return
        video_loop()

def video_loop():
    global cap, running, video_label

    if running:
        ret, frame = cap.read()
        if ret:
            #print(frame.shape)
            try:
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)

                video_label.imgtk = imgtk
                video_label.configure(image=imgtk)
            except Exception as e:
                print(f"Error in video loop: {e}")
                stop_video()
        else:
            print("Failed to capture frame.")
        video_label.after(10, video_loop)

def stop_video():
    global cap, running, video_label
    running = False

    if cap:
        cap.release()
    
    #blank = np.zeros((480, 640, 3),dtype='uint8')
    #offimg = cv.putText(blank,host_name,(255,255),cv.FONT_HERSHEY_TRIPLEX,1.0,(0,255,0),2)
    video_label.configure(image="")


app = Meeting()
app.Create_Meeting("dharshan")


