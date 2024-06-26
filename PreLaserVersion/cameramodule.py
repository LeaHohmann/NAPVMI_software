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

        self.triggerbutton = tk.Button(self.leftframe, text="Triggered acquisition: OFF", background="red", command=self.settrigger)
        self.triggerbutton.pack(side=tk.TOP, pady=(5,30))

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

        self.sumimageslabel = tk.Message(self.leftframe, text="Number of frames to sum (single image acquisition, multiframe live):", anchor=tk.NW, font=("Helvetica,12"), width=250)
        self.sumimageslabel.pack(side=tk.TOP, pady=5)

        self.numberofframes = tk.IntVar(self.leftframe, value=1)
        self.sumimages = tk.Entry(self.leftframe, textvariable=self.numberofframes)
        self.sumimages.pack(side=tk.TOP, pady=(0,30))

        self.xpixelframe = tk.Frame(self.leftframe)
        self.xpixelframe.pack(side=tk.TOP, pady=(0,20))

        self.xpixellabel = tk.Label(self.xpixelframe, text="X-range (whole frame: 0-1287):")
        self.xpixellabel.pack(side=tk.LEFT)

        self.xpixellower = tk.IntVar(self.xpixelframe, value=0)
        self.xpixelstart = tk.Entry(self.xpixelframe, textvariable=self.xpixellower, width=10)
        self.xpixelstart.pack(side=tk.LEFT)

        self.xpixelupper = tk.IntVar(self.xpixelframe, value=1287)
        self.xpixelend = tk.Entry(self.xpixelframe, textvariable=self.xpixelupper, width=10)
        self.xpixelend.pack(side=tk.LEFT)

        self.ypixelframe = tk.Frame(self.leftframe)
        self.ypixelframe.pack(side=tk.TOP, pady=(0,30))

        self.ypixellabel = tk.Label(self.ypixelframe, text="Y-range (whole frame: 0-963):")
        self.ypixellabel.pack(side=tk.LEFT)

        self.ypixellower = tk.IntVar(self.ypixelframe, value=0)
        self.ypixelstart = tk.Entry(self.ypixelframe, textvariable=self.ypixellower, width=10)
        self.ypixelstart.pack(side=tk.LEFT)

        self.ypixelupper = tk.IntVar(self.ypixelframe, value=963)
        self.ypixelend = tk.Entry(self.ypixelframe, textvariable=self.ypixelupper, width=10)
        self.ypixelend.pack(side=tk.LEFT)

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
        self.canvas.get_tk_widget().pack(side=tk.TOP, expand=0, fill=tk.BOTH, pady=(10,5))

        self.signalwarnings = tk.Label(self.rightframe, text="", font=("Helvetica,11"), background="white")
        self.signalwarnings.pack(side=tk.TOP, expand=1, fill=tk.X, pady=(0,5))

        self.signallabel = tk.Label(self.rightframe, text="Total signal:", font=("Helvetica,11"), anchor=tk.E, background="White")
        self.signallabel.pack(side=tk.TOP,expand=1, fill=tk.X, pady=(0,10))
        
        self.startlive = tk.Button(self.rightframe, text="Live", command=self.start_singleframelive)
        self.startlive.pack(side=tk.LEFT, ipadx=5, ipady=5, pady=(0,10))

        self.summedlive = tk.Button(self.rightframe, text="Multiframe live", command=self.start_multiframelive)
        self.summedlive.pack(side=tk.LEFT, ipadx=5, ipady=5, pady=(0,10))

        self.multiframe = tk.Button(self.rightframe, text="Single image", command=self.acquireimage)
        self.multiframe.pack(side=tk.LEFT, ipadx=5, ipady=5, pady=(0,10))

        self.takexslice = tk.Button(self.rightframe, text="X slice", command=self.acquirexslice)
        self.takexslice.pack(side=tk.LEFT, ipadx=5, ipady=5, pady=(0,10))

        self.takeyslice = tk.Button(self.rightframe, text="Y slice", command=self.acquireyslice)
        self.takeyslice.pack(side=tk.LEFT, ipadx=5, ipady=5, pady=(0,10))

        self.saveslice = tk.Button(self.rightframe, text="Save slice", command=self.save_slice, state=tk.DISABLED)
        self.saveslice.pack(side=tk.RIGHT, ipadx=5, ipady=5, pady=(0,10))

        self.savearray = tk.Button(self.rightframe, text="Save array", command=self.save_asarray, state=tk.DISABLED)
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

        self.node_triggermode = PySpin.CEnumerationPtr(self.nodemap.GetNode("TriggerMode"))
        self.node_triggermode.SetIntValue(0)
        self.node_triggerselector = PySpin.CEnumerationPtr(self.nodemap.GetNode("TriggerSelector"))
        if not PySpin.IsReadable(self.node_triggerselector) or not PySpin.IsWritable(self.node_triggerselector):
            messagebox.showerror("Error", "Couldn't configure camera, trigger selector could not be set. Close program and try again")
            return
        self.node_triggerselector.SetIntValue(self.node_triggerselector.GetEntryByName("FrameStart").GetValue())
        self.node_triggersource = PySpin.CEnumerationPtr(self.nodemap.GetNode("TriggerSource"))
        if not PySpin.IsReadable(self.node_triggerselector) or not PySpin.IsWritable(self.node_triggerselector):
            messagebox.showerror("Error", "Couldn't configure camera, trigger selector could not be set. Close program and try again")
            return
        self.node_triggersource.SetIntValue(self.node_triggersource.GetEntryByName("Line0").GetValue())




    def exposuretime(self,value):

        self.node_exposuretime.SetValue(float(value))
        self.exposurelabel.configure(text="Exposure time [us] : {}".format(round(self.node_exposuretime.GetValue(),2)))


    
    def gain(self,value):

        self.node_gain.SetValue(float(value))
        self.gainlabel.configure(text="Gain: {}".format(round(self.node_gain.GetValue(),2)))


    
    def settrigger(self):

        self.node_triggermode.SetIntValue(1)
        
        self.triggerbutton.configure(text="Triggered acquisition: ON", background="green", command=self.stoptrigger)



    def stoptrigger(self):

        self.node_triggermode.SetIntValue(0)

        self.triggerbutton.configure(text="Triggered acquisition: OFF", background="red", command=self.settrigger)



    def setup_acquisition(self):

        node_bufferhandling = PySpin.CEnumerationPtr(self.streamnodemap.GetNode('StreamBufferHandlingMode'))
        node_bufferhandling.SetIntValue(node_bufferhandling.GetEntryByName("NewestOnly").GetValue())

        self.node_acquisitionmode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
           

       
    def start_liveacquisition(self):
        self.setup_acquisition()
        self.node_acquisitionmode.SetIntValue(0)

        self.savearray.configure(state=tk.DISABLED)
        self.saveimage.configure(state=tk.DISABLED)
        self.saveslice.configure(state=tk.DISABLED)
        self.signalwarnings.configure(text="")

        self.running = True
        self.camera.BeginAcquisition()



    def start_singleframelive(self):
    
        self.start_liveacquisition()
        self.startlive.configure(text="Stop", command=self.stop_liveacquisition)
        self.multiframe.configure(state=tk.DISABLED)
        self.summedlive.configure(state=tk.DISABLED)
        self.takexslice.configure(state=tk.DISABLED)
        self.takeyslice.configure(state=tk.DISABLED)
        
        self.imageloop()



    def start_multiframelive(self):

        self.start_liveacquisition()
        self.summedlive.configure(text="Stop", command=self.stop_liveacquisition)
        self.multiframe.configure(state=tk.DISABLED)
        self.startlive.configure(state=tk.DISABLED)
        self.takexslice.configure(state=tk.DISABLED)
        self.takeyslice.configure(state=tk.DISABLED)

        self.multiframeloop()



    def imageloop(self):
        
        try:
            image_result = self.camera.GetNextImage(5000)
            self.image_data = image_result.GetNDArray()

        except PySpin.SpinnakerException as ex:
            
            
            self.camera.EndAcquisition()
            self.startlive.configure(text="Live", command=self.start_singleframelive)
            self.multiframe.configure(state=tk.NORMAL)
            self.summedlive.configure(state=tk.NORMAL)
            self.takexslice.configure(state=tk.NORMAL)
            self.takeyslice.configure(state=tk.NORMAL)
            messagebox.showerror("Error", "{}".format(ex))
            return

        self.displayimage()
        self.integrateimage()

        image_result.Release()

        if self.running == True:
            self.after(1, self.imageloop)
        else:
            self.camera.EndAcquisition()
            self.signalwarnings.configure(text="")
            self.startlive.configure(text="Live", command=self.start_singleframelive)
            self.multiframe.configure(state=tk.NORMAL)
            self.summedlive.configure(state=tk.NORMAL)
            self.takexslice.configure(state=tk.NORMAL)
            self.takeyslice.configure(state=tk.NORMAL)



    def multiframeloop(self):

        self.captureexception = False

        try:
            self.getmultiframeimage()
        except ValueError:
            messagebox.showerror("Error", "Set number of frames as integer number")
            self.camera.EndAcquisition()
            self.summedlive.configure(text="Multiframe live", command=self.start_multiframelive)
            self.startlive.configure(state=tk.NORMAL)
            self.multiframe.configure(state=tk.NORMAL)
            self.takexslice.configure(state=tk.NORMAL)
            self.takeyslice.configure(state=tk.NORMAL)
            return
 
        if self.captureexception == False:

            self.image_data = self.sumimage
            self.displayimage()
            self.integrateimage()

        if self.running == True and self.captureexception == False:
            self.after(1, self.multiframeloop)
        else:
            try:
                self.camera.EndAcquisition()
            except PySpin.SpinnakerException:
                pass
            self.signalwarnings.configure(text="")
            self.summedlive.configure(text="Multiframe live", command=self.start_multiframelive)
            self.startlive.configure(state=tk.NORMAL)
            self.multiframe.configure(state=tk.NORMAL)
            self.takexslice.configure(state=tk.NORMAL)
            self.takeyslice.configure(state=tk.NORMAL)



    def stop_liveacquisition(self):

        self.running = False


 
    def acquireimage(self):

        self.captureexception = False
        
        self.capturemultiframe()

        if self.captureexception == False:

            self.displayimage()
            self.integrateimage()

            self.savearray.configure(state=tk.NORMAL)
            self.saveimage.configure(state=tk.NORMAL, command=self.save_asimage)



    def acquirexslice(self):

        self.captureexception = False

        self.savearray.configure(state=tk.DISABLED)
        self.saveimage.configure(state=tk.DISABLED)
        
        self.capturemultiframe()

        if self.captureexception == False:

            self.slice = numpy.sum(self.image_data, axis=0, dtype=int)
            self.pixelvalues = numpy.arange(self.xstart,self.xend, dtype=int)

            self.displayslice()

            self.saveslice.configure(state=tk.NORMAL, text="Save X-slice")


    
    def acquireyslice(self):

        self.captureexception = False

        self.savearray.configure(state=tk.DISABLED)
        self.saveimage.configure(state=tk.DISABLED)
        
        self.capturemultiframe()

        if self.captureexception == False:

            self.slice = numpy.sum(self.image_data, axis=1, dtype=int)
            self.pixelvalues = numpy.arange(self.ystart,self.yend, dtype=int)

            self.displayslice()
        
            self.saveslice.configure(state=tk.NORMAL, text="Save Y-slice")



    def capturemultiframe(self):

        self.setup_acquisition()
        self.node_acquisitionmode.SetIntValue(2)
        node_framecount = PySpin.CIntegerPtr(self.nodemap.GetNode("AcquisitionFrameCount"))
        node_framecount.SetValue(int(self.sumimages.get()))
 
        self.sumimages.configure(state=tk.DISABLED)
        self.saveslice.configure(state=tk.DISABLED)
        
        self.camera.BeginAcquisition()
        self.getmultiframeimage()

        if self.captureexception == False:
            self.xstart = int(self.xpixelstart.get()) 
            self.xend = int(self.xpixelend.get()) + 1
            self.ystart = int(self.ypixelstart.get())
            self.yend = int(self.ypixelend.get()) +1
            self.image_data = self.sumimage[self.ystart:self.yend,self.xstart:self.xend]
            self.camera.EndAcquisition()

        self.sumimages.configure(state=tk.NORMAL)

       

    def getmultiframeimage(self):

        self.sumimage = numpy.zeros((964,1288), int)

        for i in range(int(self.sumimages.get())):

            try:
                image_result = self.camera.GetNextImage(2000)
                frame_data = image_result.GetNDArray()
                self.sumimage += frame_data
        
            except PySpin.SpinnakerException as ex:
            
                try:
                    self.camera.EndAcquisition()
                except PySpin.SpinnakerException:
                    pass
                messagebox.showerror("Error", "Stopped after {} images: {}".format(i,ex))
                self.captureexception = True
                return

        image_result.Release()



    def displayimage(self):
        
        histo, bin_steps = numpy.histogram(self.image_data, bins=[0,32,64,96,128,160,192,224,255], range=(0,256))
        x = [16,48,80,112,144,176,208,240]
        self.imagedisplay.clear()
        self.imagedisplay.imshow(self.image_data, cmap="gray", vmin=0, vmax=255)
        self.imagedisplay.axhline(y=int(self.ypixelstart.get()), color="red", linewidth=0.3)
        self.imagedisplay.axhline(y=int(self.ypixelend.get()), color="red", linewidth=0.3)
        self.imagedisplay.axvline(x=int(self.xpixelstart.get()), color="red", linewidth=0.3)
        self.imagedisplay.axvline(x=int(self.xpixelend.get()), color="red", linewidth=0.3)
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



    def displayslice(self):

        self.imagedisplay.set_aspect("auto")
        self.imagedisplay.clear()
        self.imagedisplay.plot(self.pixelvalues, self.slice)
        self.histogram.clear()
        self.canvas.draw()


    
    def integrateimage(self):

        self.totalsignal = numpy.sum(self.image_data)
        self.signallabel.configure(text="Total signal: {}".format(self.totalsignal))



    def save_asarray(self):
        
        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save array as:", filetypes=(("Binary numpy array file", "*.npy"),("All files","*.*")))
        numpy.save(filename, self.image_data)



    def save_asimage(self):

        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save image as:", filetypes=(("PNG files", "*.png"),("All files","*.*")))
        matplotlib.image.imsave(filename, self.image_data, vmin=0, cmap="gray")



    def save_slice(self):

        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save image as:", filetypes=(("Binary numpy array file", "*.npy"),("Text files","*.txt"),("All files", "*.*")))
        self.slicearray = numpy.empty((len(self.pixelvalues), 2), dtype=int)
        self.slicearray[:,0] = self.pixelvalues
        self.slicearray[:,1] = self.slice
        if filename[-3:] == "txt":
            numpy.savetxt(filename, self.slicearray, fmt="%i")
        elif filename[-3:] == "npy":
            numpy.save(filename, self.slicearray)
        else:
            messagebox.showerror("Error", "Please specify file extension (.txt, .npy)")



    def saveparameterfile(self):

        exposure = self.node_exposuretime.GetValue()
        gain = self.node_gain.GetValue()
        xstart = int(self.xpixelstart.get()) 
        xend = int(self.xpixelend.get()) + 1
        ystart = int(self.ypixelstart.get()) 
        yend = int(self.ypixelend.get()) + 1

        parameters = {"Exposure time": exposure, "Gain": gain, "Lower end x": xstart, "Upper end x": xend, "Lower end y": ystart, "Upper end x": yend}
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

        
    




