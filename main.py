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

        if HNE_Sumbit_btn:
            HNE_name_pop.destroy()

        self.Meeting_root = tb.Toplevel(title="meeting",
                                      #themename="morph",
                                      #size=(600,400)
                                      )
        self.Meeting_root.iconbitmap("ppico.ico")
        
        global cap, running, video_label,host_name
        
        host_name = name
        self.meeting_host = True

        cap = None
        running = False

        self.video_image = Image.open("img/video-camera.png")
        resize_video_image = self.video_image.resize((35,35))
        self.video_image = ImageTk.PhotoImage(resize_video_image)

        self.audio_image = Image.open("img/audio.png")
        resize_audio_image = self.audio_image.resize((35,35))
        self.audio_image = ImageTk.PhotoImage(resize_audio_image)

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
                                   font=('Arial Rounded MT Bold',14),
                                   command= lambda :self.end_meeting("End all")
                                   )
        
        close_menu.add_radiobutton(label="End meeting",
                                   variable=Close_meeting_variable,
                                   background="#6a8daf",
                                   foreground="#f8dedd",
                                   font=('Arial Rounded MT Bold',14),
                                   command= lambda: self.end_meeting("End meeting")
                                   )
        
        video_menu['menu'] = menu1
        audio_menu['menu'] = menu2
        Close_meeting['menu'] = close_menu

        #self.Meeting_root.mainloop()

        btn1.config(state=DISABLED)
        btn2.config(state=DISABLED)
        

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

    def end_meeting(self,Close):

        if Close in "End all":
            stop_video()
            self.Meeting_root.destroy()
            btn1.config(state=NORMAL)
            btn2.config(state=NORMAL)

        if Close in "End meeting":
            stop_video()
            self.Meeting_root.destroy()
            btn1.config(state=NORMAL)
            btn2.config(state=NORMAL)

#app = Meeting()
#app.Create_Meeting("dharshan")

#GUI Creation
root = tb.Window(title="quak join",themename="morph",size=(800,400))

root.iconbitmap("ppico.ico")

#Meeting obj

meeting = Meeting()


#function

def connection_pop():
    con_pop = tb.Toplevel(size=(600,450))
    con_pop.iconbitmap("ppico.ico")

    SERVER_IP_label = tb.Label(con_pop,text="Enter the ID of the meeting:",font=("Rockwell Extra Bold",18))
    SERVER_IP_label.pack(padx=40,pady=10)
    
    SERVER_IP_entry = tb.Entry(con_pop,bootstyle="success")
    SERVER_IP_entry.pack(padx=40,ipadx=60,pady=10)

    Meeting_password_label = tb.Label(con_pop,text="Enter the Password:",font=("Rockwell Extra Bold",18))
    Meeting_password_label.pack(padx=40,pady=10)

    Meeting_password_entry = tb.Entry(con_pop,bootstyle = "success")
    Meeting_password_entry.pack(padx=40,ipadx=60,pady=10)

    name_entry_label = tb.Label(con_pop, text="Enter your Name:",font=("Rockwell Extra Bold",18))
    name_entry_label.pack(padx=40,pady=10)

    name_entry = tb.Entry(con_pop,bootstyle="success")
    name_entry.pack(padx=40,ipadx=60,pady=10)

    Sumbit_btn = tb.Button(con_pop,text="CONNECT",bootstyle="info")
    Sumbit_btn.pack(padx=10,pady=20)

def host_name_entry():

    global HNE_name_pop, HNE_Sumbit_btn

    HNE_name_pop = tb.Toplevel(size=(600,250))
    HNE_name_pop.iconbitmap("ppico.ico")
    HNE_name_entry_label = tb.Label(HNE_name_pop, text="Enter your Name:",font=("Rockwell Extra Bold",18))
    HNE_name_entry_label.pack(padx=40,pady=10)

    HNE_name_entry = tb.Entry(HNE_name_pop,bootstyle="success")
    HNE_name_entry.pack(padx=40,ipadx=60,pady=10)

    HNE_Sumbit_btn = tb.Button(HNE_name_pop,text="CONNECT",bootstyle="info",command=lambda: meeting.Create_Meeting(HNE_name_entry))
    HNE_Sumbit_btn.pack(padx=10,pady=20)

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

app_icon1 = Image.open("img/video-camera.png")
resize_app_icon1 = app_icon1.resize((35,35))
meeting_icon = ImageTk.PhotoImage(resize_app_icon1)

app_icon2 = Image.open("img/add.png")
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