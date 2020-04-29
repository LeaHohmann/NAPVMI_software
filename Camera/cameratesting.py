import PySpin
import tkinter as tk
import numpy
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Livegui(tk.Tk):

    def __init__(self):
        self.system = PySpin.System.GetInstance()
        self.cameralist = self.system.GetCameras()
        self.camera = ""
       
        tk.Tk.__init__(self)

        self.protocol("WM_DELETE_WINDOW", self.quit_window)

        self.camerainit()


    def camerainit(self):
        if self.cameralist.GetSize() == 0:
            print("No cameras connected")
        
        for cam in self.cameralist:

            tldevice_nodemap = cam.GetTLDeviceNodeMap()
            node_serialno = PySpin.CStringPtr(tldevice_nodemap.GetNode("DeviceSerialNumber"))
            if PySpin.IsAvailable(node_serialno) and PySpin.IsReadable(node_serialno):
                serialnumber = node_serialno.ToString()
            else:
                serialnumber = "0"

            if serialnumber == "18479311":
                self.camera = cam
                self.camera.Init()
                self.nodemap = self.camera.GetNodeMap()
                self.streamnodemap = self.camera.GetTLStreamNodeMap()

        del cam
        self.cameralist.Clear()

        if self.camera == "":
            print("Couldn't connect to camera")

        else:
            self.setup_acquisition()
            self.guiinit()


    def guiinit(self):
        self.imageplot = matplotlib.figure.Figure()
        self.img = self.imageplot.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.imageplot, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, expand=1, fill=tk.BOTH)

        self.startstop = tk.Button(self, text="Start", command=self.startacquisition)
        self.startstop.pack(side=tk.TOP, ipadx=5, ipady=5, pady=10)



    def quit_window(self):
        if self.startstop["text"] == "Stop":
            self.running = False
            self.camera.EndAcquisition()
            
        self.camera.DeInit()
        del self.camera
        self.system.ReleaseInstance()
        self.quit()


    def setup_acquisition(self):

        node_bufferhandlingmode = PySpin.CEnumerationPtr(self.streamnodemap.GetNode('StreamBufferHandlingMode'))
        node_bhmode_newestonly = node_bufferhandlingmode.GetEntryByName('NewestOnly')
        node_bufferhandlingmode.SetIntValue(node_bhmode_newestonly.GetValue())
    
        node_acquisitionmode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
        node_acmode_continuous = node_acquisitionmode.GetEntryByName('Continuous')
        node_acquisitionmode.SetIntValue(node_acmode_continuous.GetValue())
   

    def startacquisition(self):
       self.startstop.configure(text="Stop", command=self.stopacquisition)
       
       self.running = True
       self.camera.BeginAcquisition()
       
       self.imageloop() 
           

    def imageloop(self):

        try:
            image_result = self.camera.GetNextImage()
            image_data = image_result.GetNDArray()
        
        except PySpin.SpinnakerException as ex:
            print("Error: {}".format(ex))
            return
            
        self.img.clear()
        self.img.imshow(image_data, cmap="gray")
        self.canvas.draw()
        image_result.Release()

        if self.running == True:
            self.after(1, self.imageloop)
        else:
            self.camera.EndAcquisition()
       
  
    def stopacquisition(self):
       
        self.startstop.configure(text="Start", command=self.startacquisition)

        self.running = False



root = Livegui()
root.mainloop()
    
