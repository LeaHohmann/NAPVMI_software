import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
import numpy as np

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source

        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack()

        # Button that lets the user take a snapshot
        self.btn_snapshot=tkinter.Button(window, text="Snapshot", width=50, command=self.snapshot)
        self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)
        #Button to set camera gain
        self.btn_gain=tkinter.Button(window,text='gain',width=20,command=self.set_gain)
        self.btn_gain.pack(anchor=tkinter.W,expand=True)
        #Button to stop aquisition
        self.btn_stop = tkinter.Button(window,text='STOP',width=50)
        self.btn_stop.pack(anchor=tkinter.W,expand=True)
        # After it is called once, the update method will be automatically called everydelaymilliseconds
        self.delay = 15
        self.update()
        #set number of frames for acq.
        self.ent_frame_lab = tkinter.Label()
        self.ent_frame = tkinter.Entry(window)
        self.ent_frame.pack

        self.window.mainloop()

    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        nmax = 10
        i = 0
        working = frame
        if ret:
            while i < nmax:
                #if self.btn_stop():
                #    break
                print(i)
                ret, frame = self.vid.get_frame()
                working =working + frame / nmax
                i += 1
            print(type(working[1,2,2]))
            print(type(working[1,2,2]))
            toplot = working.sum(axis=2)
            #cv2.imwrite("working-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(working, cv2.COLOR_RGB2BGR))
            cv2.imwrite("working-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg",toplot)            
            print('done')

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

        self.window.after(self.delay, self.update)

    def set_gain(self):
        mip=cv2.VideoCapture(0)
        self.gain = mip.get(cv2.CAP_PROP_GAIN)
        print(self.gain)



class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        #trying to fix gain button
        #self.gain = self.vid.get(cv2.CAP_PROP_GAIN)
        mip=cv2.VideoCapture(video_source)
        self.gain = mip.get(cv2.CAP_PROP_GAIN)
        print("cool", self.gain)
        #self.vid.set(cv2.CAP_PROP_GAIN,-4)
        #self.gain = self.vid.get(cv2.CAP_PROP_GAIN)
        #print(self.gain)
        #def set_gain(self):
        #self.vid.set(cv2.CAP_PROP_GAIN,-6)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)



    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
# Create a window and pass it to the Application object
App(tkinter.Tk(), "Tkinter and OpenCV")