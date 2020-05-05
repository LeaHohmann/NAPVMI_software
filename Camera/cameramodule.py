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

        self.camerasetup()
        self.guiinit()


    def guiinit(self):
        
        self.leftframe = tk.Frame(self)
        self.leftframe.pack(side=tk.LEFT, fill=tk.Y, padx=40)

        self.rightframe = tk.Frame(self)
        self.rightframe.pack(side=tk.LEFT, padx=10)

        self.settingslabel = tk.Label(self.leftframe, text="Camera settings", anchor=tk.NW, font=("Helvetica", 18))
        self.settingslabel.pack(side=tk.TOP, pady=(10,30))

        self.exposurelabel = tk.Label(self.leftframe, text="Exposure time [us] : {}".format(round(self.node_exposuretime.GetValue(),2)), anchor=tk.NW, font=("Helvetica",12))
        self.exposurelabel.pack(side=tk.TOP, pady=5)

        self.exposureslider = tk.Scale(self.leftframe, from_=40.00, to=32000.00, resolution=30.00, orient=tk.HORIZONTAL, length=200, command=self.exposuretime)
        self.exposureslider.set(self.node_exposuretime.GetValue())
        self.exposureslider.pack(side=tk.TOP, pady=(0,30))

        self.gainlabel = tk.Label(self.leftframe, text="Gain: {}".format(round(self.node_gain.GetValue(),2)), anchor=tk.NW, font=("Helvetica",12))
        self.gainlabel.pack(side=tk.TOP, pady=5)

        self.gainslider = tk.Scale(self.leftframe, from_=-10.75, to=23.05, resolution=0.26, orient=tk.HORIZONTAL, length=200, command=self.gain)
        self.gainslider.set(self.node_gain.GetValue())
        self.gainslider.pack(side=tk.TOP, pady=(0,30))

        self.sumimageslabel = tk.Label(self.leftframe, text="Number of images to sum:", anchor=tk.NW, font=("Helvetica,12"))
        self.sumimageslabel.pack(side=tk.TOP, pady=5)

        self.sumimages = tk.Entry(self.leftframe)
        self.sumimages.pack(side=tk.TOP, pady=(0,30))

        self.figure = matplotlib.figure.Figure(figsize=[7.0,6.0])
        self.grid = self.figure.add_gridspec(ncols=1, nrows=2, height_ratios=[5,1])
        self.imagedisplay = self.figure.add_subplot(self.grid[0,0])
        self.histogram = self.figure.add_subplot(self.grid[1,0])

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.rightframe)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, expand=1, fill=tk.BOTH, pady=10)
        
        self.startlive = tk.Button(self.rightframe, text="Display live", command=self.start_liveacquisition)
        self.startlive.pack(side=tk.LEFT, ipadx=5, ipady=5, pady=20)

        self.singleframe = tk.Button(self.rightframe, text="Single frame", command=self.capturesingleframe)
        self.singleframe.pack(side=tk.LEFT, ipadx=5, ipady=5, pady=20)

    
    def camerasetup(self):
        
        node_autoexposure = PySpin.CEnumerationPtr(self.nodemap.GetNode("ExposureAuto"))
        node_autoexposure.SetIntValue(0)
        
        node_autogain = PySpin.CEnumerationPtr(self.nodemap.GetNode("GainAuto"))
        node_autogain.SetIntValue(0)

        node_autoexpocomp = PySpin.CEnumerationPtr(self.nodemap.GetNode("pgrExposureCompensationAuto"))
        node_autoexpocomp.SetIntValue(0)

        self.node_exposuretime = PySpin.CFloatPtr(self.nodemap.GetNode("ExposureTime"))
        self.node_gain = PySpin.CFloatPtr(self.nodemap.GetNode("Gain"))


    def exposuretime(self,value):

        self.node_exposuretime.SetValue(float(value))
        self.exposurelabel.configure(text="Exposure time [us] : {}".format(round(self.node_exposuretime.GetValue(),2)))

    
    def gain(self,value):

        self.node_gain.SetValue(float(value))
        self.gainlabel.configure(text="Gain: {}".format(round(self.node_gain.GetValue(),2)))



    def setup_live(self):

        node_bufferhandling = PySpin.CEnumerationPtr(self.streamnodemap.GetNode('StreamBufferHandlingMode'))
        node_bufferhandling.SetIntValue(node_bufferhandling.GetEntryByName("NewestOnly").GetValue())

        node_acquisitionmode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
        node_acquisitionmode.SetIntValue(0)



    def setup_singleframe(self):

        node_bufferhandling = PySpin.CEnumerationPtr(self.streamnodemap.GetNode('StreamBufferHandlingMode'))
        node_bufferhandling.SetIntValue(node_bufferhandling.GetEntryByName("NewestOnly").GetValue())

        node_acquisitionmode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
        node_acquisitionmode.SetIntValue(1)
 


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
            channel_stats = image_result.CalculateChannelStatistics(0)
            image_histogram = channel_stats.histogram

        except PySpin.SpinnakerException as ex:
            
            try:
                self.camera.EndAcquisition()
            except PySpin.SpinnakerException:
                pass
            self.startlive.configure(text="Display live", command=self.start_liveacquisition)
            tk.messagebox.showerror("Error", "{}".format(ex))

        self.imagedisplay.clear()
        self.imagedisplay.imshow(image_data, cmap="gray")
        self.histogram.clear()
        self.histogram.plot(image_histogram)
        self.canvas.draw()
        image_result.Release()

        if self.running == True:
            self.after(30, self.imageloop)
        else:
            self.camera.EndAcquisition()


    def stop_liveacquisition(self):
        self.running = False

        self.startlive.configure(text="Display live", command=self.start_liveacquisition)


    def capturesingleframe(self):
        
        self.setup_singleframe()
        
        self.camera.BeginAcquisition()
        
        try:
            image_result = self.camera.GetNextImage()
            image_data = image_result.GetNDArray()
            channel_stats = image_result.CalculateChannelStatistics(0)
            image_histogram = channel_stats.histogram
        
        except PySpin.SpinnakerException as ex:
            
            try:
                self.camera.EndAcquisition()
            except PySpin.SpinnakerException:
                pass
            tk.messagebox.showerror("Error", "{}".format(ex))

        self.camera.EndAcquisition()

        self.imagedisplay.clear()
        self.imagedisplay.imshow(image_data, cmap="gray")
        self.histogram.clear()
        self.histogram.plot(image_histogram)
        self.canvas.draw()
        
        try:
            image_result.Release()
        except PySpin.SpinnakerException:
            pass



    def quit_cameraapp(self):
        
        if self.startlive['text'] == "Stop":
            self.running = False

        self.camera = ""

        
    




