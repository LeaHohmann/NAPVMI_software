import PySpin
import tkinter as tk


class CameraApp(tk.Frame):

    def __init__(self,root,serialnumber):
        tk.Frame.__init__(self,root)
        self.pack()

        self.root = root
        self.camera = ""
        self.serialnumber = serialnumber

        self.connect = tk.Button(self, Text="Connect to camera", command=self.connectcamera)
        self.connect.pack(side=tk.TOP, ipadx=5, ipady=5, padx=5, pady=5)

        self.message = tk.Label(self, Text="")
        self.message.pack(side=tk.BOTTOM, padx=5)


    def connectcamera(self):
        self.system = PySpin.System.GetInstance()
        self.cameralist = system.GetCameras()

        if self.cameralist.GetSize() == 0:
            self.message.configure(Text="No cameras connected. Connect a camera and try again")
            self.cameralist.Clear()
            self.system.ReleaseInstance()

        else:
            self.cameraident()
            self.cameralist.Clear()
            
            if self.camera == "":
                self.message.configure(Text="Camera not found. Connect the camera and try again")
                self.system.ReleaseInstance()
            else:
                self.guiinit()

    def cameraident(self):
        for cam in self.cameralist:

            device_nodemap = cam.GetTLDeviceNodeMap()
            node_serialno = PySpin.CStringPtr(device_nodemap.GetNode("DeviceSerialNumber"))
            if PySpin.IsAvailabla(node_serialno) and PySpin.IsReadable(node_serialno):
                serialno = node_serialno.ToString()
            else:
                serialno = "0"

            if serialno == self.serialnumber:
                self.camera = cam
                self.message.configure(Text="Connected to camera")
                self.nodemap = device_nodemap
                break
    
        del cam


    def guiinit(self):
        self.connect.configure(Text="Disconnect camera", command=self.disconnect)

        #Rest of camera gui goes here


    def disconnect(self):
        self.camera =""
        self.system.ReleaseInstance()

        self.connect.configure(Text="Connect to camera", command=self.connectcamera)

        #Destroy rest of the GUI

    
