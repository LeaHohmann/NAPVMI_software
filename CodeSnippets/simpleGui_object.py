import tkinter as tk
import cv2
import numpy as np
from PIL import Image, ImageTk

def quit_(window):
    window.destroy()

class Group(tk.Frame): # group is a class that inherites all the attributes and methids, e.g. pack() rom Frame

    def set_new_val(self):
        #print('command executed') # for debugging
        value = self.new_value.get() # 'unpack' te value from the variable
        cap.set(self.camera_prop, float(value)) # set the new value
        set_val = cap.get(self.camera_prop) # ask if new value was set
        self.label.configure(text = set_val) # display the new value

    def create_widgets(self):
        new_value_str=tk.StringVar() # initialise the value, without it the code complains it cannot convert the value 
        #new_value_str.set('-8')
        new_value_str.set(cap.get(self.camera_prop))

        self.entry = tk.Entry(self.window,textvariable=new_value_str) # creation of entry field
        self.entry.pack() # make the entry field appear in the frame
        self.new_value = new_value_str # assign a variable to the entry


        self.label = tk.Label(self.window,text=new_value_str) # label creation
        self.label.pack(fill = 'x') # make label appear
        
        self.button = tk.Button(self.window, text=self.name)# creation of button
        self.button["command"]=self.set_new_val # mset the command of the button
        self.button.pack(fill = 'x')# make button appear

    def __init__(self,window,name,position,camera_prop):
        tk.Frame.__init__(self, window) # creates the instance of a frame object
        self.pack() # makes sure the frame appears

        self.window = window # assigns a variable / creates an attribute of the class object
        self.name = name
        self.camera_prop = camera_prop

        self.create_widgets()

cap = cv2.VideoCapture(0)

window = tk.Tk()


gain_control = Group(window,'gain','left', 15) # the object gain_control of Class Group is created, whereby the init function is executed

image_width_control = Group(window,'Image width','left', 3) # the object image_width_control of Class Group is created, whereby the init function is executed

image_height_control = Group(window,'Image height','left', 4) # the object image_width_control of Class Group is created, whereby the init function is executed


display_frame = tk.Frame(window)
display_frame.pack()

###############up to here works quite well

#####displaying the image doesn;t work, but does start the camera
#nmax = 100
#i = 0
#while i < nmax:
#    _, frame = cap.read()
#    gray_im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#    a = Image.fromarray(gray_im)
#    b  = ImageTk.PhotoImage(image=gray_im)
#    i += 1
##    if cv2.waitKey(33) & 0xFF == ord('a'):
##        break



##doesn'r have a command yet
start_button = tk.Button(master=display_frame,text = 'Start')
start_button.pack()


##Works as intended
quit_button = tk.Button(master=window, text='Quit',command=lambda:quit_(window))
quit_button.pack()
nmax = 30



window.mainloop()















