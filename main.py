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

SERVER = ""
PORT= 65432
ADDR = (SERVER,PORT)


class Meeting():
    def __init__(self):
        self.video_image = Image.open("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/img/video-camera.png")
        resize_video_image = self.video_image.resize((35,35))
        self.video_image = ImageTk.PhotoImage(resize_video_image)

        self.audio_image = Image.open("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/img/audio.png")
        resize_audio_image = self.audio_image.resize((35,35))
        self.audio_image = ImageTk.PhotoImage(resize_audio_image) 

        self.info_image = Image.open("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/img/information.png")
        resize_info_image = self.info_image.resize((35,35))
        self.info_image = ImageTk.PhotoImage(resize_info_image)

        self.received_frame = {}
        self.lock = threading.Lock()

        

    def Create_Meeting(self,host_name):

        if HNE_Sumbit_btn:
            HNE_name_pop.destroy()

        self.Meeting_root = tb.Toplevel(title="meeting")
        self.Meeting_root.iconbitmap("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/ppico.ico")
        
        global cap,running,video_label,recv_video_label, recv_video_label2,recv_video_label3
        
        self.name = host_name
        cap = None

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

        video_variable = StringVar(value="Off")
        audio_variable= StringVar(value="Mute")
        Close_meeting_variable = StringVar()

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
                              variable=video_variable,
                              background="#06f912",
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14),
                              command = lambda: start_stop_video(status=True,name=self.name)
                              )

        menu1.add_radiobutton(label="Off",
                              variable=video_variable,
                              background="#d4342b",
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14),
                              command = lambda: start_stop_video(status=False,name=self.name)
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
        close_menu.add_radiobutton(label="End all meeting",
                                   variable=Close_meeting_variable,
                                   background="#d4342b",
                                   foreground="#f8dedd",
                                   font=('Arial Rounded MT Bold',14),
                                   command= lambda :self.end_meeting("End all meeting")
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

        video_alignment_frame = tb.Frame(container_frame)
        video_alignment_frame.pack(pady=5)


        video_label = tb.Label(video_alignment_frame)
        video_label.pack(pady=5,padx=5,side="left")

        recv_video_label = tb.Label(video_alignment_frame)
        recv_video_label.pack(pady=10,padx=5,side="left")

        video_alignment_frame2 = tb.Frame(container_frame)
        video_alignment_frame2.pack(pady=5)


        recv_video_label2 = tb.Label(video_alignment_frame2)
        recv_video_label2.pack(pady=5,padx=5,side="left")

        recv_video_label3 = tb.Label(video_alignment_frame2)
        recv_video_label3.pack(pady=5,padx=5,side="left")

        start_stop_video(status=False,name=self.name)
        #blank_frame(430,470)
        


        btn1.config(state=DISABLED)
        btn2.config(state=DISABLED)
        

    def connecting_meeting(self,part_name):
        if MC_Sumbit_btn:
            con_pop.destroy()

        self.Meeting_root = tb.Toplevel(title="meeting",
                                        position= (0,0)
                                        )
        self.Meeting_root.iconbitmap("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/ppico.ico")
        
        global cap,running,video_label,recv_video_label,recv_video_label2,recv_video_label3
        
        self.name = part_name

        cap = None

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

        video_variable = StringVar(value="Off")
        audio_variable= StringVar(value="Mute")

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
                              variable=video_variable,
                              background="#06f912",
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14),
                              command = lambda: start_stop_video(status=True,name=self.name)
                              )

        menu1.add_radiobutton(label="Off",
                              variable=video_variable,
                              background="#d4342b",
                              foreground="#f8dedd",
                              font=('Arial Rounded MT Bold',14),
                              command = lambda: start_stop_video(status=False,name=self.name)
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


        video_label = tb.Label(video_alignment_frame)
        video_label.pack(pady=5)

        video_label = tb.Label(video_alignment_frame)
        video_label.pack(pady=5,padx=5,side="left")

        recv_video_label = tb.Label(video_alignment_frame)
        recv_video_label.pack(pady=10,padx=5,side="left")

        video_alignment_frame2 = tb.Frame(container_frame)
        video_alignment_frame2.pack(pady=5)


        recv_video_label2 = tb.Label(video_alignment_frame2)
        recv_video_label2.pack(pady=5,padx=5,side="left")

        recv_video_label3 = tb.Label(video_alignment_frame2)
        recv_video_label3.pack(pady=5,padx=5,side="left")
        
        start_stop_video(status=False,name=self.name)
        blank_frame(430,470)

        btn1.config(state=DISABLED)
        btn2.config(state=DISABLED)
    '''
    def start_stop_video(self,status = False, name=None):
        global running, video_label
        running = status
        self.cap = cv.VideoCapture(0)
        if running:
            if not self.cap.isOpened():
                print("Error: Could not open video source.")
                running = False
                return
            
            self.video_loop()

        if not running:
            if self.cap:
                self.cap.release()
                
            blank = np.zeros((430,470,3),dtype='uint8')
            text_size = cv.getTextSize(name,cv.FONT_HERSHEY_SIMPLEX,1.0,2)[0]
            text_x = (blank.shape[1] - text_size[0])//2
            text_y = (blank.shape[0] + text_size[1])//2
            text_frame = cv.putText(blank,name,(text_x,text_y),cv.FONT_HERSHEY_SIMPLEX,1.0,(255,255,255),2)
            img = Image.fromarray(text_frame)
            imageTK = ImageTk.PhotoImage(img)
            video_label.imageTK = imageTK
            video_label.configure(image=imageTK)


    def video_loop(self):
        global running, video_label
        if running:
            ret, frame = self.cap.read()
            if ret:
                try:

                    new_width = 470
                    new_height = 430
                    
                    new_frame = cv.resize(frame,(new_width,new_height))
                    frame = cv.cvtColor(new_frame,cv.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    imgTk = ImageTk.PhotoImage(img)
                    video_label.imgTk = imgTk
                    video_label.configure(image = imgTk)
                except Exception as e:
                    print(f"Error in video loop: {e}")
                    self.start_stop_video(status=False)

            else:
                print("failed to capture frame.")
            video_label.after(10, self.video_loop)   
    '''
    def send_video(self):
        pass

    def recv_video(self):
        pass
    def send_audio(self):
        pass

    def recv_audio(self):
        pass

    def end_meeting(self,Close):

        if Close in "End all meeting":
            start_stop_video(status=False)
            self.Meeting_root.destroy()
            btn1.config(state=NORMAL)
            btn2.config(state=NORMAL)

        if Close in "End meeting":
            start_stop_video(status=False)
            self.Meeting_root.destroy()
            btn1.config(state=NORMAL)
            btn2.config(state=NORMAL)

#GUI Creation
root = tb.Window(title="quak join",themename="morph",size=(800,400))

root.iconbitmap("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/ppico.ico")

#Meeting obj

meeting = Meeting()

#function

def connection_pop():
    global con_pop, MC_Sumbit_btn

    con_pop = tb.Toplevel(size=(600,450))
    con_pop.iconbitmap("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/ppico.ico")

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
    HNE_name_pop.iconbitmap("C:/Users/dharshan/Desktop/lang and tools/pyvsc/final_year_project/ppico.ico")
    HNE_name_entry_label = tb.Label(HNE_name_pop, text="Enter your Name:",font=("Rockwell Extra Bold",18))
    HNE_name_entry_label.pack(padx=40,pady=10)

    HNE_name_entry = tb.Entry(HNE_name_pop,bootstyle="success")
    HNE_name_entry.pack(padx=40,ipadx=60,pady=10)

    HNE_Sumbit_btn = tb.Button(HNE_name_pop,text="CONNECT",bootstyle="info",command=lambda: meeting.Create_Meeting(HNE_name_entry.get()))
    HNE_Sumbit_btn.pack(padx=10,pady=20)

def start_stop_video(status = False, name=None):
    global cap, running, video_label
    running = status
    if running:
        cap = cv.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open video source.")
            running = False
            return
        
        video_loop()

    if not running:
        if cap:
            cap.release()
            cap = None
        blank = np.zeros((430,470,3),dtype='uint8')
        text_size = cv.getTextSize(name,cv.FONT_HERSHEY_SIMPLEX,1.0,2)[0]
        text_x = (blank.shape[1] - text_size[0])//2
        text_y = (blank.shape[0] + text_size[1])//2
        text_frame = cv.putText(blank,name,(text_x,text_y),cv.FONT_HERSHEY_SIMPLEX,1.0,(255,255,255),2)
        img = Image.fromarray(text_frame)
        imageTK = ImageTk.PhotoImage(img)
        video_label.imageTK = imageTK
        video_label.configure(image=imageTK)


def video_loop():
    global cap, running, video_label
    if running:
        ret, frame = cap.read()
        if ret:
            try:

                new_width = 470
                new_height = 430
                
                new_frame = cv.resize(frame,(new_width,new_height))
                frame = cv.cvtColor(new_frame,cv.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgTk = ImageTk.PhotoImage(img)
                video_label.imgTk = imgTk
                video_label.configure(image = imgTk)
            except Exception as e:
                print(f"Error in video loop: {e}")
                start_stop_video(status=False)

        else:
            print("failed to capture frame.")
        video_label.after(10, video_loop)   

'''
def start_video():
    global cap, running

    if not running:
        running = True
        cap = cv.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open video source.")
            running = False
            return
        
        #threading.Thread(target=meeting.send_video).start()
        video_loop()


def video_loop():
    global cap, running, video_label

    if running:
        ret, frame = cap.read()
        if ret:
            #print(frame.shape)
            try:
                #width, height = frame.shape[:2]
                #print(width,height)
                new_width = 470
                new_height = 430

                resize_video_frame = cv.resize(frame, (new_width,new_height))

                frame = cv.cvtColor(resize_video_frame, cv.COLOR_BGR2RGB)
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
    
    blank_frame(430,470)
'''
def blank_frame(h,w):
    global  recv_video_label, recv_video_label2, recv_video_label3
    #blank = np.zeros((h,w,3),dtype='uint8')
    
    # if name:
    #     text_size = cv.getTextSize(name,cv.FONT_HERSHEY_TRIPLEX,1.0,2)[0]
    #     text_x = (blank.shape[1] - text_size[0])//2
    #     text_y = (blank.shape[0] + text_size[1])//2
    #     cv.putText(blank,name,(text_x,text_y),cv.FONT_HERSHEY_TRIPLEX,1.0,(255,255,255),2)
    
    blank = np.zeros((h,w),dtype='uint8')
    img = Image.fromarray(blank)
    imageTk = ImageTk.PhotoImage(img)
    recv_video_label.imageTk = imageTk 
    recv_video_label.configure(image=imageTk)

    recv_video_label2.imageTk = imageTk 
    recv_video_label2.configure(image=imageTk)

    recv_video_label3.imageTk = imageTk 
    recv_video_label3.configure(image=imageTk)

app_icon1 = Image.open("final_year_project/img/video-camera.png") #type: ignore
resize_app_icon1 = app_icon1.resize((35,35))
meeting_icon = ImageTk.PhotoImage(resize_app_icon1)

app_icon2 = Image.open("final_year_project/img/add.png") #type: ignore
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