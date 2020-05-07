import PySpin
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
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
        self.canvas.get_tk_widget().pack(side=tk.TOP, expand=1, fill=tk.BOTH, pady=(10,5))

        self.signalwarnings = tk.Label(self.rightframe, text="", font=("Helvetica,12"), background="white")
        self.signalwarnings.pack(side=tk.TOP, expand=1, fill=tk.X, pady=(0,10))
        
        self.startlive = tk.Button(self.rightframe, text="Display live", command=self.start_liveacquisition)
        self.startlive.pack(side=tk.LEFT, ipadx=5, ipady=5, pady=(0,10))

        self.singleframe = tk.Button(self.rightframe, text="Single frame", command=self.capturesingleframe)
        self.singleframe.pack(side=tk.LEFT, ipadx=5, ipady=5, pady=(0,10))

        self.multiframe = tk.Button(self.rightframe, text="Summed multiframe image", command=self.capturemultiframe)
        self.multiframe.pack(side=tk.LEFT, ipadx=5, ipady=5, pady=(0,10))

        self.savearray = tk.Button(self.rightframe, text="Save as array", command=self.save_asarray, state=tk.DISABLED)
        self.savearray.pack(side=tk.RIGHT, ipadx=5,ipady=5, pady=(0,10))

        self.saveimage = tk.Button(self.rightframe, text="Save image", command=self.save_asimage, state=tk.DISABLED)
        self.saveimage.pack(side=tk.RIGHT,ipadx=5, ipady=5, pady=(0,10))

    
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

        node_bufferhandling = PySpin.CEnumerationPtr(self.streamnodemap.GetNode("StreamBufferHandlingMode"))
        node_bufferhandling.SetIntValue(node_bufferhandling.GetEntryByName("NewestOnly").GetValue())

        node_acquisitionmode = PySpin.CEnumerationPtr(self.nodemap.GetNode("AcquisitionMode"))
        node_acquisitionmode.SetIntValue(1)


    
    def setup_multiframe(self):

        node_bufferhandling = PySpin.CEnumerationPtr(self.streamnodemap.GetNode("StreamBufferHandlingMode"))
        node_bufferhandling.SetIntValue(node_bufferhandling.GetEntryByName("NewestOnly").GetValue())

        node_acquisitionmode = PySpin.CEnumerationPtr(self.nodemap.GetNode("AcquisitionMode"))
        node_acquisitionmode.SetIntValue(2)
        node_framecount = PySpin.CIntegerPtr(self.nodemap.GetNode("AcquisitionFrameCount"))
        node_framecount.SetValue(int(self.sumimages.get()))
 


    def start_liveacquisition(self):
        self.setup_live()

        self.startlive.configure(text="Stop", command=self.stop_liveacquisition)
        self.savearray.configure(state=tk.DISABLED)
        self.saveimage.configure(state=tk.DISABLED)
        self.signalwarnings.configure(text="")

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
            messagebox.showerror("Error", "{}".format(ex))

        histo, bin_steps = numpy.histogram(image_data, bins=[0,32,64,96,128,160,192,224,255], range=(0,256))
        x = [16,48,80,112,144,176,208,240]
        self.imagedisplay.clear()
        self.imagedisplay.imshow(image_data, cmap="gray", vmin=0, vmax=255)
        self.histogram.clear()
        self.histogram.bar(x,histo, width=10, align='center', log=True, tick_label=[0,32,64,96,128,160,192,224])
        self.canvas.draw()
        if numpy.sum(histo[1:]) == 0:
            self.signalwarnings.configure(text="No / low signal", anchor=tk.W, foreground="dark red")
        elif numpy.sum(histo[3:]) < 10:
            self.signalwarnings.configure(text="Low signal", anchor=tk.W, foreground="dark orange")
        elif histo[7] >= 10:
            self.signalwarnings.configure(text="Strong Oversaturation", anchor=tk.E, foreground="dark red")
        elif numpy.sum(histo[6:]) >= 20:
            self.signalwarnings.configure(text="Oversaturation", anchor=tk.E, foreground="dark orange")
        else:
            self.signalwarnings.configure(text="")
        

        image_result.Release()

        if self.running == True:
            self.after(30, self.imageloop)
        else:
            self.camera.EndAcquisition()
            self.signalwarnings.configure(text="")


    def stop_liveacquisition(self):
        self.running = False

        self.startlive.configure(text="Display live", command=self.start_liveacquisition)


    def capturesingleframe(self):
        
        self.setup_singleframe()

        self.camera.BeginAcquisition()
        
        try:
            image_result = self.camera.GetNextImage()
            self.image_data = image_result.GetNDArray()
            self.convertedimage = image_result.Convert(PySpin.PixelFormat_Mono8)
        
        except PySpin.SpinnakerException as ex:
            
            try:
                self.camera.EndAcquisition()
            except PySpin.SpinnakerException:
                pass
            tk.messagebox.showerror("Error", "{}".format(ex))
            return

        self.camera.EndAcquisition()
        
        histo, bin_steps = numpy.histogram(self.image_data, bins=[0,32,64,96,128,160,192,224,255], range=(0,256))
        x = [16,48,80,112,144,176,208,240]
        self.imagedisplay.clear()
        self.imagedisplay.imshow(self.image_data, cmap="gray", vmin=0, vmax=255)
        self.histogram.clear()
        self.histogram.bar(x,histo, width=10, align='center', log=True, tick_label=[0,32,64,96,128,160,192,224])
        self.canvas.draw()
        self.savearray.configure(state=tk.NORMAL)
        self.saveimage.configure(state=tk.NORMAL, command=self.save_asimage)
        if numpy.sum(histo[1:]) == 0:
            self.signalwarnings.configure(text="No / low signal", anchor=tk.W, foreground="dark red")
        elif numpy.sum(histo[3:]) < 10:
            self.signalwarnings.configure(text="Low signal", anchor=tk.W, foreground="dark orange")
        elif histo[7] >= 10:
            self.signalwarnings.configure(text="Strong Oversaturation", anchor=tk.E, foreground="dark red")
        elif numpy.sum(histo[6:]) >= 20:
            self.signalwarnings.configure(text="Oversaturation", anchor=tk.E, foreground="dark orange")
        else:
            self.signalwarnings.configure(text="")
                
        
        try:
            image_result.Release()
        except PySpin.SpinnakerException:
            pass



    def capturemultiframe(self):

        self.setup_multiframe()
        self.sumimages.configure(state=tk.DISABLED)
        
        self.camera.BeginAcquisition()
        sum_image = numpy.zeros((964,1288))

        for i in range(int(self.sumimages.get())):

            try:
                image_result = self.camera.GetNextImage()
                image_data = image_result.GetNDArray()
                sum_image += image_data
        
            except PySpin.SpinnakerException as ex:
            
                try:
                    self.camera.EndAcquisition()
                except PySpin.SpinnakerException:
                    pass
                tk.messagebox.showerror("Error", "Stopped after {} images: {}".format(i,ex))
                return

            image_result.Release()

        self.camera.EndAcquisition()
        self.image_data = sum_image.astype(int)
        
        histo, bin_steps = numpy.histogram(self.image_data, bins=[0,32,64,96,128,160,192,224,255], range=(0,256))
        x = [16,48,80,112,144,176,208,240]
        self.imagedisplay.clear()
        self.imagedisplay.imshow(self.image_data, vmin=0, vmax=255, cmap="gray")
        self.histogram.clear()
        self.histogram.bar(x,histo, width=10, align='center', log=True, tick_label=[0,32,64,96,128,160,192,224])
        self.canvas.draw()
        self.savearray.configure(state=tk.NORMAL)
        self.saveimage.configure(state=tk.NORMAL, command=self.save_assumimage)
        if numpy.sum(histo[1:]) == 0:
            self.signalwarnings.configure(text="No / low signal", anchor=tk.W, foreground="dark red")
        elif numpy.sum(histo[3:]) < 10:
            self.signalwarnings.configure(text="Low signal", anchor=tk.W, foreground="dark orange")
        elif histo[7] >= 10:
            self.signalwarnings.configure(text="Strong Oversaturation", anchor=tk.E, foreground="dark red")
        elif numpy.sum(histo[6:]) >= 20:
            self.signalwarnings.configure(text="Oversaturation", anchor=tk.E, foreground="dark orange")
        else:
            self.signalwarnings.configure(text="")
        
        self.sumimages.configure(state=tk.NORMAL)



    def save_asimage(self):
        
        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save image as:", filetypes=(("PNG files", "*.png"),("All files","*.*")))
        self.convertedimage.Save(filename)


    def save_asarray(self):
        
        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save array as:", filetypes=(("Binary numpy array file", "*.npy"),("All files","*.*")))
        numpy.save(filename, self.image_data)


    def save_assumimage(self):

        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save image as:", filetypes=(("PNG files", "*.png"),("All files","*.*")))
        matplotlib.image.imsave(filename, self.image_data, vmin=0, vmax=255, cmap="gray")


    def quit_cameraapp(self):
        
        if self.startlive['text'] == "Stop":
            self.running = False

        self.camera = ""

        
    




