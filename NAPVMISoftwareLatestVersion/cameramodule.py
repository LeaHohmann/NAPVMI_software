import PySpin
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import numpy
import matplotlib 
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import colors
import ast
import time
import threading

class CameraApp(tk.Frame):


    def __init__(self,root,system,camera):
        tk.Frame.__init__(self,root)
        self.pack()

        self.root = root
        self.system = system
        self.camera = camera
        self.nodemap = self.camera.GetNodeMap()
        self.streamnodemap = self.camera.GetTLStreamNodeMap()
        
        self.wbrpoints = {"red":((0.0,1,1),(0.5,0.0,0.0),(1.0,1.0,1.0)),"green":((0.0,1.0,1.0),(0.5,0.0,0.0),(1.0,0.0,0.0)),"blue":((0.0,1.0,1.0),(0.5,0.0,0.0),(1.0,0.0,0.0))}
        self.cmapwbr = colors.LinearSegmentedColormap("wbr",segmentdata=self.wbrpoints)
        
        self.cmaplist = {"inferno": "inferno", "wbr": self.cmapwbr}

        self.camerasetup()
        self.guiinit()
        
        self.autorange()



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
        self.exposureslider.pack(side=tk.TOP, pady=(0,5))
        
        self.manualexposureframe = tk.Frame(self.leftframe)
        self.manualexposureframe.pack(side=tk.TOP, pady=(0,20))

        self.exposureentry = tk.Entry(self.manualexposureframe)
        self.exposureentry.pack(side=tk.LEFT)
        self.exposurebutton = tk.Button(self.manualexposureframe, text="Set", command=self.setexposure)
        self.exposurebutton.pack(side=tk.LEFT, padx=5)

        self.gainlabel = tk.Label(self.leftframe, text="Gain: {}".format(round(self.node_gain.GetValue(),2)), anchor=tk.NW, font=("Helvetica",12))
        self.gainlabel.pack(side=tk.TOP, pady=5)

        self.gainslider = tk.Scale(self.leftframe, from_=-10.75, to=23.05, resolution=0.26, orient=tk.HORIZONTAL, length=200, command=self.gain)
        self.gainslider.set(self.node_gain.GetValue())
        self.gainslider.pack(side=tk.TOP, pady=(0,5))

        self.manualgainframe = tk.Frame(self.leftframe)
        self.manualgainframe.pack(side=tk.TOP, pady=(0,20))

        self.gainentry = tk.Entry(self.manualgainframe)
        self.gainentry.pack(side=tk.LEFT)
        self.gainbutton = tk.Button(self.manualgainframe, text="Set", command=self.setgain)
        self.gainbutton.pack(side=tk.LEFT, padx=5)

        self.sumimageslabel = tk.Message(self.leftframe, text="Number of frames to sum:", anchor=tk.NW, font=("Helvetica,12"), width=250)
        self.sumimageslabel.pack(side=tk.TOP, pady=5)

        self.sumimages = tk.Entry(self.leftframe)
        self.sumimages.pack(side=tk.TOP, pady=(0,30))
        self.sumimages.insert(tk.END, "1")

        self.thresholdlabel = tk.Label(self.leftframe, text="Threshold:", font=("Helvetica",12))
        self.thresholdlabel.pack(side=tk.TOP, pady=5)

        self.thresholdentry = tk.Entry(self.leftframe)
        self.thresholdentry.pack(side=tk.TOP, pady=(0,30))
        self.thresholdentry.insert(tk.END, "0")
        
        self.colorrangelabel = tk.Label(self.leftframe, text="Color map:", font=("Helvetica",12))
        self.colorrangelabel.pack(side=tk.TOP, pady=5)

        self.cmap = tk.StringVar(self.leftframe)
        self.cmap.set("inferno")
        self.cmapselect = tk.OptionMenu(self.leftframe, self.cmap, *self.cmaplist.keys())
        self.cmapselect.pack(side=tk.TOP,pady=(0,5))

        self.colorrangeframe = tk.Frame(self.leftframe)
        self.colorrangeframe.pack(side=tk.TOP, pady=(0.20))

        self.colorrangelower = tk.Entry(self.colorrangeframe)
        self.colorrangelower.pack(side=tk.LEFT,pady=(0,20))
        self.colorrangelower.insert(tk.END,"0")

        self.colorrangeupper = tk.Entry(self.colorrangeframe)
        self.colorrangeupper.pack(side=tk.LEFT,pady=(0,20))
        self.colorrangeupper.insert(tk.END,"255")

        self.autovar = tk.IntVar()
        self.rangeauto = tk.Checkbutton(self.colorrangeframe, text="Auto", variable=self.autovar, onvalue=1, offvalue=0)
        self.rangeauto.pack(side=tk.LEFT,pady=(0,20))
        
        self.zoomlabel = tk.Label(self.leftframe, text="Select zoom region:", font=("Helvetica",12))
        self.zoomlabel.pack(side=tk.TOP,pady=5)
        
        self.zoomframe1 = tk.Frame(self.leftframe)
        self.zoomframe1.pack(side=tk.TOP, pady=(0,5))
        
        self.zoominstruction = tk.Label(self.zoomframe1, text="Enter zoom region center and width (whole image: 1287x963)")
        self.zoominstruction.pack(side=tk.TOP,pady=5)
        
        self.xlabel = tk.Label(self.zoomframe1, text="Center X:")
        self.xlabel.pack(side=tk.LEFT)
        
        self.xcenter = tk.Entry(self.zoomframe1)
        self.xcenter.pack(side=tk.LEFT)
        
        self.ylabel = tk.Label(self.zoomframe1, text="Y:")
        self.ylabel.pack(side=tk.LEFT)
        
        self.ycenter = tk.Entry(self.zoomframe1)
        self.ycenter.pack(side=tk.LEFT)
        
        self.zoomframe2 = tk.Frame(self.leftframe)
        self.zoomframe2.pack(side=tk.TOP,pady=(0,5))
        
        self.widthlabel = tk.Label(self.zoomframe2, text="Width:")
        self.widthlabel.pack(side=tk.LEFT)
        
        self.width = tk.Entry(self.zoomframe2)
        self.width.pack(side=tk.LEFT)
        
        self.heightlabel = tk.Label(self.zoomframe2, text="Height:")
        self.heightlabel.pack(side=tk.LEFT)
        
        self.height = tk.Entry(self.zoomframe2)
        self.height.pack(side=tk.LEFT)
        
        self.zoomframe3 = tk.Frame(self.leftframe)
        self.zoomframe3.pack(side=tk.TOP,pady=(0,20))
        
        self.displayzoom = tk.IntVar(self.zoomframe3, value=0)
        self.zoomdisplay = tk.Checkbutton(self.zoomframe3, text="Apply zoom to display", variable=self.displayzoom, onvalue=1, offvalue=0)
        self.zoomdisplay.pack(side=tk.LEFT)
        
        self.datazoom = tk.IntVar(self.zoomframe3, value=0)
        self.zoomdata = tk.Checkbutton(self.zoomframe3, text="Apply zoom to data", variable=self.datazoom, onvalue=1, offvalue=0)
        self.zoomdata.pack(side=tk.LEFT)
        
        self.zoomint = tk.Button(self.zoomframe3, text="Show integrated signal", command=self.integratezoom, state=tk.DISABLED)
        self.zoomint.pack(side=tk.LEFT)
        self.zoomintegration = False
        
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
        
        self.statuslabel = tk.Label(self.rightframe, text="", font=("Helvetica,11"), anchor=tk.E, background="White")
        self.statuslabel.pack(side=tk.TOP,expand=1, fill=tk.X, pady=(0,10))
        
        self.summedlive = tk.Button(self.rightframe, text="Live", command=self.start_multiframelive)
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
        
        
    
    def autorange(self):
    
        self.xstart = 0
        self.xend = 1287
        self.ystart = 0
        self.yend = 963

       
    
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



    def setexposure(self):

        try:
            self.exposureslider.set(float(self.exposureentry.get()))
        except KeyError:
            messagebox.showerror("Error", "Please enter an exposure value to set")



    def exposuretime(self,value):

        self.node_exposuretime.SetValue(float(value))
        self.exposurelabel.configure(text="Exposure time [us] : {}".format(round(self.node_exposuretime.GetValue(),2)))


    
    def setgain(self):
        
        try:
            self.gainslider.set(float(self.gainentry.get()))
        except KeyError:
            messagebox.showerror("Error", "Please enter a gain value to set")


    
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
        
        if self.datazoom.get() == 1:
            self.zoomdisplay.select()
        
        try:
            self.threshold = int(self.thresholdentry.get())
        except ValueError:
            messagebox.showerror("Error", "Set threshold as integer number. No thresholding performed")
            self.thresholdentry.delete(0,tk.END)
            self.thresholdentry.insert(tk.END,"0")
            self.threshold = 0
    
                
       
    def start_liveacquisition(self):
        self.setup_acquisition()
        self.node_acquisitionmode.SetIntValue(0)

        self.savearray.configure(state=tk.DISABLED)
        self.saveimage.configure(state=tk.DISABLED)
        self.saveslice.configure(state=tk.DISABLED)
        self.signalwarnings.configure(text="")

        self.running = True
        self.camera.BeginAcquisition()


   
    def start_multiframelive(self):

        self.start_liveacquisition()
        self.summedlive.configure(text="Stop", command=self.stop_acquisition)
        self.multiframe.configure(state=tk.DISABLED)
        self.takexslice.configure(state=tk.DISABLED)
        self.takeyslice.configure(state=tk.DISABLED)
        if self.datazoom.get() == 0 and self.displayzoom.get() == 0:
            self.zoomint.configure(state=tk.NORMAL)
            self.zoomdisplay.configure(state=tk.DISABLED)
            self.zoomdata.configure(state=tk.DISABLED)

        self.multiframeloop()



    def multiframeloop(self):

        self.captureexception = False
        
        self.sumimage = numpy.zeros((964,1288), int)
        self.lasttwenty = numpy.zeros((964,1288), int)

        try:
            framecount = int(self.sumimages.get())
        except ValueError:
            framecount = 1
        
        self.counter = 0
        t1 = threading.Thread(target=lambda: self.getmultiframeimage(framecount))
        t1.start()
        
        self.multiframeloop2(framecount)
        
        
        
    def multiframeloop2(self,framecount):
    
        if self.counter < framecount and self.running:
        
            self.after(2, lambda: self.multiframeloop2(framecount))
 
        else:
        
            if self.captureexception == False:

                self.image_data = self.sumimage
                
                self.displayimage(framecount)
                self.integrateimage()

            if self.running and self.captureexception == False:
                self.after(1, self.multiframeloop)
            else:
                try:
                    self.camera.EndAcquisition()
                except PySpin.SpinnakerException:
                    pass
                self.signalwarnings.configure(text="")
                self.summedlive.configure(text="Live", command=self.start_multiframelive)
                self.multiframe.configure(state=tk.NORMAL)
                self.takexslice.configure(state=tk.NORMAL)
                self.takeyslice.configure(state=tk.NORMAL)


    def stop_acquisition(self):

        self.running = False
        self.statuslabel.configure(text="Acquisition stopped")
        if self.datazoom.get() == 0 and self.displayzoom.get() == 0:
            self.zoomint.configure(state=tk.DISABLED)
            self.zoomdisplay.configure(state=tk.NORMAL)
            self.zoomdata.configure(state=tk.NORMAL)


 
    def acquireimage(self):

        self.captureexception = False
        self.running = True
        
        self.imtype = "image"
        
        self.multiframe.configure(text="Stop", command=self.stop_acquisition)
        
        self.capturemultiframe()

       
       

    def acquirexslice(self):

        self.captureexception = False
        self.running = True

        self.savearray.configure(state=tk.DISABLED)
        self.saveimage.configure(state=tk.DISABLED)
        
        self.imtype = "xslice"
        
        self.takexslice.configure(text="Stop", command=self.stop_acquisition)
        
        self.capturemultiframe()

        

    
    def acquireyslice(self):

        self.captureexception = False
        self.running = True

        self.savearray.configure(state=tk.DISABLED)
        self.saveimage.configure(state=tk.DISABLED)
        
        self.imtype = "yslice"
        
        self.takeyslice.configure(text="Stop", command=self.stop_acquisition)
        
        self.capturemultiframe()
            



    def capturemultiframe(self):

        self.setup_acquisition()
        self.node_acquisitionmode.SetIntValue(0)
 
        self.sumimages.configure(state=tk.DISABLED)
        self.saveslice.configure(state=tk.DISABLED)
        
        self.camera.BeginAcquisition()
        
        self.sumimage = numpy.zeros((964,1288), int)
        self.lasttwenty = numpy.zeros((964,1288), int)
        
        try:
            framecount = int(self.sumimages.get())
        except ValueError:
            framecount = 1
        
        self.counter = 0
        t1 = threading.Thread(target=lambda: self.getmultiframeimage(framecount))
        t1.start()
        
        self.capturemultiframe2(framecount)
        
        
        
    def capturemultiframe2(self, framecount):
    
        if self.counter < framecount and self.running:
        
            if self.counter%20 == 0:
                displaydata = self.lasttwenty
                self.quickdisplay(displaydata)
                self.lasttwenty = numpy.zeros((964,1288), int)
        
            self.after(2, lambda: self.capturemultiframe2(framecount))

        else:

            if self.captureexception == False:
                
                if self.datazoom.get() == 1:  
                    self.image_data = self.sumimage[self.ystart:self.yend,self.xstart:self.xend]
                else:
                    self.image_data = self.sumimage
                    
            
                if self.imtype == "image":
                
                    self.displayimage(framecount)
                    self.integrateimage()

                    self.savearray.configure(state=tk.NORMAL)
                    self.saveimage.configure(state=tk.NORMAL, command=self.save_asimage)
                    self.multiframe.configure(text="Single image", command=self.acquireimage)
                
                elif self.imtype == "xslice":
                
                    self.slicedata = numpy.sum(self.image_data, axis=0, dtype=int)
                    if self.datazoom.get() == 1:
                        self.pixelvalues = numpy.arange(self.xstart,self.xend, dtype=int)
                    else:
                        self.pixelvalues = numpy.arange(0,1287, dtype=int)

                    self.displayslice(self.xstart,self.xend)

                    self.saveslice.configure(state=tk.NORMAL, text="Save X-slice")
                    self.takexslice.configure(text="X-slice", command=self.acquirexslice)
                    
                elif self.imtype == "yslice":
                
                    self.slicedata = numpy.sum(self.image_data, axis=1, dtype=int)
                    if self.datazoom.get() == 1:
                        self.pixelvalues = numpy.arange(self.ystart,self.yend, dtype=int)
                    else:
                        self.pixelvalues = numpy.arange(0,963, dtype=int)

                    self.displayslice(self.ystart,self.yend)
                
                    self.saveslice.configure(state=tk.NORMAL, text="Save Y-slice")
                    self.takeyslice.configure(text="Y-slice", command=self.acquireyslice)
                    
                self.statuslabel.configure(text="Acquisition finished")


            self.camera.EndAcquisition() 

            self.sumimages.configure(state=tk.NORMAL)

       

    def getmultiframeimage(self,framecount):

        while self.counter < framecount and self.running:
        
            try:
                image_result = self.camera.GetNextImage(3000)
                frame_data = image_result.GetNDArray()
                if self.threshold > 0:
                    frame_data = frame_data*(frame_data>self.threshold)
                self.sumimage += frame_data
                self.lasttwenty += frame_data
            
            except PySpin.SpinnakerException as ex:
                
                try:
                    self.camera.EndAcquisition()
                except PySpin.SpinnakerException:
                    pass
                messagebox.showerror("Error", "Stopped after {} images: {}".format(self.counter,ex))
                self.captureexception = True
                running = False
                return

            image_result.Release()
            self.statuslabel.configure(text="Acquisition: {} of {} frames".format(self.counter,framecount))
            self.counter += 1
            
            time.sleep(0.05)



    def displayimage(self,framecount):
        
        try:
            self.uppercrange = int(self.colorrangeupper.get())
            self.lowercrange = int(self.colorrangelower.get())
        except ValueError:
            self.uppercrange = 255
            self.lowercrange = 0
           
        if self.displayzoom.get() == 1 or self.zoomintegration == True:
            try:
                self.xstart = int(int(self.xcenter.get())-int(self.width.get())/2)
                self.xend = int(int(self.xcenter.get())+int(self.width.get())/2)
                self.ystart = int(int(self.ycenter.get())-int(self.height.get())/2)
                self.yend = int(int(self.ycenter.get())+int(self.height.get())/2)
            except ValueError:
                messagebox.showerror("Error", "Invalid zoom range values, no zoom performed")
                self.zoomdisplay.deselect()
                self.zoomdata.deselect()
                self.autorange()
        
        if self.displayzoom.get() == 1 and self.datazoom.get() == 0:
            displayimage = self.image_data[self.ystart:self.yend,self.xstart:self.xend]
        else:
            displayimage = self.image_data

        perframe = self.image_data/framecount
        histo, bin_steps = numpy.histogram(perframe.astype(int), bins=[0,32,64,96,128,160,192,224,255], range=(0,256))
        x = [16,48,80,112,144,176,208,240]
        self.imagedisplay.clear()
        if self.autovar.get() == 0:
            self.imagedisplay.imshow(displayimage, cmap=self.cmaplist[self.cmap.get()], vmin=self.lowercrange, vmax=self.uppercrange)
        else:
            self.imagedisplay.imshow(displayimage, cmap=self.cmaplist[self.cmap.get()])
        if self.zoomintegration == True:
            self.imagedisplay.plot([self.xstart,self.xend],[self.ystart,self.ystart],color="green",linewidth=1)
            self.imagedisplay.plot([self.xstart,self.xstart],[self.ystart,self.yend],color="green",linewidth=1)
            self.imagedisplay.plot([self.xend,self.xend],[self.ystart,self.yend],color="green",linewidth=1)
            self.imagedisplay.plot([self.xstart,self.xend],[self.yend,self.yend],color="green",linewidth=1)
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
            
            
            
            
    def quickdisplay(self,displaydata):
    
        perframe = displaydata/20
        histo, bin_steps = numpy.histogram(perframe.astype(int), bins=[0,32,64,96,128,160,192,224,255], range=(0,256))
        x = [16,48,80,112,144,176,208,240]
        self.imagedisplay.clear()
        
        self.imagedisplay.imshow(displaydata, cmap=self.cmaplist[self.cmap.get()])
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
            



    def displayslice(self,start,end):

        self.imagedisplay.set_aspect("auto")
        self.imagedisplay.clear()
        if self.dispayzoom.get() == 1 and self.datazoom.get() == 0:
            self.imagedisplay.plot(self.pixelvalues[start:end], self.slicedata[start:end])
        self.imagedisplay.plot(self.pixelvalues, self.slicedata)
        self.histogram.clear()
        self.canvas.draw()


    
    def integrateimage(self):

        if self.displayzoom.get() == 1 and self.datazoom.get() == 0:
            self.totalsignal = numpy.sum(self.image_data[self.ystart:self.yend,self.xstart:self.xend])
        else:
            self.totalsignal = numpy.sum(self.image_data)
        self.signallabel.configure(text="Total signal: {}".format(self.totalsignal))
        
        if self.zoomintegration == True:
            self.zoomsignal = numpy.sum(self.image_data[self.ystart:self.yend,self.xstart:self.xend])
            self.zoomintlabel.configure(text=str(self.zoomsignal))
            
        
        
        
    def integratezoom(self):
    
        self.zoomintwindow = tk.Toplevel(self,width=400,height=200)
        self.zoomintlabel = tk.Label(self.zoomintwindow,text="0", font=("Helvetica", 40))
        self.zoomintlabel.pack()
        
        self.zoomint.configure(state=tk.DISABLED)
        self.zoomintegration = True
        
        self.zoomintwindow.protocol("WM_DELETE_WINDOW", self.quitzoomint)
        
    
    def quitzoomint(self):
    
        self.zoomintegration = False
        self.zoomint.configure(state=tk.NORMAL)
        
        self.zoomintwindow.destroy()
        



    def save_asarray(self):
        
        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save array as:", filetypes=(("Binary numpy array file", "*.npy"),("All files","*.*")))
        if filename[-4:] != ".npy":
            filename = filename + ".npy"
        
        numpy.save(filename, self.image_data)

        paramfilename = filename[:-4] + "_parameters.txt"
        self.parametersaver(paramfilename)




    def save_asimage(self):

        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save image as:", filetypes=(("PNG files", "*.png"),("All files","*.*")))
        matplotlib.image.imsave(filename, self.image_data, vmin=0, cmap="gray")

        paramfilename = filename[:-4] + "_parameters.txt"
        self.parametersaver(paramfilename)



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

        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save parameters:", filetypes=(("Text files", "*.txt"),("All files", "*.*")))

        self.parametersaver(filename)

        

    def parametersaver(self,filename):

        exposure = self.node_exposuretime.GetValue()
        gain = self.node_gain.GetValue()
        framecount = int(self.sumimages.get())
        threshold = int(self.thresholdentry.get())
        xstart = self.xstart 
        xend = self.xend
        ystart = self.ystart 
        yend = self.yend

        parameters = {"Exposure time": exposure, "Gain": gain, "Number of frames": framecount, "Threshold": threshold, "Lower end x": xstart, "Upper end x": xend, "Lower end y": ystart, "Upper end y": yend}
        
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
        framecount = parameters["Number of frames"]
        threshold = parameters["Threshold"]
        x = (parameters["Lower end x"],parameters["Upper end x"])
        y = (parameters["Lower end y"],parameters["Upper end y"])
        width = int(x[1])-int(x[0])
        height = int(y[1])-int(y[0])
        self.node_exposuretime.SetValue(exposuretime)
        self.exposureslider.set(self.node_exposuretime.GetValue())
        self.exposurelabel.configure(text="Exposure time [us]: {}".format(round(self.node_exposuretime.GetValue(),2)))
        self.node_gain.SetValue(gain)
        self.gainslider.set(self.node_gain.GetValue())
        self.gainlabel.configure(text="Gain: {}".format(round(self.node_gain.GetValue(),2)))
        self.sumimages.delete(0,tk.END)
        self.sumimages.insert(0,str(framecount))
        self.thresholdentry.delete(0,tk.END)
        self.thresholdentry.insert(0,str(threshold))
        self.width.delete(0,tk.END)
        self.width.insert(0,str(width))
        self.height.delete(0,tk.END)
        self.height.insert(0,str(height))
        self.xcenter.delete(0,tk.END)
        self.xcenter.insert(0,str(int(x[0])+width//2))
        self.ycenter.delete(0,tk.END)
        self.ycenter.insert(0,str(int(y[0])+height//2))



    def quit_cameraapp(self):

        self.camera = ""

        
    




