import PySpin
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import numpy
import matplotlib 
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ast
import time


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

        self.saveparameters = tk.Button(self.leftframe, text="Save parameter file", command=self.saveparameterfile)
        self.saveparameters.pack(side=tk.LEFT, pady=(50,0))

        self.loadparameters = tk.Button(self.leftframe, text="Load parameters", command=self.loadparameterfile)
        self.loadparameters.pack(side=tk.LEFT, pady=(50,0))

        self.figure = matplotlib.figure.Figure(figsize=[7.0,6.0])
        self.grid = self.figure.add_gridspec(ncols=1, nrows=2, height_ratios=[5,1])
        self.imagedisplay = self.figure.add_subplot(self.grid[0,0])
        self.histogram = self.figure.add_subplot(self.grid[1,0])

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.rightframe)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, expand=1, fill=tk.BOTH, pady=(10,5))

        self.signalwarnings = tk.Label(self.rightframe, text="", font=("Helvetica,12"), background="white")
        self.signalwarnings.pack(side=tk.TOP, expand=1, fill=tk.X, pady=(0,10))
        
        self.startlive = tk.Button(self.rightframe, text="Display live", command=self.start_singleframelive)
        self.startlive.pack(side=tk.LEFT, ipadx=5, ipady=5, pady=(0,10))

        self.summedlive = tk.Button(self.rightframe, text="Display multiframe live", command=self.start_multiframelive)
        self.summedlive.pack(side=tk.LEFT, ipadx=5, ipady=5, pady=(0,10))

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



    def setup_acquisition(self):

        node_bufferhandling = PySpin.CEnumerationPtr(self.streamnodemap.GetNode('StreamBufferHandlingMode'))
        node_bufferhandling.SetIntValue(node_bufferhandling.GetEntryByName("NewestOnly").GetValue())

        self.node_acquisitionmode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
           

       
    def start_liveacquisition(self):
        self.setup_acquisition()
        self.node_acquisitionmode.SetIntValue(0)

        self.savearray.configure(state=tk.DISABLED)
        self.saveimage.configure(state=tk.DISABLED)
        self.signalwarnings.configure(text="")

        self.running = True
        self.camera.BeginAcquisition()



    def start_singleframelive(self):
    
        self.start_liveacquisition()
        self.startlive.configure(text="Stop", command=self.stop_liveacquisition)
        self.singleframe.configure(state=tk.DISABLED)
        self.multiframe.configure(state=tk.DISABLED)
        self.summedlive.configure(state=tk.DISABLED)
        
        self.imageloop()



    def start_multiframelive(self):

        self.start_liveacquisition()
        self.summedlive.configure(text="Stop", command=self.stop_liveacquisition)
        self.singleframe.configure(state=tk.DISABLED)
        self.multiframe.configure(state=tk.DISABLED)
        self.startlive.configure(state=tk.DISABLED)

        self.multiframeloop()



    def imageloop(self):
        
        try:
            image_result = self.camera.GetNextImage()
            self.image_data = image_result.GetNDArray()

        except PySpin.SpinnakerException as ex:
            
            try:
                self.camera.EndAcquisition()
            except PySpin.SpinnakerException:
                pass
            self.startlive.configure(text="Display live", command=self.start_liveacquisition)
            messagebox.showerror("Error", "{}".format(ex))

        self.displayimage()

        image_result.Release()

        if self.running == True:
            self.after(1, self.imageloop)
        else:
            self.camera.EndAcquisition()
            self.signalwarnings.configure(text="")
            self.startlive.configure(text="Display live", command=self.start_singleframelive)
            self.singleframe.configure(state=tk.NORMAL)
            self.multiframe.configure(state=tk.NORMAL)
            self.summedlive.configure(state=tk.NORMAL)



    def multiframeloop(self):

        try:
            self.getmultiframeimage()
        except ValueError:
            messagebox.showerror("Error", "Choose a number of frames")
            self.camera.EndAcquisition()
            self.summedlive.configure(text="Display multiframe live", command=self.start_multiframelive)
            self.startlive.configure(state=tk.NORMAL)
            self.multiframe.configure(state=tk.NORMAL)
            self.singleframe.configure(state=tk.NORMAL)
            return
 
        self.displayimage()

        if self.running == True:
            self.after(1, self.multiframeloop)
        else:
            self.camera.EndAcquisition()
            self.signalwarnings.configure(text="")
            self.summedlive.configure(text="Display multiframe live", command=self.start_multiframelive)
            self.startlive.configure(state=tk.NORMAL)
            self.multiframe.configure(state=tk.NORMAL)
            self.singleframe.configure(state=tk.NORMAL)



    def stop_liveacquisition(self):
        self.running = False



    def capturesingleframe(self):
       
        self.setup_acquisition()
        self.node_acquisitionmode.SetIntValue(1)


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

        self.displayimage()
        
        self.savearray.configure(state=tk.NORMAL)
        self.saveimage.configure(state=tk.NORMAL, command=self.save_asimage)
               
        
        try:
            image_result.Release()
        except PySpin.SpinnakerException:
            pass



    def capturemultiframe(self):

        self.setup_acquisition()
        self.node_acquisitionmode.SetIntValue(2)
        node_framecount = PySpin.CIntegerPtr(self.nodemap.GetNode("AcquisitionFrameCount"))
        node_framecount.SetValue(int(self.sumimages.get()))
 
        self.sumimages.configure(state=tk.DISABLED)
        
        self.camera.BeginAcquisition()
        self.getmultiframeimage()
        self.camera.EndAcquisition()
        
        self.displayimage()

        self.savearray.configure(state=tk.NORMAL)
        self.saveimage.configure(state=tk.NORMAL, command=self.save_assumimage)
       
        self.sumimages.configure(state=tk.NORMAL)



    def getmultiframeimage(self):

        self.image_data = numpy.zeros((964,1288), int)

        for i in range(int(self.sumimages.get())):

            try:
                image_result = self.camera.GetNextImage()
                frame_data = image_result.GetNDArray()
                self.image_data += frame_data
        
            except PySpin.SpinnakerException as ex:
            
                try:
                    self.camera.EndAcquisition()
                except PySpin.SpinnakerException:
                    pass
                tk.messagebox.showerror("Error", "Stopped after {} images: {}".format(i,ex))
                return

        image_result.Release()



    def displayimage(self):
        
        histo, bin_steps = numpy.histogram(self.image_data, bins=[0,32,64,96,128,160,192,224,255], range=(0,256))
        x = [16,48,80,112,144,176,208,240]
        self.imagedisplay.clear()
        self.imagedisplay.imshow(self.image_data, cmap="gray", vmin=0, vmax=255)
        self.histogram.clear()
        self.histogram.bar(x,histo, width=14, align='center', log=True, tick_label=["0-31","32-63","64-95","96-127","128-159","160-191","192-223","224-255"])
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
        


    def save_asimage(self):
        
        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save image as:", filetypes=(("PNG files", "*.png"),("All files","*.*")))
        self.convertedimage.Save(filename)



    def save_asarray(self):
        
        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save array as:", filetypes=(("Binary numpy array file", "*.npy"),("All files","*.*")))
        numpy.save(filename, self.image_data)



    def save_assumimage(self):

        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save image as:", filetypes=(("PNG files", "*.png"),("All files","*.*")))
        matplotlib.image.imsave(filename, self.image_data, vmin=0, vmax=255, cmap="gray")



    def saveparameterfile(self):

        exposure = self.node_exposuretime.GetValue()
        gain = self.node_gain.GetValue()

        parameters = {"Exposure time": exposure, "Gain": gain}
        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save parameters:", filetypes=(("Text files", "*.txt"),("All files", "*.*")))
        f = open(filename, "w")
        f.write(str(parameters))
        f.close()



    def loadparameterfile(self):

        filename = filedialog.askopenfilename(initialdir="C:/", title="Open parameter file:", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        f = open(filename, "r")
        parameters = ast.literal_eval(f.read())
        f.close()

        exposuretime = parameters["Exposure time"]
        gain = parameters["Gain"]
        self.node_exposuretime.SetValue(exposuretime)
        self.exposureslider.set(self.node_exposuretime.GetValue())
        self.exposurelabel.configure(text="Exposure time [us]: {}".format(round(self.node_exposuretime.GetValue(),2)))
        self.node_gain.SetValue(gain)
        self.gainslider.set(self.node_gain.GetValue())
        self.gainlabel.configure(text="Gain: {}".format(round(self.node_gain.GetValue(),2)))



    def quit_cameraapp(self):

        self.camera = ""

        
    




