import PySpin
import tkinter as tk
import numpy
import matplotlib 
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CameraApp(tk.Frame):

    def __init__(self,root,system,camera):
        tk.Frame.__init__(self,root)
        self.pack()

        self.root = root
        self.system = system
        self.camera = camera
        self.nodemap = self.camera.GetNodeMap()
        self.streamnodemap = self.camera.GetTLStreamNodeMap()

        self.guiinit()


    def guiinit(self):
        
        self.leftframe = tk.Frame(self)
        self.leftframe.pack(side=tk.LEFT, padx=10)

        self.rightframe = tk.Frame(self)
        self.rightframe.pack(side=tk.LEFT, padx=10)

        self.settingslabel = tk.Label(self.leftframe, text="Camera settings:")
        self.settingslabel.pack(side=tk.TOP, pady=10)

        self.figure = matplotlib.figure.Figure()
        self.imagedisplay = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.rightframe)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, expand=1, fill=tk.BOTH)
        
        self.startlive = tk.Button(self.rightframe, text="Display live", command=self.start_liveacquisition)
        self.startlive.pack(side=tk.LEFT, ipadx=5, ipady=5, pady=20)


    def setup_live(self):

        node_bufferhandling = PySpin.CEnumerationPtr(self.streamnodemap.GetNode('StreamBufferHandlingMode'))
        node_newestonly = node_bufferhandling.GetEntryByName('NewestOnly')
        node_bufferhandling.SetIntValue(node_newestonly.GetValue())

        node_acquisitionmode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
        node_continuous = node_acquisitionmode.GetEntryByName('Continuous')
        node_acquisitionmode.SetIntValue(node_continuous.GetValue())


    def start_liveacquisition(self):
        self.setup_live()

        self.startlive.configure(text="Stop", command=self.stop_liveacquisition)

        self.running = True
        self.camera.BeginAcquisition()
        
        self.imageloop()


    def imageloop(self):
        
        try:
            image_result = self.camera.GetNextImage()
            image_data = image_result.GetNDArray()

        except PySpin.SpinnakerException as ex:
            
            try:
                self.camera.EndAcquisition()
            except PySpin.SpinnakerException:
                pass
            self.startlive.configure(text="Display live", command=self.start_liveacquisition)
            tk.messagebox.showerror("Error", "{}".format(ex))

        self.imagedisplay.clear()
        self.imagedisplay.imshow(image_data, cmap="gray")
        self.canvas.draw()
        image_result.Release()

        if self.running == True:
            self.after(1, self.imageloop)
        else:
            self.camera.EndAcquisition()


    def stop_liveacquisition(self):
        self.running = False

        self.startlive.configure(text="Display live", command=self.start_liveacquisition)


    def quit_cameraapp(self):
        
        if self.startlive['text'] == "Stop":
            self.running = False

        self.camera = ""

        
    




