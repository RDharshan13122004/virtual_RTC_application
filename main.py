from tkinter import *
import ttkbootstrap as tb
from PIL import Image,ImageTk
from client import Meeting

#GUI Creation
root = tb.Window(title="Dharshan",themename="morph",size=(800,400))

root.iconbitmap("final_year_project/ppico.ico")

#Meeting obj

meeting = Meeting()


#function

def connection_pop():
    con_pop = tb.Toplevel(size=(600,450))
    con_pop.iconbitmap("final_year_project/ppico.ico")

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

    name_pop = tb.Toplevel(size=(600,250))
    name_pop.iconbitmap("final_year_project/ppico.ico")
    name_entry_label = tb.Label(name_pop, text="Enter your Name:",font=("Rockwell Extra Bold",18))
    name_entry_label.pack(padx=40,pady=10)

    name_entry = tb.Entry(name_pop,bootstyle="success")
    name_entry.pack(padx=40,ipadx=60,pady=10)

    Sumbit_btn = tb.Button(name_pop,text="CONNECT",bootstyle="info",command=lambda: meeting.Create_Meeting(name_entry))
    Sumbit_btn.pack(padx=10,pady=20)



app_icon1 = Image.open("final_year_project/img/video-camera.png")
resize_app_icon1 = app_icon1.resize((35,35))
meeting_icon = ImageTk.PhotoImage(resize_app_icon1)

app_icon2 = Image.open("final_year_project/img/add.png")
resize_app_icon2 = app_icon2.resize((35,35))
meeting_icon2 = ImageTk.PhotoImage(resize_app_icon2)

title_label = tb.Label(root,text="Dharshan",bootstyle="primary",font=("Old English Text MT",50,'bold'))
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