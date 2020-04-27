import PySpin
import tkinter as tk


class CameraApp(tk.Frame):

    def __init__(self,root,serialnumber):
        tk.Frame.__init__(self,root)
        self.pack()

        self.root = root
        self.system = PySpin.System.GetInstance()
        self.camera = ""
        self.serialnumber = serialnumber
        self.status = "disconnected"

        self.connect = tk.Button(self, text="Connect to camera", command=self.connectcamera)
        self.connect.pack(side=tk.TOP, ipadx=5, ipady=5, padx=5, pady=5)

        self.message = tk.Label(self, text="")
        self.message.pack(side=tk.BOTTOM, padx=5)


    def connectcamera(self):
        self.cameralist = self.system.GetCameras()

        if self.cameralist.GetSize() == 0:
            self.message.configure(text="No cameras connected. Connect a camera and try again")
            self.cameralist.Clear()

        else:
            self.cameraident()
            self.cameralist.Clear()
            
            if self.camera == "":
                self.message.configure(text="Camera not found. Connect the camera and try again")
            else:
                self.guiinit()

        self.status = "connected"

    def cameraident(self):
        for cam in self.cameralist:

            tldevice_nodemap = cam.GetTLDeviceNodeMap()
            node_serialno = PySpin.CStringPtr(tldevice_nodemap.GetNode("DeviceSerialNumber"))
            if PySpin.IsAvailable(node_serialno) and PySpin.IsReadable(node_serialno):
                serialno = node_serialno.ToString()
            else:
                serialno = "0"

            if serialno == self.serialnumber:
                self.camera = cam
                self.camera.Init()
                self.message.configure(text="Connected to camera")
                self.nodemap = self.camera.GetNodeMap()
                break
    
        del cam


    def guiinit(self):
        self.connect.configure(text="Disconnect camera", command=self.disconnect)
        
        self.display = tk.Frame(self)
        self.display.pack(expand=1, fill=tk.BOTH,ipadx=5,ipady=5)


        #Rest of camera gui goes here


    def disconnect(self):
        self.camera.DeInit()
        self.camera =""

        self.message.configure(text="")

        self.connect.configure(text="Connect to camera", command=self.connectcamera)

        self.status = "disconnected"


    def quitthesystem(self):
        if self.status == "connected":
            self.camera.DeInit()
            self.camera=""
        
        self.system.ReleaseInstance()

    
