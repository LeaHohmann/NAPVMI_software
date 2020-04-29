#This program fulfills the role and functionalities of the main module in the full GUI later on

import tkinter as tk
import cameramodule
import PySpin


class Root(tk.Tk):

    def __init__(self):
        #Init: Fetches system instance and sets up the connect button as well as the function that is called when window is closed

        self.system = PySpin.System.GetInstance()
        self.camera = ""
        self.serialnumber = "18479311"
        self.camerastatus = "disconnected"

        tk.Tk.__init__(self)

        self.protocol("WM_DELETE_WINDOW", self.quitgui)

        self.connect = tk.Button(self, text="Connect to Camera", command=self.connectcamera)
        self.connect.pack(side=tk.TOP, ipadx=5, ipady=5, pady=10)


    def connectcamera(self):
        #Called on pressing connect. Fetches cameralist, calls on cameraident to see if our camera is there. If yes, initializes the camera GUI (from cameramodule)
        
        self.cameralist = self.system.GetCameras()
        
        if self.cameralist.GetSize() == 0:
            tk.messagebox.showerror("Error", "No cameras connected. Connect camera and try again")
            self.cameralist.Clear()
            return
        else:
            self.cameraident()
            self.cameralist.Clear()

        if self.camera == "":
            tk.messagebox.showerror("Error", "Camera not found.")
        else:
            self.connect.destroy()
            self.camerainit()
            self.camerastatus = "connected"
    
    
    
    def cameraident(self):
        #Called by connectcamera. Cycles through all detected cameras and checks the serial number. If it finds our camera it sets it up as the class camera variable
        
        for cam in self.cameralist:
            tldevice_nodemap = cam.GetTLDeviceNodeMap()
            node_serialno = PySpin.CStringPtr(tldevice_nodemap.GetNode("DeviceSerialNumber"))
            serialno = node_serialno.ToString()
            del tldevice_nodemap

            if serialno == self.serialnumber:
                self.camera = cam
                self.camera.Init()
                break

        del cam


    def camerainit(self):
        #Calls a class instance of the cameramodule camera GUI
        self.cameragui = cameramodule.CameraApp(self,self.system,self.camera)

    
    def quitgui(self):
        #Function called upon closing window to ensure proper disconnection of camera

        if self.camerastatus == "connected":
            self.cameragui.quit_cameraapp()
            self.camera.DeInit()
            
        self.camera = ""
        self.system.ReleaseInstance()
        self.destroy()


root = Root()
root.mainloop()


